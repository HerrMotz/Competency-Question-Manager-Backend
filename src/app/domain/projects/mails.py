from itertools import chain
from typing import Literal

from domain.accounts.services import InvitedUsers
from lib.mails import MailParameters, MailService

from .models import Project


class ProjectMailService:
    @staticmethod
    def subject(name: str) -> str:
        return f"Welcome to {name} on CQ-Manager!"

    @staticmethod
    def body(type: Literal["manager", "ontology engineer"], project: str) -> str:
        return f"You've been assigned as '{type}' to '{project}' a project on CQ-Manger."

    @staticmethod
    async def send_invitation_mail(
        mail_service: MailService,
        users: InvitedUsers,
        project: Project,
        role: Literal["manager", "ontology engineer"],
    ):
        mails = [
            MailParameters(
                user.email,
                ProjectMailService.subject(project.name),
                ProjectMailService.body(role, project.name),
                False,
            )
            for user in chain(map(lambda u: u[0], users.created), users.existing)
        ]
        await mail_service.send_emails_async(mails)
