# Onion Skin Flipbook

Draw a six-frame pixel animation in a desktop editor built with Tkinter and Pillow. Each frame is a 32×32 bitmap.

## Run

Use Python 3.10 or newer with Tkinter available. Install Pillow if needed, then launch the editor from the repository folder.

```sh
python -m pip install Pillow
python flipbook.py
```

## Draw and play

- Select a frame with buttons **1–6**. On frames 2–6, the previous frame's ink appears in light gray as a drawing guide.
- Click or drag with **Pencil** to add ink or **Eraser** to clear it. Both tools work one pixel at a time.
- Select **Play** to loop the six frames at 100 ms per frame. Playback shows the artwork on white. Select **Stop** to return to editing.
- Select **Export GIF…** to save the same loop at 32×32 with black ink and an opaque white background. The GIF may combine consecutive identical frames into one longer frame while preserving the playback timing.

## Try a bounce

Draw a 5×5 ball in all six frames. Keep its center at `x = 16` and place it at the following heights, counting pixels from zero at the top left.

| Frame | 1 | 2 | 3 | 4 | 5 | 6 |
| --- | --- | --- | --- | --- | --- | --- |
| Center `y` | 11 | 13 | 19 | 29 | 19 | 13 |

Press **Play** to see how the wider spacing near the bottom makes the ball move faster there.

Then clear frame 4 while keeping the ball in frame 3. While editing frame 4, you should see a light-gray ball from frame 3. During preview and in the exported GIF, frame 4 should appear all white from 300 to 400 ms in each loop.

## Tests

```sh
python -m unittest
```
