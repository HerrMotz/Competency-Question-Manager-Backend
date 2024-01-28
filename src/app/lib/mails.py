from __future__ import annotations

import smtplib
import ssl
from contextlib import _GeneratorContextManager, contextmanager  # pyright: ignore[reportPrivateUsage]
from dataclasses import dataclass
from email.mime.text import MIMEText
from os import environ
from typing import Generator, Literal, NamedTuple

from litestar.concurrency import sync_to_thread
from litestar.di import Provide

MailParameters = NamedTuple("MailParameters", [("receiver", str), ("subject", str), ("body", str), ("html", bool)])


@dataclass(frozen=True)
class MailService:
    smtp_server: str
    port: int
    username: str = ""
    password: str = ""
    sender: str = "CQ-Manager"
    context: Literal["ssl", "tls"] = "ssl"
    stdout: bool = True

    @contextmanager
    def _create_tls_context(self) -> Generator[smtplib.SMTP, None, None]:
        """Yields a `tls` secured server context (use as context manager)."""
        try:
            context = ssl.create_default_context()
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.starttls(context=context)
            server.login(self.username, self.password)
            yield server
        finally:
            server.close()  # pyright: ignore

    @contextmanager
    def _create_ssl_context(self) -> Generator[smtplib.SMTP_SSL, None, None]:
        """Yields an `ssl` secured server context (use as context manager)."""
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.username, self.password)
            yield server

    def _create_context(self) -> _GeneratorContextManager[smtplib.SMTP]:
        """Dispatches context use between `ssl` or a `tls` (use as context manager)."""
        return self._create_ssl_context() if self.context == "ssl" else self._create_tls_context()

    def _create_message(self, receivers: list[str] | str, subject: str, body: str, html: bool = False) -> MIMEText:
        """Builds a `MIMEText` message."""
        msg = MIMEText(body, "html" if html else "plain")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ", ".join(receivers) if isinstance(receivers, list) else receivers
        return msg

    def send_email(self, receivers: list[str] | str, subject: str, body: str, html: bool = False):
        """Send a single mail to one or more receivers."""
        if self.stdout:
            print(f"Send message.")
            return
        with self._create_context() as server:
            msg = self._create_message(receivers, subject, body, html)
            server.send_message(msg)

    async def send_email_async(self, receivers: list[str] | str, subject: str, body: str, html: bool = False):
        """Wraps `send_email` asynchronously using a worker thread."""
        await sync_to_thread(self.send_email, receivers, subject, body, html)

    def send_emails(self, messages: list[MailParameters]):
        """Sends multiple distinct mails to various receivers.

        Notes:
            * sends multiple *different* mails instead of a single on (see `send_email`)
            * all mails are send under the same context (as opposed to multiple `send_email` calls)
        """
        if self.stdout:
            print(f"Send {len(messages)} messages.")
            return
        with self._create_context() as server:
            for receiver, subject, body, html in messages:
                msg = self._create_message(receiver, subject, body, html)
                server.send_message(msg)

    async def send_emails_async(self, messages: list[MailParameters]):
        """Wraps `send_emails` asynchronously using a worker thread."""
        await sync_to_thread(self.send_emails, messages)

    @property
    def dependency(self) -> Provide:
        """Gets this middleware as dependency for litestar's dependency injection."""
        return Provide(lambda: self, sync_to_thread=False)

    @classmethod
    def from_env(cls) -> MailService:
        smtp_server = environ.get("SMPT_SERVER")
        port = environ.get("SMPT_PORT")
        username = environ.get("SMPT_USER")
        password = environ.get("SMPT_PASSWORD")
        sender = environ.get("SMPT_SENDER")
        context = environ.get("SMPT_SECURITY_CONTEXT")
        stdout = environ.get("USE_SMPT")
        return cls(smtp_server, int(port if port else "587"), username, password, sender, context, None if not stdout else True)  # pyright: ignore
