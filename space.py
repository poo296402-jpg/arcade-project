import os
import random
import pygame

screen_width = 600
screen_height = 600
ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "space-invader-assets", "images")
SOUND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "space-invader-assets", "sounds")

# Laser Class
class Laser(pygame.sprite.Sprite):
    def __init__(self, pos, speed, color="white"):
        super().__init__()
        self.image = pygame.Surface((4, 16))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.speed = speed
        self.height_y_constraint = screen_height

    def destroy(self):
        if self.rect.y <= -50 or self.rect.y >= self.height_y_constraint + 50:
            self.kill()

    def update(self):
        self.rect.y += self.speed
        self.destroy()

# Obstacle Block Class
class Block(pygame.sprite.Sprite):
    def __init__(self, size, color, x, y):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

shape = [
    '  xxxxxxx',
    ' xxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxxxxxxxxxx',
    'xxx     xxx',
    'xx       xx'
]

# Alien Class
class Alien(pygame.sprite.Sprite):
    def __init__(self, color, x, y):
        super().__init__()
        file_path = os.path.join(ASSET_DIR, color + ".png")
        try:
            self.image = pygame.image.load(file_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (36, 26))
        except Exception:
            self.image = pygame.Surface((36, 26))
            self.image.fill((255, 0, 0) if color == "red" else (0, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, direction):
        self.rect.x += direction

def run_game():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Space Invaders")
    clock = pygame.time.Clock()

    # Larger Font Setup for Pixeled.ttf
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "Pixeled.ttf")
    if not os.path.exists(font_path):
        font_path = os.path.join(base_dir, "pixeled.ttf")
    
    font = pygame.font.Font(font_path, 16) if os.path.exists(font_path) else pygame.font.Font(None, 28)
    game_over_font = pygame.font.Font(font_path, 22) if os.path.exists(font_path) else pygame.font.Font(None, 36)

    # Audio Setup helper
    def load_sound(filename):
        path = os.path.join(SOUND_DIR, filename)
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except pygame.error:
                pass
        return None

    laser_sound = load_sound("laser.wav") or load_sound("shoot.wav")
    if laser_sound:
        laser_sound.set_volume(0.6)

    explosion_sound = load_sound("explosion.wav") or load_sound("die.wav")
    if explosion_sound:
        explosion_sound.set_volume(0.8)

    # Force Background Music using Sound channel with volume set to maximum (1.0)
    bgm_channel = None
    music_path = r"C:\Users\natti\Downloads\arcade-game-project\space-invader-assets\sounds\music.wav"
    if not os.path.exists(music_path):
        music_path = os.path.join(SOUND_DIR, "music.wav")

    if os.path.exists(music_path):
        try:
            bgm_sound = pygame.mixer.Sound(music_path)
            bgm_sound.set_volume(1.0)  # Max volume for BGM
            bgm_channel = bgm_sound.play(loops=-1)
        except Exception as e:
            print(f"BGM Sound error: {e}")

    # Player Class
    class Player(pygame.sprite.Sprite):
        def __init__(self, pos, constraint, speed):
            super().__init__()
            try:
                self.image = pygame.image.load(os.path.join(ASSET_DIR, "player.png")).convert_alpha()
                self.image = pygame.transform.scale(self.image, (34, 20))
            except Exception:
                self.image = pygame.Surface((34, 20))
                self.image.fill((0, 255, 255))
            
            self.rect = self.image.get_rect(midbottom=pos)
            self.speed = speed
            self.max_x_constraint = constraint
            self.ready = True
            self.laser_time = 0
            self.laser_cooldown = 450

            self.lasers = pygame.sprite.Group()

        def get_input(self):
            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rect.x += self.speed
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rect.x -= self.speed

            if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.ready:
                self.shoot_laser()
                self.ready = False
                self.laser_time = pygame.time.get_ticks()

        def recharge(self):
            if not self.ready:
                current_time = pygame.time.get_ticks()
                if current_time - self.laser_time >= self.laser_cooldown:
                    self.ready = True

        def constraint(self):
            if self.rect.left <= 0:
                self.rect.left = 0
            if self.rect.right >= self.max_x_constraint:
                self.rect.right = self.max_x_constraint

        def shoot_laser(self):
            self.lasers.add(Laser(self.rect.center, -7, "white"))
            if laser_sound:
                laser_sound.play()

        def update(self):
            self.get_input()
            self.constraint()
            self.recharge()
            self.lasers.update()

    # Main Game Class
    class Game:
        def __init__(self, screen, screen_width):
            player_sprite = Player((300, 565), screen_width, 4)
            self.player = pygame.sprite.GroupSingle()
            self.player.add(player_sprite)
            self.screen = screen

            self.shape = shape
            self.block_size = 5
            self.blocks = pygame.sprite.Group()
            self.create_multiple_obstacles(0, 440, 0, 150, 300, 450)

            self.aliens = pygame.sprite.Group()
            self.alien_lasers = pygame.sprite.Group()
            self.alien_setup()
            self.alien_direction = 1
            self.alien_move_counter = 0

            self.score = 0
            self.high_score = 0
            self.lives = 3
            self.game_over = False

            # Load visual life icon matching user screenshot style
            try:
                self.life_icon = pygame.image.load(os.path.join(ASSET_DIR, "player.png")).convert_alpha()
                self.life_icon = pygame.transform.scale(self.life_icon, (28, 16))
            except Exception:
                self.life_icon = pygame.Surface((28, 16))
                self.life_icon.fill((0, 255, 255))

        def create_obstacle(self, x_start, y_start, offset_x):
            for row_index, row in enumerate(self.shape):
                for col_index, col in enumerate(row):
                    if col == 'x':
                        x = x_start + col_index * self.block_size + offset_x
                        y = y_start + row_index * self.block_size
                        block = Block(self.block_size, (241, 79, 80), x, y)
                        self.blocks.add(block)

        def create_multiple_obstacles(self, x_start, y_start, *offset):
            for offset_x in offset:
                self.create_obstacle(x_start, y_start, offset_x)

        def alien_setup(self):
            alien_colors = ("yellow", "green", "green", "red", "red")
            for row_index, color in enumerate(alien_colors):
                for col_index in range(8):
                    x = 60 + col_index * 58
                    y = 50 + row_index * 38
                    self.aliens.add(Alien(color, x, y))

        def alien_position_checker(self):
            all_aliens = self.aliens.sprites()
            for alien in all_aliens:
                if alien.rect.right >= screen_width - 15:
                    self.alien_direction = -1
                    self.move_aliens_down(12)
                    break
                elif alien.rect.left <= 15:
                    self.alien_direction = 1
                    self.move_aliens_down(12)
                    break

        def move_aliens_down(self, distance):
            for alien in self.aliens:
                alien.rect.y += distance

        def alien_shoot(self):
            if self.aliens.sprites() and not self.game_over:
                random_alien = random.choice(self.aliens.sprites())
                self.alien_lasers.add(Laser(random_alien.rect.center, 4, "red"))

        def collision_checks(self):
            # Player lasers vs Aliens and Blocks
            if self.player.sprite.lasers:
                for laser in self.player.sprite.lasers:
                    if pygame.sprite.spritecollide(laser, self.blocks, True):
                        laser.kill()
                    
                    aliens_hit = pygame.sprite.spritecollide(laser, self.aliens, True)
                    if aliens_hit:
                        laser.kill()
                        self.score += len(aliens_hit) * 100
                        self.high_score = max(self.high_score, self.score)
                        if explosion_sound:
                            explosion_sound.play()

            # Alien lasers vs Player and Blocks
            if self.alien_lasers:
                for laser in self.alien_lasers:
                    if pygame.sprite.spritecollide(laser, self.blocks, True):
                        laser.kill()

                    if pygame.sprite.spritecollide(laser, self.player, False):
                        laser.kill()
                        self.lives -= 1
                        if explosion_sound:
                            explosion_sound.play()
                        
                        # Respawn player and clear enemy lasers on life loss
                        if self.lives > 0:
                            self.player.sprite.rect.center = (300, 565)
                            self.player.sprite.lasers.empty()
                            self.alien_lasers.empty()
                        else:
                            self.game_over = True

            # Aliens vs Player or Bottom boundary
            if self.aliens:
                for alien in self.aliens:
                    pygame.sprite.spritecollide(alien, self.blocks, True)
                    if pygame.sprite.spritecollide(alien, self.player, False) or alien.rect.bottom >= 490:
                        self.game_over = True

        def run(self):
            if not self.game_over:
                self.player.update()
                
                self.alien_move_counter += 1
                if self.alien_move_counter >= 2:
                    self.aliens.update(self.alien_direction)
                    self.alien_position_checker()
                    self.alien_move_counter = 0

                self.alien_lasers.update()
                self.collision_checks()

            # Draw Game Sprites
            self.blocks.draw(self.screen)
            self.aliens.draw(self.screen)
            self.alien_lasers.draw(self.screen)
            self.player.sprite.lasers.draw(self.screen)
            self.player.draw(self.screen)

            # Draw Larger Score HUD
            score_surf = font.render(f"SCORE: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_surf, (20, 15))

            # Draw visual life icons at top right
            for i in range(self.lives):
                x_pos = screen_width - 40 - (i * 38)
                self.screen.blit(self.life_icon, (x_pos, 18))

            # Game Over Display
            if self.game_over:
                go_surf = game_over_font.render("GAME OVER", True, (255, 0, 0))
                restart_surf = font.render("Press 'R' to Restart", True, (255, 255, 255))
                self.screen.blit(go_surf, go_surf.get_rect(center=(screen_width / 2, screen_height / 2 - 25)))
                self.screen.blit(restart_surf, restart_surf.get_rect(center=(screen_width / 2, screen_height / 2 + 20)))

        def reset(self):
            self.score = 0
            self.lives = 3
            self.game_over = False
            self.aliens.empty()
            self.blocks.empty()
            self.alien_lasers.empty()
            self.player.sprite.lasers.empty()
            self.player.sprite.rect.center = (300, 565)
            self.create_multiple_obstacles(0, 440, 0, 150, 300, 450)
            self.alien_setup()

    game = Game(screen, screen_width)

    # Timer event for alien firing lasers every 1.2 seconds
    ALIEN_SHOOT = pygame.USEREVENT + 1
    pygame.time.set_timer(ALIEN_SHOOT, 1200)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if bgm_channel:
                    bgm_channel.stop()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if bgm_channel:
                        bgm_channel.stop()
                    running = False
                if event.key == pygame.K_r and game.game_over:
                    game.reset()

            if event.type == ALIEN_SHOOT:
                game.alien_shoot()

        screen.fill((15, 10, 35))
        game.run()

        pygame.display.flip()
        clock.tick(60)

    if bgm_channel:
        bgm_channel.stop()
    return

if __name__ == '__main__':
    run_game()