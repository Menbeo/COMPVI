import pygame
import cv2
import mediapipe as mp
import numpy as np
import sys
import time
import math
import os
import random

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1200, 675
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Your Professor!")
clock = pygame.time.Clock()
try:
    font = pygame.font.Font("Minecraft.ttf", 32)
except:
    # Fallback to system font if custom font fails to load
    font = pygame.font.SysFont('Arial', 32)
    print("Custom font not found, using system font instead")

# Load assets
def load_image(path, size=None):
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

# Load sounds
def load_sound(path, volume=1.0):
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    return sound

# Game assets
try:
    background = load_image("bg.png", (WIDTH, HEIGHT))
    guide_img = load_image("welcome.png", (WIDTH, HEIGHT))
    next_img = load_image("next.png", (106, 60))
    start_img = load_image("start.png", (143, 80))
    endgame_img = load_image("endgame.png", (WIDTH, HEIGHT))
    heart_img = load_image("heart.png", (30, 30))
    unwanted_imgs = [load_image("fscore.png", (90, 60))]
    name_enter = pygame.image.load("entername_text.png").convert_alpha() 
    name_enter = pygame.transform.scale(name_enter, (389, 219))
    selectprof_text = pygame.image.load("selectprof_text.png").convert_alpha() 
    selectprof_text = pygame.transform.scale(selectprof_text, (547, 308))
    out_time = load_image("out_time.png", (WIDTH, HEIGHT))
    out_lives = load_image("out_lives.png", (WIDTH, HEIGHT))
    hand_img = load_image("hand.png", (89,89))
    
    # Professor assets
    professor_images = {
        0: {'selected': load_image("linhhuynh.png", (200, 200)),
            'unselected': load_image("linhhuynh_unselected.png", (200, 200))},
        1: {'selected': load_image("quanle.png", (200, 200)),
            'unselected': load_image("quanle_unselected.png", (200, 200))},
        2: {'selected': load_image("duongphung.png", (200, 200)),
            'unselected': load_image("duongphung_unselected.png", (200, 200))},
        3: {'selected': load_image("linhtran.png", (200, 200)),
            'unselected': load_image("linhtran_unselected.png", (200, 200))}
    }
    
    # Load sounds
    bg_sfx = load_sound("background_music.mp3", 0.3)
    wrong_sfx = load_sound("wrong.mp3", 0.2)
    right_sfx = load_sound("right.mp3", 0.2)
    
except pygame.error as e:
    print(f"Error loading assets: {e}")
    sys.exit()

