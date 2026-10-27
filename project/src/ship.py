from dataclasses import dataclass, field

@dataclass
class Ship:
    """Представление боевого корабля."""
    start_row: int
    start_col: int
    size: int
    is_horizontal: bool
    hits: set[tuple[int, int]] = field(default_factory=set) # Безопасное создание пустого множества для каждого нового корабля

    @property
    def coordinates(self):
        """Возвращает список координат всех палуб корабля (row, col)."""
        coords = []
        for i in range(self.size):
            if self.is_horizontal: # Если корабль горизонтальный - увеличиваем столбец, если вертикальный - строку
                coords.append((self.start_row, self.start_col+i))
            else:
                coords.append((self.start_row+i, self.start_col))
        return coords

    def hit(self, row, col):
        """Регистрирует попадание в палубу."""
        if (row, col) in self.coordinates:
            self.hits.add((row, col))

    @property
    def is_sunk(self):
        """Возвращает True, если все палубы корабля поражены."""
        return len(self.hits) == self.size
