import pygame
import random
import os

def run_game():
    pygame.init()
    pygame.key.set_repeat(150, 75)

    screen = pygame.display.set_mode((420, 600))
    pygame.display.set_caption("Tetris")

    clock = pygame.time.Clock()

    # --- PIXEL FONT SETUP ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(base_dir, "Pixeled.ttf")
    if not os.path.exists(font_path):
        font_path = os.path.join(base_dir, "pixeled.ttf")

    music_path = os.path.join(base_dir, "tetris-music", "music.mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)

    font = pygame.font.Font(font_path, 12) if os.path.exists(font_path) else pygame.font.Font(None, 24)

    #colors
    class Colors:
        dark_grey = (26, 31, 40)
        green = (42, 230, 23)
        red = (132, 18, 18)
        orange = (226, 116, 17)
        yellow = (237, 234, 4)
        purple = (166, 0, 247)
        cyan = (21, 204, 209)
        blue = (13, 64, 216)

        @classmethod
        def get_cell_color(cls):
            return [cls.dark_grey, cls.green, cls.red, cls.orange, cls.yellow, cls.purple, cls.cyan, cls.blue]

    #grid
    class Grid:
        def __init__(self):
            self.num_cols = 10
            self.num_rows = 20
            self.cell_size = 30
            self.grid = [[0 for _ in range(self.num_cols)] for _ in range(self.num_rows)]
            self.colors = Colors.get_cell_color()

        def is_inside(self, row, column):
            return 0 <= row < self.num_rows and 0 <= column < self.num_cols

        def is_empty(self, row, column):
            return self.is_inside(row, column) and self.grid[row][column] == 0

        def is_row_full(self, row):
            for column in range(self.num_cols):
                if self.grid[row][column] == 0:
                    return False
            return True

        def clear_row(self, row):
            for column in range(self.num_cols):
                self.grid[row][column] = 0

        def move_row_down(self, row, num_rows):
            if not 0 <= row < self.num_rows or not 0 <= row + num_rows < self.num_rows:
                return
            for column in range(self.num_cols):
                self.grid[row + num_rows][column] = self.grid[row][column]
                self.grid[row][column] = 0

        def clear_full_rows(self):
            # Rebuild the board from the rows that are not full.  This also
            # handles row 0 and multiple adjacent completed rows correctly.
            remaining_rows = [
                row for row in self.grid
                if any(cell == 0 for cell in row)
            ]
            completed = self.num_rows - len(remaining_rows)
            self.grid = (
                [[0 for _ in range(self.num_cols)] for _ in range(completed)]
                + remaining_rows
            )
            return completed

        def draw(self, screen):
            for row in range(self.num_rows):
                for column in range(self.num_cols):
                    cell_value = self.grid[row][column]
                    if not 0 <= cell_value < len(self.colors):
                        cell_value = 0
                    cell_rect = pygame.Rect(
                        column * self.cell_size,
                        row * self.cell_size,
                        self.cell_size - 1,
                        self.cell_size - 1,
                    )
                    pygame.draw.rect(screen, self.colors[cell_value], cell_rect)

    # position
    class Position:
        def __init__(self, row, column):
            self.row = row
            self.column = column

    #block
    class Block:
        def __init__(self, id):
            self.id = id
            self.cells = {}
            self.cells_size = 30
            self.row_offset = 0
            self.column_offset = 0
            self.rotation_state = 0
            self.color = Colors.get_cell_color()

        def move(self, rows, columns):
            self.row_offset += rows
            self.column_offset += columns

        def get_cell_positions(self):
            tiles = self.cells.get(self.rotation_state, ())
            moved_tiles = []
            for position in tiles:
                position = Position(position.row + self.row_offset, position.column + self.column_offset)
                moved_tiles.append(position)
            return moved_tiles

        def rotate(self):
            if len(self.cells) <= 1:
                return
            self.rotation_state += 1
            if self.rotation_state == len(self.cells):
                self.rotation_state = 0

        def undo_rotation(self):
            self.rotation_state -= 1
            if self.rotation_state < 0:
                self.rotation_state = len(self.cells) - 1

        def draw(self, screen):
            tiles = self.get_cell_positions()
            for tile in tiles:
                if not (0 <= tile.row < 20 and 0 <= tile.column < 10):
                    continue
                tile_rect = pygame.Rect(tile.column * self.cells_size + 1, tile.row * self.cells_size + 1,
                self.cells_size - 1, self.cells_size - 1)
                color = self.color[self.id] if 0 <= self.id < len(self.color) else self.color[0]
                pygame.draw.rect(screen, color, tile_rect)

    #blocks
    class LBlock(Block):
        def __init__(self):
            super().__init__(id = 1)
            self.cells = {
                0: [Position(0, 2), Position(1, 0), Position(1, 1), Position(1, 2)], 
                1: [Position(0, 1), Position(1, 1), Position(2, 1), Position(2, 2)],
                2: [Position(1, 0), Position(1, 1), Position(1, 2), Position(2, 2)],
                3: [Position(0, 0), Position(0, 1), Position(1, 1), Position(2, 1)]
            }
            self.move(0, 3)

    class JBlock(Block):
        def __init__(self):
            super().__init__(id = 2)
            self.cells = {
                0: [Position(0,0), Position(1,0), Position(1,1), Position(1,2)],
                1: [Position(0,1), Position(0,2), Position(1,1), Position(2,1)],
                2: [Position(1,0), Position(1,1), Position(1,2), Position(2,2)],
                3: [Position(0,1), Position(1,1), Position(2,0), Position(2,1)]
            }
            self.move(0, 3)

    class IBlock(Block):
        def __init__(self):
            super().__init__(id = 3)
            self.cells = {
                0: [Position(1,0), Position(1,1), Position(1,2), Position(1,3)],
                1: [Position(0,2), Position(1,2), Position(2,2), Position(3,2)],
                2: [Position(2,0), Position(2,1), Position(2,2), Position(2,3)],
                3: [Position(0,1), Position(1,1), Position(2,1), Position(3,1)]
            }
            self.move(-1, 3)

    class OBlock(Block):
        def __init__(self):
            super().__init__(id = 4)
            self.cells = {
                0: [Position(0,0), Position(0,1), Position(1,0), Position(1,1)],
                1: [Position(0,0), Position(0,1), Position(1,0), Position(1,1)],
                2: [Position(0,0), Position(0,1), Position(1,0), Position(1,1)],
                3: [Position(0,0), Position(0,1), Position(1,0), Position(1,1)]
            }
            self.move(0, 4)

    class SBlock(Block):
        def __init__(self):
            super().__init__(id = 5)
            self.cells = {
                0: [Position(0,1), Position(0,2), Position(1,0), Position(1,1)],
                1: [Position(0,1), Position(1,1), Position(1,2), Position(2,2)],
                2: [Position(1,1), Position(1,2), Position(2,0), Position(2,1)],
                3: [Position(0,0), Position(1,0), Position(1,1), Position(2,1)]
            }
            self.move(0, 3)

    class TBlock(Block):
        def __init__(self):
            super().__init__(id = 6)
            self.cells = {
                0: [Position(0,1), Position(1,0), Position(1,1), Position(1,2)],
                1: [Position(0,1), Position(1,1), Position(1,2), Position(2,1)],
                2: [Position(1,0), Position(1,1), Position(1,2), Position(2,1)],
                3: [Position(0,1), Position(1,0), Position(1,1), Position(2,1)]
            }
            self.move(0, 3)

    class ZBlock(Block):
        def __init__(self):
            super().__init__(id = 7)
            self.cells = {
                0: [Position(0,0), Position(0,1), Position(1,1), Position(1,2)],
                1: [Position(0,2), Position(1,1), Position(1,2), Position(2,1)],
                2: [Position(1,0), Position(1,1), Position(2,1), Position(2,2)],
                3: [Position(0,1), Position(1,0), Position(1,1), Position(2,0)]
            }
            self.move(0, 3)

    class Game:
        def __init__(self):
            self.grid = Grid()
            self.blocks = [LBlock(), JBlock(), IBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
            self.current_block = self.get_random_block()
            self.next_block = self.get_random_block()
            self.game_over = False
            self.score = 0
            self.best = 0

        def get_random_block(self):
            if len(self.blocks) == 0:
                self.blocks = [LBlock(), JBlock(), IBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
            block = random.choice(self.blocks)
            self.blocks.remove(block)
            return block

        def move_left(self):
            if self.game_over:
                return
            self.current_block.move(0, -1)
            if not self.block_inside() or not self.block_fits():
                 self.current_block.move(0, 1)

        def move_right(self):
            if self.game_over:
                return
            self.current_block.move(0, 1)
            if not self.block_inside() or not self.block_fits():
                 self.current_block.move(0, -1)

        def lock_block(self):
            tiles = self.current_block.get_cell_positions()
            for position in tiles:
                if self.grid.is_inside(position.row, position.column):
                    self.grid.grid[position.row][position.column] = self.current_block.id
            self.current_block = self.next_block
            self.next_block = self.get_random_block()
            completed = self.grid.clear_full_rows()
            # A completed-row count can exceed four when several rows are
            # already full, so keep the score lookup within the valid range.
            self.score += (0, 100, 300, 500, 800)[min(completed, 4)]
            self.best = max(self.best, self.score)
            if not self.block_fits():
                self.game_over = True

        def block_fits(self):
            tiles = self.current_block.get_cell_positions()
            for tile in tiles:
                if not self.grid.is_inside(tile.row, tile.column):
                    return False
                if not self.grid.is_empty(tile.row, tile.column):
                    return False
            return True

        def move_down(self):
            if self.game_over:
                return
            self.current_block.move(1, 0)
            if not self.block_inside() or not self.block_fits():
                 self.current_block.move(-1, 0)
                 self.lock_block()

        def rotate(self):
            if self.game_over:
                return
            self.current_block.rotate()
            if not self.block_inside() or not self.block_fits():
                self.current_block.undo_rotation()

        def block_inside(self):
            tiles = self.current_block.get_cell_positions()
            for tile in tiles:
                if not self.grid.is_inside(tile.row, tile.column):
                   return False
            return True

        def reset(self):
            best_score = self.best
            self.grid = Grid()
            self.blocks = [LBlock(), JBlock(), IBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
            self.current_block = self.get_random_block()
            self.next_block = self.get_random_block()
            self.game_over = False
            self.score = 0
            self.best = best_score

        def draw(self, screen):
            self.grid.draw(screen)
            self.current_block.draw(screen)

        def draw_next_block(self, screen):
            preview_tiles = self.next_block.cells[0]
            cell_size = 24
            preview_x = 345
            preview_y = 85
            min_row = min(tile.row for tile in preview_tiles)
            min_column = min(tile.column for tile in preview_tiles)

            for tile in preview_tiles:
                tile_rect = pygame.Rect(
                    preview_x + (tile.column - min_column) * cell_size,
                    preview_y + (tile.row - min_row) * cell_size,
                    cell_size - 1,
                    cell_size - 1,
                )
                pygame.draw.rect(
                    screen,
                    self.next_block.color[self.next_block.id],
                    tile_rect,
                )

    game = Game()

    GAME_UPDATE = pygame.USEREVENT
    pygame.time.set_timer(GAME_UPDATE, 1000)

    rotate_held = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.key.set_repeat()
                pygame.mixer.music.stop()
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.key.set_repeat()
                    pygame.mixer.music.stop()
                    pygame.quit()
                    return
                if event.key == pygame.K_LEFT:
                    game.move_left()
                if event.key == pygame.K_RIGHT:
                    game.move_right()
                if event.key == pygame.K_DOWN:
                    game.move_down()
                if event.key == pygame.K_SPACE and not rotate_held:
                    game.rotate()
                    rotate_held = True
                if event.key == pygame.K_r and game.game_over:
                    game.reset()
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                rotate_held = False
            if event.type == GAME_UPDATE:
                game.move_down()

        screen.fill((10, 25, 70))
        game.draw(screen)
        next_surface = font.render("NEXT", True, (255, 255, 255))
        screen.blit(next_surface, (335, 45))
        game.draw_next_block(screen)

        score_surface = font.render(f"SCORE {game.score}", True, (255, 255, 255))
        best_surface = font.render(f"BEST {game.best}", True, (255, 255, 255))
        screen.blit(score_surface, score_surface.get_rect(topright=(415, 5)))
        screen.blit(best_surface, best_surface.get_rect(topright=(415, 25)))

        # Draw Game Over message matching Flappy Bird style
        if game.game_over:
            game_over_surface = font.render("GAME OVER", True, (255, 0, 0))
            restart_surface = font.render("Press 'R' to Restart", True, (255, 255, 255))
            screen.blit(game_over_surface, game_over_surface.get_rect(center=(300 / 2, 600 / 2 - 20)))
            screen.blit(restart_surface, restart_surface.get_rect(center=(300 / 2, 600 / 2 + 20)))

        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    run_game()