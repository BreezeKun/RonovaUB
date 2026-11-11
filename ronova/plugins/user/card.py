import asyncio
import os
from io import BytesIO

import curl_cffi
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Message

from config import LAST_FM_API

API_KEY = LAST_FM_API
LASTFM_USER = "BreezeMeowMeow"

BG_PATH = "/assest/bg.jpg"      # your background (kept exactly as you wrote it)
FONT_PATH = "/assest/font.ttf"       # optional custom font, falls back automatically
CARD_SIZE = (1280, 720)              # PC / 16:9 dimension

# Last.fm's default "no artwork" placeholder hash
LASTFM_PLACEHOLDER = "2a96cbd8b46e442fc41c2b86b821562f"


# ---------------------------------------------------------------- helpers
def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        FONT_PATH,
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    """Trim text with an ellipsis so it fits max_width."""
    if draw.textlength(text, font=font) <= max_width:
        return text
    while text and draw.textlength(text + "...", font=font) > max_width:
        text = text[:-1]
    return text.rstrip() + "..."


def cover_resize(img: Image.Image, size) -> Image.Image:
    """Resize + center-crop to fully cover size (like CSS background-size: cover)."""
    tw, th = size
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    img = img.resize((int(iw * scale) + 1, int(ih * scale) + 1), Image.LANCZOS)
    left = (img.width - tw) // 2
    top = (img.height - th) // 2
    return img.crop((left, top, left + tw, top + th))


def rounded(img: Image.Image, radius: int) -> Image.Image:
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *img.size), radius, fill=255)
    img.putalpha(mask)
    return img


def circle(img: Image.Image, size: int) -> Image.Image:
    img = cover_resize(img.convert("RGBA"), (size, size))
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * 4, size * 4), fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    img.putalpha(mask)
    return img


