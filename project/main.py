import sys
from src.board import Board
from src.ui import (
    ask_coordinate,
    init_screen,
    move_cursor_home,
    render_battle_field,
    setup_player_ships,
)


def play_game():
    """Управляет игровым циклом матча: расстановка флота, поочерёдная стрельба и фиксация победы."""
    player1 = input("Введите имя первого игрока: ").strip() or "Игрок 1"
    player2 = input("Введите имя второго игрока: ").strip() or "Игрок 2"

    board1 = Board()
    board2 = Board()

    # Расстановка кораблей
    setup_player_ships(board1, player1)
    setup_player_ships(board2, player2)

    init_screen() # "Обновление" терминала
    current_player = player1
    target_board = board2
    opponent_name = player2
    status_msg = f"Бой начался! Первым ходит {current_player}."

    # Начало игрового цикла
    while True:
        move_cursor_home()

        # Показываем поле с "туманом"
        render_battle_field(board1, board2,hide_ships=True, title1=player1, title2=player2)
        print("\033[J", end="", flush=True)
        print('\n'+status_msg)
        print(f"Ход: {current_player} (цель: {opponent_name})")

        # Обработка выстрела
        row, col = ask_coordinate("Введите координаты выстрела: ")
        result = target_board.receive_shot(row, col)
        if result == "duplicate":
            status_msg = "Вы уже стреляли в эту клетку! Выберите другую."
            continue
        elif result == "miss": # Переход хода при промахе
            move_cursor_home()
            render_battle_field(board1, board2, hide_ships=True, title1=player1, title2=player2)
            print("\033[J", end="", flush=True)
            input("\nМимо! Нажмите Enter, чтобы передать ход...") # "Постановка на паузу" для перехода хода
            current_player, opponent_name = opponent_name, current_player
            if target_board==board2:
                target_board = board1
            else:
                target_board = board2
            status_msg = f"{opponent_name} промахнулся! Ход переходит к вам."
            continue
        elif result == "hit":
            status_msg = f"Попал! Ход остаётся у {current_player}."
            continue
        elif result == "sunk":
            if target_board.all_ships_sunk:
                break
            else:
                status_msg = f"Убил! Ход остаётся у {current_player}."
                continue

    # После победы выводим оба поля без "тумана войны"
    move_cursor_home()
    render_battle_field(board1, board2, hide_ships=False, title1=player1, title2=player2)
    print("\033[J", end="", flush=True)
    print("\nУничтожил последний! Все корабли противника потоплены!")
    print(f"Поздравляем {current_player} с победой!")


if __name__ == "__main__":
    try:
        play_game()
    except (KeyboardInterrupt, EOFError): # Обработка аварийного прерывания программы (Ctrl + C, Ctrl + D)
        print("\n\nИгра прервана пользователем. До свидания!")
        sys.exit(0)