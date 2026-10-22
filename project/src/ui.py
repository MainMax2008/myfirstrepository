import sys
import os
from src.board import Board
from src.ship import Ship


RESET = "\033[0m"
BOLD = "\033[1m"

CYAN = "\033[36m"   # Координаты
DIM = "\033[2m"     # Заголовки
BLUE = "\033[34m"   # Вода
GREEN = "\033[32m"  # Живой корабль
RED = "\033[31m"    # Попадание / огонь
GRAY = "\033[90m"   # Промах / всплеск

WATER_CHAR = f"{BLUE}~{RESET}"
SHIP_CHAR = f"{GREEN}■{RESET}"
HIT_CHAR = f"{RED}X{RESET}"
MISS_CHAR = f"{GRAY}•{RESET}"



def init_screen():
    """Полная очистка экрана перед началом игры."""
    # 1. Системная очистка
    os.system("cls" if os.name == "nt" else "clear")

    # 2. Жёсткий ANSI-сброс:
    # \033[2J — очистить экран
    # \033[3J — удалить всю историю скролла (scrollback)
    # \033[H  — вернуть курсор в (1, 1)
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush()

def move_cursor_home():
    """Возвращает курсор в верхний левый угол терминала (1, 1)."""
    sys.stdout.write("\033[H")
    sys.stdout.flush()

def get_cell_symbol(board, row, col, hide_ships: bool = False):
    """Возвращает строковый символ для клетки (row, col) с учётом тумана войны."""
    if (row,col) in board.hits:
        return HIT_CHAR
    elif (row,col) in board.misses:
        return MISS_CHAR
    elif board.get_ship_at(row,col) is not None:
        return WATER_CHAR if hide_ships else SHIP_CHAR
    else:
        return WATER_CHAR

def get_board_lines(board, hide_ships=False):
    """Преобразует доску в список форматированных строк (для удобного вывода рядом)."""
    header = f"   {CYAN}A B C D E F G H I J{RESET}"
    l = [header]
    for r in range(10):
        buf = []
        for c in range(10):
            buf.append(get_cell_symbol(board, r, c, hide_ships))
        s = " ".join(buf)
        ready_s = f"{CYAN}{r+1:2d}{RESET} " + s
        l.append(ready_s)
    return l

def render_battle_field(board1, board2,title1="Игрок 1", title2="Игрок 2", hide_ships: bool = True,):
    """Отрисовывает оба поля бок о бок (Side-by-Side) во время боя.
    По умолчанию оба поля скрыты туманом войны (hide_ships=True)."""
    move_cursor_home()
    lines1 = get_board_lines(board1, hide_ships=hide_ships)
    lines2 = get_board_lines(board2, hide_ships=hide_ships)
    t1 = f"[ {title1} ]"
    t2 = f"[ {title2} ]"
    print(f"   {BOLD}{t1:^19}{RESET}   │      {BOLD}{t2:^19}{RESET}")
    for l1,l2 in zip(lines1,lines2):
        print(f"{l1}   │   {l2}")

def render_single_board(board, title="Ваше поле", hide_ships=False):
    """Отрисовывает одно поле (используется на этапе расстановки кораблей). """
    move_cursor_home()
    t = f"[ {title} ]"
    print(f"   {BOLD}{t:^19}{RESET}")
    lines = get_board_lines(board, hide_ships=hide_ships)
    for l in lines:
        print(l)

def parse_coordinate(coord_str):
    """
    Преобразует строку вида 'A1' или 'j10' в пару индексов (row, col).
    Поддерживает регистронезависимый ввод и отсекает случайные пробелы.
    Вызывает ValueError при некорректном формате или выходе за границы.
    """
    clean = coord_str.strip().upper()
    if not clean:
        raise ValueError("Координата не может быть пустой.")

    columns = "ABCDEFGHIJ"
    col_char = clean[0]
    row_part = clean[1:].strip()

    if col_char not in columns:
        raise ValueError(f"Неизвестный столбец '{col_char}'. Допустимы только буквы от A до J.")

    if not row_part.isdigit():
        raise ValueError(f"Номер строки должен быть числом от 1 до 10, получено '{row_part}'.")

    row = int(row_part) - 1
    if not (0 <= row < 10):
        raise ValueError(f"Строка {row_part} вне диапазона. Допустимы числа от 1 до 10.")

    col = columns.index(col_char)
    return row, col

def ask_coordinate(prompt):
    """Запрашивает координаты у игрока до тех пор, пока не будет введено корректное значение."""
    while True:
        user_input = input(prompt)
        try:
            return parse_coordinate(user_input)
        except ValueError as err:
            print(f"{RED}Ошибка:{RESET} {err} Попробуйте снова.")


def ask_orientation():
    """
    Запрашивает ориентацию корабля до ввода корректного значения.
    Возвращает True для горизонтального положения (h) и False для вертикального (v).
    """
    while True:
        choice = input("Направление (h — горизонтально, v — вертикально): ").strip().lower()
        if choice == 'h':
            return True
        elif choice == 'v':
            return False
        print(f"{RED}Ошибка:{RESET} введите 'h' или 'v'.")

FLEET = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
CLEAR_LINE = "\033[K"

def setup_player_ships(board, player_name):
    """
    Организует пошаговую ручную расстановку флота игрока на переданной доске.
    Обрабатывает ввод координат и ориентации для каждого корабля,
    проверяет правила коллизий и скрывает экран по завершении расстановки.
    """
    init_screen()
    error_msg = ""
    for size in FLEET:
        placed = False
        while not placed:
            print("\033[H", end="")
            render_single_board(board, title=f"Флот: {player_name}")
            print("\033[J", end="")
            if error_msg:
                print(f"{RED}{error_msg}{RESET}{CLEAR_LINE}")
                error_msg = ""
            print(f"\nСтавим {size}-палубный корабль:{CLEAR_LINE}")
            row, col = ask_coordinate("Введите координаты: ")
            is_horizontal = True
            if size>1:
                is_horizontal = ask_orientation()
            ship = Ship(row,col, size, is_horizontal, )
            if board.place_ship(ship):
                placed = True
            else:
                error_msg = "Ошибка: корабль не помещается или касается другого корабля!"

    print("\033[H", end="")
    render_single_board(board, title=f"Флот: {player_name}")
    print("\033[J", end="")
    print(f"\n{GREEN}Все корабли успешно расставлены!{RESET}")
    input("\nНажмите Enter, чтобы передать ход...")
    init_screen()


