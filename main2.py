# Hand tracking + Pygame falling object + Catch logic
import pygame
import cv2
import mediapipe as mp
import numpy as np
import sys
import time
import math

# --- Init MediaPipe ---
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# --- Init Pygame ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Your Professor!")
font = pygame.font.SysFont('Arial', 24)

# --- Camera setting ---
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
sw, sh = 640, 480
cap.set(3, sw)
cap.set(4, sh)

# --- Dummy Falling Object ---
object_x = np.random.randint(100, 700)
object_y = 0
fall_speed = 5

# --- Score & Timer ---
score = 0
start_time = time.time()
game_duration = 30  # seconds

#Scoreboard
def show_scoreboard(display_surface, clock):
    scoreboard_surface = font.render('Scoreboard:', True, 'red')
    scoreboard_position = (0,0)
# --- Load background and object image ---
background = pygame.image.load("bg.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

object_img = pygame.image.load("duongpm.png")
object_img = pygame.transform.scale(object_img, (50, 50))  # scale object size

# --- Variables ---
hand_status = "OPEN"
hand_x, hand_y = 0, 0
catch_distance = 50  # khoảng cách tay - vật thể để bắt

# --- MediaPipe Hands ---
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    running = True
    while running:
        screen.blit(background, (0, 0))

        # --- Handle Pygame Events ---
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

        # --- Hand tracking ---
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x9, y9 = hand_landmarks.landmark[9].x * sw, hand_landmarks.landmark[9].y * sh
                x12, y12 = hand_landmarks.landmark[12].x * sw, hand_landmarks.landmark[12].y * sh

                hand_x, hand_y = int(x9 / sw * WIDTH), int(y9 / sh * HEIGHT)  # scale to pygame window

                # Check hand status
                if y12 > y9:
                    hand_status = "Closed"
                else:
                    hand_status = "OPEN"

                # Draw key points in OpenCV window
                cv2.circle(image, (int(x9), int(y9)), 10, (0, 255, 0), -1)
                cv2.circle(image, (int(x12), int(y12)), 10, (0, 0, 255), -1)
                cv2.putText(image, hand_status, (50, 80), 0, 1.5, (0, 0, 255), 2)

        # --- Show camera feed separately ---
        cv2.imshow('MediaPipe Hands', image)

        # --- Dummy Hand on Game Screen ---
        pygame.draw.circle(screen, (0, 255, 0), (hand_x, hand_y), 30)

        # --- Falling Object ---
        screen.blit(object_img, (object_x, object_y))
        object_y += fall_speed

        # --- Check Catch (distance + closed hand) ---
        dx = hand_x - (object_x + 25)  # +25 vì object size 50x50 (lấy tâm object)
        dy = hand_y - (object_y + 25)
        distance = math.hypot(dx, dy)

        if distance < catch_distance and hand_status == "Closed":
            score += 1
            print(f"Caught! Score: {score}")
            # Reset object
            object_x = np.random.randint(100, 700)
            object_y = 0

        # --- If object falls out of screen, reset ---
        if object_y > HEIGHT:
            object_y = 0
            object_x = np.random.randint(100, 700)

        # --- Score + Timer ---
        current_time = int(time.time() - start_time)
        remaining = max(0, game_duration - current_time)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        time_text = font.render(f"Time left: {remaining}s", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 40))

        # --- End Game ---
        if remaining <= 0:
            game_over = font.render("Game Over!", True, (255, 0, 0))
            screen.blit(game_over, (WIDTH // 2 - 80, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(3000)
            break

        pygame.display.update()
        pygame.time.Clock().tick(30)

        # --- Exit when press 'ESC' ---
        if cv2.waitKey(1) & 0xFF == 27:
            break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
