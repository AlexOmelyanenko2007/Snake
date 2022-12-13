import pygame
import sys
import random
# import pygame_menu идея в будущем использовать для главного меню
pygame.init()

# Настройки и создание окна
x = 400
y = 600
# screen = pygame.display.set_mode((x, y))
pygame.display.set_caption("Змейка")

# Контроль FPS
clock = pygame.time.Clock()
FPS = 45

# Игровые переменные
running = True
color_fone = (160, 82, 45)
white = (255, 255, 255)
burlywood = (255, 222, 173)
header_color = (139, 69, 19)
snake_color = (0, 172, 0)
size_block = 20
count_blocks = 20
margin = 1
header_margin = 70
red = (255, 0, 0)
size = [size_block * count_blocks + 2 * size_block + margin * count_blocks,
        size_block * count_blocks + 2 * size_block + margin * count_blocks + header_margin]

screen = pygame.display.set_mode(size)
courier = pygame.font.SysFont('courier', 36)


class SnakeBlock:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_inside(self):
        return 0 <= self.x < count_blocks and 0 <= self.y < count_blocks

    def __eq__(self, other): # метод для равенства
        return isinstance(other, SnakeBlock) and self.x == other.x and self.y == other.y


def get_random_empty_block():
    x = random.randint(0, count_blocks - 1)
    y = random.randint(0, count_blocks - 1)
    empty_block = SnakeBlock(x, y)
    while empty_block in snake_blocks:
        empty_block.x = random.randint(0, count_blocks - 1)
        empty_block.y = random.randint(0, count_blocks - 1)
    return empty_block


def draw_block(color, row, column):
    pygame.draw.rect(screen, color, [size_block + column * size_block + margin * (column + 1),
                                     header_margin + size_block + row * size_block + margin * (row + 1),
                                     size_block,
                                     size_block])


snake_blocks = [SnakeBlock(9, 8), SnakeBlock(9, 9), SnakeBlock(9, 10)]
apple = get_random_empty_block()
d_row = buf_row = 0
d_col = buf_col = 1
total = 0
speed = 1

#Игровой цикл
while running:
    clock.tick(FPS)
    #Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print('exit')
            pygame.quit()
            sys.exit()
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and d_col != 0:
                buf_row = -1
                buf_col = 0
            if event.key == pygame.K_DOWN and d_col != 0:
                buf_row = 1
                buf_col = 0
            if event.key == pygame.K_LEFT and d_row != 0:
                buf_row = 0
                buf_col = -1
            if event.key == pygame.K_RIGHT and d_row != 0:
                buf_row = 0
                buf_col = 1


    screen.fill(color_fone)
    pygame.draw.rect(screen, header_color, [0, 0, size[0], header_margin])
    text_total = courier.render(f"Total: {total}", 0, white)
    text_speed = courier.render(f"Speed: {speed}", 0, white)
    screen.blit(text_total, (size_block, size_block))
    screen.blit(text_speed, (size_block + 230, size_block))

    for row in range(count_blocks):
        for column in range(count_blocks):
            if (row + column) % 2 == 0:
                color = burlywood
            else:
                color = white
            draw_block(color, row, column)

    head = snake_blocks[-1]
    if not head.is_inside():
        print('crash')
        pygame.quit()
        sys.exit()

    draw_block(red, apple.x, apple.y)
    for block in snake_blocks:
        draw_block(snake_color, block.x, block.y)

    if apple == head:
        total += 1
        speed = total // 5 + 1
        snake_blocks.append(apple)
        apple = get_random_empty_block()

    d_row = buf_row
    d_col = buf_col
    new_head = SnakeBlock(head.x + d_row, head.y + d_col)
    # snake_blocks.append(new_head)
    # snake_blocks.pop(0)

    if new_head in snake_blocks:
        print('crash yourself')
        pygame.quit()
        sys.exit()

    snake_blocks.append(new_head)
    snake_blocks.pop(0)

    pygame.display.flip()
    clock.tick(3 + speed)



