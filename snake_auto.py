import pygame
import random
import math
import time
import csv



class Block:

    # COLORS
    HEAD = (0, 0, 0)
    BODY = (50, 50, 50)
    FOOD = (100, 255, 100)
    BLANK = (255, 255, 255)
    CURRENT = (252,238,167)

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
        elif self.kind == 'current':
            self.color = self.CURRENT

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


def listen_key_events(blocks, snake):
    run = True
    restart = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif pygame.mouse.get_pressed()[2]: # RIGHT click
            snake_move(blocks, snake)
        elif pygame.mouse.get_pressed()[1]: # CENTER click
            snake_debug(blocks, snake)
        elif event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_UP: # K_UP
                move_snake(blocks, snake, 0)

            elif event.key == pygame.K_DOWN: # K_DOWN
                move_snake(blocks, snake, 1)

            elif event.key == pygame.K_RIGHT: # K_RIGHT
                move_snake(blocks, snake, 2)

            elif event.key == pygame.K_LEFT: # K_LEFT
                move_snake(blocks, snake, 3)

            elif event.key == pygame.K_RETURN: # ENTER
                restart = True

            elif event.key == pygame.K_SPACE: # SPACE
                try:
                    food = get_food(blocks)
                    head = snake[0]
                    path = find_path (blocks, head, food)
                    move_through_path(blocks, snake, path)
                except:
                    pass

    return run, restart


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
       

def get_food(blocks):
    for row in blocks: 
        for block in row:
            if block.kind == 'food':
                x, y = block.get_index()
                return block


def update_costs(blocks, end):
    for row in blocks:
        for block in row:
            block.restart_params()
            block.set_heuristic(end)


def get_path(current, start):
    path = list()
    parent = current
    path.append(parent)
    solved = False
    while not solved:
        parent = parent.parent
        if parent == start:
            solved = True
        else:
            path.append(parent)
    # print('path size =', len(path))
    return path


def find_path(blocks, start, end):
    update_costs(blocks, end)
    borders = list()
    visited = list() 
    borders.append(start)
    solved = False
    while not solved:
        try:
            current = borders.pop(0)
        except:
            # print('not able to solve pathfinding algorithm')
            return
        if current == end:
            solved = True
            path = get_path(current, start)
            color_path = [x for x in path if x.kind == 'blank']
            for i in color_path:
                i.convert_to('current')
            return path
        else: 
            visited.append(current)
            childs = current.get_neighbours(blocks)
            # Probably a try: except: is needed here
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
        for brick in row:
            brick.show(win)


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


def snake_move(blocks, snake):
    snake[0].convert_to('body')
    snake[-1].convert_to('blank')
    snake.pop()
    x, y = snake[0].get_index()
    blocks[y][x+1].convert_to('head')
    snake.insert(0, blocks[y][x+1])


def get_dir(dir):
    if dir == 0: # K_UP
        return 0, -1
    elif dir == 1: # K_DOWN
        return 0, 1
    elif dir == 2: # K_RIGHT
        return 1, 0
    elif dir == 3: # K_LEFT
        return -1, 0


def valid_dir(snake, x_dir, y_dir):
    x_head_index, y_head_index = snake[0].get_index()
    x_prev_index, y_prev_index = snake[1].get_index()
    # If snake wants to flip direction
    if x_head_index + x_dir == x_prev_index and y_head_index + y_dir == y_prev_index:
        return False
    return True

def get_pos(block):
    x = block.x_index
    y = block.y_index
    return x, y

def move_random(blocks, snake):
    neighs = snake[0].get_neighbours(blocks)
    neighs = [x for x in neighs if x.kind == 'blank' or x.kind == 'current']
    if len(neighs) > 0:
        move_through_path(blocks, snake, neighs)
    else:
        while True:
            dir = random.randint(0,3)
            x_dir, y_dir = get_dir(dir)
            if valid_dir(snake, x_dir, y_dir):
                move_snake(blocks, snake, dir)
                return


