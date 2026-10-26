"""Offline regression tests for icon/generate.py (no network, mocked genai)."""

import importlib.util
import sys
import types as pytypes
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "icon" / "generate.py"


class _Config:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def gen(monkeypatch):
    google = pytypes.ModuleType("google")
    genai = pytypes.ModuleType("google.genai")
    types = pytypes.ModuleType("google.genai.types")
    types.GenerateContentConfig = _Config
    genai.Client = mock.MagicMock()
    genai.types = types
    google.genai = genai
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.genai", genai)
    monkeypatch.setitem(sys.modules, "google.genai.types", types)
    spec = importlib.util.spec_from_file_location("icon_generate_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.GEMINI_API_KEY = "test-key"
    return mod


def _response(text, finish_reason=None):
    cand = mock.Mock()
    cand.finish_reason = finish_reason
    cand.content = None
    return mock.Mock(text=text, candidates=[cand])


def test_viewbox_size_only_touches_root_tag(gen):
    src = '<svg viewBox="0 0 24 24" stroke-width="2"><rect width="10" height="8"/></svg>'
    out = gen.apply_viewbox_size(src, 48)
    assert 'stroke-width="2"' in out
    assert '<rect width="10" height="8"/>' in out
    assert 'viewBox="0 0 24 24"' in out
    root = out[: out.index(">") + 1]
    assert 'width="48"' in root and 'height="48"' in root


def test_viewbox_size_handles_width_and_height_independently(gen):
    out = gen.apply_viewbox_size("<svg width='10' viewBox='0 0 24 24'><path d='M0 0'/></svg>", 32)
    root = out[: out.index(">") + 1]
    assert "width=\"32\"" in root and "height=\"32\"" in root
    assert "width='10'" not in root


@pytest.mark.parametrize("src, kept", [
    ('<svg aria-label="height=\'2\'" viewBox="0 0 24 24"><path/></svg>',
     {"aria-label": "height='2'"}),
    ("<svg aria-label='width=\"2\" height=\"3\"' viewBox='0 0 24 24'><path/></svg>",
     {"aria-label": 'width="2" height="3"'}),
    ('<svg data-note="a > b width=\'1\'" height="5" viewBox="0 0 24 24"><path/></svg>',
     {"data-note": "a > b width='1'"}),
    ("<svg data-note='x>y height=\"2\"' width='7'><rect width='1' height='1'/></svg>",
     {"data-note": 'x>y height="2"'}),
])
def test_viewbox_size_ignores_attribute_text_inside_quoted_values(gen, src, kept):
    out = gen.apply_viewbox_size(src, 24)
    root = ET.fromstring(out)
    assert root.get("width") == "24" and root.get("height") == "24"
    for name, value in kept.items():
        assert root.get(name) == value
    for child in root:
        assert child.get("width") in (None, "1")


def test_generate_icon_uses_large_token_budget(gen, tmp_path):
    client = gen.genai.Client.return_value
    client.models.generate_content.return_value = _response(
        '<svg viewBox="0 0 24 24"><path d="M0 0"/></svg>')
    out = tmp_path / "a.svg"
    assert gen.generate_icon("crane", output_path=str(out)) == str(out)
    cfg = client.models.generate_content.call_args.kwargs["config"]
    assert cfg.max_output_tokens >= 16384


def test_generate_icon_reports_max_tokens(gen, capsys):
    client = gen.genai.Client.return_value
    client.models.generate_content.return_value = _response(
        '```svg\n<svg viewBox="0 0 24 24"><path d="M 15 14 H 19', "MAX_TOKENS")
    assert gen.generate_icon("crane") is None
    assert "MAX_TOKENS" in capsys.readouterr().out
    assert client.models.generate_content.call_count == 1


def test_generate_icon_reports_empty_output_separately(gen, capsys):
    client = gen.genai.Client.return_value
    client.models.generate_content.return_value = _response("", "STOP")
    assert gen.generate_icon("crane") is None
    out = capsys.readouterr().out
    assert "empty response" in out and "MAX_TOKENS" not in out


def test_generate_icon_handles_none_text(gen, capsys):
    client = gen.genai.Client.return_value
    client.models.generate_content.return_value = _response(None, "SAFETY")
    assert gen.generate_icon("crane") is None
    assert "empty response" in capsys.readouterr().out


def test_generate_batch_reports_max_tokens(gen, tmp_path, capsys):
    client = gen.genai.Client.return_value
    client.models.generate_content.return_value = _response(
        '<svg viewBox="0 0 24 24"><path d="M 15 14 H 19', "MAX_TOKENS")
    assert gen.generate_batch("crane", 2, str(tmp_path)) == []
    out = capsys.readouterr().out
    assert "MAX_TOKENS" in out and "Error generating icons" not in out


def test_generate_batch_handles_empty_response(gen, tmp_path, capsys):
    client = gen.genai.Client.return_value
    resp = _response(None, "SAFETY")
    resp.candidates = []
    client.models.generate_content.return_value = resp
    assert gen.generate_batch("crane", 2, str(tmp_path)) == []
    out = capsys.readouterr().out
    assert "empty response" in out and "Error generating icons" not in out


def test_generate_batch_warns_when_truncated_after_some_icons(gen, tmp_path, capsys):
    client = gen.genai.Client.return_value
    client.models.generate_content.return_value = _response(
        '<svg viewBox="0 0 24 24"><path d="M0 0"/></svg>\n'
        '<svg viewBox="0 0 24 24"><path d="M 15 14 H 19', "MAX_TOKENS")
    assert len(gen.generate_batch("crane", 2, str(tmp_path))) == 1
    assert "MAX_TOKENS" in capsys.readouterr().out


def _run_main(gen, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["generate.py", *args])
    gen.main()


def test_main_exits_1_when_icon_request_fails(gen, monkeypatch, tmp_path):
    client = gen.genai.Client.return_value
    client.models.generate_content.side_effect = RuntimeError("429 RESOURCE_EXHAUSTED")
    with pytest.raises(SystemExit) as raised:
        _run_main(gen, monkeypatch, "--prompt", "crane", "--output", str(tmp_path / "a.svg"))
    assert raised.value.code == 1


def test_main_exits_1_when_batch_generates_nothing(gen, monkeypatch, tmp_path):
    client = gen.genai.Client.return_value
    resp = _response(None, "SAFETY")
    resp.candidates = []
    client.models.generate_content.return_value = resp
    with pytest.raises(SystemExit) as raised:
        _run_main(gen, monkeypatch, "--prompt", "crane", "--batch", "2",
                  "--output-dir", str(tmp_path))
    assert raised.value.code == 1


def test_main_exits_0_when_icon_is_saved(gen, monkeypatch, tmp_path):
    client = gen.genai.Client.return_value
    client.models.generate_content.return_value = _response(
        '<svg viewBox="0 0 24 24"><path d="M0 0"/></svg>')
    _run_main(gen, monkeypatch, "--prompt", "crane", "--output", str(tmp_path / "a.svg"))
    assert (tmp_path / "a.svg").exists()


def test_main_list_styles_exits_0(gen, monkeypatch):
    _run_main(gen, monkeypatch, "--list-styles")
