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
pygame.display.set_caption("Catch Your Professor")
font = pygame.font.SysFont('arcadeclassic', 50)

# --- Camera setting ---
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
sw, sh = 640, 480
cap.set(3, sw)
cap.set(4, sh)

# --- Dummy Falling Object ---
object_x = np.random.randint(100, 700)
object_y = 0
fall_speed = 5
speed_increase_interval = 5  # mỗi 5 giây tăng tốc 1 lần
last_speed_update = 0

# --- Score & Timer ---
score = 0
start_time = time.time()
game_duration = 30  # seconds

# --- Load background and object image ---
background = pygame.image.load("bg.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

object_img = pygame.image.load("duongpm.png")
object_img = pygame.transform.scale(object_img, (1687 // 50, 3000 // 50))

# --- Load unwanted object image ---
unwanted_object_img = pygame.image.load("F.png")
unwanted_object_img = pygame.transform.scale(unwanted_object_img, (90, 60))  # scale unwanted object size

# --- Multiple falling objects ---
num_objects = 5
objects = []
for _ in range(num_objects):
    x = np.random.randint(100, 700)
    y = np.random.randint(-600, 0)  # random height above screen
    objects.append([x, y])

# --- Multiple falling unwanted objects ---
unwanted_objects = []
for _ in range(num_objects):
    x = np.random.randint(100, 700)
    y = np.random.randint(-600, 0)  # random height above screen
    unwanted_objects.append([x, y])

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

            # --- Check Catch with both hands for regular objects ---
            for hand in hand_positions:
                dx = hand['x'] - (obj_x + 25)
                dy = hand['y'] - (obj_y + 25)
                distance = math.hypot(dx, dy)

                # Check for catching regular objects
                if (
                    distance < catch_distance and
                    hand['status'] == "Closed" and
                    hand['prev_status'] == "OPEN"
                ):
                    score += 1
                    print(f"Caught! Score: {score}")
                    objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0)]  # reset the object
                    break

        # --- Falling Unwanted Objects ---
        for i in range(len(unwanted_objects)):
            unwanted_obj_x, unwanted_obj_y = unwanted_objects[i]
            screen.blit(unwanted_object_img, (unwanted_obj_x, unwanted_obj_y))
            unwanted_obj_y += fall_speed
            unwanted_objects[i][1] = unwanted_obj_y

            # --- Check for overlap with unwanted objects ---
            for hand in hand_positions:
                dx = hand['x'] - (unwanted_obj_x + 25)
                dy = hand['y'] - (unwanted_obj_y + 25)
                distance = math.hypot(dx, dy)

                # Check for overlap (distance should be less than catch_distance)
                if distance < catch_distance:
                    score -= 1  # Decrease score when overlapping with unwanted object
                    print(f"Unwanted Object Overlap! Score: {score}")
                    unwanted_objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0)]  # reset the unwanted object
                    break

        # --- If unwanted object falls out of screen ---
        for i in range(len(unwanted_objects)):
            unwanted_obj_x, unwanted_obj_y = unwanted_objects[i]
            if unwanted_obj_y > HEIGHT:
                unwanted_objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0)]  # reset unwanted object

        # --- Score + Timer ---
        current_time = int(time.time() - start_time)
        remaining = max(0, game_duration - current_time)
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        time_text = font.render(f"Time left: {remaining}s", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 40))

        # --- Game Over Handling ---
        if remaining <= 0:
            game_over = font.render("Game Over!", True, (255, 0, 0))
            screen.blit(game_over, (WIDTH // 2 - 80, HEIGHT // 2))
            pygame.display.update()
            pygame.time.wait(3000)
            break

        # Tăng tốc độ rơi theo thời gian
        if current_time - last_speed_update >= speed_increase_interval:
            fall_speed += 0.2  # tăng nhẹ
            last_speed_update = current_time

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