import pygame
import random

class Block:

    # COLORS
    HEAD = (0, 0, 0)
    BODY = (50, 50, 50)
    FOOD = (100, 255, 100)
    BLANK = (255, 255, 255)

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

    def show(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.size, self.size))

    def get_index(self):
        return self.x_index, self.y_index


WIDTH = 600
HEIGHT = 600
ROWS = 15
SIZE = WIDTH // ROWS

GRID_COLOR = (200, 200, 200)

pygame.init()

WIN = pygame.display.set_mode(( WIDTH, HEIGHT))
pygame.display.set_caption("SNAKE A*")

game_over = False


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

    return run, restart

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


'''
K_UP      up arrow       0
K_DOWN    down arrow     1
K_RIGHT   right arrow    2
K_LEFT    left arrow     3
'''

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
            
            if x_index < 0 or y_index < 0:
                game_over = True
                return
                
            if blocks[y_index][x_index].kind == 'food':
                create_food(blocks, snake, (x_index, y_index))
                deleted_body.convert_to('body')
                snake.append(deleted_body)
            blocks[y_index][x_index].convert_to('head')
            snake.insert(0, blocks[y_index][x_index])
    except: # OUT OF BOUNDS EXCEPTION
        print('EXCEPTION')
        game_over = True


def snake_debug(blocks, snake):
    for row in blocks:
        for block in row:
            if block.kind == 'food':
                print ('block_x =', block.x_index, 'block_y =' , block.y_index)


def create_food(blocks, snake, head_pos):
    solved = False
    while not solved:
        x_food = random.randint(0, ROWS - 1)
        y_food = random.randint(0, ROWS - 1)
        proposed_food = blocks[y_food][x_food]
        if proposed_food.kind == 'blank' and not (x_food == head_pos[0] and y_food == head_pos[1]):
            solved = True
            blocks[y_food][x_food].convert_to('food')
    

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
    for i in snake[1:]:
        if i == head:
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


if __name__ == '__main__':

    run = True
    blocks = create_blocks(ROWS, SIZE)
    snake = create_snake(blocks)
    create_food(blocks, snake, (snake[0].x_index, snake[0].y_index))

    while run:

        run, restart = listen_key_events(blocks, snake)
        draw_blocks(WIN, blocks)
        draw_grid(WIN, ROWS, SIZE, GRID_COLOR)

        check_game_over(blocks, snake)

        if game_over:
            if restart:
                restart_blocks(blocks)
                del snake
                snake = create_snake(blocks)
                create_food(blocks, snake, (snake[0].x_index, snake[0].y_index))
                game_over = False

            score = get_size(snake)
            show_game_over(WIN, score)
            pygame.display.update()

        pygame.display.update()






    
