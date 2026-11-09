import sys
import ctypes
import pygame

# Fix Windows DPI scaling cut-offs when spawned or run standalone
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

pygame.init()

WIDTH = 893
HEIGHT = 800
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Arcade Flashback Classics - Breakout")
clock = pygame.time.Clock()
FPS = 60

WHITE = (255, 255, 255)
GREY = (212, 210, 212)
BLACK = (0, 0, 0)
BLUE = (0, 97, 148)

RED = (162, 8, 8)
ORANGE = (183, 119, 0)
GREEN = (0, 127, 33)
YELLOW = (197, 199, 37)

score = 0
balls = 1
velocity = 4

paddle_width = 54
paddle_height = 20
wall_width = 16

all_sprites_list = pygame.sprite.Group()

class Brick(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        pygame.draw.rect(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()

class Paddle(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        pygame.draw.rect(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()

    def moveRight(self, pixels):
        self.rect.x += pixels
        if self.rect.x > WIDTH - wall_width - paddle_width:
            self.rect.x = WIDTH - wall_width - paddle_width

    def moveLeft(self, pixels):
        self.rect.x -= pixels
        if self.rect.x < wall_width:
            self.rect.x = wall_width

class Ball(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.velocity = [velocity, -velocity]

    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

    def bounce(self, axis):
        if axis == "x":
            self.velocity[0] = -self.velocity[0]
        elif axis == "y":
            self.velocity[1] = -self.velocity[1]

paddle = Paddle(BLUE, paddle_width, paddle_height)
paddle.rect.x = WIDTH // 2 - paddle_width // 2
paddle.rect.y = HEIGHT - 65

ball = Ball(WHITE, 10, 10)
ball.rect.x = WIDTH // 2 - 5
ball.rect.y = HEIGHT // 2 - 5

all_bricks = pygame.sprite.Group()

brick_width = 55
brick_height = 16
x_gap = 7
y_gap = 5
wall_width = 16


def bricks():
    row_colors = [RED, RED, ORANGE, ORANGE, GREEN, GREEN, YELLOW, YELLOW]
    for j, color in enumerate(row_colors):
        for i in range(14):
            brick = Brick(color, brick_width, brick_height)
            brick.rect.x = wall_width + i * (brick_width + x_gap)
            brick.rect.y = 215 + j * (y_gap + brick_height)
            all_sprites_list.add(brick)
            all_bricks.add(brick)

    all_sprites_list.add(paddle)
    all_sprites_list.add(ball)


def main():
    global score
    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.moveLeft(10)
        if keys[pygame.K_RIGHT]:
            paddle.moveRight(10)

        ball.update()

        if ball.rect.y <= 20:
            ball.velocity[1] = abs(ball.velocity[1])

        if ball.rect.x >= WIDTH - wall_width - 10:
            ball.velocity[0] = -abs(ball.velocity[0])

        if ball.rect.x <= wall_width:
            ball.velocity[0] = abs(ball.velocity[0])

        if ball.rect.colliderect(paddle.rect):
            if ball.velocity[1] > 0:
                ball.rect.y = paddle.rect.y - ball.rect.height
                ball.velocity[1] = -abs(ball.velocity[1])
                hit_pos = (ball.rect.centerx - paddle.rect.centerx) / (paddle_width / 2)
                ball.velocity[0] = int(hit_pos * 6)

        for brick in list(all_bricks):
            if ball.rect.colliderect(brick.rect):
                if abs(ball.rect.right - brick.rect.left) < 10 or abs(ball.rect.left - brick.rect.right) < 10:
                    ball.velocity[0] = -ball.velocity[0]
                else:
                    ball.velocity[1] = -ball.velocity[1]
                all_bricks.remove(brick)
                all_sprites_list.remove(brick)
                score += 1
                break

        if ball.rect.y > HEIGHT:
            ball.rect.x = WIDTH // 2 - 5
            ball.rect.y = HEIGHT // 2 - 5
            ball.velocity = [velocity, -velocity]

        screen.fill(BLACK)

        pygame.draw.line(screen, GREY, [0, 19], [WIDTH, 19], 40)
        pygame.draw.line(screen, GREY, [(wall_width / 2) - 1, 0], [(wall_width / 2) - 1, HEIGHT], wall_width)
        pygame.draw.line(screen, GREY, [(WIDTH - wall_width / 2) - 1, 0], [(WIDTH - wall_width / 2) - 1, HEIGHT], wall_width)

        pygame.draw.line(screen, BLUE, [(wall_width / 2) - 1, HEIGHT - 65 + paddle_height / 2 - 54 / 2], [(wall_width / 2) - 1, HEIGHT - 65 + paddle_height / 2 - 54 / 2 + 54], wall_width)
        pygame.draw.line(screen, BLUE, [(WIDTH - wall_width / 2) - 1, HEIGHT - 65 + paddle_height / 2 - 54 / 2], [(WIDTH - wall_width / 2) - 1, HEIGHT - 65 + paddle_height / 2 - 54 / 2 + 54], wall_width)

        pygame.draw.line(screen, RED, [(wall_width / 2) - 1, 212.5], [(wall_width / 2) - 1, 212.5 + 2 * brick_height + 2 * y_gap], wall_width)
        pygame.draw.line(screen, RED, [(WIDTH - wall_width / 2) - 1, 212.5], [(WIDTH - wall_width / 2) - 1, 212.5 + 2 * brick_height + 2 * y_gap], wall_width)

        pygame.draw.line(screen, ORANGE, [(wall_width / 2) - 1, 212.5 + 2 * brick_height + 2 * y_gap], [(wall_width / 2) - 1, 212.5 + 4 * brick_height + 4 * y_gap], wall_width)
        pygame.draw.line(screen, ORANGE, [(WIDTH - wall_width / 2) - 1, 212.5 + 2 * brick_height + 2 * y_gap], [(WIDTH - wall_width / 2) - 1, 212.5 + 4 * brick_height + 4 * y_gap], wall_width)

        pygame.draw.line(screen, GREEN, [(wall_width / 2) - 1, 212.5 + 4 * brick_height + 4 * y_gap], [(wall_width / 2) - 1, 212.5 + 6 * brick_height + 6 * y_gap], wall_width)
        pygame.draw.line(screen, GREEN, [(WIDTH - wall_width / 2) - 1, 212.5 + 4 * brick_height + 4 * y_gap], [(WIDTH - wall_width / 2) - 1, 212.5 + 6 * brick_height + 6 * y_gap], wall_width)

        pygame.draw.line(screen, YELLOW, [(wall_width / 2) - 1, 212.5 + 6 * brick_height + 6 * y_gap], [(wall_width / 2) - 1, 212.5 + 8 * brick_height + 8 * y_gap], wall_width)
        pygame.draw.line(screen, YELLOW, [(WIDTH - wall_width / 2) - 1, 212.5 + 6 * brick_height + 6 * y_gap], [(WIDTH - wall_width / 2) - 1, 212.5 + 8 * brick_height + 8 * y_gap], wall_width)

        all_sprites_list.draw(screen)
        pygame.display.flip()

    pygame.quit()


def run_game():
    main()


if __name__ == "__main__":
    bricks()
    main()