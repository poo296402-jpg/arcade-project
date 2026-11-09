import pygame
import random
import os

def run_game():
    ROWS = 25
    COLLUMNS = ROWS
    TILE_SIZE = 25
    GAME_WIDTH = TILE_SIZE * COLLUMNS
    GAME_HEIGHT = TILE_SIZE * ROWS

    pygame.init()
    sound_directory = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "snake-sounds"
    )
    
    # Optional sound loading (wrapped in try/except so game doesn't crash if folder is missing)
    try:
        die_sound = pygame.mixer.Sound(os.path.join(sound_directory, "die.wav"))
        eat_sound = pygame.mixer.Sound(os.path.join(sound_directory, "eat.wav"))
    except Exception:
        die_sound = None
        eat_sound = None

    window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Snake Arcade")
    clock = pygame.time.Clock()

    # Robust font loading for Pixeled.ttf (handles different capitalizations)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "Pixeled.ttf")
    if not os.path.exists(font_path):
        font_path = os.path.join(base_dir, "pixeled.ttf")

    # Pixel fonts run larger, so size 14-16 fits nicely at the top
    score_font = pygame.font.Font(font_path, 14) if os.path.exists(font_path) else pygame.font.Font(None, 24)

    def get_random(limit):
        return random.randint(0, limit-1) * TILE_SIZE

    snake = [pygame.Rect(get_random(COLLUMNS), get_random(ROWS), TILE_SIZE, TILE_SIZE)]
    snake_velocity = (0, 0)
    move_timer = 0
    score = 0
    high_score = 0

    def place_food():
        while True:
            candidate = pygame.Rect(get_random(COLLUMNS), get_random(ROWS), TILE_SIZE, TILE_SIZE)
            if not any(candidate.colliderect(part) for part in snake):
                return candidate

    food = place_food()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                new_velocity = snake_velocity
                if event.key in (pygame.K_UP, pygame.K_w):
                    new_velocity = (0, -TILE_SIZE)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    new_velocity = (0, TILE_SIZE)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    new_velocity = (-TILE_SIZE, 0)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    new_velocity = (TILE_SIZE, 0)

                if new_velocity != (-snake_velocity[0], -snake_velocity[1]):
                    snake_velocity = new_velocity

        move_timer += clock.get_time()
        if move_timer >= 100:
            move_timer = 0

            if snake_velocity != (0, 0):
                new_head = snake[0].copy()
                new_head.move_ip(snake_velocity)
                snake.insert(0, new_head)

                hit_wall = not window.get_rect().contains(new_head)
                hit_self = any(new_head.colliderect(part) for part in snake[1:])
                if hit_wall or hit_self:
                    if die_sound:
                        die_sound.play()
                    snake = [pygame.Rect(get_random(COLLUMNS), get_random(ROWS), TILE_SIZE, TILE_SIZE)]
                    snake_velocity = (0, 0)
                    score = 0
                    food = place_food()
                elif new_head.colliderect(food):
                    if eat_sound:
                        eat_sound.play()
                    score += 1
                    high_score = max(high_score, score)
                    food = place_food()
                else:
                    snake.pop()

        window.fill("black")
        pygame.draw.rect(window, "red", food)
        for snake_part in snake:
            pygame.draw.rect(window, "green", snake_part)

        # Render and draw the score & high score text
        score_text = score_font.render(f"SCORE: {score}   BEST: {high_score}", True, "white")
        window.blit(score_text, (15, 12))

        pygame.display.update()
        clock.tick(60)
        
    pygame.display.quit()

if __name__ == "__main__":
    run_game()