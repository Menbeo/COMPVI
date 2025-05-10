import pygame
import sys
import cv2
import mediapipe as mp
import numpy as np
import time
import random
import math

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 1200, 675
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Camera Setting ---
cap = cv2.VideoCapture(0)
sw, sh = 640, 480
cap.set(3, sw)
cap.set(4, sh)

# --- Init MediaPipe ---
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# --- Sound Setup ---
pygame.init()
pygame.mixer.init()
bg_sfx = pygame.mixer.Sound("background_music.mp3")
bg_sfx.set_volume(0.3)
wrong_sfx = pygame.mixer.Sound("wrong.mp3")
wrong_sfx.set_volume(0.2)
right_sfx = pygame.mixer.Sound("right.mp3")
right_sfx.set_volume(0.2)

# --- Load Resources ---
guide_imgs = [pygame.image.load("welcome.png")]
guide_imgs = [pygame.transform.scale(img, (1200, 675)) for img in guide_imgs]

start_img = pygame.image.load("start.png").convert_alpha()
start_img = pygame.transform.scale(start_img, (150, 50))
start_img_rect = start_img.get_rect(center=(WIDTH // 2, HEIGHT - 55))
endgame_img = pygame.image.load("endgame.png")
endgame_img = pygame.transform.scale(endgame_img, (1200, 675))

highscore_text_img = pygame.image.load("highscore_text.png")
cup_img = pygame.image.load("cup.png")
cup_img = pygame.transform.scale(cup_img, (37, 37))
newgame_img = pygame.image.load("newgame.png")


# professor_files = ["duongphung.png", "linhtran.png", "linhhuynh.png", "quanle.png"]
# professor_names = ["Thầy Dương", "Thầy Linh", "Thầy Khánh", "Thầy Tiến"]
# professor_imgs = [pygame.transform.scale(pygame.image.load(f), (50, 50)) for f in professor_files]

# object_img = pygame.image.load("duongphung.png")
# object_img = pygame.transform.scale(object_img, (50, 50))

unwanted_imgs = [pygame.image.load("fscore.png")]
unwanted_imgs = [pygame.transform.scale(img, (50, 50)) for img in unwanted_imgs]

# --- Load Next Button Image ---
next_img = pygame.image.load("next.png").convert_alpha()
# Resize ảnh nếu cần (VD: 120x50)
next_img = pygame.transform.scale(next_img, (120, 50))
next_img_rect = next_img.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))

