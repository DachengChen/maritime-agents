import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self) -> None:
        self.settings = get_settings()
        template_path = Path(__file__).resolve().parents[1] / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_report_html(self, markdown_content: str, requirement_text: str) -> str:
        template = self.jinja_env.get_template("report_email.html")
        return template.render(requirement_text=requirement_text, markdown_content=markdown_content)

    def send_report_email(self, recipient_email: str, subject: str, markdown_content: str, html_content: str) -> None:
        if self.settings.email_delivery_mode.lower() == "mock":
            logger.info("Mock email send: to=%s subject=%s", recipient_email, subject)
            return

        # TODO: Add providers like Resend/SendGrid for production delivery.
        self._send_smtp(recipient_email, subject, markdown_content, html_content)

    def _send_smtp(self, recipient_email: str, subject: str, markdown_content: str, html_content: str) -> None:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.settings.smtp_sender
        message["To"] = recipient_email
        message.attach(MIMEText(markdown_content, "plain", "utf-8"))
        message.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as smtp:
            if self.settings.smtp_use_tls:
                smtp.starttls()
            if self.settings.smtp_username and self.settings.smtp_password:
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
            smtp.sendmail(self.settings.smtp_sender, [recipient_email], message.as_string())


email_service = EmailService()
