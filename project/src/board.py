from src.ship import Ship


class Board:
    """Игровое поле 10x10 для одного игрока."""
    SIZE = 10 # Размер доски - константа

    def __init__(self):
        self.ships: list[Ship] = [] # Указание для IDE, какой тип данных будет лежать в списке
        self.hits = set()
        self.misses = set()

    def _in_bounds(self, row, col):
        """Проверяет, находится ли координата в пределах поля 10x10."""
        return 0 <= row < self.SIZE and 0 <= col < self.SIZE

    def get_ship_at(self, row, col):
        """Возвращает корабль на указанной клетке или None, если клетка пуста."""
        for ship in self.ships:
            if (row, col) in ship.coordinates:
                return ship
        return None

    def can_place_ship(self, ship: Ship):
        """
        Проверяет, можно ли разместить корабль по правилам:
        1. Все палубы внутри поля 10x10.
        2. В радиусе 1 клетки (включая диагонали) нет других кораблей.
        """
        for r,c in ship.coordinates:
            if not self._in_bounds(r, c):
                return False

            # Проверяем квадрат 3x3 вокруг каждой палубы
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    existing_ship = self.get_ship_at(nr, nc)
                    if existing_ship is not None and existing_ship is not ship: # # Условие истинно, если клетка занята ЧУЖИМ кораблём (палубы этого же корабля игнорируются)
                        return False
        return True

    def place_ship(self, ship):
        """Размещает корабль на поле, если проверка правил прошла успешно."""
        if not self.can_place_ship(ship):
            return False
        self.ships.append(ship)
        return True

    def _mark_halo(self, ship):
        """Обводит потопленный корабль ореолом из промахов."""
        for r,c in ship.coordinates: # Для каждой палубы потопленного корабля обходим квадрат 3 х 3
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if self._in_bounds(nr,nc) and (nr,nc) not in self.hits:
                        self.misses.add((nr,nc))

    def receive_shot(self, row, col):
        """
        Обрабатывает выстрел по указанной клетке и обновляет состояние игры.
        Принимает координаты клетки (row, col). Если выстрел приводит к потоплению
        корабля, автоматически размечает окрестность промахов вокруг него.
        Возвращает:
            "out_of_bounds" — координаты находятся за пределами поля;
            "duplicate"     — в эту клетку уже производился выстрел ранее;
            "miss"          — выстрел пришёлся в пустую воду;
            "hit"           — ранение корабля (остались целые палубы);
            "sunk"          — корабль полностью уничтожен.`
        """
        if not self._in_bounds(row, col):
            return "out_of_bounds"

        if (row, col) in self.hits or (row, col) in self.misses:
            return "duplicate"

        ship = self.get_ship_at(row, col)
        if ship is None:
            self.misses.add((row, col))
            return "miss"

        self.hits.add((row, col))
        ship.hit(row, col)
        if ship.is_sunk:
            self._mark_halo(ship)
            return "sunk"
        else:
            return "hit"

    @property
    def all_ships_sunk(self) -> bool:
        """Возвращает True, если все корабли на поле потоплены."""
        if not self.ships:
            return False
        return all(ship.is_sunk for ship in self.ships)