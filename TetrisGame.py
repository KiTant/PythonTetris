import pygame
import random
import time

WIDTH, HEIGHT = 300, 600
ROWS, COLS = 20, 10
CELL_SIZE = WIDTH // COLS
INITIAL_FPS = 60
MOVE_DELAY = 150

BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
WHITE = (255, 255, 255)
BORDER_COLOR = (30, 30, 30)
BACKGROUND_COLOR = (10, 10, 30)
COLORS = [
    (0, 255, 255), (0, 0, 255), (255, 165, 0),
    (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)
]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

print("""\n\nCONTROLS:
Move Left - A or Left Arrow
Move Right - D or Right Arrow
Rotate clockwise - W or Up Arrow
Drop: Soft - S or Down Arrow
Drop: Hard - Backspace or Return""")


class Tetromino:
    def __init__(self):
        self.shape = random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0
        self.placed = False

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def get_cells(self):
        return [(self.x + j, self.y + i)
                for i, row in enumerate(self.shape)
                for j, val in enumerate(row) if val]

    def collision(self, grid, dx=0, dy=0):
        for x, y in self.get_cells():
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= COLS or ny >= ROWS:
                return True
            if ny >= 0 and grid[ny][nx]:
                return True
        return False


def draw_cell(screen, x, y, color, alpha=255):
    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    cell_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
    cell_surface.fill((*color, alpha))
    screen.blit(cell_surface, rect.topleft)
    pygame.draw.rect(screen, BORDER_COLOR, rect, 2)

    if alpha == 255:
        highlight = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 255, 255, 30), (0, 0, CELL_SIZE, CELL_SIZE))
        screen.blit(highlight, (x * CELL_SIZE, y * CELL_SIZE))


def draw_grid(screen, grid):
    for y in range(ROWS):
        for x in range(COLS):
            color = grid[y][x] if grid[y][x] else GRAY
            draw_cell(screen, x, y, color)


def animate_clear(screen, grid, lines_to_clear):
    for _ in range(3):
        for y in lines_to_clear:
            for x in range(COLS):
                draw_cell(screen, x, y, WHITE)
        pygame.display.flip()
        time.sleep(0.05)
        draw_grid(screen, grid)
        pygame.display.flip()
        time.sleep(0.05)


def clear_lines(grid, screen):
    lines_to_clear = [y for y, row in enumerate(grid) if all(row)]
    if lines_to_clear:
        animate_clear(screen, grid, lines_to_clear)
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    lines_cleared = ROWS - len(new_grid)
    return [[0] * COLS for _ in range(lines_cleared)] + new_grid, len(lines_to_clear)


def draw_background(screen):
    screen.fill(BACKGROUND_COLOR)
    for i in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (20, 20, 50), (i, 0), (i, HEIGHT))
    for j in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (20, 20, 50), (0, j), (WIDTH, j))


def hard_drop(tetromino, grid):
    while not tetromino.collision(grid, dy=1):
        tetromino.y += 1
        tetromino.placed = True


def get_ghost_piece(tetromino, grid):
    ghost = Tetromino()
    ghost.shape = tetromino.shape
    ghost.color = tetromino.color
    ghost.x = tetromino.x
    ghost.y = tetromino.y
    while not ghost.collision(grid, dy=1):
        ghost.y += 1
    return ghost


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    grid = [[0] * COLS for _ in range(ROWS)]
    current = Tetromino()
    tetromino_count = 0
    score = 0
    running = True
    fall_time = 0
    last_move = pygame.time.get_ticks()

    while running:
        dt = clock.tick(INITIAL_FPS)
        fall_time += dt
        draw_background(screen)
        draw_grid(screen, grid)

        ghost = get_ghost_piece(current, grid)
        for x, y in ghost.get_cells():
            if y >= 0:
                draw_cell(screen, x, y, current.color, alpha=60)

        for x, y in current.get_cells():
            if y >= 0:
                draw_cell(screen, x, y, current.color)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                now = pygame.time.get_ticks()
                if now - last_move > MOVE_DELAY:
                    if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and not current.collision(grid, dx=-1) and current.placed is False:
                        current.x -= 1
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and not current.collision(grid, dx=1) and current.placed is False:
                        current.x += 1
                    elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and not current.collision(grid, dy=1) and current.placed is False:
                        current.y += 1
                    elif event.key == pygame.K_UP or event.key == pygame.K_w and current.placed is False:
                        current.rotate()
                        if current.collision(grid):
                            for _ in range(3):
                                current.rotate()
                    last_move = now
                if (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN) and not current.collision(grid, dy=1):
                    hard_drop(current, grid)

        if fall_time > 600:
            if not current.collision(grid, dy=1):
                current.y += 1
            else:
                current.placed = True
                for x, y in current.get_cells():
                    if y >= 0:
                        grid[y][x] = current.color
                grid, lines = clear_lines(grid, screen)
                score += 100
                score += lines * 1500
                print(f"Current score: {score}")
                current = Tetromino()
                tetromino_count += 1
                if current.collision(grid):
                    print(f"Game Over! Score: {score}; Game will close in 10 seconds")
                    time.sleep(10)
                    running = False
            fall_time = 0

    pygame.quit()

if __name__ == '__main__':
    main()
