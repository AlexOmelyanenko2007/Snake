import random
import sys

import pygame
import pygame_menu

import pygame_widgets
from pygame_widgets.button import Button

from sql import ScoreTable

pygame.init()

# Настройки, создание окна и загрузка картинок
x = 400
y = 600
bg_image = pygame.image.load("resources/menu.png")
pygame.display.set_caption("Змейка")

# Игровые переменные
size_block = 20
count_blocks = 20
margin = 1
header_margin = 70
size = [size_block * count_blocks + 2 * size_block + margin * count_blocks,
        size_block * count_blocks + 2 * size_block + margin * count_blocks + header_margin]
screen = pygame.display.set_mode(size)
courier = pygame.font.SysFont('courier', 24)

"""
Класс StateSystem используется чтобы внедрить состояние нашего приложения
"""


class StateSystem:
    state = 'main'

    def __init__(self):
        pass

    # меню
    def open_main(self):
        self.state = 'main'

    # настройки
    def open_settings(self):
        self.state = 'settings'

    # игра
    def open_game(self):
        self.state = 'game'

    # пауза
    def open_pause(self):
        self.state = 'pause'

    # таблица рекордов
    def open_scores(self):
        self.state = 'scores'

    # получение состояния
    def get_state(self):
        return self.state


"""
Класс MapSnake используется для внедрения разнообразия карт
"""


class MapSnake:
    maps = {
        'default': {
            'major': (255, 255, 255),
            'minor': (255, 222, 173)
        },
        'coca-cola': {
            'major': (255, 255, 255),
            'minor': (255, 100, 100)
        }
    }

    now_map = 'default'

    def __init__(self):
        pass

    def set_map(self, map_name):
        self.now_map = map_name
        return self.maps[map_name]

    def get_now_map(self):
        return self.maps[self.now_map]

    def get_maps(self):
        return self.maps


"""
Класс MusicSnake используется для того чтобы внедрить разнообразие музыки
"""


class MusicSnake:
    musics = {
        'default': 'resources/musique4.wav',
        'ghostbusters': 'resources/ghostbusters.mp3'
    }

    now_music = 'default'

    def __init__(self):
        pass

    def set_music(self, music_name):
        self.now_music = music_name
        return self.musics[music_name]

    def get_now_music(self):
        return self.musics[self.now_music]

    def get_musics(self):
        return self.musics


"""
Класс SnakeBlock используется для того чтобы разделить змейку на блоки и отслеживать перемещение
"""


class SnakeBlock:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def is_inside(self):
        return 0 <= self.x < count_blocks and 0 <= self.y < count_blocks

    def __eq__(self, other):  # метод для сравнения
        return isinstance(other, SnakeBlock) and self.x == other.x and self.y == other.y


"""
Класс Game это главный модуль управления нашего приложения
"""


