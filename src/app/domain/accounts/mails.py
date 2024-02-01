from lib.mails import MailParameters, MailService

from .services import InvitedUsers


class UserMailService:
    subject: str = "You've been invited to join CQ-Manager!"

    @staticmethod
    def body(mail: str, password: str) -> str:
        return f"You've been invited to join CQ-Manager!\n\nYour initial credentials are: '{mail}' & '{password}'."

    @staticmethod
    async def send_invitation_mail(mail_service: MailService, users: InvitedUsers):
        mails = [
            MailParameters(user.email, UserMailService.subject, UserMailService.body(user.email, password), False)
            for user, password in users.created
        ]
        await mail_service.send_emails(mails)
