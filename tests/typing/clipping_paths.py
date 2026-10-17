from typing import Literal
from oxidize_pdf import ClippingPath, ClippingPathCommand, Page, WindingRule

path = ClippingPath()
chained: ClippingPath = path.move_to(1, 2).line_to(3, 4).curve_to(5, 6, 7, 8, 9, 10).close_path()
path.add_rect(1, 2, 3, 4).add_circle(10, 20, 5).add_ellipse(10, 20, 5, 3)
path.add_rounded_rect(1, 2, 20, 10, 5).add_polygon([(1, 2), (3, 4), (5, 6)])
other: ClippingPath = path.with_winding_rule(WindingRule.EvenOdd)
empty: bool = other.is_empty
commands: list[ClippingPathCommand] = other.commands
kind: Literal['move_to', 'line_to', 'curve_to', 'rectangle', 'close_path'] = commands[0].kind
coordinates: list[float] = commands[0].coordinates
operations: str = other.to_pdf_operations()
Page(100, 100).set_clipping_path(other)
path.clear()