class Game:
    # Тема меню
    main_theme = pygame_menu.themes.THEME_DARK.copy()
    main_theme.set_background_color_opacity(0.7)

    # Инициализация переменных меню
    menu = None
    menu_pause = None
    menu_preferences = None
    menu_scores = None

    # База нашей змейки
    snake_blocks = [SnakeBlock(9, 8), SnakeBlock(9, 9), SnakeBlock(9, 10)]

    state = StateSystem()

    music = MusicSnake()
    bg_music = None
    apple_sound = None
    good_apple_sound = None
    bad_apple_sound = None
    game_fail_sound = None
    game_start_sound = None

    score_table = None
    score_result = None
    table_scores = None

    # Цвета
    color_fone = (160, 82, 45)
    white = (255, 255, 255)
    burlywood = (255, 222, 173)
    header_color = (139, 69, 19)
    snake_color = (0, 172, 0)
    red = (255, 0, 0)
    yellow = (255, 255, 0)
    black = (0, 0, 0)

    # Имя пользователя
    username = 'guest'

    map_snake = None
    map_color = None

    snake_sprite = {}

    d_row = buf_row = 0
    d_col = buf_col = 1
    total = 0
    speed = 1

    # Контроль FPS
    clock = pygame.time.Clock()
    FPS = 45

    running = True

    # Конструктор где мы все инициализируем
    def __init__(self):
        self.score_table = ScoreTable()
        self.init_sound()
        pygame.mixer.init()
        self.map_snake = MapSnake()
        self.init_main_menu()
        self.init_pause_menu()
        self.init_preferences_menu()
        self.init_scores_menu()
        self.load_images()

    # Обновление картинки
    def update(self):
        screen.blit(bg_image, (0, 0))
        events = pygame.event.get()
        self.map_color = self.map_snake.get_now_map()

        for event in events:
            if event.type == pygame.QUIT:
                exit()

        # Связь состояний и их меню
        if self.state.get_state() == 'main':
            if self.menu.is_enabled():
                self.menu.update(events)
                self.menu.draw(screen)
        elif self.state.get_state() == 'pause':
            if self.menu_pause.is_enabled():
                self.menu_pause.update(events)
                self.menu_pause.draw(screen)
        elif self.state.get_state() == 'settings':
            if self.menu_preferences.is_enabled():
                self.menu_preferences.update(events)
                self.menu_preferences.draw(screen)
        elif self.state.get_state() == 'scores':
            if self.menu_scores.is_enabled():
                self.menu_scores.update(events)
                self.menu_scores.draw(screen)
        else:
            self.start_the_game()

    def init_main_menu(self):
        self.menu = pygame_menu.Menu('Змейка', 300, 300,
                                     theme=self.main_theme)

        self.menu.add.text_input('Имя:', default='guest', onchange=self.change_username)
        self.menu.add.button('Играть', self.start_the_game)
        self.menu.add.button('Топ игроков', self.open_scores_and_update_table)
        self.menu.add.button('Выход', pygame_menu.events.EXIT)

    def init_pause_menu(self):
        self.menu_pause = pygame_menu.Menu('Пауза', 300, 300,
                                           theme=self.main_theme)

        self.menu_pause.add.button('Назад', lambda: self.state.open_game())
        self.menu_pause.add.button('Настройки', self.preferences)
        self.menu_pause.add.button('Выход', pygame_menu.events.EXIT)

    def init_preferences_menu(self):
        temp_maps = self.map_snake.get_maps()
        temp_music = self.music.get_musics()
        pref_theme = pygame_menu.themes.THEME_DARK.copy()
        pref_theme.set_background_color_opacity(0.7)
        self.menu_preferences = pygame_menu.Menu('Настройки', 400, 400,
                                                 theme=pref_theme)
        self.menu_preferences.add.button('Назад', lambda: self.state.open_pause())
        self.menu_preferences.add.dropselect('Карта', [(map, temp_maps[map]) for map in temp_maps.keys()],
                                             onchange=self.set_map_color)
        self.menu_preferences.add.dropselect('Музыка', [(music, temp_music[music]) for music in temp_music.keys()],
                                             onchange=self.set_game_music)
        self.menu_preferences.add.button('Выход', pygame_menu.events.EXIT)

    def init_scores_menu(self):
        self.menu_scores = pygame_menu.Menu('Таблица лидеров', 400, 500,
                                            theme=self.main_theme)

        self.table_scores = self.menu_scores.add.table(table_id='my_table', font_size=20)
        self.load_score_table()

    def init_sound(self):
        self.apple_sound = pygame.mixer.Sound('resources/apple.ogg')
        self.good_apple_sound = pygame.mixer.Sound('resources/good_apple.ogg')
        self.bad_apple_sound = pygame.mixer.Sound('resources/bad_apple.ogg')
        self.game_fail_sound = pygame.mixer.Sound('resources/game_fail.ogg')
        self.game_start_sound = pygame.mixer.Sound('resources/game_start.ogg')

    def load_images(self):
        self.snake_sprite['head'] = pygame.image.load('resources/snake-head.png')
        self.snake_sprite['middle'] = pygame.image.load('resources/snake-body.png')
        self.snake_sprite['corner'] = pygame.image.load('resources/snake-corner.png')
        self.snake_sprite['tail'] = pygame.image.load('resources/snake-tail.png')
        self.snake_sprite['apple'] = pygame.image.load('resources/apple.png')
        self.snake_sprite['good_apple'] = pygame.image.load('resources/good_apple.png')
        self.snake_sprite['bad_apple'] = pygame.image.load('resources/bad_apple.png')

    # Используется исключительно для фона в виде шашечек
    def draw_block(self, color, row, column):
        pygame.draw.rect(screen, color, [size_block + column * size_block + margin * (column + 1),
                                         header_margin + size_block + row * size_block + margin * (row + 1),
                                         size_block,
                                         size_block], width=0)

    # Отрисовка спрайта
    def draw_sprite(self, row, column, characted, rotate):
        now_image = self.snake_sprite[characted].copy()
        screen.blit(pygame.transform.rotate(now_image, rotate),
                    [size_block + column * size_block + margin * (column + 1),
                     header_margin + size_block + row * size_block + margin * (row + 1),
                     size_block,
                     size_block])

    # Генерация блока
    def get_random_empty_block(self):
        x_coord = random.randint(0, count_blocks - 1)
        y_coord = random.randint(0, count_blocks - 1)
        empty_block = SnakeBlock(x_coord, y_coord)
        while empty_block in self.snake_blocks:
            empty_block.x = random.randint(0, count_blocks - 1)
            empty_block.y = random.randint(0, count_blocks - 1)
        return empty_block

    # Старт игры
    def start_the_game(self):
        # Кнопка паузы
        button = Button(
            screen, x - 30, size_block / 2, 50, 50, text='||',
            fontSize=40, margin=5,
            inactiveColour=(255, 255, 255),
            pressedColour=(0, 255, 0), radius=50,
            onClick=self.stay_game_pause
        )

        # Музыка начала игры
        self.game_start_sound.play()

        # Фоновая музыка
        self.bg_music = pygame.mixer.music
        self.bg_music.load(self.music.get_now_music())
        self.bg_music.set_volume(0.2)
        self.bg_music.play(loops=-1)  # зацикливаем

        # Размеры и еда
        apple = self.get_random_empty_block()
        good_apple = self.get_random_empty_block()
        bad_apple = self.get_random_empty_block()

        while self.running:
            self.clock.tick(self.FPS)
            # Обработка событий
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    print('exit')
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.d_col != 0:
                        self.buf_row = -1
                        self.buf_col = 0
                    if event.key == pygame.K_DOWN and self.d_col != 0:
                        self.buf_row = 1
                        self.buf_col = 0
                    if event.key == pygame.K_LEFT and self.d_row != 0:
                        self.buf_row = 0
                        self.buf_col = -1
                    if event.key == pygame.K_RIGHT and self.d_row != 0:
                        self.buf_row = 0
                        self.buf_col = 1
                    if event.key == pygame.K_p:
                        self.stay_game_pause()

            # Рисуем наши фоновые статичные и нестатичные элементы
            screen.fill(self.color_fone)
            pygame.draw.rect(screen, self.header_color, [0, 0, size[0], header_margin])
            text_total = courier.render(f"Total: {self.total}", 0, self.white)
            text_speed = courier.render(f"Speed: {self.speed}", 0, self.white)
            screen.blit(text_total, (size_block, size_block))
            screen.blit(text_speed, (size_block + 180, size_block))

            # Рисуем шашечки
            for row in range(count_blocks):
                for column in range(count_blocks):
                    if (row + column) % 2 == 0:
                        # color = self.burlywood
                        color = self.map_color['major']
                    else:
                        # color = self.white
                        color = self.map_color['minor']
                    self.draw_block(color, row, column)

            head = self.snake_blocks[-1]

            # Когда змея улетает за поля
            if not head.is_inside():
                self.game_fail_sound.play()
                self.record_best_score()
                self.restart_game()
                break

            # Яблоки
            self.draw_sprite(apple.x, apple.y, 'apple', 0)
            self.draw_sprite(good_apple.x, good_apple.y, 'good_apple', 0)
            self.draw_sprite(bad_apple.x, bad_apple.y, 'bad_apple', 0)

            for i, block in enumerate(self.snake_blocks):
                characted = ''  # "Характеристика" нашего блока - то есть на каком месте стоит наш блок

                if i == 0:
                    characted = 'tail'
                elif i == len(self.snake_blocks) - 1:
                    characted = 'head'
                else:
                    characted = 'middle'

                br, pn = self.get_block_rotate(i)  # получаем разворот нашего блока при повороте змейки или движении

                pn_check = pn.split(' - ')

                if pn_check[0] != pn_check[1]:
                    characted = 'corner' # фиксируем угловой блок так как для него мы считаем более сложный поворот

                self.draw_sprite(block.x, block.y, characted, br)

            if apple == head:  # едим обычное яблоко
                self.total += 1
                self.speed = self.total // 5 + 1
                self.snake_blocks.append(apple)
                apple = self.get_random_empty_block()

                # Музыка для apple
                self.apple_sound.play()

            if good_apple == head:  # едим крутое яблоко
                self.total += 2
                self.speed = self.total // 5 + 1
                self.snake_blocks.append(good_apple)
                good_apple = self.get_random_empty_block()

                # Музыка для good_apple
                self.good_apple_sound.play()

            if bad_apple == head:  # едим отравленное яблоко
                self.total -= 1
                self.speed = (abs(self.total) + 6) // 5
                self.snake_blocks.append(bad_apple)
                bad_apple = self.get_random_empty_block()

                # Музыка для bad_apple
                self.bad_apple_sound.play()

            self.d_row = self.buf_row
            self.d_col = self.buf_col
            new_head = SnakeBlock(head.x + self.d_row, head.y + self.d_col)

            # когда змея ест себя же
            if new_head in self.snake_blocks:
                self.game_fail_sound.play()
                self.restart_game()
                break

            if self.state.get_state() is 'pause': # пауза (мы оставляем змейку на том же месте и все статистики)
                break

            # перемещаем нашу змейку
            self.snake_blocks.append(new_head)
            self.snake_blocks.pop(0)
            pygame.display.flip()

            button.listen(events)
            pygame_widgets.update(events)
            pygame.display.update()

            self.clock.tick(3 + self.speed)

    # расчет поворота блока змейки
    def get_block_rotate(self, i):
        """
        right - right 0
        left - left 180
        up - up 90
        down - down -90


        right - down -180
        right - up 180

        left - down 0
        left - up 90

        up - right 0 - it's corner sprite
        up - left -90

        down - right 90
        down - left 180
        """
        rotate_base = {
            'right - right': 0,
            'left - left': 180,
            'up - up': 90,
            'down - down': -90,
            'right - down': -90,
            'right - up': 180,
            'left - down': 0,
            'left - up': 90,
            'up - right': 0,
            'up - left': -90,
            'down - right': 90,
            'down - left': 180,
            ' - ': 0
        }

        temp_prev = self.get_prev_block_characted(i)
        temp_next = self.get_next_block_characted(i)

        if temp_prev is '':
            temp_prev = temp_next
        if temp_next is '':
            temp_next = temp_prev

        pseudo_name = temp_prev + ' - ' + temp_next

        return rotate_base[pseudo_name], pseudo_name

    # получаем "характеристику" блока следующего за нашим
    def get_next_block_characted(self, i):
        """
        print(vec_x, vec_y)

        по человечески:
        vec y   x
        ->  0   1
        <-  0   -1
        ^   -1  0
        v   1   0
        """

        now_vec = self.get_vec_block(1, i)
        res = ''

        if now_vec == [0, 1]:
            res = 'right'
        elif now_vec == [0, -1]:
            res = 'left'
        elif now_vec == [-1, 0]:
            res = 'up'
        elif now_vec == [1, 0]:
            res = 'down'

        return res

    # получаем "характеристику" блока предыдущего за нашим
    def get_prev_block_characted(self, i):
        now_vec = self.get_vec_block(-1, i)
        res = ''

        if now_vec == [0, 1]:
            res = 'left'
        elif now_vec == [0, -1]:
            res = 'right'
        elif now_vec == [-1, 0]:
            res = 'down'
        elif now_vec == [1, 0]:
            res = 'up'

        return res

    # считаем вектор движения
    def get_vec_block(self, way, i):
        '''
        way 1 - next
        way -1 - prev
        '''
        try:
            vec_x = self.snake_blocks[i + way].x - self.snake_blocks[i].x
        except IndexError:
            vec_x = ''

        try:
            vec_y = self.snake_blocks[i + way].y - self.snake_blocks[i].y
        except IndexError:
            vec_y = ''

        return [vec_x, vec_y]

    # перезагружаем игру
    def restart_game(self):
        self.snake_blocks = [SnakeBlock(9, 8), SnakeBlock(9, 9), SnakeBlock(9, 10)]
        self.d_row = self.buf_row = 0
        self.d_col = self.buf_col = 1
        self.total = 0
        self.speed = 1
        self.state.open_main()

    # вспомогательное открытие настроек
    def preferences(self):
        self.state.open_settings()

    # ставим цвета карты
    def set_map_color(self, args, new_val):
        self.map_snake.set_map(args[0][0])

    # ставим музыку
    def set_game_music(self, args, new_val):
        self.music.set_music(args[0][0])

    # если на паузе, останавливаем музыку
    def stay_game_pause(self):
        self.bg_music.stop()
        self.state.open_pause()

    # смена имени пользователя
    def change_username(self, new_val):
        self.username = new_val

    # забиваем наш рекорд, если он есть конечно
    def record_best_score(self):
        self.score_table.set_score_by_username(self.username, self.total)

    # открываем таблицу лидеров с обновлением с базы
    def open_scores_and_update_table(self):
        self.score_result = self.score_table.get_scores()
        self.state.open_scores()
        self.load_score_table()

    # обновляем нашу таблицу лидеров
    def load_score_table(self):
        self.score_result = self.score_table.get_scores()
        # self.table_scores = None
        self.menu_scores.clear()
        self.menu_scores.add.button('Назад', lambda: self.state.open_main())
        self.table_scores = self.menu_scores.add.table(table_id='my_table', font_size=20)
        self.table_scores.default_cell_padding = 5
        self.table_scores.default_row_background_color = 'white'
        self.table_scores.add_row(['Player', 'Best record'],
                                  cell_font=pygame_menu.font.FONT_OPEN_SANS_BOLD,
                                  cell_font_color=(0, 0, 0))
        for r in self.score_result:
            self.table_scores.add_row([r[0], r[1]], cell_font_color=(30, 30, 30))


game = Game()

while True:
    game.update()
    pygame.display.update()
    # pygame_widgets.update(events)  # Call once every loop to allow widgets to render and listen
