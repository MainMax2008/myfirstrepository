from src.board import Board
from src.ui import *

def play_game():
    player1 = input("Введите имя первого игрока: ").strip() or "Игрок 1"
    player2 = input("Введите имя второго игрока: ").strip() or "Игрок 2"

    board1 = Board()
    board2 = Board()

    setup_player_ships(board1, player1)
    setup_player_ships(board2, player2)

    init_screen()
    current_player = player1
    target_board = board2
    opponent_name = player2
    status_msg = f"Бой начался! Первым ходит {current_player}."

    while True:
        move_cursor_home()

        render_battle_field(board1, board2,hide_ships=True, title1=player1, title2=player2)
        print("\033[J", end="", flush=True)
        print("                                                ")
        print(status_msg)
        print(f"Ход: {current_player} (цель: {opponent_name})")

        row, col = ask_coordinate("Введите координаты выстрела: ")
        result = target_board.receive_shot(row, col)
        if result == "duplicate":
            status_msg = "Вы уже стреляли в эту клетку! Выберите другую."
            continue
        elif result == "miss":
            move_cursor_home()
            render_battle_field(board1, board2, hide_ships=True, title1=player1, title2=player2)
            print("\033[J", end="", flush=True)
            print("                                           ")
            input("Мимо! Нажмите Enter, чтобы передать ход...")
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
                status_msg = "Уничтожил последний! Это победа!"
                break
            else:
                status_msg = f"Убил! Ход остаётся у {current_player}."
                continue

    move_cursor_home()
    render_battle_field(board1, board2, hide_ships=False, title1=player1, title2=player2)
    print("\033[J", end="", flush=True)
    print("                                         ")
    print(f"Поздравляем {current_player} с победой!")


if __name__ == "__main__":
    play_game()