# from pyrogram import Client, filters
# from pyrogram.types import Message, ReplyParameters

from config import PREFIXES, ADMIN_ID , TEST_SUDO
import unicodedata as un
# from ..shared import QUOTE_STATE
# from ..decorators import get_string

# QUOTLY_BOT: str = "QuotLyBot"

# QUOTE_COMMAND:list[str] = ["q"]

# def quote_state(
#         status:bool = False, 
#         user_chat_id:int | None = None, 
#         user_message_id: int | None = None
#         ) -> None:
#     QUOTE_STATE.status = status
#     QUOTE_STATE.user_chat_id = user_chat_id
#     QUOTE_STATE.user_message_id = user_message_id

# @Client.on_message(filters.user(QUOTLY_BOT) & filters.sticker & filters.bot, group= 0)
# async def get_quote(c:Client, m:Message):
#     if  QUOTE_STATE.status and m.sticker:
#         await c.send_sticker(
#             chat_id = QUOTE_STATE.user_chat_id, 
#             sticker = m.sticker.file_id, 
#             reply_parameters= ReplyParameters(message_id = QUOTE_STATE.user_message_id)
#             )
#         quote_state()
        

# @Client.on_message(filters.command(QUOTE_COMMAND, prefixes=PREFIXES) & filters.user(ADMIN_ID), group= 2)
# @get_string("quote")
# async def quote(c:Client, m:Message):
#     """
#     Get quotes of your message or replied message
#     Usage: q [message] or reply to message with q
#     """
    
#     rm = m.reply_to_message
#     command = m.command[0]

#     if command == "q":
#         if rm:
#             await c.forward_messages(QUOTLY_BOT, m.chat.id, rm.id)
#             quote_state(status=True, user_chat_id = m.chat.id, user_message_id = m.id)
#         elif len(m.command) > 1:
#             await c.send_message(QUOTLY_BOT, " ".join(m.command[1:]))
#             quote_state(status=True, user_chat_id = m.chat.id, user_message_id = m.id)
#         else:
#             await m.reply("usage: q <text> or q with replying to a message")


import asyncio
import io
import re
import textwrap
import traceback
from dataclasses import dataclass
 
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, errors, filters, types
from pyrogram.types import Message
 
from ..decorators import get_string
from config import PREFIXES

modules_help = {}
prefix = PREFIXES
 
QUOTLY_BOT = "QuotLyBot"
MAX_QBOT_MESSAGES = 15
DEFAULT_BG_URL = "https://graph.org/file/1fd74fa4a4dbf1655f3ec.jpg"
 
