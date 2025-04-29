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

# --- Load background and object image ---
background = pygame.image.load("bg.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

object_img = pygame.image.load("tobias.png")
object_img = pygame.transform.scale(object_img, (50, 50))  # scale object size

# --- Multiple falling objects ---
num_objects = 5
objects = []
for _ in range(num_objects):
    x = np.random.randint(100, 700)
    y = np.random.randint(-600, 0)  # random height above screen
    objects.append([x, y])


# --- Variables ---
hand_status = "OPEN"
hand_x, hand_y = 0, 0
catch_distance = 50  # khoảng cách tay - vật thể để bắt

# --- MediaPipe Hands ---
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    running = True
    prev_hand_status = {}  # key = hand index (0, 1), value = 'OPEN' or 'Closed'

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
        hand_positions = []  # reset mỗi frame

        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                x9, y9 = hand_landmarks.landmark[9].x * sw, hand_landmarks.landmark[9].y * sh
                x12, y12 = hand_landmarks.landmark[12].x * sw, hand_landmarks.landmark[12].y * sh

                hand_px = int(x9 / sw * WIDTH)
                hand_py = int(y9 / sh * HEIGHT)

                status = "Closed" if y12 > y9 else "OPEN"
                prev_status = prev_hand_status.get(idx, "OPEN")  # mặc định OPEN nếu chưa có

                hand_positions.append({
                    'x': hand_px,
                    'y': hand_py,
                    'status': status,
                    'prev_status': prev_status,
                    'index': idx
                })

                # Cập nhật trạng thái mới nhất
                prev_hand_status[idx] = status

                # Vẽ tay
                cv2.circle(image, (int(x9), int(y9)), 10, (0, 255, 0), -1)
                cv2.circle(image, (int(x12), int(y12)), 10, (0, 0, 255), -1)
                cv2.putText(image, status, (int(x9), int(y9 - 20)), 0, 1, (255, 0, 0), 2)



        # --- Show camera feed separately ---
        cv2.imshow('MediaPipe Hands', image)

        # --- Dummy Hand on Game Screen ---
        pygame.draw.circle(screen, (0, 255, 0), (hand_x, hand_y), 30)
        for hand in hand_positions:
            pygame.draw.circle(screen, (0, 255, 0), (hand['x'], hand['y']), 30)


        # --- Falling Objects ---
        for i in range(len(objects)):
            obj_x, obj_y = objects[i]
            screen.blit(object_img, (obj_x, obj_y))
            obj_y += fall_speed
            objects[i][1] = obj_y

        for i in range(len(objects)):
            obj_x, obj_y = objects[i]
            screen.blit(object_img, (obj_x, obj_y))
            obj_y += fall_speed
            objects[i][1] = obj_y

            # --- Check Catch with both hands ---
            for i in range(len(objects)):
                obj_x, obj_y = objects[i]
                screen.blit(object_img, (obj_x, obj_y))
                obj_y += fall_speed
                objects[i][1] = obj_y

                for hand in hand_positions:
                    dx = hand['x'] - (obj_x + 25)
                    dy = hand['y'] - (obj_y + 25)
                    distance = math.hypot(dx, dy)

                    # Chỉ tính bắt nếu tay gần object và vừa chuyển từ OPEN -> Closed
                    if (
                        distance < catch_distance and
                        hand['status'] == "Closed" and
                        hand['prev_status'] == "OPEN"
                    ):
                        score += 1
                        print(f"Caught! Score: {score}")
                        objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0)]
                        break


            # --- If falls out of screen ---
            if obj_y > HEIGHT:
                objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0)]


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
