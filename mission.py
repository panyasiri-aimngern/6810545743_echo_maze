class Mission:
    def __init__(self, checkpoints: list[tuple[int, int]]):
        self.checkpoints = checkpoints
        self.collected: set[tuple[int, int]] = set()

    def collect(self, x: int, y: int) -> bool:
        pos = (x, y)
        if pos in self.checkpoints and pos not in self.collected:
            self.collected.add(pos)
            return True
        return False

    @property
    def is_complete(self) -> bool:
        return len(self.collected) == len(self.checkpoints)

    @property
    def count(self) -> tuple[int, int]:
        return len(self.collected), len(self.checkpoints)
