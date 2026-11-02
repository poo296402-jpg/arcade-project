import pygame
import random
import os

def run_game():
    GAME_WIDTH = 360
    GAME_HEIGHT = 640

    bird_x = GAME_WIDTH / 8
    bird_y = GAME_HEIGHT / 2
    bird_width = 34
    bird_height = 24

    class Bird(pygame.Rect):
        def __init__(self, img):
            pygame.Rect.__init__(self, bird_x, bird_y, bird_width, bird_height)
            self.img = img

    pipe_x = GAME_WIDTH
    pipe_y = 0
    pipe_width = 64
    pipe_height = 512

    class Pipe(pygame.Rect):
        def __init__(self, img):
            pygame.Rect.__init__(self, pipe_x, pipe_y, pipe_width, pipe_height)
            self.img = img
            self.passed = False

    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    window = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()

    # Robust font loading for Pixeled.ttf / pixeled.ttf
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "Pixeled.ttf")
    if not os.path.exists(font_path):
        font_path = os.path.join(base_dir, "pixeled.ttf")

    font = pygame.font.Font(font_path, 14) if os.path.exists(font_path) else pygame.font.Font(None, 24)

    background_image = pygame.image.load("flappybird-assets/flappybirdbg.png")
    bird_image = pygame.image.load("flappybird-assets/flappybird.png")
    bird_image = pygame.transform.scale(bird_image, (bird_width, bird_height))
    top_pipe_image = pygame.image.load("flappybird-assets/toppipe.png")
    top_pipe_image = pygame.transform.scale(top_pipe_image, (pipe_width, pipe_height))
    bottom_pipe_image = pygame.image.load("flappybird-assets/bottompipe.png")
    bottom_pipe_image = pygame.transform.scale(bottom_pipe_image, (pipe_width, pipe_height))

    # Audio files are optional so the game still runs if they are not present.
    asset_folder = r"flappybird-assets/sounds/"

    def load_sound(*filenames):
        for filename in filenames:
            path = os.path.join(asset_folder, filename)
            if os.path.exists(path):
                try:
                    return pygame.mixer.Sound(path)
                except pygame.error:
                    pass
        return None

    jump_sound = load_sound("flap.wav")
    score_sound = load_sound("score.wav")
    game_over_sound = load_sound("die.wav")

    for music_file in ("music.wav",):
        music_path = os.path.join(asset_folder, music_file)
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
                break
            except pygame.error:
                pass

    # Game variables
    bird = Bird(bird_image)
    pipes = []
    velocity_x = -2
    velocity_y = 0
    gravity = 0.4
    score = 0
    high_score = 0
    game_over = False

    def set_game_over():
        nonlocal game_over
        if not game_over:
            game_over = True
            if game_over_sound:
                game_over_sound.play()

    def reset_game():
        nonlocal velocity_y, score, game_over
        bird.x = bird_x
        bird.y = bird_y
        velocity_y = 0
        pipes.clear()
        score = 0
        game_over = False

    def move():
        nonlocal velocity_y, game_over, score, high_score
        if game_over:
            return

        # Apply gravity to bird
        velocity_y += gravity
        bird.y += velocity_y

        # Check collision with floor or ceiling
        if bird.y <= 0 or bird.y >= GAME_HEIGHT - bird_height:
            set_game_over()

        for pipe in pipes:
            pipe.x += velocity_x

            # Check collision with pipes
            if bird.colliderect(pipe):
                set_game_over()

            # Score logic (check when passing top pipe)
            if pipe.img == top_pipe_image and not pipe.passed and pipe.x + pipe_width < bird.x:
                pipe.passed = True
                score += 1
                high_score = max(high_score, score)
                if score_sound:
                    score_sound.play()

        # Remove off-screen pipes
        while len(pipes) > 0 and pipes[0].x < -pipe_width:
            pipes.pop(0)

    def draw():
        window.blit(background_image, (0, 0))
        window.blit(bird.img, bird)

        for pipe in pipes:
            window.blit(pipe.img, pipe)

        # Draw Score and Best High Score at the top
        score_surface = font.render(f"SCORE: {score}   BEST: {high_score}", True, (255, 255, 255))
        window.blit(score_surface, score_surface.get_rect(center=(GAME_WIDTH / 2, 35)))

        # Draw Game Over message
        if game_over:
            game_over_surface = font.render("GAME OVER", True, (255, 0, 0))
            restart_surface = font.render("Press 'R' to Restart", True, (255, 255, 255))
            window.blit(game_over_surface, game_over_surface.get_rect(center=(GAME_WIDTH / 2, GAME_HEIGHT / 2 - 40)))
            window.blit(restart_surface, restart_surface.get_rect(center=(GAME_WIDTH / 2, GAME_HEIGHT / 2 + 10)))

    def create_pipes():
        if game_over:
            return
        opening_space = GAME_HEIGHT / 4
        random_pipe_y = random.randint(-int(pipe_height * 3 / 4), -int(pipe_height / 4))

        top_pipe = Pipe(top_pipe_image)
        top_pipe.y = random_pipe_y
        pipes.append(top_pipe)

        bottom_pipe = Pipe(bottom_pipe_image)
        bottom_pipe.y = top_pipe.y + pipe_height + opening_space
        pipes.append(bottom_pipe)

    create_pipes_timer = pygame.USEREVENT + 0
    pygame.time.set_timer(create_pipes_timer, 1500)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_SPACE and not game_over:
                    velocity_y = -7
                    if jump_sound:
                        jump_sound.play()
                if event.key == pygame.K_r and game_over:
                    reset_game()

            if event.type == create_pipes_timer:
                create_pipes()

        move()
        draw()
        pygame.display.update()
        clock.tick(60)

    pygame.display.quit()
    pygame.mixer.music.stop()
    pygame.mixer.quit()

if __name__ == "__main__":
    run_game()