from itertools import chain

from domain.accounts.services import InvitedUsers
from lib.mails import MailParameters, MailService

from .models import Group


class GroupMailService:
    @staticmethod
    def subject(name: str) -> str:
        return f"Welcome to '{name}' on CQ-Manager!"

    @staticmethod
    def body(group: str, project: str) -> str:
        return f"You've been added to '{group}' a group within the '{project}' project on CQ-Manger."

    @staticmethod
    async def send_invitation_mail(mail_service: MailService, users: InvitedUsers, group: Group):
        mails = [
            MailParameters(
                user.email,
                GroupMailService.subject(group.name),
                GroupMailService.body(group.name, group.project.name),
                False,
            )
            for user in chain(map(lambda u: u[0], users.created), users.existing)
        ]
        await mail_service.send_emails(mails)
