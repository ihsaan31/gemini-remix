import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import with_image_v3_async


class _FakeAsyncHandler:
    async def get(self):
        return {
            "images": [
                {
                    "url": "https://example.com/generated.png",
                    "content_type": "image/png",
                }
            ]
        }


class _FakeResponse:
    content = b"generated image"

    def raise_for_status(self):
        return None


def _capture_submit(monkeypatch):
    captured = {}

    class FakeAsyncClient:
        def __init__(self, key):
            captured["key"] = key

        async def submit(self, model_name, arguments):
            captured["model_name"] = model_name
            captured["arguments"] = arguments
            return _FakeAsyncHandler()

    monkeypatch.setattr(with_image_v3_async.fal_client, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(with_image_v3_async.requests, "get", lambda url: _FakeResponse())
    return captured


def test_remix_images_async_sends_gpt_image_2_edit_size_preset(monkeypatch, tmp_path):
    captured = _capture_submit(monkeypatch)

    with_image_v3_async.remix_images(
        image_paths=[],
        prompt="Create a product photo.",
        MODEL_NAME="openai/gpt-image-2/edit",
        output_dir=str(tmp_path),
        api_key="test-key",
        aspect_ratio="1:1",
    )

    assert captured["arguments"]["prompt"] == "Create a product photo."
    assert captured["arguments"]["image_size"] == "square_hd"


def test_remix_images_async_sends_gpt_image_2_5_size_preset(
    monkeypatch, tmp_path
):
    captured = _capture_submit(monkeypatch)

    with_image_v3_async.remix_images(
        image_paths=[],
        prompt="Create a product photo.",
        MODEL_NAME="openai/gpt-image-2.5/flare/edit",
        output_dir=str(tmp_path),
        api_key="test-key",
        aspect_ratio="1:1",
    )

    assert captured["model_name"] == "openai/gpt-image-2.5/flare/edit"
    assert captured["arguments"]["image_size"] == "square_hd"


def test_remix_images_async_sends_auto_image_size(
    monkeypatch, tmp_path
):
    captured = _capture_submit(monkeypatch)

    with_image_v3_async.remix_images(
        image_paths=[],
        prompt="Create a product photo.",
        MODEL_NAME="openai/gpt-image-2/edit",
        output_dir=str(tmp_path),
        api_key="test-key",
        aspect_ratio="auto",
    )

    assert captured["arguments"]["prompt"] == "Create a product photo."
    assert captured["arguments"]["image_size"] == "auto"


def test_remix_images_async_sends_landscape_gpt_image_2_edit_size_preset(
    monkeypatch, tmp_path
):
    captured = _capture_submit(monkeypatch)

    with_image_v3_async.remix_images(
        image_paths=[],
        prompt=None,
        MODEL_NAME="openai/gpt-image-2/edit",
        output_dir=str(tmp_path),
        api_key="test-key",
        aspect_ratio="16:9",
    )

    assert captured["arguments"]["prompt"].endswith(
        "with better lighting and depth of field."
    )
    assert captured["arguments"]["image_size"] == "landscape_16_9"


def test_remix_images_async_keeps_custom_dimensions_for_other_fal_models(
    monkeypatch, tmp_path
):
    captured = _capture_submit(monkeypatch)

    with_image_v3_async.remix_images(
        image_paths=[],
        prompt="Create a product photo.",
        MODEL_NAME="fal-ai/nano-banana-2/edit",
        output_dir=str(tmp_path),
        api_key="test-key",
        aspect_ratio="9:16",
    )

    assert captured["arguments"]["prompt"] == "Create a product photo."
    assert captured["arguments"]["image_size"] == {"width": 720, "height": 1280}
