import os
import re
import subprocess
import traceback

from pyrogram import Client, filters
from pyrogram.types import Message, ReplyParameters

from config import ADMIN_ID, BOT, PREFIXES
from ..utilities import eval_helper
from ..decorators import get_string

_cwd = os.getcwd()

DANGEROUS_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\brm\s+--no-preserve-root\b",
    r"\bmkfs\b",
    r"\bdd\b.*(of=/dev/)",
    r":\(\)\s*\{.*\}",
    r"\bchmod\s+-R\s+777\b",
    r"\bshutdown\b",
    r"\breboot\b",
    r"\binit\s+0\b",
    r"\bpkill\b",
    r"\bkillall\b",
    r">\s*/dev/sd[a-z]",
    r"\bformat\b",
    r"\bfdisk\b",
    r"\bwipefs\b",
    r"\bsystemctl\s+(stop|disable)\b",
    r"\bcurl\b.*\|\s*(bash|sh)\b",
    r"\bwget\b.*\|\s*(bash|sh)\b",
    r"echo\s+.+>\s*/proc/sysrq-trigger",
    r"sysrq-trigger",
    r"\bsudo\s+rm\b",
    r"\bchown\s+-R\b",
    r"\bmv\b.*/dev/null",
    r"\bnohup\b.*&\s*$",
    r"\bcrontab\s+-r\b",
    r"\biptables\s+-F\b",
    r"\bufw\s+disable\b",
    r"/etc/passwd",
    r"/etc/shadow",
]

def is_dangerous(command: str) -> str | None:
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return pattern
    return None


@Client.on_message(filters.command("sh", prefixes=PREFIXES) & filters.user(ADMIN_ID), group= 2)
@get_string("shell")
async def cmd_bash(c: Client, m: Message):
    """
    To execute a shell command
    Usage: sh [shell command]
    """
    global _cwd

    parts = m.text.split(None, 1)
    if len(parts) == 1:
        return await m.reply("No command provided.")

    command = parts[1].strip()

    matched = is_dangerous(command)
    if matched:
        return await m.reply(
            f"**Dangerous command blocked!**\n\n"
            f"Command: `{command}`\n"
            f"Matched: `{matched}`"
        )

    try:
        if command.startswith("cd "):
            target = os.path.abspath(os.path.join(_cwd, command[3:].strip()))
            if os.path.isdir(target):
                _cwd = target
                output = f"Directory changed to: {_cwd}"
            else:
                output = "Directory not found."
        else:
            proc = subprocess.Popen(
                command, shell=True, cwd=_cwd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = proc.communicate()
            output = (stdout + "\n" + stderr).strip() or "Done."
    except Exception:
        output = traceback.format_exc()

    eval_helper["result"] = output
    eval_helper["code"] = command
    eval_helper["chat_id"] = m.chat.id

    results = await c.get_inline_bot_results(bot=BOT, query="eval")
    x = await c.send_inline_bot_result(
        chat_id=m.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_parameters=ReplyParameters(message_id=m.id)
    )
    eval_helper["message_id"] = x.id
    eval_helper["sent_id"] = m.id