def move_snake(blocks, snake, dir):
    global game_over
    try:
        x_dir, y_dir = get_dir(dir)
        if valid_dir(snake, x_dir, y_dir):
            snake[0].convert_to('body')
            snake[-1].convert_to('blank')
            deleted_body = snake.pop()
            x, y = snake[0].get_index()
            x_index, y_index = x + x_dir, y + y_dir
            new_head = blocks[y_index][x_index]
            
            if x_index < 0 or y_index < 0: # OUT OF BOUNDS
                game_over = True
                return

            new_head.convert_to('head')
            snake.insert(0, blocks[y_index][x_index])
    except: # OUT OF BOUNDS EXCEPTION
        game_over = True
        return



def snake_debug(blocks, snake):
    for row in blocks:
        for block in row:
            if block.kind == 'food':
                print ('block_x =', block.x_index, 'block_y =' , block.y_index)


def create_food(blocks, snake, head):
    valid_positions = list()
    for rows in blocks:
        for block in rows:
            if block.kind != 'head' and block.kind != 'body':
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
    global game_over
    head = snake[0]
    for body in snake[1:]:
        if body == head:
            game_over = True


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
    msg = 'Try again? Press: ENTER'
    print_text(win, msg, 400, 32)


def get_size(snake):
    counter = 0
    for i in snake:
        counter += 1
    return counter


def restart_blocks(blocks):
    for row in blocks:
        for block in row:
            block.convert_to('blank')

def clean_path(blocks):
    for row in blocks:
        for block in row:
            if block.kind == 'current':
                block.convert_to('blank')

def create_dict(my_list):
    dictionary = {}
    for item in  my_list:
        if item in dictionary:
            dictionary[item] =+ 1
        else:
            dictionary[item] = 1
    return dictionary



WIDTH = 600
HEIGHT = 600
ROWS = 15   # 6, 8, 10, 15
SIZE = WIDTH // ROWS

GRID_COLOR = (200, 200, 200)

pygame.init()

WIN = pygame.display.set_mode(( WIDTH, HEIGHT))
pygame.display.set_caption("SNAKE A*")

game_over = False


if __name__ == '__main__':
    iter = 0
    run = True
    blocks = create_blocks(ROWS, SIZE)
    snake = create_snake(blocks)
    food = create_food(blocks, snake, snake[0])
    path = []
    color_path = []
    game_count = 0
    game_limit = 3
    scores = []

    while run:

        run, restart = listen_key_events(blocks, snake)
        draw_blocks(WIN, blocks)
        draw_grid(WIN, ROWS, SIZE, GRID_COLOR)

        # MOVE AUTO
        clean_path(blocks)
        tail = snake[-1]

        if not game_over:
            if food == snake[0]:
                tail.convert_to('body')
                snake.append(tail)
                food = create_food(blocks, snake, snake[0])
            pygame.display.update()
            path = find_path (blocks, snake[0], food)
            if path:
                move_through_path(blocks, snake, path)
            else:
                move_random(blocks, snake)


        check_game_over(blocks, snake)

        if game_over:
            score = get_size(snake)
            show_game_over(WIN, score)
            pygame.display.update()
            # experimental
            time.sleep(2)
            restart = True
            if restart:
                restart_blocks(blocks)
                del snake
                snake = create_snake(blocks)
                food = create_food(blocks, snake, (snake[0].x_index, snake[0].y_index))
                game_over = False
                game_count += 1
                scores.append(score)
                if game_count > game_limit - 1:
                    run = False
            pygame.display.update()

        time.sleep(0.05)
        pygame.display.update()
    
    scores_dict = create_dict(scores)
    print('scores:', scores_dict)
    with open('innovators.csv', 'w', newline='') as csv_file:
        wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
        wr.writerow(scores)
    pygame.quit()
    exit()






    
