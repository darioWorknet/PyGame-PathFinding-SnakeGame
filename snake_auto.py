import pygame
import random
import math
import time
import csv

class Block:
    # COLORS
    HEAD = (0, 0, 0)
    BODY = (50, 50, 50)
    FOOD = (141,182,0)
    BLANK = (255, 255, 255)
    PATH = (252,238,167)

    def __init__(self, size, x_index, y_index):
        self.kind = 'blank'
        self.update_color()
        self.size = size
        self.x = x_index * size
        self.y = y_index * size
        self.x_index = x_index
        self.y_index = y_index

    def convert_to(self, kind):
        self.kind = kind
        self.update_color()

    def update_color(self):
        if self.kind == 'head':
            self.color = self.HEAD
        elif self.kind == 'body':
            self.color = self.BODY
        elif self.kind == 'food':
            self.color = self.FOOD
        elif self.kind == 'blank':
            self.color = self.BLANK
        elif self.kind == 'path':
            self.color = self.PATH

    def show(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))

    def get_index(self):
        return self.x_index, self.y_index

    def get_neighbours(self, blocks):
        neighs = list()
        for i in range(-1, 2):
            for j in range(-1, 2):
                x, y = self.x_index + i, self.y_index + j
                if (i != 0 and j != 0) or (i == 0 and j == 0):
                    pass
                # UP, DOWN, LEFT & RIGHT
                elif x >= 0 and y >= 0 and x < ROWS and y < ROWS:
                    neighs.append(blocks[y][x])
        return neighs

    def set_acc_cost(self, parent):
        self.G = parent.G + 1

    def set_heuristic(self, target):
        x1, y1 = self.get_index()
        x2, y2 = target.get_index()
        x, y = (x1-x2), (y1-y2)
        self.H = math.sqrt(x**2 + y**2)

    def restart_params(self):
        self.G = 0
        self.H = 0
        self.cost = 0
        self.parent = None
        
    def set_cost(self, parent, target):
        self.set_acc_cost(parent) # Update self.G
        self.set_heuristic(target) # Update self.H
        self.cost = self.G + self.H
        self.parent = parent 
        return self.cost



# _______________ GAME FUNCTIONS ___________________#

def get_dir(dir):
    if dir == 0: # UP
        return 0, -1
    elif dir == 1: # DOWN
        return 0, 1
    elif dir == 2: # RIGHT
        return 1, 0
    elif dir == 3: # LEFT
        return -1, 0


def valid_dir(snake, x_dir, y_dir):
    x_head_index, y_head_index = snake[0].get_index()
    x_prev_index, y_prev_index = snake[1].get_index()
    # If snake wants to flip direction
    if x_head_index + x_dir == x_prev_index and y_head_index + y_dir == y_prev_index:
        return False
    return True


def move_snake(blocks, snake, dir):
    x_dir, y_dir = get_dir(dir)
    if valid_dir(snake, x_dir, y_dir):
        snake[0].convert_to('body')
        snake[-1].convert_to('blank')
        x, y = snake[0].get_index()
        x_index, y_index = x + x_dir, y + y_dir
        if x_index >= ROWS or y_index >= ROWS:
            return
        new_head = blocks[y_index][x_index]
        new_head.convert_to('head')
        snake.insert(0, new_head)


def move_through_path(blocks, snake, path):
    reference = path.pop()
    x1, y1 = snake[0].get_index()
    x2, y2 = reference.get_index()
    if y1-y2 == 1: # UP
        move_snake(blocks, snake, 0)
    elif y1-y2 == -1: # DOWN
        move_snake(blocks, snake, 1)
    elif x1-x2 == -1: # RIGHT
        move_snake(blocks, snake, 2)
    elif x1-x2 == 1: # LEFT
        move_snake(blocks, snake, 3)


def move_random(blocks, snake):
    neighs = snake[0].get_neighbours(blocks)
    neighs = [x for x in neighs if x.kind == 'blank' or x.kind == 'path']
    if len(neighs) > 0:
        move_through_path(blocks, snake, neighs)
    else:
        while True:
            dir = random.randint(0,3)
            x_dir, y_dir = get_dir(dir)
            if valid_dir(snake, x_dir, y_dir):
                move_snake(blocks, snake, dir)
                return
       
# SET ACCUMULATED COST TO ZERO AND UPDATE HEURISTICS FOR EACH BLOCK
def update_costs(blocks, end):
    for row in blocks:
        for block in row:
            block.restart_params()
            block.set_heuristic(end)

# WHEN PATH HAS BEEN FOUND, IT RETURNS THE PATH
def get_path(current, start):
    path = list()
    path.append(current)
    solved = False
    parent = current
    while not solved:
        parent = parent.parent
        if parent == start:
            solved = True
        else:
            path.append(parent)
    return path

