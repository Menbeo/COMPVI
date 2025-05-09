import pygame
import cv2
import mediapipe as mp
import numpy as np
import sys
import time
import math
import os

# --- Sound ---
pygame.init()
pygame.mixer.init()
bg_sfx = pygame.mixer.Sound("background_music.mp3")
bg_sfx.set_volume(0.3)


# --- Game Level ---
current_level = 1 

# --- Init MediaPipe ---
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# --- Init Pygame ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Your Professor!")
font = pygame.font.SysFont('Arial', 24)

# --- Camera Setting ---
cap = cv2.VideoCapture(0)
sw, sh = 640, 480
cap.set(3, sw)
cap.set(4, sh)

# --- Load background and object image ---
background = pygame.image.load("bg.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
object_img = pygame.image.load('duongpm.png')
object_img = pygame.transform.scale(object_img, (50, 50)) 

# --- Falling Obstacles Images ---
obstacles_img = ['F.png', 'kahoot.png'] 
obstacles_img2 = ['quanle.png', 'vinhlinh.png'] 
unwanted_img = [pygame.transform.scale(pygame.image.load(img), (90, 60)) for img in obstacles_img]
unwanted_img2 = [pygame.transform.scale(pygame.image.load(img), (20, 10)) for img in obstacles_img]

# --- Player Name ---
def ask_player_name():
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 40)
    color = pygame.Color('dodgerblue2')
    text = ''
    done = False

    while not done:
        screen.fill((255, 255, 255))
        title = font.render("Enter your name:", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(text) > 0:
                    return text
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 15:
                        text += event.unicode

        txt_surface = font.render(text, True, (0, 0, 0))
        input_box.w = max(200, txt_surface.get_width() + 10)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        pygame.time.Clock().tick(30)

# --- Score Functions ---
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

# --- Initialize Player Name ---
bg_sfx.play(loops=-1)
player_name = ask_player_name()

# --- Game Variables ---
object_x = np.random.randint(100, 700)
object_y = 0
fall_speed = 5
score = 0
start_time = time.time()
game_duration = 30  # seconds
hand_status = "OPEN"
hand_x, hand_y = 0, 0
catch_distance = 50

# --- Initialize Falling Obstacles ---
num_obstacles = 10
falling_obstacles = []

def generate_obstacles(num, base_speed):
    obstacles = []
    for i in range(num // 2): 
        obstacles.append({
            'image': unwanted_img[i % len(unwanted_img)],
            'x': np.random.randint(100, 700),
            'y': -60 * (i + 1),  
            'fall_speed': base_speed + (i % 3)
        })
    for i in range(num // 2, num):
        obstacles.append({
            'image': unwanted_img2[i % len(unwanted_img2)],  # Using the second set of obstacles
            'x': np.random.randint(100, 700),
            'y': -60 * (i - num // 2 + 1) + 150,  # Adjust for second row (add offset for falling lower)
            'fall_speed': base_speed + (i % 3)
        })
    return obstacles

falling_obstacles = generate_obstacles(num_obstacles, 3)

# --- Main Game Loop ---
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    running = True
    while running:
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x9 = hand_landmarks.landmark[9].x * sw
                y9 = hand_landmarks.landmark[9].y * sh
                x12 = hand_landmarks.landmark[12].x * sw
                y12 = hand_landmarks.landmark[12].y * sh

                hand_x = int(x9 / sw * WIDTH)
                hand_y = int(y9 / sh * HEIGHT)

                hand_status = "Closed" if y12 > y9 else "OPEN"

        cv2.imshow('MediaPipe Hands', image)

        # --- Draw Hand & Object ---
        pygame.draw.circle(screen, (0, 255, 0), (hand_x, hand_y), 30)
        screen.blit(object_img, (object_x, object_y))
        object_y += fall_speed

        # --- Catch Main Object ---
        dx = hand_x - (object_x + 25)
        dy = hand_y - (object_y + 25)
        distance = math.hypot(dx, dy)

        if distance < catch_distance and hand_status == "Closed":
            score += 1
            object_x = np.random.randint(100, 700)
            object_y = 0

        if object_y > HEIGHT:
            object_y = 0
            object_x = np.random.randint(100, 700)

        # --- Falling Obstacles ---
        for obstacle in falling_obstacles:
            obstacle['y'] += obstacle['fall_speed']
            screen.blit(obstacle['image'], (obstacle['x'], obstacle['y']))

            dx_ob = hand_x - (obstacle['x'] + 45)
            dy_ob = hand_y - (obstacle['y'] + 30)
            dist_ob = math.hypot(dx_ob, dy_ob)

            if dist_ob < catch_distance and hand_status == "Closed":
                score -= 1
                obstacle['y'] = -60
                obstacle['x'] = np.random.randint(100, 700)

            if obstacle['y'] > HEIGHT:
                obstacle['y'] = -60
                obstacle['x'] = np.random.randint(100, 700)

        # --- LEVEL UP ---
        if current_level == 1 and score > 10:

            current_level = 2
            game_duration  = game_duration - 10
            fall_speed += 1
            falling_obstacles += generate_obstacles(5, 4)
            print("Level 2")

        if current_level == 2 and score > 20:
            current_level = 3
            fall_speed += 2
            game_duration = game_duration - 10
            falling_obstacles += generate_obstacles(5, 5)
            print("Level 3")

        # --- Score and Timer ---
        current_time = int(time.time() - start_time)
        remaining = max(0, game_duration - current_time)
        screen.blit(font.render(f"Score: {score}", True, (0, 0, 0)), (10, 10))
        screen.blit(font.render(f"Time left: {remaining}s", True, (0, 0, 0)), (10, 40))

        if remaining <= 0:
            save_score(player_name, score)
            screen.blit(font.render("Game Over!", True, (255, 0, 0)), (WIDTH // 2 - 80, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(2000)
            show_high_scores()
            break

        pygame.display.update()
        pygame.time.Clock().tick(30)


        if cv2.waitKey(1) & 0xFF == 27:
            break

# # --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
