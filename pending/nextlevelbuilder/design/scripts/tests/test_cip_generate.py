"""Offline regression tests for cip/generate.py (no network, stubbed genai)."""

import importlib.util
import sys
import types as pytypes
from pathlib import Path
from unittest import mock

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "cip" / "generate.py"

JPEG = b"\xff\xd8\xff\xe0jpeg-bytes"
PNG = b"\x89PNG\r\n\x1a\npng-bytes"

PROMPT_DATA = {
    "prompt": "business card mockup",
    "deliverable": "Business Card",
    "brand": "Demo",
    "style": "Corporate Minimal",
    "mockup_context": "desk",
}


class _Config:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def load_cip(monkeypatch):
    """Return a loader for a fresh cip/generate.py with google.genai stubbed.

    cip/generate.py imports its own `core` module, which shares a name with the
    ui-ux-pro-max search core, so sys.modules and sys.path are restored afterwards.
    """
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GEMINI_FLASH_IMAGE_MODEL", raising=False)
    monkeypatch.delenv("GEMINI_PRO_IMAGE_MODEL", raising=False)

    with mock.patch.dict(sys.modules):
        sys.modules.pop("core", None)
        google = pytypes.ModuleType("google")
        genai = pytypes.ModuleType("google.genai")
        types = pytypes.ModuleType("google.genai.types")
        types.GenerateContentConfig = types.ImageConfig = _Config
        genai.Client = mock.MagicMock()
        genai.types = types
        google.genai = genai
        sys.modules.update(
            {"google": google, "google.genai": genai, "google.genai.types": types}
        )

        def load():
            spec = importlib.util.spec_from_file_location("cip_generate_under_test", SCRIPT)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.client = genai.Client.return_value
            return mod

        yield load


@pytest.fixture
def cip(load_cip):
    return load_cip()


def _image_response(mime_type, data):
    part = pytypes.SimpleNamespace(
        inline_data=pytypes.SimpleNamespace(mime_type=mime_type, data=data))
    return pytypes.SimpleNamespace(
        candidates=[pytypes.SimpleNamespace(content=pytypes.SimpleNamespace(parts=[part]))])


def _run_main(cip, monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["generate.py", "--brand", "Demo", *args])
    cip.main()


@pytest.mark.parametrize("mime_type, data, extension", [
    ("image/jpeg", JPEG, ".jpg"),
    ("image/png", PNG, ".png"),
    ("image/webp", b"RIFFwebp", ".webp"),
])
def test_mockup_extension_follows_returned_image_type(cip, tmp_path, mime_type, data, extension):
    cip.client.models.generate_content.return_value = _image_response(mime_type, data)
    filepath = cip.generate_with_nano_banana(PROMPT_DATA, tmp_path, model_key="pro")
    assert Path(filepath).suffix == extension
    assert Path(filepath).read_bytes() == data


def test_pro_uses_the_ga_model(cip, tmp_path):
    cip.client.models.generate_content.return_value = _image_response("image/png", PNG)
    cip.generate_with_nano_banana(PROMPT_DATA, tmp_path, model_key="pro")
    assert cip.client.models.generate_content.call_args.kwargs["model"] == "gemini-3-pro-image"


def test_model_ids_can_be_overridden_from_the_environment(load_cip, monkeypatch):
    monkeypatch.setenv("GEMINI_FLASH_IMAGE_MODEL", "flash-next")
    monkeypatch.setenv("GEMINI_PRO_IMAGE_MODEL", "pro-next")
    assert load_cip().MODELS == {"flash": "flash-next", "pro": "pro-next"}


def test_main_exits_1_when_single_deliverable_fails(cip, monkeypatch, tmp_path):
    cip.client.models.generate_content.side_effect = RuntimeError("429 RESOURCE_EXHAUSTED")
    with pytest.raises(SystemExit) as raised:
        _run_main(cip, monkeypatch, "--deliverable", "business card", "--no-logo-prompt",
                  "--output", str(tmp_path))
    assert raised.value.code == 1


def test_main_exits_1_when_every_deliverable_in_a_set_fails(cip, monkeypatch, tmp_path):
    cip.client.models.generate_content.side_effect = RuntimeError("429 RESOURCE_EXHAUSTED")
    with pytest.raises(SystemExit) as raised:
        _run_main(cip, monkeypatch, "--deliverables", "business card,letterhead",
                  "--no-logo-prompt", "--output", str(tmp_path))
    assert raised.value.code == 1


def test_main_exits_0_when_part_of_a_set_is_generated(cip, monkeypatch, tmp_path):
    cip.client.models.generate_content.side_effect = [
        RuntimeError("429 RESOURCE_EXHAUSTED"),
        _image_response("image/png", PNG),
    ]
    _run_main(cip, monkeypatch, "--deliverables", "business card,letterhead",
              "--no-logo-prompt", "--output", str(tmp_path))
    assert len(list(tmp_path.glob("*.png"))) == 1


def test_main_prompt_only_exits_0(cip, monkeypatch):
    _run_main(cip, monkeypatch, "--deliverable", "business card", "--prompt-only")
    cip.client.models.generate_content.assert_not_called()