# Initialize camera
cap = cv2.VideoCapture(0)
sw, sh = 640, 480
cap.set(3, sw)
cap.set(4, sh)

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Screen functions
def show_guide_screen():
    """Show the game guide screen"""
    next_rect = next_img.get_rect(bottomright=(WIDTH-20, HEIGHT-20))
    
    while True:
        screen.blit(guide_img, (0, 0))
        screen.blit(next_img, next_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and next_rect.collidepoint(event.pos):
                return "ready"
        
        pygame.display.flip()
        clock.tick(FPS)

def show_ready_screen():
    """Show the ready screen with player name input and professor selection"""
    name = ''
    selected_profs = []
    active = False
    
    # Load background
    ready_bg = load_image("readyscreen.png", (WIDTH, HEIGHT))
    
    # Name input setup
    name_bar = load_image("namebar.png", (592, 333))  # Điều chỉnh kích thước phù hợp
    input_box = pygame.Rect(120, 141,537,46)
    
    # Start button setup
    start_rect = start_img.get_rect(center=(WIDTH//2, HEIGHT - 50))
    
    # Professor setup - ĐỒNG BỘ 1 CÁCH XÁC ĐỊNH VỊ TRÍ
    prof_positions = {
        0: {"prof": (108, 294), "name": (59, 438), "img": "linhhuynh_name.png"},
        1: {"prof": (356, 294), "name": (296, 438), "img": "quanle_name.png"},
        2: {"prof": (604, 294), "name": (551, 438), "img": "duongphung_name.png"},
        3: {"prof": (852, 294), "name": (822, 438), "img": "linhtran_name.png"}
    }
    
    # Load name images
    name_images = {}
    for i, pos in prof_positions.items():
        try:
            img = pygame.image.load(pos["img"]).convert_alpha()
            name_images[i] = pygame.transform.scale(img, (293, 165)) 
        except:
            print(f"Không tìm thấy ảnh: {pos['img']}")
            name_images[i] = pygame.Surface((120,40), pygame.SRCALPHA)

    while True:
        screen.blit(ready_bg, (0, 0))
        
        screen.blit(name_enter, (101, -22))  # Position without keywords
        screen.blit(selectprof_text, (101, 115))  # Position without keywords
        # --- NAME INPUT ---
        # Hiển thị ô nhập tên
        screen.blit(name_bar, (92, 0))
        
        # Hiển thị text đã nhập
        name_surface = font.render(name, True, BLACK)
        screen.blit(name_surface, (input_box.x + 10, input_box.y + 5))
        
        # Vẽ khung khi active
        if active:
            pygame.draw.rect(screen, (0, 0, 255), input_box, 2)
        
        # --- PROFESSOR SELECTION ---
        prof_rects = {}
        for i, prof in professor_images.items():
            # Lấy vị trí từ dictionary
            prof_pos = prof_positions[i]["prof"]
            name_pos = prof_positions[i]["name"]
            
            # Hiển thị ảnh giáo sư
            img = prof['selected'] if i in selected_profs else prof['unselected']
            screen.blit(img, prof_pos)
            
            # Hiển thị tên
            screen.blit(name_images[i], name_pos)
            
            # Lưu hitbox (dùng Rect chuẩn)
            prof_rects[i] = pygame.Rect(prof_pos[0], prof_pos[1], img.get_width(), img.get_height())
            
            # # Highlight khi chọn
            # if i in selected_profs:
            #     pygame.draw.rect(screen, (0, 255, 0), prof_rects[i], 3)
        
        # --- START BUTTON ---
        if 1 <= len(selected_profs) <= 3 and len(name) > 0:
            screen.blit(start_img, start_rect)
        else:
            faded = start_img.copy()
            faded.fill((100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(faded, start_rect)
        
        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", None, None
                
            # Xử lý click chuột
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Kiểm tra click vào ô tên
                active = input_box.collidepoint(mouse_pos)
                
                # Kiểm tra click vào giáo sư
                for i, rect in prof_rects.items():
                    if rect.collidepoint(mouse_pos):
                        if i in selected_profs:
                            selected_profs.remove(i)
                        elif len(selected_profs) < 3:
                            selected_profs.append(i)
                
                # Kiểm tra nút Start
                if start_rect.collidepoint(mouse_pos) and 1 <= len(selected_profs) <= 3 and len(name) > 0:
                    return "main", name, [professor_images[i]['selected'] for i in selected_profs]
            
            # Xử lý nhập tên
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN:
                    if 1 <= len(selected_profs) <= 3 and len(name) > 0:
                        return "main", name, [professor_images[i]['selected'] for i in selected_profs]
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    if len(name) < 20:  # Giới hạn độ dài tên
                        name += event.unicode
        
        pygame.display.flip()
        clock.tick(FPS)

def run_main_game(player_name, selected_profs):
    """Run the main game loop"""
    # Game variables
    lives = 3
    score = 0
    fall_speed = 5
    current_level = 1
    start_time = time.time()
    game_duration = 45

    # Initialize objects
    num_objects = 5
    objects = [[np.random.randint(100, WIDTH-100), np.random.randint(-600, 0)] for _ in range(num_objects)]
    unwanted_objects = [[np.random.randint(100, WIDTH-100), np.random.randint(-600, 0), 0] for _ in range(num_objects)]
    level2_img = pygame.image.load("level2.png").convert_alpha()
    level3_img = pygame.image.load("level3.png").convert_alpha()
    # Scale images if needed (adjust size to fit your screen)
    level2_img = pygame.transform.scale(level2_img, (955, 537))
    level3_img = pygame.transform.scale(level3_img, (955, 537))

    # Start background music
    # Initialize MediaPipe
    mp_hands = mp.solutions.hands

    bg_sfx.play(-1)
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        running = True
        prev_hand_status = {}
        while running:
            screen.blit(background, (0, 0))
            # Get camera frame
            ret, image = cap.read()
            if not ret:
                break

            image = cv2.flip(image, 1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image) 
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Hand tracking
            hand_positions = []
            if results.multi_hand_landmarks:
                for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    x9 = hand_landmarks.landmark[9].x * sw
                    y9 = hand_landmarks.landmark[9].y * sh
                    cv2.circle(image, (int(x9), int(y9)), 10, (0,255,0), -1)
                    x12 = hand_landmarks.landmark[12].x * sw
                    y12 = hand_landmarks.landmark[12].y * sh
                    cv2.circle(image, (int(x12), int(y12)), 10, (0,0,255), -1)
                    hand_x = int(x9 / sw * WIDTH)
                    hand_y = int(y9 / sh * HEIGHT)
                    status = "Closed" if y12 > y9 else "OPEN"
                    prev_status = prev_hand_status.get(idx, "OPEN")
                    hand_positions.append({'x': hand_x, 'y': hand_y, 'status': status, 'prev_status': prev_status})
                    prev_hand_status[idx] = status

                    #---Show vid--
                # cv2.imshow('MediaPipe Hands', image)
                hand_img_width, hand_img_height = hand_img.get_size()
                hand_offset_x = hand_img_width // 2
                hand_offset_y = hand_img_height // 2

                for hand in hand_positions:
                    screen.blit(hand_img, (hand['x'] - hand_offset_x, hand['y'] - hand_offset_y))

            # Update and draw objects
            for obj in objects:
                obj_x, obj_y = obj
                prof_img = random.choice(selected_profs)
                screen.blit(prof_img, (obj_x, obj_y))
                obj[1] += fall_speed

                # Check collision
                for hand in hand_positions:
                    dx = hand['x'] - (obj_x + 25)
                    dy = hand['y'] - (obj_y + 25)
                    if math.hypot(dx, dy) < 230 and hand['prev_status'] == "Closed" and hand['status'] == "OPEN":
                        score += 1
                        right_sfx.play()
                        obj[0] = random.randint(100, WIDTH-100)
                        obj[1] = random.randint(-600, 0)
                        break

                if obj_y > HEIGHT:
                    obj[0] = random.randint(100, WIDTH-100)
                    obj[1] = random.randint(-600, 0)

            # Update and draw unwanted objects
            for uw in unwanted_objects:
                uw_x, uw_y, img_idx = uw
                screen.blit(unwanted_imgs[img_idx], (uw_x, uw_y))
                uw[1] += fall_speed

                # Check collision
                for hand in hand_positions:
                    dx = hand['x'] - (uw_x + 45)
                    dy = hand['y'] - (uw_y + 30)
                    if math.hypot(dx, dy) < 100:
                        if hand['status'] == "Closed" or hand['status'] == "OPEN":
                            lives -= 1
                            wrong_sfx.play()
                            uw[0] = random.randint(100, WIDTH-100)
                            uw[1] = random.randint(-600, 0)
                            break

                if uw_y > HEIGHT:
                    uw[0] = random.randint(100, WIDTH-100)
                    uw[1] = random.randint(-600, 0)

            # --- LEVEL UP ---
            if current_level == 1 and score > 10:
                #display the level
                screen.blit(level2_img, (97, 87))
                pygame.display.update()
                pygame.time.wait(2000)
                current_level = 2
                game_duration -= 10
                fall_speed += 1
                unwanted_objects.append([np.random.randint(100, WIDTH-100), np.random.randint(-600, 0), np.random.randint(0, len(unwanted_imgs))])


            if current_level == 2 and score > 20:
                screen.blit(level3_img, (97, 87))
                pygame.display.update()
                pygame.time.wait(2000)
                current_level = 3
                fall_speed += 2
                game_duration -= 10
                unwanted_objects.append([np.random.randint(100, WIDTH-100), np.random.randint(-600, 0), np.random.randint(0, len(unwanted_imgs))])


            # Display UI
            for i in range(lives):
                screen.blit(heart_img, (10 + i * 35, 10))

            current_time = int(time.time() - start_time)
            remaining = max(0, game_duration - current_time)

            score_text = font.render(f"Score: {score}", True, BLACK)
            time_text = font.render(f"Time: {remaining}s", True, BLACK)
            level_text = font.render(f"Level: {current_level}", True, BLACK)

            screen.blit(score_text, (10, 50))
            screen.blit(time_text, (10, 90))
            screen.blit(level_text, (10, 130))

            # Check game over
            if remaining <= 0:
                running = False
                screen.blit(out_time, (0, 0))
                pygame.time.wait(5000)
            if lives <= 0:
                screen.blit(out_lives, (0, 0))
                running = False
                pygame.time.wait(3000)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return "quit"

            pygame.display.flip()
            clock.tick(FPS)
    bg_sfx.stop()
    return "end", score, player_name

def show_end_screen(score, player_name):
    """Show the end game screen with high scores"""
    high_score_img = load_image("high_score.png", (602, 339)) 
    # Save score
    with open("high_scores.txt", "a") as f:
        f.write(f"{player_name}:{score}\n")
    
    try:
        with open("high_scores.txt", "r") as f:
            scores = []
            for line in f.readlines():
                # Remove whitespace and split by colon
                parts = line.strip().split(":")
                # Check if the line has exactly two parts and the score is a valid integer
                if len(parts) == 2 and parts[1].isdigit():
                    scores.append(parts)
            # Sort by score (converted to integer) in descending order, take top 5
            top_scores = sorted(scores, key=lambda x: int(x[1]), reverse=True)[:5]
    except FileNotFoundError:
        top_scores = []

    # # Load high scores
    # try:
    #     with open("high_scores.txt", "r") as f:
    #         scores = [line.strip().split(":") for line in f.readlines()]
    #         top_scores = sorted(scores, key=lambda x: (x[1]), reverse=True)[:5]
    # except FileNotFoundError:
    #     top_scores = []
    
    # Display loop
    while True:
        screen.blit(endgame_img, (0, 0))
        
        # Display player score
        score_text = font.render(f"Your Score: {score}", True, WHITE)
        screen.blit(score_text, (780,251))
        
        screen.blit(high_score_img, (587,-1))
        
        for i, (name, score) in enumerate(top_scores):
            entry = font.render(f"{i+1}. {name}: {score}", True, WHITE)
            screen.blit(entry, (804, 286 + i*40))
        
        # Display continue prompt
        continue_text = font.render("Click anywhere to continue...", True, WHITE)
        screen.blit(continue_text, (650,603))
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "guide"
        
        pygame.display.flip()
        clock.tick(FPS)

# Main game loop
def main():
    state = "guide"
    player_name = ""
    selected_profs = []
    score = 0
    
    while True:
        if state == "guide":
            state = show_guide_screen()
        elif state == "ready":
            state, player_name, selected_profs = show_ready_screen()
        elif state == "main":
            result = run_main_game(player_name, selected_profs)
            if result == "quit":
                # screen.blit(out_time, (0, 0))
                # pygame.time.wait(2000)
                break
            state, score, player_name = result
        elif state == "end":
            state = show_end_screen(score, player_name)
        elif state == "quit":
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()