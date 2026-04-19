from __future__ import annotations

from dataclasses import dataclass

from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QFont, QFontMetricsF

from ..model import OcrPage, OcrToken

try:
    from .GapTree_Sort_Algorithm.gap_tree import GapTree
except ImportError:  # pragma: no cover - only when the vendored module is missing
    GapTree = None


@dataclass(frozen=True, order=True)
class TextPosition:
    token_index: int
    character_index: int = 0


@dataclass(frozen=True)
class SelectionRange:
    anchor: TextPosition
    focus: TextPosition

    @property
    def normalized(self) -> tuple[TextPosition, TextPosition]:
        return (self.anchor, self.focus) if self.anchor <= self.focus else (self.focus, self.anchor)


class OcrLayout:
    def __init__(self, page: OcrPage, font: QFont | None = None) -> None:
        self.page = page
        self.font = font or QFont("Arial")
        self.tokens = self._reading_order(page.tokens)
        self.lines = self._cluster_lines(self.tokens)
        self.line_by_token = {
            token_index: line_index
            for line_index, line in enumerate(self.lines)
            for token_index in line
        }
        self.character_rects = [self._character_rects(token) for token in self.tokens]

    @staticmethod
    def _cluster_lines(tokens: list[OcrToken]) -> list[list[int]]:
        lines: list[list[int]] = []
        for index, token in sorted(
            enumerate(tokens), key=lambda pair: (pair[1].rect.center_y, pair[1].rect.left)
        ):
            best_line = None
            best_distance = float("inf")
            for line_index, line in enumerate(lines):
                members = [tokens[item] for item in line]
                center_y = sum(item.rect.center_y for item in members) / len(members)
                height = sum(item.rect.height for item in members) / len(members)
                distance = abs(token.rect.center_y - center_y)
                if distance <= min(token.rect.height, height) * 0.55 and distance < best_distance:
                    best_line = line_index
                    best_distance = distance
            if best_line is None:
                lines.append([index])
            else:
                lines[best_line].append(index)
        lines.sort(key=lambda line: sum(tokens[index].rect.center_y for index in line) / len(line))
        for line in lines:
            line.sort(key=lambda index: tokens[index].rect.left)
        return lines

    @classmethod
    def _reading_order(cls, tokens: list[OcrToken]) -> list[OcrToken]:
        """Order OCR boxes by the page's columns and then by each column's rows.

        GapTree derives persistent vertical gaps from the OCR boxes and builds a
        layout tree around them. This preserves human reading order for pages
        whose columns share the same vertical positions, where a simple
        top-to-bottom, left-to-right sort interleaves the columns.
        """
        source = sorted(tokens, key=lambda item: item.order)
        if len(source) < 2 or GapTree is None:
            return source
        sorter = GapTree(
            lambda token: (
                token.rect.left,
                token.rect.top,
                token.rect.right,
                token.rect.bottom,
            )
        )
        ordered = sorter.sort(source)
        # A lone item beside a wider paragraph can leave a vertical gap that
        # looks like a column to any geometry-only algorithm. Reorder only
        # when GapTree identifies at least two multi-item regions, which is a
        # stable indication of parallel columns rather than a short line.
        columns = [group for group in sorter.get_nodes_text_blocks() if len(group) > 1]
        return ordered if len(columns) > 1 else source

    def _character_rects(self, token: OcrToken) -> list[QRectF]:
        if not token.text:
            return []
        metrics = QFontMetricsF(self.font)
        advances = [max(metrics.horizontalAdvance(character), 0.01) for character in token.text]
        scale = token.rect.width / sum(advances)
        x = token.rect.left
        result: list[QRectF] = []
        for advance in advances:
            width = advance * scale
            result.append(QRectF(x, token.rect.top, width, token.rect.height))
            x += width
        return result

    def hit_test(self, point: QPointF, *, snap: bool = True) -> TextPosition | None:
        if not self.tokens:
            return None
        containing = [
            index
            for index, token in enumerate(self.tokens)
            if token.rect.contains(point.x(), point.y())
        ]
        if not containing and not snap:
            return None
        # Resolve the line first: a long line's distant center must not make
        # the pointer jump to a short adjacent line.
        line = min(
            self.lines,
            key=lambda line: min(
                max(
                    self.tokens[index].rect.top - point.y(),
                    point.y() - self.tokens[index].rect.bottom,
                    0,
                )
                for index in line
            ),
        )
        candidates = containing or line
        token_index = min(
            candidates,
            key=lambda index: max(
                self.tokens[index].rect.left - point.x(),
                point.x() - self.tokens[index].rect.right,
                0,
            ),
        )
        rects = self.character_rects[token_index]
        if not rects:
            return TextPosition(token_index, 0)
        character_index = min(
            range(len(rects)),
            key=lambda index: abs(rects[index].center().x() - point.x()),
        )
        return TextPosition(token_index, character_index)

    def selection_from_points(self, start: QPointF, end: QPointF) -> SelectionRange | None:
        """Select by glyph centers, with full intervening reading-order lines.

        Keep positions inclusive for the public range API. Mouse coordinates
        are boundaries instead: a click or a drag through whitespace is empty.
        """
        if start == end or not self.tokens:
            return None
        if not any(
            token.rect.right >= min(start.x(), end.x())
            and token.rect.left <= max(start.x(), end.x())
            and token.rect.bottom >= min(start.y(), end.y())
            and token.rect.top <= max(start.y(), end.y())
            for token in self.tokens
        ):
            return None
        bounds = [self._line_rect(line) for line in self.lines]
        start_line = next(
            (i for i, rect in enumerate(bounds) if rect.top() <= start.y() <= rect.bottom()), None
        )
        end_line = next(
            (i for i, rect in enumerate(bounds) if rect.top() <= end.y() <= rect.bottom()), None
        )
        same_line = start_line is not None and start_line == end_line
        if (same_line and start.x() > end.x()) or (not same_line and start.y() > end.y()):
            start, end = end, start
            start_line, end_line = end_line, start_line
        positions = []
        for line_index, line in enumerate(self.lines):
            rect = bounds[line_index]
            if not same_line and (rect.bottom() < start.y() or rect.top() > end.y()):
                continue
            if same_line and line_index != start_line:
                continue
            left = start.x() if line_index == start_line else float("-inf")
            right = end.x() if line_index == end_line else float("inf")
            # Outside line boxes, only consider text intersected by the drag.
            if (
                start_line is None
                and end_line is None
                and (
                    rect.right() < min(start.x(), end.x()) or rect.left() > max(start.x(), end.x())
                )
            ):
                continue
            for token_index in line:
                positions.extend(
                    TextPosition(token_index, index)
                    for index, char_rect in enumerate(self.character_rects[token_index])
                    if left <= char_rect.center().x() <= right
                )
        if not positions:
            return None
        return SelectionRange(positions[0], positions[-1])

    def _line_rect(self, line: list[int]) -> QRectF:
        rect = self._qrect(self.tokens[line[0]])
        for index in line[1:]:
            rect = rect.united(self._qrect(self.tokens[index]))
        return rect

    def selection_bands(self, selection: SelectionRange) -> list[QRectF]:
        """One band per selected line, with shared edges between nearby lines."""
        start, end = selection.normalized
        selected: dict[int, QRectF] = {}
        for token_index in range(start.token_index, end.token_index + 1):
            rects = self.character_rects[token_index]
            first = start.character_index if token_index == start.token_index else 0
            last = end.character_index + 1 if token_index == end.token_index else len(rects)
            rects = rects[first:last]
            line_index = self.line_by_token[token_index]
            for rect in rects:
                selected[line_index] = (
                    selected[line_index].united(rect) if line_index in selected else QRectF(rect)
                )

        # Use the whole line's metrics even for partial selection. Independent
        # OCR box padding otherwise creates overlapping translucent stripes.
        bounds = [self._line_rect(line) for line in self.lines]
        tops = [rect.top() for rect in bounds]
        bottoms = [rect.bottom() for rect in bounds]
        for index in range(len(bounds) - 1):
            # Only bridge actual selected neighbors. Unselected text must not
            # enlarge a single-line selection into the surrounding whitespace.
            if index not in selected or index + 1 not in selected:
                continue
            first, second = selected[index], selected[index + 1]
            if first.right() <= second.left() or second.right() <= first.left():
                continue
            upper, lower = bounds[index : index + 2]
            gap = lower.top() - upper.bottom()
            if gap <= min(upper.height(), lower.height()):
                boundary = (upper.bottom() + lower.top()) / 2
                bottoms[index] = boundary
                tops[index + 1] = boundary
        return [
            QRectF(rect.left(), tops[index], rect.width(), bottoms[index] - tops[index])
            for index, rect in selected.items()
        ]

    def selection_rects(self, selection: SelectionRange) -> list[QRectF]:
        start, end = selection.normalized
        result: list[QRectF] = []
        for token_index in range(start.token_index, end.token_index + 1):
            rects = self.character_rects[token_index]
            if not rects:
                continue
            first = start.character_index if token_index == start.token_index else 0
            last = end.character_index if token_index == end.token_index else len(rects) - 1
            result.extend(rects[first : last + 1])
        return result

    def selected_text(self, selection: SelectionRange) -> str:
        start, end = selection.normalized
        fragments: list[tuple[int, str]] = []
        for token_index in range(start.token_index, end.token_index + 1):
            text = self.tokens[token_index].text
            first = start.character_index if token_index == start.token_index else 0
            last = end.character_index if token_index == end.token_index else len(text) - 1
            fragments.append((token_index, text[first : last + 1]))
        output = ""
        previous_index: int | None = None
        for token_index, text in fragments:
            if previous_index is not None:
                previous_line = self.line_by_token.get(previous_index)
                current_line = self.line_by_token.get(token_index)
                if previous_line != current_line:
                    output += "\n"
                elif self._needs_space(self.tokens[previous_index], self.tokens[token_index]):
                    output += " "
            output += text
            previous_index = token_index
        return output

    @staticmethod
    def _needs_space(left: OcrToken, right: OcrToken) -> bool:
        gap = right.rect.left - left.rect.right
        return gap > min(left.rect.height, right.rect.height) * 0.2

    @staticmethod
    def _qrect(token: OcrToken) -> QRectF:
        rect = token.rect
        return QRectF(rect.left, rect.top, rect.width, rect.height)