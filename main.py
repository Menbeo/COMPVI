import pygame
import cv2
import mediapipe as mp
import numpy as np
import sys
import time
import math
import os

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
object_img = pygame.image.load("duongpm.png")
object_img = pygame.transform.scale(object_img, (50, 50))

# --- Functions ---
def ask_player_name():
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_active
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

def show_high_scores():
    screen.blit("bg.jpg", (0,0))
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

# --- Player Name ---
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

# --- Main Game Loop ---
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    running = True
    while running:
        screen.blit(background, (0, 0))

        # --- Pygame Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Webcam Frame ---
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
                cv2.circle(image, (int(x9), int(y9)), 10, (0, 255, 0), -1)
                cv2.circle(image, (int(x12), int(y12)), 10, (0, 0, 255), -1)

        # --- Show Webcam ---
        cv2.imshow('MediaPipe Hands', image)

        # --- Draw Hand & Object ---
        pygame.draw.circle(screen, (0, 255, 0), (hand_x, hand_y), 30)
        screen.blit(object_img, (object_x, object_y))
        object_y += fall_speed

        # --- Catch Detection ---
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

        # Exit with ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
