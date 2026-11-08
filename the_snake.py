"""Игра «Змейка»: финальный проект спринта «Изгиб Питона»."""

from random import choice, randint

import pygame

pygame.init()

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

# Цвет фона — чёрный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()

KEY_DIRECTIONS = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}


class GameObject:
    """Базовый класс для объектов на игровом поле."""

    def __init__(self, body_color=None):
        """Сохраняет общую позицию и цвет объекта."""
        self.position = BOARD_CENTER
        self.body_color = body_color

    def draw_cell(self, position, color, border=True):
        """Рисует одну клетку сетки заданным цветом."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        if border:
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Рисует объект одной клеткой в его позиции."""
        self.draw_cell(self.position, self.body_color)


class Apple(GameObject):
    """Яблоко: одна клетка поля, после съедения меняет место."""

    def __init__(self, occupied=None):
        """Красит яблоко и ставит его на свободную клетку."""
        super().__init__(APPLE_COLOR)
        self.randomize_position(occupied)

    def randomize_position(self, occupied=None):
        """Ставит яблоко на случайную свободную клетку сетки."""
        occupied = set(occupied or ())
        if len(occupied) >= GRID_WIDTH * GRID_HEIGHT:
            return
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if position not in occupied:
                self.position = position
                return

    def draw(self):
        """Рисует яблоко квадратом в одну клетку."""
        super().draw()


class Snake(GameObject):
    """Змейка: сегменты, направление, рост и столкновение с собой."""

    def __init__(self):
        """Создаёт змейку из одной клетки, которая ползёт вправо."""
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы — первого сегмента."""
        return self.positions[0]

    def update_direction(self):
        """Применяет направление, выбранное с клавиатуры."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает змейку на клетку и переносит её через край поля."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.position = new_head
        self.positions.insert(0, new_head)
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Рисует сегменты и затирает клетку, которую змейка покинула."""
        if self.last:
            self.draw_cell(
                self.last,
                BOARD_BACKGROUND_COLOR,
                border=False,
            )
        for position in self.positions:
            self.draw_cell(position, self.body_color)

    def reset(self):
        """Возвращает змейку в центр поля после столкновения с собой."""
        self.length = 1
        self.position = BOARD_CENTER
        self.positions = [self.position]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.next_direction = None
        self.last = None
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Меняет направление змейки по стрелкам, без разворота на 180°."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type != pygame.KEYDOWN:
            continue
        new_direction = KEY_DIRECTIONS.get(event.key)
        if new_direction is None:
            continue
        opposite = (-new_direction[0], -new_direction[1])
        current = game_object.next_direction or game_object.direction
        if current != opposite:
            game_object.next_direction = new_direction


def main():
    """Создаёт объекты и крутит игровой цикл, пока окно не закроют."""
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
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
