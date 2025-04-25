import pygame
import random
from queue import Queue

WIDTH = 600
ROWS = 30
WIN = pygame.display.set_mode((WIDTH + 150, WIDTH))
pygame.display.set_caption("BFS Pathfinding Visualizer")
pygame.font.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
RED = (255, 0, 0)
DARK_GREY = (50, 50, 50)
BLUE = (0, 0, 255)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self): return self.row, self.col
    def is_barrier(self): return self.color == BLACK
    def is_start(self): return self.color == ORANGE
    def is_end(self): return self.color == TURQUOISE

    def reset(self): self.color = WHITE
    def make_start(self): self.color = ORANGE
    def make_end(self): self.color = TURQUOISE
    def make_barrier(self): self.color = BLACK
    def make_open(self): self.color = GREEN
    def make_closed(self): self.color = GREY
    def make_path(self): self.color = PURPLE
    def make_error(self): self.color = RED

    def draw(self, win): pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])

def make_grid(rows, width):
    gap = width // rows
    return [[Node(i, j, gap, rows) for j in range(rows)] for i in range(rows)]

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))

def draw_sidebar(win, buttons):
    pygame.draw.rect(win, DARK_GREY, pygame.Rect(WIDTH, 0, 150, WIDTH))
    font = pygame.font.Font(None, 30)
    for i, button in enumerate(buttons):
        color = BLUE if button.get('active') else WHITE
        pygame.draw.rect(win, color, pygame.Rect(WIDTH + 10, 30 + 40 * i, 130, 30))
        text = font.render(button['text'], True, BLACK)
        win.blit(text, (WIDTH + 15, 30 + 40 * i + 5))

def draw(win, grid, rows, width, message=None, buttons=None):
    if buttons is None: buttons = []
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)
    draw_sidebar(win, buttons)
    if message:
        font = pygame.font.Font(None, 30)
        text = font.render(message, True, RED)
        win.blit(text, (WIDTH // 2 - text.get_width() // 2, WIDTH // 2 - text.get_height() // 2))
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos
    row = y // gap
    col = x // gap
    return row, col

def bfs(draw, grid, start, end, rows, width, fast=False):
    for row in grid:
        for node in row:
            # Don't reset barriers, start, or end nodes
            if node != start and node != end and not node.is_barrier():
                node.reset()

    queue = Queue()
    queue.put(start)
    visited = {start}
    came_from = {}

    while not queue.empty():
        current = queue.get()
        if current == end:
            while current in came_from:
                current = came_from[current]
                if current != start:
                    current.make_path()
                draw(WIN, grid, rows, width)
                if not fast: pygame.time.delay(10)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                neighbor.make_open()
                queue.put(neighbor)

        draw(WIN, grid, rows, width)
        if current != start: current.make_closed()
        if not fast: pygame.time.delay(10)

    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 1500:
        draw(WIN, grid, rows, width, message="Path not found!")
    return False

def random_maze(grid, rows):
    for row in grid:
        for node in row:
            node.reset()
    start, end = None, None
    while not start or not end or start == end:
        sr, sc = random.randint(0, rows - 1), random.randint(0, rows - 1)
        er, ec = random.randint(0, rows - 1), random.randint(0, rows - 1)
        start = grid[sr][sc]
        end = grid[er][ec]
    start.make_start()
    end.make_end()
    for row in grid:
        for node in row:
            if node != start and node != end and random.random() < 0.3:
                node.make_barrier()
    return start, end

def main(win, width):
    grid = make_grid(ROWS, width)
    start, end = None, None
    run = True
    fast_mode = False
    mouse_down_left = False
    mouse_down_right = False

    buttons = [
        {'text': 'Start', 'action': 'start'},
        {'text': 'Randomize', 'action': 'randomize'},
        {'text': 'Clear', 'action': 'clear'},
        {'text': 'Fast Mode', 'action': 'toggle_speed', 'active': fast_mode}
    ]

    while run:
        draw(win, grid, ROWS, width, buttons=buttons)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)

                if pos[0] > WIDTH:
                    index = (pos[1] - 30) // 40
                    if 0 <= index < len(buttons):
                        action = buttons[index]['action']
                        if action == 'start' and start and end:
                            for row_nodes in grid:
                                for node in row_nodes:
                                    node.update_neighbors(grid)
                            bfs(draw, grid, start, end, ROWS, width, fast=fast_mode)
                        elif action == 'randomize':
                            start, end = random_maze(grid, ROWS)
                        elif action == 'clear':
                            grid = make_grid(ROWS, width)
                            start = end = None
                        elif action == 'toggle_speed':
                            fast_mode = not fast_mode
                            buttons[index]['active'] = fast_mode
                else:
                    if row < ROWS and col < ROWS:
                        node = grid[row][col]
                        if event.button == 1:
                            mouse_down_left = True
                            if not start and node != end:
                                start = node
                                node.make_start()
                            elif not end and node != start:
                                end = node
                                node.make_end()
                            elif node != start and node != end:
                                node.make_barrier()
                        elif event.button == 3:
                            mouse_down_right = True
                            if node == start:
                                start = None
                            elif node == end:
                                end = None
                            node.reset()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down_left = False
                elif event.button == 3:
                    mouse_down_right = False

            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                if pos[0] < WIDTH:
                    row, col = get_clicked_pos(pos, ROWS, width)
                    if row < ROWS and col < ROWS:
                        node = grid[row][col]
                        if mouse_down_left:
                            if node != start and node != end:
                                node.make_barrier()
                        elif mouse_down_right:
                            if node == start:
                                start = None
                            elif node == end:
                                end = None
                            node.reset()

    pygame.quit()

main(WIN, WIDTH)
