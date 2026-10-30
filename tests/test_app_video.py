import ast
from pathlib import Path

import pytest
from PIL import Image, ImageFilter, ImageOps


def _helpers():
    path = Path(__file__).parent.parent / "app.py"
    tree = ast.parse(path.read_text())
    names = {"video_frame_size", "normalize_video_image"}
    module = ast.Module(
        body=[node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names],
        type_ignores=[],
    )
    namespace = {"Image": Image, "ImageFilter": ImageFilter, "ImageOps": ImageOps}
    exec(compile(module, str(path), "exec"), namespace)
    return namespace


def test_auto_size_uses_exif_orientation(tmp_path):
    source = tmp_path / "rotated.jpg"
    exif = Image.Exif()
    exif[274] = 6
    Image.new("RGB", (120, 80), "red").save(source, exif=exif)
    size = _helpers()["video_frame_size"]
    assert size(source, "Auto", "720p") == (720, 1080)
    assert size(source, "16:9", "1080p") == (1920, 1080)
    assert size(source, "4:3", "720p") == (960, 720)


@pytest.mark.parametrize("fitting", ["Fit (No Crop)", "Fill (Crop)", "Blurred Background"])
def test_mixed_shapes_share_frame_and_fit_preserves_edges(tmp_path, fitting):
    normalize = _helpers()["normalize_video_image"]
    for index, dimensions in enumerate([(40, 80), (80, 40), (61, 61)]):
        source = tmp_path / f"{index}.png"
        image = Image.new("RGB", dimensions, "red")
        image.paste("blue", (0, 0, dimensions[0], 2))
        image.save(source)
        frame = normalize(source, (120, 120), fitting)
        assert frame.size == (120, 120)
        assert frame.mode == "RGB"
        assert frame.getpixel((60, 60)) == (255, 0, 0)
        if fitting == "Fit (No Crop)":
            assert frame.getpixel((0, 0)) == (255, 255, 255) or dimensions[0] == dimensions[1]
            assert any(blue > 200 and red < 30 for red, green, blue in frame.getdata())
        elif fitting == "Fill (Crop)":
            assert frame.getpixel((0, 119)) == (255, 0, 0)


def test_transparency_becomes_white(tmp_path):
    source = tmp_path / "transparent.png"
    Image.new("RGBA", (40, 40), (0, 0, 0, 0)).save(source)
    frame = _helpers()["normalize_video_image"](source, (120, 120), "Fit (No Crop)")
    assert frame.getextrema() == ((255, 255), (255, 255), (255, 255))


def test_mp4_mixed_images_keep_order_duration_and_white_padding(tmp_path):
    moviepy = pytest.importorskip("moviepy")
    if hasattr(moviepy, "ImageClip"):
        ImageClip = moviepy.ImageClip
        concatenate = moviepy.concatenate_videoclips
        VideoFileClip = moviepy.VideoFileClip
    else:
        from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips as concatenate

    normalize = _helpers()["normalize_video_image"]
    clips = []
    final = None
    output = tmp_path / "result.mp4"
    try:
        for index, (dimensions, color) in enumerate([((40, 80), "red"), ((80, 40), "blue")]):
            source = tmp_path / f"source_{index}.png"
            normalized = tmp_path / f"frame_{index}.png"
            Image.new("RGB", dimensions, color).save(source)
            normalize(source, (120, 120), "Fit (No Crop)").save(normalized)
            clip = ImageClip(str(normalized))
            clip = clip.with_duration(1) if hasattr(clip, "with_duration") else clip.set_duration(1)
            clips.append(clip)
        final = concatenate(clips, method="chain")
        final.write_videofile(str(output), fps=8, codec="libx264", audio=False,
                             ffmpeg_params=["-pix_fmt", "yuv420p"], logger=None)
        with VideoFileClip(str(output)) as video:
            assert tuple(video.size) == (120, 120)
            assert abs(video.duration - 2) < 0.05
            first = video.get_frame(0.5)
            second = video.get_frame(1.5)
            assert first[60, 60, 0] > 240
            assert second[60, 60, 2] > 240
            assert first[60, 0].min() > 240
            assert second[0, 60].min() > 240
    finally:
        if final is not None:
            final.close()
        for clip in clips:
            clip.close()
