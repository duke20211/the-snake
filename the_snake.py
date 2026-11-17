"""Игра «Змейка»: финальный проект спринта «Изгиб Питона»."""

from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
BOARD_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета игры. DEFAULT_BODY_COLOR — сигнал, что свой цвет забыли передать.
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
DEFAULT_BODY_COLOR = (255, 0, 255)

# Скорость движения змейки:
SPEED = 20

# Поворот из текущего направления по стрелке. Разворота на 180° нет.
TURNS = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Инициализация игры:
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Общий чертёж объекта на клетке поля.

    Хранит координаты и цвет. Как именно рисовать объект, решает наследник:
    у яблока и змейки разное число клеток.
    """

    def __init__(self, body_color=DEFAULT_BODY_COLOR):
        """Кладёт объект в центр поля и запоминает его цвет.

        Args:
            body_color: Цвет RGB. По умолчанию яркий, чтобы забытый
            цвет было видно на поле.
        """
        self.position = BOARD_CENTER
        self.body_color = body_color

    def draw_cell(self, position, color, border=True):
        """Рисует одну клетку сетки. Этим пользуются все объекты.

        Args:
            position: Левый верхний угол клетки в пикселях.
            color: Цвет заливки.
            border: Рамка клетки. Для стирания следа её не рисуют.
        """
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        if border:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Заготовка отрисовки. Наследник обязан заменить этот метод."""
        raise NotImplementedError(
            f'Определите draw() в классе {type(self).__name__}.'
        )


class Apple(GameObject):
    """Еда на одну клетку.

    После съедения выбирает новую клетку вне тела змейки.
    В начале игры не встаёт в центр, где уже находится змейка.
    """

    def __init__(self, occupied=None):
        """Красит яблоко и уводит его с занятых клеток.

        Args:
            occupied: Клетки, на которые яблоко ставить нельзя.
            Пустой список означает старт игры: занят центр поля.
        """
        super().__init__(APPLE_COLOR)
        if not occupied:
            occupied = (BOARD_CENTER,)
        self.randomize_position(occupied)

    def randomize_position(self, occupied):
        """Ставит яблоко на случайную клетку вне списка occupied.

        Args:
            occupied: Запрещённые координаты. Параметр обязателен.
        """
        occupied = set(occupied)
        if len(occupied) >= GRID_WIDTH * GRID_HEIGHT:
            return
        while self.position in occupied:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )

    def draw(self):
        """Рисует яблоко в его текущей клетке."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Змейка: список клеток, голова хранится первой.

    Сама двигается, растёт и возвращается в центр.
    Экран не очищает — это делает игровой цикл в main().
    """

    def __init__(self):
        """Собирает змейку из одной клетки в центре. Ползёт вправо."""
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы — первый элемент positions."""
        return self.positions[0]

    def update_direction(self):
        """Подставляет направление, которое выбрал игрок."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает голову на клетку и выходит с края на противоположный.

        Хвост удаляется, только если змейка не выросла.
        Координаты удалённой клетки остаются в last для стирания.
        """
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Рисует новую голову и стирает только покинутую клетку.

        Тело между ними уже нарисовано и не меняется.
        """
        if self.last:
            self.draw_cell(
                self.last,
                BOARD_BACKGROUND_COLOR,
                border=False,
            )
        self.draw_cell(self.get_head_position(), self.body_color)

    def reset(self):
        """Возвращает змейку в центр: одна клетка и случайный курс.

        Поле после этого очищает main(), не сама змейка.
        """
        self.length = 1
        self.position = BOARD_CENTER
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Меняет направление по стрелкам.

    Новое направление берётся из TURNS. Пары «назад» в словаре нет,
    поэтому змейка не разворачивается на 180°.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type != pg.KEYDOWN:
            continue
        game_object.next_direction = TURNS.get(
            (game_object.direction, event.key),
            game_object.direction,
        )


def main():
    """Запускает поле, змейку и яблоко и крутит игровой цикл.

    На каждом кадре читает клавиши, двигает змейку, проверяет яблоко
    или столкновение с собой и обновляет экран.
    """
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)
        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
