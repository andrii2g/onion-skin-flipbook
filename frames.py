from collections.abc import Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image


SIZE = 32
FRAME_COUNT = 6
FRAME_DELAY_MS = 100

_PALETTE = [255, 255, 255, 0, 0, 0]


def new_frames() -> list[Image.Image]:
    """Create six independent one-bit ink masks."""
    return [Image.new("1", (SIZE, SIZE)) for _ in range(FRAME_COUNT)]


def render_frame(frame: Image.Image, guide: Image.Image | None = None) -> Image.Image:
    """Render the ink over white, with an optional gray guide beneath it."""
    image = Image.new("L", (SIZE, SIZE), 255)
    if guide is not None:
        image.paste(192, mask=guide)
    image.paste(0, mask=frame)
    return image


def export_gif(frames: Sequence[Image.Image], destination: str | Path) -> None:
    """Export the clean ink masks and replace the destination on success."""
    artwork = []
    for frame in frames:
        image = Image.new("P", (SIZE, SIZE), 0)
        image.putpalette(_PALETTE)
        image.paste(1, mask=frame)
        artwork.append(image)

    destination = Path(destination)
    temporary = NamedTemporaryFile(dir=destination.parent, delete=False)
    temporary_path = Path(temporary.name)
    try:
        with temporary:
            artwork[0].save(
                temporary,
                format="GIF",
                save_all=True,
                append_images=artwork[1:],
                duration=FRAME_DELAY_MS,
                loop=0,
                disposal=1,
                optimize=False,
            )
        temporary_path.replace(destination)
    finally:
        temporary_path.unlink(missing_ok=True)