# A* PATHFINDING ALGORITHM
def find_path(blocks, start, end):
    update_costs(blocks, end)
    borders = list()
    visited = list() 
    borders.append(start)
    solved = False
    while not solved:
        try: # GET BEST OPTION
            current = borders.pop(0)
        except: # PATH TO FOOD IS BLOCKED
            return
        if current == end:
            solved = True
            path = get_path(current, start)
            color_path = [x for x in path if x.kind == 'blank']
            for i in color_path:
                i.convert_to('path')
            return path
        else: 
            visited.append(current)
            childs = current.get_neighbours(blocks)

            try:
                childs = [child for child in childs if child.cost < borders[0].cost and child not in visited and child.kind != 'body']
            except:
                childs = [child for child in childs if child not in visited and child.kind != 'body']
            for child in childs:
                child.set_cost(current, end)
                borders.append(child)
            

def create_blocks(rows, size):
    blocks = list()
    for i in range(rows):
        blocks.append([])
        for j in range(rows):
            new_block = Block(size, j, i)
            blocks[i].append(new_block)
    return blocks


def draw_blocks(win, blocks):
    for row in blocks:
        for block in row:
            block.show(win)


def create_snake(blocks):
    snake = list()
    starting_x = 5
    starting_y = 3
    initial_size = 4
    blocks[starting_y][starting_x].convert_to('head')
    snake.append(blocks[starting_y][starting_x])
    for i in range(initial_size):
        blocks[starting_y][starting_x - 1 - i].convert_to('body')
        snake.append(blocks[starting_y][starting_x - 1 - i])
    return snake


def create_food(blocks, snake):
    valid_positions = list()
    for rows in blocks:
        for block in rows:
            if block not in snake:
                valid_positions.append(block)
    proposed_food = random.choice(valid_positions)
    proposed_food.convert_to('food')
    return proposed_food
    

def draw_grid(win, rows, size, color):
    for i in range(rows + 1):
        x = i * size
        pygame.draw.line(win, color, (x ,0), (x, HEIGHT), 2)
    for i in range(rows + 1):
        y = i * size
        pygame.draw.line(win, color, (0 ,y), (WIDTH, y), 2)


def check_game_over(blocks, snake):
    for body in snake[1:]:
        # If head hits body
        if body == snake[0]:
            return True
    return False


def print_text(win, msg, height_pos, font_size):
    font = pygame.font.Font('freesansbold.ttf', font_size)
    text = font.render(msg, False, (255, 100, 255))
    text_rect = text.get_rect()
    text_rect.center = (WIDTH // 2, height_pos)
    win.blit(text, text_rect)

    
def show_game_over(win, score):
    win.fill((10,10,10))
    msg = 'GAME OVER'
    print_text(win, msg, 200, 42)
    msg = 'Your score: ' + str(score)
    print_text(win, msg, 300, 32)
    msg = 'Restarting new game...'
    print_text(win, msg, 400, 32)


def restart_blocks(blocks):
    for row in blocks:
        for block in row:
            block.convert_to('blank')


def clean_path(path):
    if path:
        for block in path:
            if block.kind == 'path':
                block.convert_to('blank')


def create_CSV(filename, scores):
    with open(filename, 'w', newline='') as csv_file:
        wr = csv.writer(csv_file)
        wr.writerow(['Scores'])
        for score in scores:
            wr.writerow([score])


# GAME CONFIGURATION ____________________________________
WIDTH = 600
HEIGHT = WIDTH
ROWS = 15   # 6, 8, 10, 15
SIZE = WIDTH // ROWS
GRID_COLOR = (200, 200, 200)

# PYGAME CONFIG. ________________________________________
pygame.init()
WIN = pygame.display.set_mode(( WIDTH, HEIGHT))
pygame.display.set_caption("SNAKE A* -- Iteration: 1")



if __name__ == '__main__':
    run = True
    game_over = False
    blocks = create_blocks(ROWS, SIZE)
    snake = create_snake(blocks)
    food = create_food(blocks, snake)
    path = []
    color_path = []
    scores = []

    game_count = 0
    game_limit = 2 # How many games?

    while run:
        # EXIT LISTENER
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # DRAW BOARD
        draw_blocks(WIN, blocks)
        draw_grid(WIN, ROWS, SIZE, GRID_COLOR)

        # MOVE AUTO
        clean_path(path)
        tail = snake[-1]

        if not game_over:
            if food == snake[0]:
                tail.convert_to('body')
                snake.append(tail)
                food = create_food(blocks, snake)
            pygame.display.update()
            path = find_path (blocks, snake[0], food)
            if path:
                move_through_path(blocks, snake, path)
            else:
                move_random(blocks, snake)

        game_over = check_game_over(blocks, snake)

        if game_over:
            # time.sleep(0.5)
            score = len(snake)
            show_game_over(WIN, score)
            pygame.display.update()
            # time.sleep(1)
            restart = True
            if restart:
                game_count += 1
                pygame.display.set_caption("SNAKE A* -- Iteration: " + str(game_count + 1))
                restart_blocks(blocks)
                del snake
                snake = create_snake(blocks)
                food = create_food(blocks, snake)
                game_over = False
                scores.append(score)
                # EXIT GAME, WHEN DESIRED GAMES HAVE BEEN PLAYED
                if game_count > game_limit - 1:
                    run = False

            pygame.display.update()

        # time.sleep(0.05)
        pygame.display.update()
    
    # CREATE CSV & STORE SCORES
    filename = 'scores.csv'
    create_CSV(filename, scores)

    # EXIT PYGAME
    pygame.quit()
    exit()