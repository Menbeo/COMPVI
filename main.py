import pygame
import cv2
import numpy as np
import sys
import time

# --- Init Pygame ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Your Professor!")
font = pygame.font.SysFont('Arial', 24)

# --- Init OpenCV ---
cap = cv2.VideoCapture(0)

# --- Dummy Falling Object ---
object_x = np.random.randint(100, 700)
object_y = 0
fall_speed = 5

# --- Score & Timer ---
score = 0
start_time = time.time()
game_duration = 30  # seconds

# --- Load background ---
background = pygame.image.load("bg.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# --- Main Loop ---
running = True
while running:
    screen.blit(background, (0, 0))

    # --- Handle Pygame Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Webcam (show in separate window) ---
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    cv2.imshow("Camera", frame)

    # --- Dummy Hand (mouse position) ---
    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.circle(screen, (0, 255, 0), (mouse_x, mouse_y), 30)

    # --- Dummy Falling Object ---
    pygame.draw.rect(screen, (255, 0, 0), (object_x, object_y, 30, 30))
    object_y += fall_speed
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

    # --- Check if user closes OpenCV window or presses 'q' ---
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
