import os
import subprocess

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Message

from config import ADMIN_ID, PREFIXES


@Client.on_message(
    filters.command("fetch", prefixes=PREFIXES) & filters.user(ADMIN_ID)
)
async def fetch(client: Client, message: Message):

    proc = subprocess.Popen(
        "fastfetch",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = proc.communicate()
    output = (stdout + "\n" + stderr).strip() or "Done."

    font_path = subprocess.check_output(
        ["fc-match", "-f", "%{file}", "monospace"],
        text=True
    ).strip()

    font = ImageFont.truetype(font_path, 14)

    lines = output.splitlines()

    padding = 15
    line_spacing = 2

    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

    bboxes = [
        dummy.textbbox((0, 0), line, font=font)
        for line in lines
    ]

    width = max(bbox[2] for bbox in bboxes) + padding * 2
    height = (
        sum(bbox[3] - bbox[1] for bbox in bboxes)
        + line_spacing * (len(lines) - 1)
        + padding * 2
    )

    image = Image.new(
        "RGBA",
        (width, height),
        (30, 30, 30, 255)
    )

    draw = ImageDraw.Draw(image)

    y = padding

    for line, bbox in zip(lines, bboxes):
        draw.text(
            (padding, y),
            line,
            font=font,
            fill=(255, 255, 255, 255)
        )

        y += bbox[3] - bbox[1] + line_spacing

    path = "fastfetch.png"

    image.save(
        path,
        format="PNG",
        optimize=True,
        compress_level=9
    )

    try:
        await message.reply_photo(path)
    finally:
        if os.path.exists(path):
            os.remove(path)