from dataclasses import dataclass


@dataclass
class BoardBlock:
    x: int
    y: int

    def __add__(self, other):
        return BoardBlock(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self