import sys
import os
import subprocess
from src.ship import Ship


RESET = "\033[0m" # Сброс всех параметров терминала
BOLD = "\033[1m"  # Жирный шрифт

CYAN = "\033[36m"   # Координаты
DIM = "\033[2m"     # Заголовки
BLUE = "\033[34m"   # Вода
GREEN = "\033[32m"  # Живой корабль
RED = "\033[31m"    # Попадание
GRAY = "\033[90m"   # Промах

WATER_CHAR = f"{BLUE}~{RESET}"
SHIP_CHAR = f"{GREEN}■{RESET}"
HIT_CHAR = f"{RED}X{RESET}"
MISS_CHAR = f"{GRAY}•{RESET}"

FLEET = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1] # Корабли одного игрока
CLEAR_LINE = "\033[K" # Очистка строки до конца вправо
CLEAR_TERMINAL = "\033[J" # Очистка всего пространства от курсора до конца экран


def init_screen():
    """Полная очистка экрана перед началом игры."""
    # 1. Системная очистка
    # shell=True нужен здесь, так как cls/clear — это встроенные команды командного интерпретатора
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True) # Универсальная команда для разных систем

    # 2. Жёсткий ANSI-сброс:
    # \033[2J — очистить экран
    # \033[3J — удалить всю историю скролла (scrollback)
    # \033[H  — вернуть курсор в (1, 1)
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush() # Отправка команд в терминал

def move_cursor_home():
    """Возвращает курсор в верхний левый угол терминала (1, 1)."""
    sys.stdout.write("\033[H")
    sys.stdout.flush()

def get_cell_symbol(board, row, col, hide_ships=False): # hide_ships - включения "тумана войны"
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
    lines = [header]
    for r in range(10):
        buf = []
        for c in range(10):
            buf.append(get_cell_symbol(board, r, c, hide_ships))
        s = " ".join(buf)
        ready_s = f"{CYAN}{r+1:2d}{RESET} " + s # Каждый номер строки занимает два символа
        lines.append(ready_s)
    return lines

def render_battle_field(board1, board2,title1="Игрок 1", title2="Игрок 2", hide_ships: bool = True):
    """Отрисовывает оба поля бок о бок (Side-by-Side) во время боя.
    По умолчанию оба поля скрыты туманом войны (hide_ships=True)."""
    move_cursor_home()
    lines1 = get_board_lines(board1, hide_ships=hide_ships)
    lines2 = get_board_lines(board2, hide_ships=hide_ships)
    t1 = f"[ {title1} ]"
    t2 = f"[ {title2} ]"
    print(f"   {BOLD}{t1:^19}{RESET}   │      {BOLD}{t2:^19}{RESET}") # Выравнивание заголовков полей по центру
    for l1,l2 in zip(lines1,lines2):
        print(f"{l1}   │   {l2}")

def render_single_board(board, title="Ваше поле", hide_ships=False):
    """Отрисовывает одно поле (используется на этапе расстановки кораблей)."""
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
    col_char = clean[0] # Столбец
    row_num = clean[1:].strip()  # Строка

    if col_char not in columns:
        raise ValueError(f"Неизвестный столбец '{col_char}'. Допустимы только буквы от A до J.")

    if not row_num.isdigit():
        raise ValueError(f"Номер строки должен быть числом от 1 до 10, получено '{row_num}'.")

    row = int(row_num) - 1 # Пользователю удобнее вводить число от 1 до 10, а в коде легче работать с числом от 0 до 9
    if not (0 <= row < 10):
        raise ValueError(f"Строка {row_num} вне диапазона. Допустимы числа от 1 до 10.")

    col = columns.index(col_char)
    return row, col

def ask_coordinate(prompt):
    """
    Запрашивает координаты у игрока до тех пор, пока не будет введено корректное значение.
    При ошибке затирает некорректную строку на месте, исключая скролл терминала.
    """
    current_prompt = prompt
    while True:
        user_input = input(current_prompt).strip()
        try:
            return parse_coordinate(user_input)
        except ValueError as err:
            # \033[F — поднимает курсор на 1 строку вверх (куда пользователь нажал Enter)
            # \033[K — стирает строку от курсора до конца
            current_prompt = f"\033[F{CLEAR_LINE}{RED}Ошибка ({err})!{RESET} {prompt}"

def ask_orientation(prompt: str = "Направление (h — горизонтально, v — вертикально): "):
    """
    Запрашивает ориентацию корабля до ввода корректного значения.
    Возвращает True для горизонтального положения (h) и False для вертикального (v).
    """
    current_prompt = prompt
    while True:
        choice = input(current_prompt).strip().lower()
        if choice == "h":
            return True
        if choice == "v":
            return False

        current_prompt = f"\033[F{CLEAR_LINE}{RED}Ошибка (введите 'h' или 'v')!{RESET} {prompt}"


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
            # Перерисовка поля происходит поверх старого отображения, что исключает мерцание
            move_cursor_home()
            render_single_board(board, title=f"Флот: {player_name}")
            print(f"{CLEAR_TERMINAL}", end="")
            if error_msg:
                print(f"\n{RED}{error_msg}{RESET}{CLEAR_LINE}")
                error_msg = ""
            print(f"\nСтавим {size}-палубный корабль:{CLEAR_LINE}")
            row, col = ask_coordinate("Введите координаты: ")
            is_horizontal = True
            if size>1:
                is_horizontal = ask_orientation()
            ship = Ship(row, col, size, is_horizontal)
            if board.place_ship(ship):
                placed = True
            else:
                error_msg = "Ошибка: корабль не помещается или касается другого корабля!"

    # После расстановки флота игроку показывается его поле, игра "ставится на паузу" и ждёт второго игрока
    move_cursor_home()
    render_single_board(board, title=f"Флот: {player_name}")
    print(f"{CLEAR_TERMINAL}", end="")
    print(f"\n{GREEN}Все корабли успешно расставлены!{RESET}")
    input("\nНажмите Enter, чтобы передать ход...")
    init_screen() # Полная очистка терминала, второй игрок не увидит поле первого
