import unittest
from src.board import Board
from src.ship import Ship
from src.ui import parse_coordinate


class TestBoard(unittest.TestCase):

    def setUp(self):
        """Выполняется перед каждым тестом: создаёт чистую доску."""
        self.board = Board()

    def test_shot_out_of_bounds(self):
        """Проверяем, что выстрел за пределы сетки возвращает 'out_of_bounds'."""
        # Выстрел с отрицательными координатами
        result = self.board.receive_shot(-1, 0)
        self.assertEqual(result, "out_of_bounds")

        # Выстрел с координатами, превышающими размер поля
        result_too_large = self.board.receive_shot(10, 10)
        self.assertEqual(result_too_large, "out_of_bounds")

    def test_shot_miss_empty_water(self):
        """Проверяем промах при стрельбе по пустой воде."""
        # На пустой доске любой выстрел — это промах
        result = self.board.receive_shot(0, 0)

        # Метод должен вернуть статус 'miss'
        self.assertEqual(result, "miss")
        # Клетка должна добавиться в список промахов
        self.assertIn((0, 0), self.board.misses)

    def test_duplicate_shot(self):
        """Проверяем реакцию на повторный выстрел в ту же клетку."""
        # Делаем первый выстрел
        self.board.receive_shot(2, 2)

        # Стреляем второй раз в ту же координату
        second_shot = self.board.receive_shot(2, 2)
        self.assertEqual(second_shot, "duplicate")

    def test_shot_hit_and_sunk(self):
        """Проверяем ранение, потопление корабля и автоматическую расстановку ореола."""
        # Размещаем 2-палубный горизонтальный корабль на клетках (1, 1) и (1, 2)
        self.ship = Ship(1, 1, 2, True)
        self.board.place_ship(self.ship)

        # Первое попадание (ранение)
        result = self.board.receive_shot(1, 1)
        self.assertEqual(result, "hit")
        self.assertIn((1, 1), self.board.hits)

        # Второе попадание (уничтожение корабля)
        second_result = self.board.receive_shot(1, 2)
        self.assertEqual(second_result, "sunk")
        self.assertTrue(self.board.all_ships_sunk)

        # Проверка обводки: клетки вокруг уничтоженного судна должны стать промахами
        self.assertIn((0, 0), self.board.misses)  # Диагональная клетка
        self.assertIn((1, 3), self.board.misses)  # Клетка сбоку от носа

    def test_can_place_ship(self):
        """Проверяем правила расстановки: границы поля, наложение и дистанцию между кораблями."""
        # Попытка выставить корабль за пределы сетки (палубы 8, 9, 10, 11)
        self.ship = Ship(0, 8, 4, True)
        result = self.board.place_ship(self.ship)
        self.assertFalse(result)

        self.ship = Ship(0, 2, 2, True)
        self.board.place_ship(self.ship)

        # Попытка прямого наложения: второй корабль пересекает занятую клетку (0, 2)
        self.second_ship = Ship(0, 2, 2, False)
        second_result = self.board.place_ship(self.second_ship)
        self.assertFalse(second_result)

        # Попытка поставить корабль вплотную
        self.third_ship = Ship(1, 1, 4, True)
        third_result = self.board.place_ship(self.third_ship)
        self.assertFalse(third_result)

    def test_all_ships_sunk(self):
        """Проверяем корректность победы при наличии нескольких кораблей."""
        # Ставим два отдельных 1-палубных корабля
        self.first_ship = Ship(0, 0, 1, True)
        self.second_ship = Ship(2, 2, 1, False)
        self.board.place_ship(self.first_ship)
        self.board.place_ship(self.second_ship)

        # Топим первый корабль: бой должен продолжаться
        self.board.receive_shot(0, 0)
        result = self.board.all_ships_sunk
        self.assertFalse(result)

        # Топим второй корабль: все суда уничтожены, должна быть победа
        self.board.receive_shot(2, 2)
        second_result = self.board.all_ships_sunk
        self.assertTrue(second_result)


class TestShip(unittest.TestCase):

    def setUp(self):
        """Создаём горизонтальный и вертикальный корабли перед каждым тестом."""
        self.ship = Ship(0, 0, 2, True)
        self.second_ship = Ship(3, 0, 2, False)

    def test_new_ship(self):
        """Проверяем начальное состояние корабля и генерацию палубных координат."""
        # Новый корабль не должен быть потоплен
        result = self.ship.is_sunk
        self.assertFalse(result)

        # Ожидаемые координаты для горизонтального и вертикального судов
        coords_1 = [(0, 0), (0, 1)]
        coords_2 = [(3, 0), (4, 0)]

        # Проверяем корректность формирования координат палуб
        second_result = self.ship.coordinates
        third_result = self.second_ship.coordinates
        self.assertEqual(coords_1, second_result)
        self.assertEqual(coords_2, third_result)

    def test_hit_ship(self):
        """Проверяем получение урона, учёт попаданий и гибель судна."""
        # Первое попадание по кораблю
        self.ship.hit(0, 0)
        result = self.ship.hits
        self.assertIn((0, 0), result)

        # Корабль ранен, но ещё на плаву
        second_result = self.ship.is_sunk
        self.assertFalse(second_result)

        # Второе попадание добивает корабль
        self.ship.hit(0, 1)
        third_result = self.ship.is_sunk
        self.assertTrue(third_result)


class TestParseCoordinate(unittest.TestCase):

    def test_valid_coordinates(self):
        """Проверяет корректное преобразование валидных координат разного регистра и границ поля."""
        cases = [("A1", (0, 0)), ("a1", (0, 0)), ("J10", (9, 9)), ("j10", (9, 9)), ("e5", (4, 4)), ("B7", (6, 1)), ("C2", (1, 2)), ("A 5", (4, 0))]
        for coord_str, expected in cases:
            with self.subTest(coord=coord_str): # Изоляция каждого теста в итерации, если один тест провален, остальные продолжатся
                self.assertEqual(parse_coordinate(coord_str), expected)

    def test_invalid_letter_raises_error(self):
        """Проверяет выброс ValueError при вводе недопустимой буквы строки."""
        invalid_letters = ["K1", "Z5", "1A", "Б1"]
        for item in invalid_letters:
            with self.subTest(coord=item):
                with self.assertRaises(ValueError): # Проверка выброса нужного исключения
                    parse_coordinate(item)

    def test_out_of_bounds_number_raises_error(self):
        """Проверяет выброс ValueError при выходе числового индекса за пределы 1-10."""
        invalid_numbers = ["A0", "A11", "J99", "C-1"]
        for item in invalid_numbers:
            with self.subTest(coord=item):
                with self.assertRaises(ValueError):
                    parse_coordinate(item)

    def test_malformed_and_empty_input_raises_error(self):
        """Проверяет реакцию парсера на пустые строки, пробелы и некорректную длину."""
        malformed = ["", "   ", "A", "10", "A100", "hello"]
        for item in malformed:
            with self.subTest(coord=item):
                with self.assertRaises(ValueError):
                    parse_coordinate(item)


if __name__ == "__main__":
    unittest.main()
