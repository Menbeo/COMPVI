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
font = pygame.font.SysFont('Arial', 32)

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
    next_img = load_image("next.png", (120, 50))
    start_img = load_image("start.png", (150, 50))
    endgame_img = load_image("endgame.png", (WIDTH, HEIGHT))
    heart_img = load_image("heart.png", (30, 30))
    unwanted_imgs = [load_image("fscore.png", (90, 60))]
    
    # Professor assets
    professor_images = {
        0: {'selected': load_image("linhhuynh.png", (60, 60)),
            'unselected': load_image("linhhuynh_unselected.png", (60, 60))},
        1: {'selected': load_image("quanle.png", (60, 60)),
            'unselected': load_image("quanle_unselected.png", (60, 60))},
        2: {'selected': load_image("duongphung.png", (60, 60)),
            'unselected': load_image("duongphung_unselected.png", (60, 60))},
        3: {'selected': load_image("linhtran.png", (60, 60)),
            'unselected': load_image("linhtran_unselected.png", (60, 60))}
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
    input_box = pygame.Rect(WIDTH//2 - 100, 50, 200, 40)
    active = False
    
    ready_bg = load_image("readyscreen.png", (WIDTH, HEIGHT))
    name_bar = load_image("namebar.png", (200, 40))
    
    start_rect = start_img.get_rect(center=(WIDTH//2, HEIGHT-55))
    
    while True:
        screen.blit(ready_bg, (0, 0))
        
        # Name input
        screen.blit(name_bar, input_box)
        name_surface = font.render(name, True, BLACK)
        screen.blit(name_surface, (input_box.x + 10, input_box.y + 5))
        
        # Professor selection
        for i, prof in professor_images.items():
            x = 100 + i * 150
            y = 160
            img = prof['selected'] if i in selected_profs else prof['unselected']
            screen.blit(img, (x, y))
        
        # Start button (only enabled when valid)
        if 1 <= len(selected_profs) <= 3 and len(name) > 0:
            screen.blit(start_img, start_rect)
        else:
            faded = start_img.copy()
            faded.fill((100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(faded, start_rect)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", None, None
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check name input
                active = input_box.collidepoint(event.pos)
                
                # Check professor selection
                for i in range(len(professor_images)):
                    px = 100 + i * 150
                    if pygame.Rect(px, 160, 60, 60).collidepoint(event.pos):
                        if i in selected_profs:
                            selected_profs.remove(i)
                        elif len(selected_profs) < 3:
                            selected_profs.append(i)
                
                # Check start button
                if start_rect.collidepoint(event.pos) and 1 <= len(selected_profs) <= 3 and len(name) > 0:
                    return "main", name, [professor_images[i]['selected'] for i in selected_profs]
            
            if event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and 1 <= len(selected_profs) <= 3 and len(name) > 0:
                    return "main", name, [professor_images[i]['selected'] for i in selected_profs]
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
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
    
    # Start background music
    bg_sfx.play(-1)
    
    running = True
    while running:
        screen.blit(background, (0, 0))
        
        # Get camera frame
        ret, frame = cap.read()
        if not ret:
            continue
            
        frame = cv2.flip(frame, 1)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        
        # Hand tracking
        hand_positions = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                x9 = int(hand_landmarks.landmark[9].x * sw)
                y9 = int(hand_landmarks.landmark[9].y * sh)
                x12 = int(hand_landmarks.landmark[12].x * sw)
                y12 = int(hand_landmarks.landmark[12].y * sh)
                
                status = "Closed" if y12 > y9 else "OPEN"
                hand_x = int(x9 / sw * WIDTH)
                hand_y = int(y9 / sh * HEIGHT)
                
                hand_positions.append({'x': hand_x, 'y': hand_y, 'status': status})
                pygame.draw.circle(screen, (0, 255, 0), (hand_x, hand_y), 30)
        
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
                if math.hypot(dx, dy) < 50 and hand['status'] == "Closed":
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
                dx = hand['x'] - (uw_x + 25)
                dy = hand['y'] - (uw_y + 25)
                if math.hypot(dx, dy) < 50:
                    lives -= 1
                    wrong_sfx.play()
                    uw[0] = random.randint(100, WIDTH-100)
                    uw[1] = random.randint(-600, 0)
                    break
            
            if uw_y > HEIGHT:
                uw[0] = random.randint(100, WIDTH-100)
                uw[1] = random.randint(-600, 0)
        
        # Check level up
        if current_level == 1 and score > 4:
            current_level = 2
            fall_speed += 1
        elif current_level == 2 and score > 8:
            current_level = 3
            fall_speed += 2
        
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
        if remaining <= 0 or lives <= 0:
            running = False
        
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
    # Save score
    with open("highscores.txt", "a") as f:
        f.write(f"{player_name}:{score}\n")
    
    # Load high scores
    try:
        with open("highscores.txt", "r") as f:
            scores = [line.strip().split(":") for line in f.readlines()]
            top_scores = sorted(scores, key=lambda x: int(x[1]), reverse=True)[:5]
    except FileNotFoundError:
        top_scores = []
    
    # Display loop
    while True:
        screen.blit(endgame_img, (0, 0))
        
        # Display player score
        score_text = font.render(f"Your Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 200))
        
        # Display high scores
        title = font.render("High Scores:", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 250))
        
        for i, (name, score) in enumerate(top_scores):
            entry = font.render(f"{i+1}. {name}: {score}", True, WHITE)
            screen.blit(entry, (WIDTH//2 - entry.get_width()//2, 300 + i*40))
        
        # Display continue prompt
        continue_text = font.render("Click anywhere to continue...", True, WHITE)
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT-100))
        
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