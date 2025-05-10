import pygame
import random
from ui import show_guides, ready_screen, main_screen, end_game_screen, save_score

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
FPS = 30

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# Load Sounds
pygame.mixer.init()
bg_sfx = pygame.mixer.Sound("assets/sounds/background_music.mp3")
bg_sfx.set_volume(0.3)
wrong_sfx = pygame.mixer.Sound("assets/sounds/wrong.mp3")
wrong_sfx.set_volume(0.2)
right_sfx = pygame.mixer.Sound("assets/sounds/right.mp3")
right_sfx.set_volume(0.2)

# Load Images
guide_imgs = [pygame.image.load("assets/images/welcome.png")]
guide_imgs = [pygame.transform.scale(img, (WIDTH, HEIGHT)) for img in guide_imgs]
start_img = pygame.image.load("assets/images/start.png").convert_alpha()
start_img = pygame.transform.scale(start_img, (150, 50))
endgame_img = pygame.image.load("assets/images/endgame.png")
highscore_text_img = pygame.image.load("assets/images/highscore_text.png")
cup_img = pygame.image.load("assets/images/cup.png")
newgame_img = pygame.image.load("assets/images/newgame.png")
unwanted_imgs = [pygame.image.load("assets/images/fscore.png")]
unwanted_imgs = [pygame.transform.scale(img, (50, 50)) for img in unwanted_imgs]
background = pygame.image.load("assets/images/game_bg.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Main Game Loop
while True:
    show_guides(screen, guide_imgs)
    player_name, selected_profs = ready_screen(screen, font, start_img)
    object_img = selected_profs[random.randint(0, len(selected_profs) - 1)]

    # Game variables
    lives = 3
    score = 0
    game_duration = 45
    fall_speed = 5
    current_level = 1
    num_objects = 5
    objects = [[random.randint(100, 700), random.randint(-600, 0)] for _ in range(num_objects)]
    unwanted_objects = [[random.randint(100, 700), random.randint(-600, 0), random.randint(0, len(unwanted_imgs) - 1)] for _ in range(3)]

    main_screen(screen, player_name, object_img, unwanted_imgs, background, font, right_sfx, wrong_sfx,
                lives, score, game_duration, fall_speed, current_level, objects, unwanted_objects)

    if not end_game_screen(screen, font, endgame_img, cup_img, newgame_img, score, player_name):
        break