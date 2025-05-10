import pygame
import sys
import os

pygame.init()

# --- Constants ---
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ASSETS_DIR = "assets"

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hand Game")
font = pygame.font.Font(None, 36)

# --- Load Sounds ---
pygame.mixer.init()
bg_sfx = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "background_music.mp3"))
bg_sfx.set_volume(0.3)
wrong_sfx = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "wrong.mp3"))
wrong_sfx.set_volume(0.2)
right_sfx = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "right.mp3"))
right_sfx.set_volume(0.2)

# --- Load Images ---
guide_imgs = [pygame.image.load(os.path.join(ASSETS_DIR, "welcome.png"))]
guide_imgs = [pygame.transform.scale(img, (WIDTH, HEIGHT)) for img in guide_imgs]

start_img = pygame.image.load(os.path.join(ASSETS_DIR, "start.png")).convert_alpha()
start_img = pygame.transform.scale(start_img, (150, 50))
start_img_rect = start_img.get_rect(center=(WIDTH // 2, HEIGHT - 55))

next_img = pygame.image.load(os.path.join(ASSETS_DIR, "next.png")).convert_alpha()
next_img = pygame.transform.scale(next_img, (120, 50))
next_img_rect = next_img.get_rect(bottomright=(WIDTH - 20, HEIGHT - 20))

endgame_img = pygame.image.load(os.path.join(ASSETS_DIR, "endgame.png"))
highscore_text_img = pygame.image.load(os.path.join(ASSETS_DIR, "highscore_text.png"))
cup_img = pygame.image.load(os.path.join(ASSETS_DIR, "cup.png"))
newgame_img = pygame.image.load(os.path.join(ASSETS_DIR, "newgame.png"))
unwanted_imgs = [pygame.image.load(os.path.join(ASSETS_DIR, "fscore.png"))]
unwanted_imgs = [pygame.transform.scale(img, (50, 50)) for img in unwanted_imgs]


def show_guides():
    img = guide_imgs[0]
    while True:
        screen.blit(img, (0, 0))
        screen.blit(next_img, next_img_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and next_img_rect.collidepoint(event.pos):
                return


def ready_screen():
    name = ''
    selected_profs = []
    input_box = pygame.Rect(WIDTH // 2 - 100, 50, 200, 40)

    ready_screen_img = pygame.image.load(os.path.join(ASSETS_DIR, 'readyscreen.png'))

    professor_images = {
        0: {'selected': pygame.image.load(os.path.join(ASSETS_DIR, 'linhhuynh.png')), 'unselected': pygame.image.load(os.path.join(ASSETS_DIR, 'linhhuynh_unselected.png'))},
        1: {'selected': pygame.image.load(os.path.join(ASSETS_DIR, 'quanle.png')), 'unselected': pygame.image.load(os.path.join(ASSETS_DIR, 'quanle_unselected.png'))},
        2: {'selected': pygame.image.load(os.path.join(ASSETS_DIR, 'duongphung.png')), 'unselected': pygame.image.load(os.path.join(ASSETS_DIR, 'duongphung_unselected.png'))},
        3: {'selected': pygame.image.load(os.path.join(ASSETS_DIR, 'linhtran.png')), 'unselected': pygame.image.load(os.path.join(ASSETS_DIR, 'linhtran_unselected.png'))}
    }

    for i in professor_images:
        professor_images[i]['selected'] = pygame.transform.scale(professor_images[i]['selected'], (60, 60))
        professor_images[i]['unselected'] = pygame.transform.scale(professor_images[i]['unselected'], (60, 60))

    professor_name_imgs = [
        pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, 'duongphung_name.png')), (60, 20)),
        pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, 'linhtran_name.png')), (60, 20)),
        pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, 'linhhuynh_name.png')), (60, 20)),
        pygame.transform.scale(pygame.image.load(os.path.join(ASSETS_DIR, 'quanle_name.png')), (60, 20)),
    ]

    name_bar_img = pygame.image.load(os.path.join(ASSETS_DIR, 'namebar.png'))
    name_bar_img = pygame.transform.scale(name_bar_img, (200, 40))

    active = False
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive

    while True:
        screen.fill(WHITE)
        screen.blit(ready_screen_img, (0, 0))
        label = font.render("Enter your name:", True, BLACK)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, 10))
        screen.blit(name_bar_img, (WIDTH // 2 - 100, 50))
        txt_surface = font.render(name, True, BLACK)
        screen.blit(txt_surface, (WIDTH // 2 - txt_surface.get_width() // 2, 55))

        label2 = font.render("Select 1 to 3 Professors", True, BLACK)
        screen.blit(label2, (WIDTH // 2 - label2.get_width() // 2, 110))

        for i, images in professor_images.items():
            x = 100 + i * 150
            y = 160
            img_to_display = images['selected'] if i in selected_profs else images['unselected']
            screen.blit(img_to_display, (x, y))
            screen.blit(professor_name_imgs[i], (x - 5, y + 65))

        if 1 <= len(selected_profs) <= 3 and len(name) > 0:
            screen.blit(start_img, start_img_rect)
        else:
            faded_img = start_img.copy()
            faded_img.fill((100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(faded_img, start_img_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                active = input_box.collidepoint(event.pos)
                color = color_active if active else color_inactive
                for i in range(len(professor_images)):
                    px = 100 + i * 150
                    if pygame.Rect(px, 160, 60, 60).collidepoint(event.pos):
                        if i in selected_profs:
                            selected_profs.remove(i)
                        elif len(selected_profs) < 3:
                            selected_profs.append(i)
                if start_img_rect.collidepoint(event.pos) and 1 <= len(selected_profs) <= 3 and len(name) > 0:
                    return name, [professor_images[i]['selected'] for i in selected_profs]
            elif event.type == pygame.KEYDOWN and active:
                if event.key == pygame.K_RETURN and 1 <= len(selected_profs) <= 3 and len(name) > 0:
                    return name, [professor_images[i]['selected'] for i in selected_profs]
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode


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


def end_game_screen(score, player_name):
    screen.fill(WHITE)
    screen.blit(endgame_img, (0, 0))
    highscore_text = font.render(f"Highest Score: {score}", True, BLACK)
    screen.blit(highscore_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
    screen.blit(cup_img, (WIDTH // 2 + 100, HEIGHT // 2 - 50))

    play_again_btn_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)
    screen.blit(newgame_img, play_again_btn_rect)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and play_again_btn_rect.collidepoint(event.pos):
                return True