def show_guides():
    img = guide_imgs[0]  # Hiển thị chỉ một ảnh hướng dẫn (hoặc tùy chọn ảnh đầu tiên)
    while True:
        screen.blit(img, (0, 0))
        screen.blit(next_img, next_img_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and next_img_rect.collidepoint(event.pos):
                return  # Thoát khỏi hàm show_guides(), chuyển sang màn hình ready


#almost done readyscreen, need to scale bg and character, add name bar

def ready_screen():
    name = ''
    selected_profs = []
    active = False
    input_box = pygame.Rect(WIDTH // 2 - 100, 50, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive

    # Load the background and professor images (both selected and unselected)
    ready_screen_img = pygame.image.load('readyscreen.png')
    
    # Professor image files
    professor_files = ["duongphung.png", "linhtran.png", "linhhuynh.png", "quanle.png"]
    professor_names = ["Thầy Dương", "Thầy Linh", "Thầy Khánh", "Thầy Tiến"]
    
    # Load and scale professor images for selected and unselected states
    professor_images = {
        0: {'selected': pygame.image.load('linhhuynh.png'), 'unselected': pygame.image.load('linhhuynh_unselected.png')},
        1: {'selected': pygame.image.load('quanle.png'), 'unselected': pygame.image.load('quanle_unselected.png')},
        2: {'selected': pygame.image.load('duongphung.png'), 'unselected': pygame.image.load('duongphung_unselected.png')},
        3: {'selected': pygame.image.load('linhtran.png'), 'unselected': pygame.image.load('linhtran_unselected.png')}
    }

    # Scale professor images
    for i in professor_images:
        professor_images[i]['selected'] = pygame.transform.scale(professor_images[i]['selected'], (60, 60))
        professor_images[i]['unselected'] = pygame.transform.scale(professor_images[i]['unselected'], (60, 60))

    # Load and scale the name images (duongphung_name.png, linhtran_name.png, etc.)
    professor_name_imgs = [
        pygame.image.load('duongphung_name.png'),
        pygame.image.load('linhtran_name.png'),
        pygame.image.load('linhhuynh_name.png'),
        pygame.image.load('quanle_name.png')
    ]

    # Scale name images to fit under the professors' images
    for i in range(len(professor_name_imgs)):
        professor_name_imgs[i] = pygame.transform.scale(professor_name_imgs[i], (60, 20))

    # Load and scale the namebar.png for input
    name_bar_img = pygame.image.load('namebar.png')
    name_bar_img = pygame.transform.scale(name_bar_img, (200, 40))  # Adjust the scale to fit the input area

    while True:
        screen.fill(WHITE)

        # Set background
        screen.blit(ready_screen_img, (0, 0))

        # Tên người chơi
        label = font.render("Enter your name:", True, BLACK)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 10))
        
        # Draw the name input bar (PNG)
        screen.blit(name_bar_img, (WIDTH // 2 - 100, 50))

        # Display the typed name on top of the name input bar
        txt_surface = font.render(name, True, BLACK)
        screen.blit(txt_surface, (WIDTH // 2 - txt_surface.get_width() // 2, 55))

        # Chọn giáo sư
        label2 = font.render("Select 1 to 3 Professors", True, BLACK)
        screen.blit(label2, (WIDTH // 2 - label2.get_width() // 2, 110))

        # Display professors (unselected by default)
        for i, images in professor_images.items():
            x = 100 + i * 150
            y = 160
            # Show the selected/unselected professor's image
            img_to_display = images['selected'] if i in selected_profs else images['unselected']
            screen.blit(img_to_display, (x, y))
            # Display the name image under the professor's image
            screen.blit(professor_name_imgs[i], (x - 5, y + 65))

        # Hiển thị nút Start
        if 1 <= len(selected_profs) <= 3 and len(name) > 0:
            screen.blit(start_img, start_img_rect)
        else:
            faded_img = start_img.copy()
            faded_img.fill((100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(faded_img, start_img_rect)

        pygame.display.flip()

        # Sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive

                # Chọn giáo sư
                for i in range(len(professor_images)):
                    px = 100 + i * 150
                    if pygame.Rect(px, 160, 60, 60).collidepoint(event.pos):  # Adjusted size for selection
                        if i in selected_profs:
                            selected_profs.remove(i)
                        elif len(selected_profs) < 3:
                            selected_profs.append(i)

                # Bấm nút Start
                if start_img_rect.collidepoint(event.pos) and 1 <= len(selected_profs) <= 3 and len(name) > 0:
                    return name, [professor_images[i]['selected'] for i in selected_profs]

            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and 1 <= len(selected_profs) <= 3 and len(name) > 0:
                    return name, [professor_images[i]['selected'] for i in selected_profs]
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode



def save_score(name, score):
    with open("high_scores.txt", "a") as f:
        f.write(f"{name},{score}\n")

def show_high_scores():
    screen.fill(WHITE)
    try:
        with open("high_scores.txt", "r") as f:
            scores = [line.strip().split(',') for line in f.readlines()]
            scores = sorted(scores, key=lambda x: int(x[1]), reverse=True)[:5]
    except FileNotFoundError:
        scores = []

    y = 100
    screen.blit(font.render("High Scores:", True, BLACK), (WIDTH // 2 - 80, y))
    for name, score in scores:
        y += 40
        screen.blit(font.render(f"{name}: {score}", True, BLACK), (WIDTH // 2 - 80, y))
    pygame.display.flip()
    pygame.time.wait(3000)

# # --- Pygame Initialization ---
# pygame.init()
# WIDTH, HEIGHT = 800, 600
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# font = pygame.font.SysFont("Arial", 24)
# clock = pygame.time.Clock()

def main_screen(player_name, object_img, unwanted_imgs, background, font, right_sfx, wrong_sfx):
    # Constants
    catch_distance = 50
    speed_increase_interval = 10
    start_time = time.time()
    last_speed_update = start_time

    mp_hands = mp.solutions.hands
    cap = cv2.VideoCapture(0)
    sw, sh = 640, 480  # Webcam resolution

    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        running = True
        prev_hand_status = {}

        while running:
            screen.blit(background, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Webcam Capture
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (sw, sh))
            frame = cv2.flip(frame, 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Hand Tracking
            hand_positions = []
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    x9, y9 = hand_landmarks.landmark[9].x * sw, hand_landmarks.landmark[9].y * sh
                    x12, y12 = hand_landmarks.landmark[12].x * sw, hand_landmarks.landmark[12].y * sh
                    status = "Closed" if y12 > y9 else "OPEN"
                    prev_status = prev_hand_status.get(idx, "OPEN")
                    hand_px = int(x9 / sw * WIDTH)
                    hand_py = int(y9 / sh * HEIGHT)
                    hand_positions.append({'x': hand_px, 'y': hand_py, 'status': status, 'prev_status': prev_status})
                    prev_hand_status[idx] = status
                    cv2.putText(image, status, (int(x9), int(y9 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                (0, 255, 0) if status == "Closed" else (0, 0, 255), 2)

            cv2.imshow('MediaPipe Hands', image)

            # Draw hands
            for hand in hand_positions:
                pygame.draw.circle(screen, (0, 255, 0), (hand['x'], hand['y']), 30)

            # Update objects
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

            # Update unwanted
            for i in range(len(unwanted_objects)):
                ux, uy, img_idx = unwanted_objects[i]
                screen.blit(unwanted_imgs[img_idx], (ux, uy))
                unwanted_objects[i][1] += fall_speed

                for hand in hand_positions:
                    dx = hand['x'] - (ux + 45)
                    dy = hand['y'] - (uy + 30)
                    if math.hypot(dx, dy) < catch_distance and hand['status'] in ["Closed", "OPEN"]:
                        wrong_sfx.play()
                        lives -= 1
                        unwanted_objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0),
                                               np.random.randint(0, len(unwanted_imgs))]
                        if lives <= 0:
                            game_over = font.render("Out of Lives! Game Over", True, (255, 0, 0))
                            screen.blit(game_over, (WIDTH // 2 - 150, HEIGHT // 2))
                            pygame.display.update()
                            pygame.time.wait(3000)
                            running = False
                        break

                if uy > HEIGHT:
                    unwanted_objects[i] = [np.random.randint(100, 700), np.random.randint(-600, 0),
                                           np.random.randint(0, len(unwanted_imgs))]

            # LEVEL UP
            if current_level == 1 and score > 4:
                screen.blit(font.render("Level 2!", True, (255, 0, 0)), (WIDTH // 2 - 80, HEIGHT // 2))
                pygame.display.update()
                pygame.time.wait(2000)
                current_level = 2
                game_duration -= 10
                fall_speed += 1
                unwanted_objects.append([np.random.randint(100, 700), np.random.randint(-600, 0),
                                         np.random.randint(0, len(unwanted_imgs))])

            if current_level == 2 and score > 8:
                screen.blit(font.render("Level 3!", True, (255, 0, 0)), (WIDTH // 2 - 80, HEIGHT // 2))
                pygame.display.update()
                pygame.time.wait(2000)
                current_level = 3
                fall_speed += 2
                game_duration -= 10
                unwanted_objects.append([np.random.randint(100, 700), np.random.randint(-600, 0),
                                         np.random.randint(0, len(unwanted_imgs))])

            # Hearts
            heart_img = pygame.image.load("hear.svg")
            heart_img = pygame.transform.scale(heart_img, (30, 30))
            for i in range(lives):
                screen.blit(heart_img, (10 + i * 35, 90))

            # Score and Time
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

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

def end_game_screen(score, player_name):
    screen.fill(WHITE)
    screen.blit(endgame_img, (0, 0))

    # Display high score
    highscore_text = font.render(f"Highest Score: {score}", True, BLACK)
    screen.blit(highscore_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))

    # Display the cup next to the highest score
    screen.blit(cup_img, (WIDTH // 2 + 100, HEIGHT // 2 - 50))

    # Show Play Again button using newgame.png
    play_again_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)
    screen.blit(newgame_img, play_again_btn_rect)  # Use the newgame.png image for the button

    pygame.display.flip()

    # Handle Play Again button click
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and play_again_btn_rect.collidepoint(event.pos):
                return True  # Return to the game start
        pygame.display.flip()


    # Handle Play Again click
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and play_again_btn.collidepoint(event.pos):
                return True  # Return to the game start
        pygame.display.flip()

# --- Main Game Loop ---
while True:
    # Show guide screen (not defined here, assuming you already have a `show_guides()` function)
    show_guides()

    player_name, selected_profs = ready_screen()
    object_img = selected_profs[random.randint(0, len(selected_profs) - 1)]

    lives = 3
    score = 0
    game_duration = 45
    fall_speed = 5
    num_objects = 5
    objects = [[random.randint(100, 700), random.randint(-600, 0)] for _ in range(num_objects)]
    unwanted_objects = [[random.randint(100, 700), random.randint(-600, 0), random.randint(0, len(unwanted_imgs) - 1)] for _ in range(num_objects)]

    start_time = time.time()
    running = True
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        while running:
            success, img = cap.read()
            if not success:
                continue

            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)
            hand_x, hand_y = -1, -1

            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    x = int(handLms.landmark[9].x * WIDTH)
                    y = int(handLms.landmark[9].y * HEIGHT)
                    hand_x, hand_y = x, y

            screen.fill(WHITE)

            for obj in objects:
                obj[1] += fall_speed
                screen.blit(object_img, (obj[0], obj[1]))
                if hand_x != -1 and abs(obj[0] - hand_x) < 40 and abs(obj[1] - hand_y) < 40:
                    score += 1
                    obj[0], obj[1] = random.randint(100, 700), random.randint(-600, 0)
                elif obj[1] > HEIGHT:
                    lives -= 1
                    obj[0], obj[1] = random.randint(100, 700), random.randint(-600, 0)

            for uw in unwanted_objects:
                uw[1] += fall_speed
                screen.blit(unwanted_imgs[uw[2]], (uw[0], uw[1]))
                if hand_x != -1 and abs(uw[0] - hand_x) < 40 and abs(uw[1] - hand_y) < 40:
                    score -= 1
                    lives -= 1
                    uw[0], uw[1] = random.randint(100, 700), random.randint(-600, 0)
                elif uw[1] > HEIGHT:
                    uw[0], uw[1] = random.randint(100, 700), random.randint(-600, 0)

            elapsed = int(time.time() - start_time)
            remaining = game_duration - elapsed
            score_text = font.render(f"Score: {score}  Lives: {lives}  Time: {remaining}", True, BLACK)
            screen.blit(score_text, (10, 10))
            pygame.display.flip()
            clock.tick(FPS)

            if remaining <= 0 or lives <= 0:
                save_score(player_name, score)
                show_high_scores()

                if end_game_screen(score, player_name):
                    break
                else:
                    pygame.quit()
                    sys.exit()
            if cv2.waitKey(1) & 0xFF == 27:
                pygame.quit()
                sys.exit()


