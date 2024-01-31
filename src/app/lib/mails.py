from __future__ import annotations

from dataclasses import dataclass
from email.mime.text import MIMEText
from os import environ
from typing import Iterable, NamedTuple
import asyncio
import aiosmtplib
from litestar.di import Provide

MailParameters = NamedTuple("MailParameters", [("receiver", str), ("subject", str), ("body", str), ("html", bool)])


@dataclass(frozen=True)
class MailService:
    sender: str
    smtp_server: str
    port: int
    stdout: bool = False

    def _create_message(self, receivers: list[str] | str, subject: str, body: str, html: bool = False) -> MIMEText:
        """Builds a `MIMEText` message."""
        msg = MIMEText(body, "html" if html else "plain")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(receivers) if isinstance(receivers, list) else receivers
        return msg

    async def send_email(self, receivers: list[str] | str, subject: str, body: str, html: bool = False):
        message = self._create_message(receivers, subject, body, html)
        if self.stdout:
            print(message)
            return
        await aiosmtplib.send(message, hostname=self.smtp_server, port=self.port)  # pyright: ignore[reportUnknownMemberType]

    async def send_emails(self, mails: Iterable[MailParameters]) -> None:
        await asyncio.gather(*[self.send_email([mail.receiver], mail.subject, mail.body, mail.html) for mail in mails])

    @property
    def dependency(self) -> Provide:
        """Gets this middleware as dependency for litestar's dependency injection."""
        return Provide(lambda: self, sync_to_thread=False)

    @classmethod
    def from_env(cls) -> MailService:
        smtp_server = environ.get("SMPT_SERVER")
        port = environ.get("SMPT_PORT")
        sender = environ.get("SMPT_SENDER")
        stdout = environ.get("USE_SMPT")
        return cls(sender, smtp_server, int(port if port else "587"), False if stdout else True)  # pyright: ignore
