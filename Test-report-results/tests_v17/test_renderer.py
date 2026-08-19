import importlib.util
import sys
from pathlib import Path


def _renderer_module():
    renderer_dir = Path(__file__).parents[2] / "report-renderer"
    if str(renderer_dir) not in sys.path:
        sys.path.insert(0, str(renderer_dir))
    path = renderer_dir / "render_report.py"
    spec = importlib.util.spec_from_file_location("render_report", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_empty_grouped_bars_render_placeholder_instead_of_dividing_by_zero():
    renderer = _renderer_module()
    output = renderer.svg_grouped_bars("Technology", {})
    assert "Data not established" in output


def test_empty_pie_renders_placeholder_instead_of_dividing_by_zero():
    renderer = _renderer_module()
    output = renderer.svg_pie({}, "Landscape")
    assert "Data not established" in output