# ---------------------------------------------------------------- data
def _get_track() -> dict:
    r = curl_cffi.get(
        "https://ws.audioscrobbler.com/2.0/",
        params={
            "method": "user.getRecentTracks",
            "user": LASTFM_USER,
            "api_key": API_KEY,
            "format": "json",
            "limit": 1,
        },
        impersonate="chrome",
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()

    if "error" in data:
        raise RuntimeError(f"Last.fm API Error: {data.get('message')}")

    tracks = data["recenttracks"]["track"]
    if not tracks:
        raise RuntimeError("No recent tracks found.")

    track = tracks[0] if isinstance(tracks, list) else tracks

    art_url = next(
        (
            i["#text"]
            for i in track.get("image", [])
            if i.get("size") == "extralarge" and i.get("#text")
        ),
        None,
    )
    if art_url and LASTFM_PLACEHOLDER in art_url:
        art_url = None

    return {
        "name": track["name"],
        "artist": track["artist"]["#text"],
        "album": track.get("album", {}).get("#text") or "Unknown Album",
        "art_url": art_url,
        "now_playing": track.get("@attr", {}).get("nowplaying") == "true",
    }


def _download_image(url: str):
    try:
        r = curl_cffi.get(url, impersonate="chrome", timeout=15)
        r.raise_for_status()
        return Image.open(BytesIO(r.content)).convert("RGB")
    except Exception:
        return None


# ---------------------------------------------------------------- render
def render_card(info: dict, user_name: str, art, pfp) -> BytesIO:
    W, H = CARD_SIZE

    # --- background (blurred + darkened so text stays readable)
    try:
        bg = Image.open(BG_PATH).convert("RGB")
    except Exception:
        bg = Image.new("RGB", CARD_SIZE, (24, 24, 32))
    bg = cover_resize(bg, CARD_SIZE).filter(ImageFilter.GaussianBlur(6))
    bg = ImageEnhance.Brightness(bg).enhance(0.55).convert("RGBA")

    # --- translucent glass panel
    panel = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle(
        (60, 60, W - 60, H - 60), radius=40,
        fill=(0, 0, 0, 120), outline=(255, 255, 255, 50), width=2,
    )
    card = Image.alpha_composite(bg, panel)

    # --- album art (left)
    ART = 440
    ax, ay = 110, (H - ART) // 2
    if art:
        art_img = rounded(cover_resize(art, (ART, ART)), 28)
    else:
        art_img = Image.new("RGBA", (ART, ART), (45, 45, 55, 255))
        d = ImageDraw.Draw(art_img)
        f = load_font(40, True)
        d.text((ART // 2, ART // 2), "No Artwork", font=f,
               fill=(150, 150, 160), anchor="mm")
        art_img = rounded(art_img, 28)

    # soft shadow
    shadow = Image.new("RGBA", CARD_SIZE, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (ax, ay + 12, ax + ART, ay + ART + 12), 28, fill=(0, 0, 0, 160))
    card = Image.alpha_composite(card, shadow.filter(ImageFilter.GaussianBlur(16)))
    card.paste(art_img, (ax, ay), art_img)

    draw = ImageDraw.Draw(card)
    tx = ax + ART + 60                 # text start x
    max_w = (W - 110) - tx             # text max width

    # --- header: pfp (optional) + "<name> is listening to..."
    header_y = 120
    PFP = 90
    text_x = tx
    if pfp:
        p = circle(pfp, PFP)
        ring = Image.new("RGBA", (PFP + 8, PFP + 8), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((0, 0, PFP + 7, PFP + 7),
                                     outline=(255, 255, 255, 200), width=3)
        card.paste(ring, (tx - 4, header_y - 4), ring)
        card.paste(p, (tx, header_y), p)
        text_x = tx + PFP + 24

    name_font = load_font(34, True)
    sub_font = load_font(26)
    hw = (W - 110) - text_x
    draw.text((text_x, header_y + 8),
              fit_text(draw, user_name, name_font, hw),
              font=name_font, fill=(255, 255, 255))
    draw.text((text_x, header_y + 54),
              "is listening to..." if info["now_playing"] else "last listened to...",
              font=sub_font, fill=(190, 190, 200))

    # --- divider
    draw.line((tx, 250, W - 110, 250), fill=(255, 255, 255, 60), width=2)

    # --- track details
    title_font = load_font(52, True)
    artist_font = load_font(34)
    album_font = load_font(28)

    draw.text((tx, 285), fit_text(draw, info["name"], title_font, max_w),
              font=title_font, fill=(255, 255, 255))
    draw.text((tx, 360), fit_text(draw, info["artist"], artist_font, max_w),
              font=artist_font, fill=(230, 230, 240))
    draw.text((tx, 410), fit_text(draw, info["album"], album_font, max_w),
              font=album_font, fill=(160, 160, 175))

    # --- status pill
    label = "NOW PLAYING" if info["now_playing"] else "RECENTLY PLAYED"
    pill_font = load_font(22, True)
    lw = int(draw.textlength(label, font=pill_font))
    py = 520
    color = (29, 185, 84) if info["now_playing"] else (120, 120, 135)
    draw.rounded_rectangle((tx, py, tx + lw + 60, py + 48), 24, fill=color)
    draw.ellipse((tx + 18, py + 17, tx + 32, py + 31), fill=(255, 255, 255))
    draw.text((tx + 44, py + 24), label, font=pill_font,
              fill=(255, 255, 255), anchor="lm")

    out = BytesIO()
    out.name = "card.png"
    card.convert("RGB").save(out, "PNG")
    out.seek(0)
    return out


# ---------------------------------------------------------------- command
@Client.on_message(filters.command("createcard") & filters.me)
async def create_card(c: Client, m: Message):
    status = await m.reply_text("🎨 Creating card...")

    try:
        info = await asyncio.to_thread(_get_track)

        art = None
        if info["art_url"]:
            art = await asyncio.to_thread(_download_image, info["art_url"])

        # Telegram profile picture (skipped if the user has none)
        pfp = None
        user = m.from_user
        if user and user.photo:
            try:
                data = await c.download_media(user.photo.big_file_id, in_memory=True)
                pfp = Image.open(data).convert("RGB")
            except Exception as e:
                print("PFP error:", repr(e))

        user_name = (user.first_name if user else None) or LASTFM_USER

        card = await asyncio.to_thread(render_card, info, user_name, art, pfp)

        caption = f"🎧 <b>{info['name']}</b> — {info['artist']}"
        await m.reply_photo(photo=card, caption=caption)
        await status.delete()

    except Exception as e:
        print("Card ERROR:", repr(e))
        await status.edit_text(f"❌ Error creating card:\n{e}")