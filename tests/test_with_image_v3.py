import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from src import with_image_v3


class _FakeHandler:
    def get(self):
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

    class FakeClient:
        def __init__(self, key):
            captured["key"] = key

        def submit(self, model_name, arguments):
            captured["model_name"] = model_name
            captured["arguments"] = arguments
            return _FakeHandler()

    monkeypatch.setattr(with_image_v3.fal_client, "SyncClient", FakeClient)
    monkeypatch.setattr(with_image_v3.requests, "get", lambda url: _FakeResponse())
    return captured


def test_remix_images_appends_aspect_ratio_instruction(monkeypatch, tmp_path):
    captured = _capture_submit(monkeypatch)

    with_image_v3.remix_images(
        image_paths=[],
        prompt="Create a product photo.",
        MODEL_NAME="openai/gpt-image-2",
        output_dir=str(tmp_path),
        api_key="test-key",
        aspect_ratio="1:1",
    )

    assert captured["arguments"]["prompt"] == (
        "Create a product photo. The final image must use a 1:1 aspect ratio."
    )


def test_remix_images_does_not_append_aspect_ratio_instruction_for_auto(
    monkeypatch, tmp_path
):
    captured = _capture_submit(monkeypatch)

    with_image_v3.remix_images(
        image_paths=[],
        prompt="Create a product photo.",
        MODEL_NAME="openai/gpt-image-2",
        output_dir=str(tmp_path),
        api_key="test-key",
        aspect_ratio="auto",
    )

    assert captured["arguments"]["prompt"] == "Create a product photo."


def test_remix_images_appends_aspect_ratio_instruction_to_default_prompt(
    monkeypatch, tmp_path
):
    captured = _capture_submit(monkeypatch)

    with_image_v3.remix_images(
        image_paths=[],
        prompt=None,
        MODEL_NAME="openai/gpt-image-2",
        output_dir=str(tmp_path),
        api_key="test-key",
        aspect_ratio="16:9",
    )

    assert captured["arguments"]["prompt"].endswith(
        "The final image must use a 16:9 aspect ratio."
    )
