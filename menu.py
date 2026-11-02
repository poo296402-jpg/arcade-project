import os

import pygame
import snake
import flappy
import space  # <--- Imports your space.py file
from builtins import BaseException, Exception, enumerate, len, print

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(filename):
    """Return an asset path relative to this file, regardless of the CWD."""
    return os.path.join(BASE_DIR, filename)

def draw_starfield(screen):
    stars = [
        (100, 50), (230, 80), (450, 40), (700, 70), (850, 30),
        (50, 150), (320, 200), (600, 170), (780, 220),
        (120, 300), (400, 350), (650, 320), (880, 290),
        (80, 400), (250, 430), (530, 410), (750, 440),
    ]
    for pos in stars:
        pygame.draw.circle(screen, (200, 220, 255), pos, 1)

def main_menu():
    pygame.init()
    
    # --- BACKGROUND MUSIC SETUP ---
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(asset_path("music.wav"))
        pygame.mixer.music.set_volume(0.5)  # Volume (0.0 to 1.0)
        pygame.mixer.music.play(loops=-1)   # Loop forever
    except Exception:
        pass

    screen_width, screen_height = 900, 520
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Arcade Flashback Classics - Game Select")
    
    # --- CUSTOM PIXEL FONT SETUP ---
    font_path = asset_path("pixeled.ttf")
    
    try:
        title_font = pygame.font.Font(font_path, 22)
        button_font = pygame.font.Font(font_path, 12)
        desc_font = pygame.font.Font(font_path, 8)
        footer_font = pygame.font.Font(font_path, 8)
    except Exception:
        title_font = pygame.font.Font(None, 32)
        button_font = pygame.font.Font(None, 24)
        desc_font = pygame.font.Font(None, 16)
        footer_font = pygame.font.Font(None, 16)

    # --- LOAD GAME PREVIEW SCREENSHOTS ---
    try:
        snake_img = pygame.transform.scale(pygame.image.load(asset_path("snake.png")), (190, 120))
    except Exception:
        snake_img = None

    try:
        flappy_img = pygame.transform.scale(pygame.image.load(asset_path("flappy.png")), (190, 120))
    except Exception:
        flappy_img = None

    try:
        space_img = pygame.transform.scale(pygame.image.load(asset_path("space.png")), (190, 120))
    except Exception:
        space_img = None

    # Game options data list
    games = [
        {
            "label": "SNAKE ARCADE", 
            "desc": "Guide the snake, eat the red food, and grow longer without hitting walls or your tail!",
            "runner": snake.run_game,
            "rect": pygame.Rect(320, 95, 530, 65),
            "preview_img": snake_img
        },
        {
            "label": "FLAPPY BIRD", 
            "desc": "Tap spacebar to flap your wings. Navigate cleanly through pipes to score points.",
            "runner": flappy.run_game,
            "rect": pygame.Rect(320, 170, 530, 65),
            "preview_img": flappy_img
        },
        {
            "label": "SPACE INVADERS", 
            "desc": "Defend Earth! Move with arrow keys and press spacebar to shoot lasers.",
            "runner": space.run_game,  # <--- Calls space.py
            "rect": pygame.Rect(320, 245, 530, 65),
            "preview_img": space_img
        },
        {
            "label": "QUIT ARCADE", 
            "desc": "Shut down the arcade cabinet and exit back to your desktop.",
            "runner": None,
            "rect": pygame.Rect(320, 320, 530, 65),
            "preview_img": None
        }
    ]

    selected_index = 0
    clock = pygame.time.Clock()

    def launch_game(runner):
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
            
        # Catch BaseException to intercept sys.exit() calls from games like space.py
        try:
            runner()
        except BaseException as e:
            print(f"Game closed: {e}")
            
        # Re-initialize the display and audio mixer so the menu recovers cleanly
        pygame.init()
        nonlocal screen
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Arcade Flashback Classics - Game Select")
        
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(asset_path("music.wav"))
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(games)
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(games)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    selected_game = games[selected_index]
                    if selected_game["runner"]:
                        launch_game(selected_game["runner"])
                    else:
                        pygame.quit()
                        return

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, game in enumerate(games):
                    if game["rect"].collidepoint(event.pos):
                        selected_index = idx
                        if game["runner"]:
                            launch_game(game["runner"])
                        else:
                            pygame.quit()
                            return

        mouse_pos = pygame.mouse.get_pos()
        for idx, game in enumerate(games):
            if game["rect"].collidepoint(mouse_pos):
                selected_index = idx

        # --- DRAWING BACKGROUND ---
        screen.fill((15, 10, 35))
        draw_starfield(screen)

        # Top Header Banner
        pygame.draw.rect(screen, (25, 20, 60), (0, 0, screen_width, 65))
        pygame.draw.line(screen, (100, 80, 200), (0, 65), (screen_width, 65), 3)
        
        title_surf = title_font.render("FLASHBACK ARCADE", True, (240, 240, 255))
        title_rect = title_surf.get_rect(midleft=(30, 32))
        screen.blit(title_surf, title_rect)

        # --- LEFT SIDE: CABINET PREVIEW PANEL ---
        cabinet_rect = pygame.Rect(40, 95, 240, 360)
        pygame.draw.rect(screen, (20, 20, 35), cabinet_rect, border_radius=8)
        pygame.draw.rect(screen, (70, 90, 160), cabinet_rect, 2, border_radius=8)
        
        mini_screen = pygame.Rect(55, 115, 210, 130)
        pygame.draw.rect(screen, (10, 10, 20), mini_screen)
        pygame.draw.rect(screen, (50, 60, 90), mini_screen, 1)
        
        current_preview_img = games[selected_index]["preview_img"]
        if current_preview_img:
            screen.blit(current_preview_img, (65, 120))
        else:
            fallback_text = button_font.render("No Screenshot", True, (150, 150, 170))
            screen.blit(fallback_text, fallback_text.get_rect(center=mini_screen.center))

        # --- FORMATTED DESCRIPTION TEXT WRAPPING ---
        desc_text = games[selected_index]["desc"]
        words = desc_text.split(" ")
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if desc_font.size(test_line)[0] < 210:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)

        start_y = 265
        for line in lines:
            desc_surf = desc_font.render(line, True, (180, 190, 210))
            screen.blit(desc_surf, (55, start_y))
            start_y += 16

        # --- RIGHT SIDE: GAME SELECTION MARQUEES ---
        for idx, game in enumerate(games):
            is_selected = (idx == selected_index)
            bg_color = (40, 60, 130) if is_selected else (25, 30, 60)
            border_color = (0, 220, 255) if is_selected else (60, 70, 110)
            
            pygame.draw.rect(screen, bg_color, game["rect"], border_radius=6)
            pygame.draw.rect(screen, border_color, game["rect"], 2, border_radius=6)

            label_surf = button_font.render(game["label"], True, (255, 255, 255) if is_selected else (190, 200, 220))
            screen.blit(label_surf, (game["rect"].x + 25, game["rect"].y + 26))

        # --- BOTTOM CONTROLS FOOTER BAR ---
        footer_rect = pygame.Rect(0, screen_height - 40, screen_width, 40)
        pygame.draw.rect(screen, (15, 10, 30), footer_rect)
        pygame.draw.line(screen, (70, 60, 120), (0, screen_height - 40), (screen_width, screen_height - 40), 2)

        controls_text = "[UP/DOWN] Select   [ENTER] Play   [ESC] Quit"
        footer_surf = footer_font.render(controls_text, True, (200, 200, 220))
        screen.blit(footer_surf, (30, screen_height - 26))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()