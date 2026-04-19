from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Rect:
    left: float
    top: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.left + self.width

    @property
    def bottom(self) -> float:
        return self.top + self.height

    @property
    def center_x(self) -> float:
        return self.left + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self.top + self.height / 2.0

    def contains(self, x: float, y: float) -> bool:
        return self.left <= x <= self.right and self.top <= y <= self.bottom

    def scaled(self, factor: float) -> Rect:
        return Rect(self.left * factor, self.top * factor, self.width * factor, self.height * factor)


@dataclass(frozen=True)
class OcrToken:
    id: str
    order: int
    text: str
    rect: Rect
    confidence: float = 1.0
    line_index: int = -1


@dataclass
class OcrPage:
    width: float
    height: float
    dpi_scale: float = 1.0
    page_index: int = 0
    tokens: list[OcrToken] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Page dimensions must be positive")
        if self.dpi_scale <= 0:
            raise ValueError("dpi_scale must be positive")
        ids = [token.id for token in self.tokens]
        if len(ids) != len(set(ids)):
            raise ValueError("OCR token IDs must be unique")

    @property
    def source_width(self) -> float:
        return self.width * self.dpi_scale

    @property
    def source_height(self) -> float:
        return self.height * self.dpi_scale