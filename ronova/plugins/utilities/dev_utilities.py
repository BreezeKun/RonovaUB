import sys
import traceback
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

eval_helper = {
    "result":None,
    "code":None,
    "chat_id":None,
    'message_id':None,
    'sent_id':None,
    "paste_id":None,
    "googleit_url":None
}

async def aexec(code: str, client, msg):
    local_vars = {
        "app": client,
        "msg": msg,
        "m": msg,
        "r": msg.reply_to_message,
        "p": print,
        "here": msg.chat.id,
        "me": msg.from_user.id,
        "__name__": __name__,
        "__package__": __package__
    }

    exec(
        "async def __ex():\n" +
        "\n".join(f"    {line}" for line in code.splitlines()),
        local_vars
    )

    return await local_vars["__ex"]()

async def get_output(parts, c, m):
    code = parts[1]

    buffer = StringIO()
    result = exception = None

    try:
        with redirect_stdout(buffer), redirect_stderr(buffer):
            result = await aexec(code, c, m)
    except Exception:
        exception = traceback.format_exc()

    output = buffer.getvalue()

    if exception:
        return exception
    if output:
        return output
    if result is not None:
        return str(result)
    return "Done."