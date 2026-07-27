from typing import Any, Optional
from datetime import datetime, timedelta, timezone

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import UserInvalid

from .errors import InvalidTime

def format_duration(dt: Optional[datetime]) -> str:
    if not dt:
        return "permanently"

    diff = dt - datetime.now(timezone.utc)
    seconds = int(diff.total_seconds())

    if seconds <= 0:
        return "permanently"

    units = [
        ("week", 604800),
        ("day", 86400),
        ("hour", 3600),
        ("minute", 60),
        ("second", 1),
    ]

    for name, unit_seconds in units:
        if seconds >= unit_seconds:
            value = round(seconds / unit_seconds)
            return f"{value} {name}{'s' if value > 1 else ''}"

    return "unknown"


class RetriveData:

    def __init__(self, c: Client, m: Message):
        self.client = c
        self.msg = m
        self.rm = self.msg.reply_to_message if self.msg.reply_to_message else None
        self.command = m.command
        self.data: dict[str, Any] = {
            "chat_id": self.msg.chat.id,
            "target_id": None,
            "time": datetime.fromtimestamp(0, timezone.utc),
            "reason": None
        }

    def get_time(self, given_time) -> bool:
        if not given_time:
            return False

        if (
            given_time[-1] in ["s", "m", "h", "w", "d"]
            and given_time[:-1].isdigit()
        ):
            time = int(given_time[:-1])
            period = given_time[-1]

            #well if anyone is reading this part lemme tell what are these numbers
            #for banning someone the time should be > 30s or it should be less than 366 days
            #so these part is precalculated here
            if (
                time <= 0 or
                (time < 30 and period == "s") or
                (time > 366 and period == "d") or
                (time > 8784 and period == "h") or
                (time > 527040 and period == "m") or
                (time > 52 and period == "w")
            ):
                raise InvalidTime("Invalid time range")

            time_allies = {
                "s": "seconds",
                "m": "minutes",
                "h": "hours",
                "w": "weeks",
                "d": "days"
            }

            self.data["time"] = datetime.now(timezone.utc) + timedelta(
                **{time_allies[period]: time}
            )
            return True

        return False

    async def ban_data(self):
        if self.rm:

            self.data["target_id"] = self.rm.from_user.id

            if len(self.command) >= 2:
                if self.get_time(given_time=self.command[1]):
                    if len(self.command) > 2:
                        self.data["reason"] = " ".join(self.command[2:])
                else:
                    self.data["reason"] = " ".join(self.command[1:])

            return self.data

        elif len(self.command) > 1 and (
            self.command[1].startswith("@") or self.command[1].isdigit()
        ):
            if self.command[1].isdigit():
                self.data["target_id"] = int(self.command[1])

            else:
                user = await self.client.get_users(self.command[1])
                if not user:
                    raise UserInvalid("User Not Found")

                self.data["target_id"] = int(user.id)

            if len(self.command) > 2:
                if self.get_time(given_time=self.command[2]):
                    if len(self.command) > 3:
                        self.data["reason"] = " ".join(self.command[3:])
                else:
                    self.data["reason"] = " ".join(self.command[2:])

            return self.data

    async def unban_data(self):
        if self.rm:

            self.data["target_id"] = self.rm.from_user.id
            return self.data

        elif len(self.command) > 1 and (
            self.command[1].startswith("@") or self.command[1].isdigit()
        ):
            if self.command[1].isdigit():
                self.data["target_id"] = int(self.command[1])

            else:
                user = await self.client.get_users(self.command[1])
                if not user:
                    raise UserInvalid("User Not Found")

                self.data["target_id"] = int(user.id)

            return self.data