# First font that loads is used. Put your own fonts first if you have them.
FONT_CANDIDATES = [
    "./temp/ArialUnicodeMS.ttf",
    "./temp/Quivira.otf",
    "DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
 
BOLD_FONT_CANDIDATES = [
    "./temp/Roboto-Medium.ttf",
    "./temp/ArialUnicodeMS.ttf",
    "DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
 
BUBBLE_COLOR = (22, 35, 48, 255)
NAME_COLORS = [
    (255, 81, 106),
    (255, 136, 94),
    (149, 92, 219),
    (83, 185, 124),
    (91, 182, 204),
    (59, 143, 239),
    (217, 85, 116),
]
MAX_QUOTE_LINES = 40
 
EMOJI_RE = re.compile(
    "["
    "\U0001f600-\U0001f64f"
    "\U0001f300-\U0001f5ff"
    "\U0001f680-\U0001f6ff"
    "\U0001f1e0-\U0001f1ff"
    "\U0001f900-\U0001f9ff"
    "\U0001fa70-\U0001faff"
    "\U00002600-\U000027bf"
    "\U0000fe0f\U0000200d"
    "]+",
    flags=re.UNICODE,
)
FLAG_RE = re.compile(r"(?<!\S)-([bs])(?!\S)")
 
# ----------------------------------------------------------------- helpers
 
 
def format_exc(e: Exception, suffix="") -> str:
    traceback.print_exc()
    err = traceback.format_exc()
    if isinstance(e, errors.RPCError):
        return (
            f"<b>Telegram API error!</b>\n"
            f"<code>[{e.CODE} {e.ID or e.NAME}] — {e.MESSAGE.format(value=e.value)}</code>\n\n<b>{suffix}</b>"
        )
    return f"<b>Error!</b>\n<code>{err}</code>"
 
 
def _get_args(message: Message) -> str:
    text = message.text or message.caption or ""
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""
 
 
def _parse_flags(args: str) -> tuple[set, str]:
    """Pull standalone -b / -s flags out of the text (so 'well-being' is safe)."""
    flags = set(FLAG_RE.findall(args))
    return flags, FLAG_RE.sub("", args).strip()
 
 
def _display_name(entity) -> str:
    if isinstance(entity, types.User):
        name = entity.first_name or ""
        if entity.last_name:
            name += " " + entity.last_name
        return name
    return getattr(entity, "title", "") or ""
 
 
def _get_font(size: int, bold: bool = False):
    for path in BOLD_FONT_CANDIDATES if bold else FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()
 
 
def get_warp_length(width: float) -> int:
    return int((20.0 / 1024.0) * width)
 
 
async def _download_bytes(client: Client, file_id: str) -> bytes | None:
    try:
        buf = await client.download_media(file_id, in_memory=True)
        return bytes(buf.getbuffer())
    except Exception:
        return None
 
 
async def _download_default_bg() -> bytes | None:
    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(DEFAULT_BG_URL) as resp,
        ):
            if resp.status == 200:
                return await resp.read()
    except Exception:
        pass
    return None
 
 
async def _get_background(client: Client, reply: Message | None):
    """Return (background image bytes or None, entity crreplyed in the picture)."""
    me = await client.get_me()
 
    if reply:
        file_id = None
        if reply.photo:
            file_id = reply.photo.file_id
        elif reply.sticker and not (reply.sticker.is_animated or reply.sticker.is_video):
            file_id = reply.sticker.file_id
 
        if file_id:
            data = await _download_bytes(client, file_id)
            if data is None:
                raise RuntimeError("Unable to extract image from the replied message.")
            return data, me
 
        entity = reply.from_user or reply.sender_chat or me
    else:
        entity = me
 
    data = None
    if entity.photo:
        data = await _download_bytes(client, entity.photo.big_file_id)
    if data is None:
        data = await _download_default_bg()
    return data, entity
 
 
def _make_quote_pic(
    bg: bytes | None, text: str, crreply: str | None, black: bool, as_sticker: bool
) -> io.BytesIO:
    img = Image.open(io.BytesIO(bg)) if bg else Image.new("RGB", (1024, 1024), (35, 35, 45))
    if black:
        img = img.convert("L")
    img = img.convert("RGBA").resize((1024, 1024))
    w, h = img.size
 
    # dark translucent panel
    nw, nh = 20 * (w // 100), 20 * (h // 100)
    panel = Image.new("RGBA", (w - nw, h - nh), (0, 0, 0, 150))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(panel, (nw // 2, nh // 2))
    img = Image.alpha_composite(img, layer)
 
    draw = ImageDraw.Draw(img)
 
    # quote text, centered
    font = _get_font(50)
    l, t, r, b = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    tw, th = r - l, b - t
    draw.multiline_text(
        ((w - tw) // 2 - l, (h - th) // 2 - t),
        text,
        font=font,
        fill="#ffffff",
        align="center",
    )
 
    # "by <name>" crreply, bottom right
    if crreply:
        crreply_text = "\n".join(
            textwrap.wrap(f"by {crreply}", get_warp_length(w / 2.5)) or [f"by {crreply}"]
        )
        l, t, r, b = draw.multiline_textbbox((0, 0), crreply_text, font=font, align="left")
        cw, ch = r - l, b - t
        x = min((w - nw + cw) / 1.6, w - nw // 2 - cw)
        y = h - nh - ch
        draw.multiline_text(
            (x - l, y - t), crreply_text, font=font, fill="#ffffff", align="left"
        )
 
    out = io.BytesIO()
    if as_sticker:
        out.name = "qpic.webp"
        img.save(out, "WEBP")
    else:
        out.name = "qpic.png"
        img.save(out, "PNG")
    out.seek(0)
    return out
 
 
# ------------------------------------------------------------------- qpic
 
 
@Client.on_message(filters.command("qpic", prefix) & filters.user(TEST_SUDO))
@get_string("quote")
async def qpic_cmd(client: Client, message: Message):
    """
    qpic [-b] [-s] [text/reply]": "Make a quote picture using the replied user's
    profile photo (or the replied photo/sticker) as background.\n
    -b — black and white, -s — send as sticker
    q [reply]*": "Make a sticker quote of the replied message
    rq [reply]*": "Same as q, but also include the message it replied to
    fq [reply] [@user/id] [text]": "Fake quote: give @user/id (or reply to someone)
    and the text they 'said'. No text = replied message's text
    frq [reply]* [@user/id] [text]": "Same as fq, but the replied message is shown
    as the reply bubble
    qbot [reply] [count 1-15] / [text]": f"Make a quote sticker using @{QUOTLY_BOT}
    """
    reply = message.reply_to_message
    reply_to = reply.id if reply else None
    ph = await client.send_message(message.chat.id, "Please wait", reply_to_message_id=reply_to)
    flags, input_str = _parse_flags(_get_args(message))
 
    if input_str:
        text = input_str
    elif reply and (reply.text or reply.caption):
        text = reply.text or reply.caption
    else:
        return await ph.edit(
            "<b>Provide input along with cmd or reply to a text message.</b>"
        )
 
    text = EMOJI_RE.sub("", text).strip()
    if not text:
        return await ph.edit("<b>Nothing left to render after removing emojis.</b>")
 
    await ph.edit("<b>Making quote pic...</b>")
 
    try:
        bg, entity = await _get_background(client, reply)
        wrapped = "\n".join(textwrap.wrap(text, 25))
        wrapped = f"“{wrapped}”"
        crreply = _display_name(entity) or None
 
        output = await asyncio.to_thread(
            _make_quote_pic, bg, wrapped, crreply, "b" in flags, "s" in flags
        )
        if "s" in flags:
            await client.send_sticker(
                message.chat.id, output, reply_to_message_id=reply_to
            )
        else:
            await client.send_photo(
                message.chat.id, output, reply_to_message_id=reply_to
            )
    except Exception as e:
        return await ph.edit(format_exc(e))
 
    await ph.delete()
 
 
# ------------------------------------------------- q / rq / fq / frq
 
 
@dataclass
class QuoteUser:
    id: int
    name: str
    photo_id: str | None = None
 
 
def _quote_user_from_user(user: types.User) -> QuoteUser:
    photo = getattr(user, "photo", None)
    return QuoteUser(
        user.id, _display_name(user) or "Unknown", photo.big_file_id if photo else None
    )
 
 
def _quote_user_from_chat(chat: types.Chat) -> QuoteUser:
    photo = getattr(chat, "photo", None)
    return QuoteUser(
        chat.id, getattr(chat, "title", None) or "Unknown", photo.big_file_id if photo else None
    )
 
 
def _message_author(msg: Message) -> QuoteUser:
    # forwarded messages: crreply the original sender
    origin = getattr(msg, "forward_origin", None)
    if isinstance(origin, types.MessageOriginUser):
        return _quote_user_from_user(origin.sender_user)
    if isinstance(origin, types.MessageOriginHiddenUser):
        return QuoteUser(0, origin.sender_user_name or "Unknown")
    if isinstance(origin, types.MessageOriginChat):
        return _quote_user_from_chat(origin.sender_chat)
    channel_cls = getattr(types, "MessageOriginChannel", None)
    if channel_cls and isinstance(origin, channel_cls):
        return _quote_user_from_chat(origin.chat)
 
    if msg.from_user:
        return _quote_user_from_user(msg.from_user)
    if msg.sender_chat:
        return _quote_user_from_chat(msg.sender_chat)
    return QuoteUser(0, "Unknown")
 
 
def _preview_text(msg: Message) -> str:
    text = msg.text or msg.caption
    if text:
        return text
    if msg.photo:
        return "Photo"
    if msg.sticker:
        return "Sticker"
    if msg.animation:
        return "GIF"
    if msg.video or msg.video_note:
        return "Video"
    if msg.voice:
        return "Voice message"
    if msg.audio:
        return "Audio"
    if msg.document:
        return "File"
    if msg.poll:
        return "Poll"
    if msg.location or msg.venue:
        return "Location"
    if msg.contact:
        return "Contact"
    return "Message"
 
 
def _looks_like_user_ref(arg: str) -> bool:
    return arg.startswith("@") or (arg.isdigit() and len(arg) >= 5)
 
 
def _name_color(user: QuoteUser) -> tuple:
    key = user.id or sum(map(ord, user.name))
    return NAME_COLORS[abs(key) % len(NAME_COLORS)]
 
 
def _line_height(font) -> int:
    return int(font.getbbox("Ag")[3] * 1.2)
 
 
def _truncate(draw, text: str, font, max_w: float) -> str:
    text = " ".join(text.split())
    if draw.textlength(text, font=font) <= max_w:
        return text
    while text and draw.textlength(text + "…", font=font) > max_w:
        text = text[:-1]
    return text + "…"
 
 
def _wrap_pixels(draw, text: str, font, max_w: float) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split(" "):
            candidate = f"{line} {word}" if line else word
            if draw.textlength(candidate, font=font) <= max_w:
                line = candidate
                continue
            if line:
                lines.append(line)
            # a single word wider than the bubble: break it by characters
            while len(word) > 1 and draw.textlength(word, font=font) > max_w:
                cut = len(word)
                while cut > 1 and draw.textlength(word[:cut], font=font) > max_w:
                    cut -= 1
                lines.append(word[:cut])
                word = word[cut:]
            line = word
        lines.append(line)
 
    if len(lines) > MAX_QUOTE_LINES:
        lines = lines[:MAX_QUOTE_LINES]
        lines[-1] = lines[-1].rstrip() + "…"
    return lines
 
 
def _make_avatar(data: bytes | None, user: QuoteUser, size: int) -> Image.Image:
    av = None
    if data:
        try:
            av = (
                Image.open(io.BytesIO(data))
                .convert("RGBA")
                .resize((size, size), Image.Resampling.LANCZOS)
            )
        except Exception:
            av = None
 
    if av is None:
        av = Image.new("RGBA", (size, size), _name_color(user) + (255,))
        d = ImageDraw.Draw(av)
        font = _get_font(size // 2, True)
        ch = (user.name[:1] or "?").upper()
        l, t, r, b = d.textbbox((0, 0), ch, font=font)
        d.text(
            ((size - (r - l)) // 2 - l, (size - (b - t)) // 2 - t),
            ch,
            font=font,
            fill="white",
        )
 
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(av, (0, 0), mask)
    return out
 
 
def _render_quote_sticker(
    text: str,
    user: QuoteUser,
    avatar: bytes | None,
    reply_user: QuoteUser | None = None,
    reply_text: str = "",
) -> io.BytesIO:
    pad, av_size, gap, margin, max_w = 26, 96, 14, 8, 560
 
    f_text = _get_font(34)
    f_name = _get_font(30, True)
    f_rname = _get_font(26, True)
    f_small = _get_font(26)
 
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = _wrap_pixels(probe, text, f_text, max_w)
    name_text = _truncate(probe, user.name, f_name, max_w)
 
    content_w = max(
        probe.textlength(name_text, font=f_name),
        *(probe.textlength(line, font=f_text) for line in lines),
    )
 
    r_name = r_text = ""
    reply_h = 0
    if reply_user:
        r_name = _truncate(probe, reply_user.name, f_rname, max_w - 20)
        r_text = _truncate(probe, reply_text, f_small, max_w - 20)
        reply_h = _line_height(f_rname) + _line_height(f_small)
        content_w = max(
            content_w,
            20 + probe.textlength(r_name, font=f_rname),
            20 + probe.textlength(r_text, font=f_small),
        )
 
    name_h = _line_height(f_name)
    text_h = len(lines) * _line_height(f_text)
    bubble_w = int(content_w) + 2 * pad
    bubble_h = pad + name_h + 8 + (reply_h + 12 if reply_user else 0) + text_h + pad
 
    width = margin * 2 + av_size + gap + bubble_w
    height = margin * 2 + max(bubble_h, av_size)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
 
    bx, by = margin + av_size + gap, height - margin - bubble_h
    draw.rounded_rectangle(
        (bx, by, bx + bubble_w, by + bubble_h), radius=30, fill=BUBBLE_COLOR
    )
 
    avatar_img = _make_avatar(avatar, user, av_size)
    img.paste(avatar_img, (margin, height - margin - av_size), avatar_img)
 
    x, y = bx + pad, by + pad
    draw.text((x, y), name_text, font=f_name, fill=_name_color(user))
    y += name_h + 8
 
    if reply_user:
        rcolor = _name_color(reply_user)
        draw.rounded_rectangle((x, y, x + 5, y + reply_h), radius=2, fill=rcolor)
        draw.text((x + 20, y), r_name, font=f_rname, fill=rcolor)
        draw.text(
            (x + 20, y + _line_height(f_rname)),
            r_text,
            font=f_small,
            fill=(180, 190, 200),
        )
        y += reply_h + 12
 
    for line in lines:
        draw.text((x, y), line, font=f_text, fill="white")
        y += _line_height(f_text)
 
    # telegram stickers: longest side must be 512
    scale = 512 / max(width, height)
    img = img.resize(
        (max(1, round(width * scale)), max(1, round(height * scale))),
        Image.Resampling.LANCZOS,
    )
    out = io.BytesIO()
    out.name = "sticker.webp"
    img.save(out, "WEBP")
    out.seek(0)
    return out
 
 
@Client.on_message(filters.command(["q", "rq", "fq", "frq"], prefix) & filters.user(TEST_SUDO))
async def stickerchat_cmd(client: Client, message: Message):
    cmd = message.command[0].lower()
    reply = message.reply_to_message

    reply_to = reply.id if reply else None
    ph = await client.send_message(message.chat.id, "Please wait", reply_to_message_id=reply_to)
 
    if cmd in ("q", "rq", "frq"):
        if not reply:
            return await ph.edit("<b>I can't quote the message. Reply to a message</b>")
        if reply.photo or reply.video_note or reply.animation:
            return await ph.edit("<b>Replied message is not supported now</b>")
 
    if cmd in ("q", "rq"):
        user = _message_author(reply)
        text = reply.text or reply.caption or ""
    else:  # fq / frq: fake quote with a given user
        args = _get_args(message)
        user = None
        text = args
        first = args.split(maxsplit=1)[0] if args else ""
        if first and _looks_like_user_ref(first):
            try:
                entity = await client.get_users(
                    first if first.startswith("@") else int(first)
                )
                user = _quote_user_from_user(entity)
                text = args[len(first) :].strip()
            except Exception:
                if first.startswith("@"):
                    return await ph.edit("<b>User not found</b>")
        if user is None:
            if not reply:
                return await ph.edit(
                    "<b>Reply to a message or give a @username / user id first</b>"
                )
            user = _message_author(reply)
        if not text and reply:
            text = reply.text or reply.caption or ""
 
    text = EMOJI_RE.sub("", text).strip()
    if not text:
        return await ph.edit("<b>I can't quote the message. No text is given</b>")
 
    await ph.edit("<b>Making quote...</b>")
 
    try:
        replied = None
        if cmd == "rq":
            full = await client.get_messages(message.chat.id, reply.id)
            rr = full.reply_to_message
            replied = rr if rr and not rr.empty else None
        elif cmd == "frq":
            replied = reply
 
        reply_user = _message_author(replied) if replied else None
        reply_text = EMOJI_RE.sub("", _preview_text(replied)).strip() if replied else ""
 
        avatar = await _download_bytes(client, user.photo_id) if user.photo_id else None
        output = await asyncio.to_thread(
            _render_quote_sticker, text, user, avatar, reply_user, reply_text
        )
        await client.send_sticker(
            message.chat.id,
            output,
            reply_to_message_id=reply.id if reply else None,
        )
    except Exception as e:
        return await ph.edit(format_exc(e))
 
    await ph.delete()
 
 
# ------------------------------------------------------------------- qbot
 
 
async def _wait_for_bot_reply(client: Client, bot: str, after_id: int, timeout: int = 30):
    for _ in range(timeout):
        await asyncio.sleep(1)
        async for msg in client.get_chat_history(bot, limit=5):
            if msg.id > after_id and msg.from_user and not msg.from_user.is_self:
                return msg
    return None
 
 
@Client.on_message(filters.command("qbot", prefix) & filters.me)
async def qbot_cmd(client: Client, message: Message):
    reply = message.reply_to_message
    reply_to = reply.id if reply else None
    ph = await client.send_message(message.chat.id, "Please wait", reply_to_message_id=reply_to)
    input_str = _get_args(message)
 
    ids: list[int] = []
    text = ""
 
    if reply and input_str.isdigit():
        count = max(1, min(int(input_str), MAX_QBOT_MESSAGES))
        msgs = await client.get_messages(
            message.chat.id, list(range(reply.id, reply.id + count))
        )
        if not isinstance(msgs, list):
            msgs = [msgs]
        ids = [m.id for m in msgs if not m.empty and m.id != message.id]
    elif input_str:
        text = input_str
    elif reply:
        ids = [reply.id]
    else:
        return await ph.edit(
            "<b>Either reply to a message or give input to the command properly</b>"
        )
 
    if not ids and not text:
        return await ph.edit("<b>No messages to quote</b>")
 
    await ph.edit("<b>Making a quote...</b>")
 
    try:
        if ids:
            sent = await client.forward_messages(QUOTLY_BOT, message.chat.id, ids)
            sent = sent if isinstance(sent, list) else [sent]
            last_id = max(m.id for m in sent)
        else:
            sent = await client.send_message(QUOTLY_BOT, text)
            last_id = sent.id
    except (errors.YouBlockedUser, errors.UserIsBlocked):
        return await ph.edit(f"<b>Please unblock @{QUOTLY_BOT} first</b>")
    except Exception as e:
        return await ph.edit(format_exc(e))
 
    response = await _wait_for_bot_reply(client, QUOTLY_BOT, last_id)
    if response is None:
        return await ph.edit(f"<b>@{QUOTLY_BOT} didn't answer in time</b>")
 
    try:
        await response.copy(
            message.chat.id, reply_to_message_id=reply.id if reply else None
        )
    except Exception as e:
        return await ph.edit(format_exc(e))
 
    await ph.delete()
 
 
modules_help["qpic"] = {
    "qpic [-b] [-s] [text/reply]": "Make a quote picture using the replied user's "
    "profile photo (or the replied photo/sticker) as background.\n"
    "-b — black and white, -s — send as sticker",
    "q [reply]*": "Make a sticker quote of the replied message",
    "rq [reply]*": "Same as q, but also include the message it replied to",
    "fq [reply] [@user/id] [text]": "Fake quote: give @user/id (or reply to someone) "
    "and the text they 'said'. No text = replied message's text",
    "frq [reply]* [@user/id] [text]": "Same as fq, but the replied message is shown "
    "as the reply bubble",
    "qbot [reply] [count 1-15] / [text]": f"Make a quote sticker using @{QUOTLY_BOT}",
}