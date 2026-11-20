from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from PIL import Image, ImageSequence

from frames import FRAME_COUNT, FRAME_DELAY_MS, SIZE, export_gif, new_frames, render_frame


class FrameTests(TestCase):
    def test_guide_lies_beneath_ink_without_changing_the_masks(self):
        guide, frame, *_ = new_frames()
        guide.putpixel((1, 1), 255)
        guide.putpixel((2, 2), 255)
        frame.putpixel((2, 2), 255)
        guide_before = guide.tobytes()
        frame_before = frame.tobytes()

        editor_view = render_frame(frame, guide)

        self.assertEqual(editor_view.getpixel((0, 0)), 255)
        self.assertEqual(editor_view.getpixel((1, 1)), 192)
        self.assertEqual(editor_view.getpixel((2, 2)), 0)
        self.assertEqual(guide.tobytes(), guide_before)
        self.assertEqual(frame.tobytes(), frame_before)

    def test_gif_preserves_artwork_and_blank_slots(self):
        frames = new_frames()
        frames[0].putpixel((1, 1), 255)
        frames[1].putpixel((1, 1), 255)
        frames[1].putpixel((2, 2), 255)
        frames[4].putpixel((4, 4), 255)
        frames[5].putpixel((5, 5), 255)

        self.assertEqual(render_frame(frames[2], frames[1]).getpixel((1, 1)), 192)

        with TemporaryDirectory() as folder:
            destination = Path(folder) / "flipbook.gif"
            export_gif(frames, destination)
            with Image.open(destination) as gif:
                self.assertEqual(gif.size, (SIZE, SIZE))
                self.assertEqual(gif.info["loop"], 0)
                decoded_slots = []
                for frame in ImageSequence.Iterator(gif):
                    # Pillow may merge adjacent identical frames into a longer hold.
                    slots, remainder = divmod(frame.info["duration"], FRAME_DELAY_MS)
                    self.assertEqual(remainder, 0)
                    decoded_slots.extend([frame.convert("RGB").tobytes()] * slots)

        self.assertEqual(len(decoded_slots), FRAME_COUNT)
        self.assertEqual(decoded_slots[2], bytes([255]) * (SIZE * SIZE * 3))
        expected_slots = [render_frame(frame).convert("RGB").tobytes() for frame in frames]
        self.assertEqual(decoded_slots, expected_slots)

    def test_failed_export_preserves_an_existing_file(self):
        def fail_to_encode(_image, output, **_options):
            output.write(b"partial GIF")
            raise OSError("encoding failed")

        with TemporaryDirectory() as folder:
            destination = Path(folder) / "flipbook.gif"
            destination.write_bytes(b"existing GIF")
            with patch.object(Image.Image, "save", autospec=True, side_effect=fail_to_encode):
                with self.assertRaisesRegex(OSError, "encoding failed"):
                    export_gif(new_frames(), destination)
            self.assertEqual(destination.read_bytes(), b"existing GIF")
            self.assertEqual(list(destination.parent.iterdir()), [destination])
