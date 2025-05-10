import pygame
import cv2
import mediapipe as mp
import numpy as np
import sys
import time
import math
import os
# --- Lives
lives = 3
# --- Sound Setup ---
pygame.init()
pygame.mixer.init()
bg_sfx = pygame.mixer.Sound("background_music.mp3")
bg_sfx.set_volume(0.3)
wrong_sfx = pygame.mixer.Sound("wrong.mp3")
wrong_sfx.set_volume(0.3)
right_sfx = pygame.mixer.Sound("right.mp3")
right_sfx.set_volume(0.3)

# --- Start Background Music ---
bg_sfx.play(-1)

# --- Game Level ---
current_level = 1

# --- Init MediaPipe ---
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# --- Pygame Window ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Your Professor!")
font = pygame.font.SysFont('Arial', 32)

# --- Camera Setting ---
cap = cv2.VideoCapture(0)
sw, sh = 640, 480
cap.set(3, sw)
cap.set(4, sh)
# --- HIGHSCORE ----
def show_high_scores():
    screen.blit(background, (0,0))
    title = font.render("High Scores", True, (255, 0, 0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

    if os.path.exists("highscores.txt"):
        with open("highscores.txt", "r") as f:
            lines = f.readlines()
            sorted_scores = sorted([line.strip().split(":") for line in lines], key=lambda x: int(x[1]), reverse=True)[:5]
            for i, (name, score) in enumerate(sorted_scores):
                line = font.render(f"{i+1}. {name} - {score}", True, (0, 0, 0))
                screen.blit(line, (WIDTH // 2 - line.get_width() // 2, 100 + i * 40))

    pygame.display.flip()
    pygame.time.wait(5000)

def save_score(name, score):
    with open("highscores.txt", "a") as f:
        f.write(f"{name}:{score}\n")
# --- Load Images ---
background = pygame.image.load("bg.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
object_img = pygame.image.load("duongpm.png")
object_img = pygame.transform.scale(object_img, (50, 50))

obstacles_img_files = ['F.png', 'kahoot.png']
unwanted_imgs = [pygame.transform.scale(pygame.image.load(img), (90, 60)) for img in obstacles_img_files]

# --- Player Name Input ---
def ask_player_name():
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((255, 255, 255))
        title = font.render("Enter your name:", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
        txt_surface = font.render(text, True, (0, 0, 0))
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()

    return text

player_name = ask_player_name()

# --- Game Parameters ---
num_objects = 5
fall_speed = 5
speed_increase_interval = 5
last_speed_update = 0
catch_distance = 50
score = 0
start_time = time.time()
game_duration = 45

# --- Object Initialization ---
objects = [[np.random.randint(100, 700), np.random.randint(-600, 0)] for _ in range(num_objects)]
unwanted_objects = [[np.random.randint(100, 700), np.random.randint(-600, 0), np.random.randint(0, len(unwanted_imgs))] for _ in range(num_objects)]

# --- MediaPipe Hands ---
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    running = True
    prev_hand_status = {}

    while running:
        screen.blit(background, (0, 0))

        # --- Pygame Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Capture Frame ---
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # --- Hand Tracking ---
        hand_positions = []

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                x9, y9 = hand_landmarks.landmark[9].x * sw, hand_landmarks.landmark[9].y * sh
                cv2.circle(image, (int(x9), int(y9)), 10, (0, 255, 0), -1)
                x12, y12 = hand_landmarks.landmark[12].x * sw, hand_landmarks.landmark[12].y * sh
                cv2.circle(image, (int(x12), int(y12)), 10, (0, 0, 255), -1)
                hand_px = int(x9 / sw * WIDTH)
                hand_py = int(y9 / sh * HEIGHT)
                status = "Closed" if y12 > y9 else "OPEN"
                prev_status = prev_hand_status.get(idx, "OPEN")
                hand_positions.append({'x': hand_px, 'y': hand_py, 'status': status, 'prev_status': prev_status})
                prev_hand_status[idx] = status
        cv2.imshow('MediaPipe Hands', image)

        # --- Draw Hands ---
        for hand in hand_positions:
            pygame.draw.circle(screen, (0, 255, 0), (hand['x'], hand['y']), 30)

        # --- Update and Draw Objects ---
        for i in range(len(objects)):
            obj_x, obj_y = objects[i]
            screen.blit(object_img, (obj_x, obj_y))
            objects[i][1] += fall_speed

            for hand in hand_positions:
                dx = hand['x'] - (obj_x + 25)
                dy = hand['y'] - (obj_y + 25)
                if math.hypot(dx, dy) < catch_distance and hand['status'] == "Closed" and hand['prev_status'] == "OPEN":
                    score += 1
                    right_sfx.play()
                    objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0)]
                    break

        # --- Update and Draw Unwanted Objects ---
        for i in range(len(unwanted_objects)):
            ux, uy, img_idx = unwanted_objects[i]
            screen.blit(unwanted_imgs[img_idx], (ux, uy))
            unwanted_objects[i][1] += fall_speed

            for hand in hand_positions:
                dx = hand['x'] - (ux + 45)
                dy = hand['y'] - (uy + 30)
                if math.hypot(dx, dy) < catch_distance and hand['prev_status'] == "OPEN":
                    wrong_sfx.play()
                    lives -=1
                    unwanted_objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0), np.random.randint(0, len(unwanted_imgs))]
                    if lives <= 0: 
                        game_over = font.render("Out of Lives! Game Over", True, (255, 0, 0))
                        screen.blit(game_over, (WIDTH // 2 - 150, HEIGHT // 2))
                        pygame.display.update()
                        pygame.time.wait(3000)
                        running = False
                    break

            if uy > HEIGHT:
                unwanted_objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0), np.random.randint(0, len(unwanted_imgs))]
        # --- LEVEL UP --- 
        if current_level == 1 and score > 4: 
            #display the level 
            screen.blit(font.render("Level 2!", True, (255, 0, 0)), (WIDTH // 2 - 80, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(2000)
            current_level = 2
            game_duration -= 10
            fall_speed += 1
            unwanted_objects.append([np.random.randint(100, 700), np.random.randint(-600, 0), np.random.randint(0, len(unwanted_imgs))])
    
            
        if current_level == 2 and score > 8: 
            screen.blit(font.render("Level 3!", True, (255, 0, 0)), (WIDTH // 2 - 80, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(2000)
            current_level = 3 
            fall_speed += 2 
            game_duration -= 10
            unwanted_objects.append([np.random.randint(100, 700), np.random.randint(-600, 0), np.random.randint(0, len(unwanted_imgs))])

        #-heart--
        heart_img = pygame.image.load("hear.svg")
        heart_img = pygame.transform.scale(heart_img, (30,30))
        for i in range(lives):
            screen.blit(heart_img, (10 + i * 35, 90))


        # --- Score + Timer ---
        current_time = int(time.time() - start_time)
        remaining = max(0, game_duration - current_time)
        screen.blit(font.render(f"{player_name}'s Score: {score}", True, (0, 0, 0)), (10, 10))
        screen.blit(font.render(f"Time left: {remaining}s", True, (0, 0, 0)), (10, 50))
        

        if remaining <= 0:
            save_score(player_name, score)
            game_over = font.render("Game Over!", True, (255, 0, 0))
            screen.blit(game_over, (WIDTH // 2 - 80, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(3000)
            show_high_scores()
            break

        if current_time - last_speed_update >= speed_increase_interval:
            fall_speed += 0.2
            last_speed_update = current_time

        pygame.display.update()
        pygame.time.Clock().tick(30)

        if cv2.waitKey(1) & 0xFF == 27:
            break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
