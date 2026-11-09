import os
import sys
import subprocess
import pygame

def main():
    # --- 1. SYSTEM INITIALIZATION ---
    pygame.init()
    
    WIDTH, HEIGHT = 900, 520
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Arcade Flashback Classics - Game Select")
    clock = pygame.time.Clock()

    # --- 2. PATH RESOLUTION FOR ASSETS & GAMES ---
    def resource_path(relative_path):
        """Get absolute path to bundled assets (fonts, music, images)"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def get_game_dir():
        """Get the true directory where external game scripts live (.py files next to exe or script)"""
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.abspath(__file__))

    # --- 3. AUDIO ENGINE ---
    def init_audio():
        try:
            pygame.mixer.init()
            music_file = resource_path("music.wav")
            if os.path.exists(music_file):
                pygame.mixer.music.load(music_file)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(loops=-1)
        except Exception:
            pass

    def stop_audio():
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception:
            pass

    init_audio()

    # --- 4. TYPOGRAPHY & ASSETS ---
    def load_assets():
        font_name = "Pixeled.ttf"
        font_path = resource_path(font_name)
        if not os.path.exists(font_path):
            font_path = resource_path("pixeled.ttf")

        try:
            t_font = pygame.font.Font(font_path, 22)
            b_font = pygame.font.Font(font_path, 12)
            d_font = pygame.font.Font(font_path, 8)
            f_font = pygame.font.Font(font_path, 8)
        except Exception:
            t_font = pygame.font.Font(None, 32)
            b_font = pygame.font.Font(None, 24)
            d_font = pygame.font.Font(None, 16)
            f_font = pygame.font.Font(None, 16)

        def load_img(filename):
            try:
                img_path = resource_path(filename)
                return pygame.transform.scale(pygame.image.load(img_path).convert(), (190, 120))
            except Exception:
                return None

        previews = {
            "snake": load_img("snake.png"),
            "flappy": load_img("flappy.png"),
            "space": load_img("space.png"),
            "tetris": load_img("tetris.png"),
            "breakout": load_img("breakout.png"),
        }
        return t_font, b_font, d_font, f_font, previews

    title_font, button_font, desc_font, footer_font, previews = load_assets()

    # --- 5. GAME CATALOG ---
    games = [
        {
            "label": "SNAKE ARCADE",
            "desc": "Guide the snake, eat the red food, and grow longer without hitting walls or your tail!",
            "script": "snake.py",
            "rect": pygame.Rect(320, 80, 530, 46),
            "preview_key": "snake"
        },
        {
            "label": "FLAPPY BIRD",
            "desc": "Tap spacebar to flap your wings. Navigate cleanly through pipes to score points.",
            "script": "flappy.py",
            "rect": pygame.Rect(320, 134, 530, 46),
            "preview_key": "flappy"
        },
        {
            "label": "SPACE INVADERS",
            "desc": "Defend Earth! Move with arrow keys and press spacebar to shoot lasers.",
            "script": "space.py",
            "rect": pygame.Rect(320, 188, 530, 46),
            "preview_key": "space"
        },
        {
            "label": "TETRIS",
            "desc": "Rotate and drop falling blocks to clear complete lines and stack up your high score.",
            "script": "tetris.py",
            "rect": pygame.Rect(320, 242, 530, 46),
            "preview_key": "tetris"
        },
        {
            "label": "BREAKOUT",
            "desc": "Bounce the ball with your paddle to break every brick without letting it fall.",
            "script": "breakout.py",
            "rect": pygame.Rect(320, 296, 530, 46),
            "preview_key": "breakout"
        },
        {
            "label": "QUIT ARCADE",
            "desc": "Shut down the arcade cabinet and exit back to your desktop.",
            "script": None,
            "rect": pygame.Rect(320, 350, 530, 46),
            "preview_key": None
        }
    ]

    # --- 6. STATIC BACKGROUND & UI SURFACES ---
    bg_surface = pygame.Surface((WIDTH, HEIGHT))
    bg_surface.fill((15, 10, 35))
    star_coords = [
        (100, 50), (230, 80), (450, 40), (700, 70), (850, 30),
        (50, 150), (320, 200), (600, 170), (780, 220),
        (120, 300), (400, 350), (650, 320), (880, 290),
        (80, 400), (250, 430), (530, 410), (750, 440),
    ]
    for pos in star_coords:
        pygame.draw.circle(bg_surface, (200, 220, 255), pos, 1)

    title_surf = title_font.render("FLASHBACK ARCADE", True, (240, 240, 255))
    fallback_surf = button_font.render("No Screenshot", True, (150, 150, 170))
    footer_surf = footer_font.render("[UP/DOWN] Select   [ENTER] Play   [ESC] Quit", True, (200, 200, 220))

    selected_index = 0

    def render_wrapped_description(text, font, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return [font.render(line, True, (180, 190, 210)) for line in lines]

    # --- 7. SUBPROCESS LAUNCH HANDLER ---
    nonlocal_screen = screen
    def launch_game(script_name):
        nonlocal nonlocal_screen
        stop_audio()
        pygame.event.clear()
        
        try:
            game_dir = get_game_dir()
            script_path = os.path.join(game_dir, script_name)
            
            # Hide menu window completely while game runs
            pygame.display.quit()
            
            # Execute python script using the exact system interpreter and correct working directory
            python_cmd = sys.executable if not getattr(sys, 'frozen', False) else "python"
            subprocess.run([python_cmd, script_path], cwd=game_dir)
        except Exception as e:
            print(f"Subprocess execution error: {e}")
        
        # Re-initialize display and bring menu back to front cleanly
        pygame.init()
        nonlocal_screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Arcade Flashback Classics - Game Select")
        
        pygame.event.clear()
        pygame.time.delay(100)
        init_audio()
        pygame.event.clear()

    # --- 8. MAIN EVENT & RENDER LOOP ---
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
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game = games[selected_index]
                    if game["script"]:
                        launch_game(game["script"])
                    else:
                        pygame.quit()
                        return

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, game in enumerate(games):
                    if game["rect"].collidepoint(event.pos):
                        selected_index = idx
                        if game["script"]:
                            launch_game(game["script"])
                        else:
                            pygame.quit()
                            return

        # Mouse Hover Synchronization
        mouse_pos = pygame.mouse.get_pos()
        for idx, game in enumerate(games):
            if game["rect"].collidepoint(mouse_pos):
                selected_index = idx

        # Frame Drawing Pipeline
        nonlocal_screen.blit(bg_surface, (0, 0))

        # Header Bar
        pygame.draw.rect(nonlocal_screen, (25, 20, 60), (0, 0, WIDTH, 65))
        pygame.draw.line(nonlocal_screen, (100, 80, 200), (0, 65), (WIDTH, 65), 3)
        nonlocal_screen.blit(title_surf, (30, 18))

        # Cabinet Preview Frame
        cabinet_rect = pygame.Rect(40, 75, 240, 395)
        pygame.draw.rect(nonlocal_screen, (20, 20, 35), cabinet_rect, border_radius=8)
        pygame.draw.rect(nonlocal_screen, (70, 90, 160), cabinet_rect, 2, border_radius=8)

        mini_screen = pygame.Rect(55, 95, 210, 130)
        pygame.draw.rect(nonlocal_screen, (10, 10, 20), mini_screen)
        pygame.draw.rect(nonlocal_screen, (50, 60, 90), mini_screen, 1)

        current_preview = previews.get(games[selected_index]["preview_key"])
        if current_preview:
            nonlocal_screen.blit(current_preview, (65, 100))
        else:
            nonlocal_screen.blit(fallback_surf, fallback_surf.get_rect(center=mini_screen.center))

        # Render Clean Wrapped Description Text
        desc_surfs = render_wrapped_description(games[selected_index]["desc"], desc_font, 210)
        start_y = 245
        for desc_surf in desc_surfs:
            nonlocal_screen.blit(desc_surf, (55, start_y))
            start_y += 14

        # Game Select Buttons
        for idx, game in enumerate(games):
            is_selected = (idx == selected_index)
            bg_color = (40, 60, 130) if is_selected else (25, 30, 60)
            border_color = (0, 220, 255) if is_selected else (60, 70, 110)

            pygame.draw.rect(nonlocal_screen, bg_color, game["rect"], border_radius=6)
            pygame.draw.rect(nonlocal_screen, border_color, game["rect"], 2, border_radius=6)

            label_color = (255, 255, 255) if is_selected else (190, 200, 220)
            label_surf = button_font.render(game["label"], True, label_color)
            nonlocal_screen.blit(label_surf, (game["rect"].x + 20, game["rect"].y + 15))

        # Footer Bar
        footer_rect = pygame.Rect(0, HEIGHT - 40, WIDTH, 40)
        pygame.draw.rect(nonlocal_screen, (15, 10, 30), footer_rect)
        pygame.draw.line(nonlocal_screen, (70, 60, 120), (0, HEIGHT - 40), (WIDTH, HEIGHT - 40), 2)
        nonlocal_screen.blit(footer_surf, (30, HEIGHT - 26))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
