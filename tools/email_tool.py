"""Email delivery tool for maritime intelligence reports.

TODO: Replace the mock implementation with a real SMTP / transactional email
      call.  Example libraries: smtplib (stdlib), SendGrid, Mailgun.

      Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, EMAIL_FROM, and
      EMAIL_TO in your .env file.
"""

from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

logger = logging.getLogger(__name__)


def send_report_email(
    subject: str,
    body_markdown: str,
    recipients: list[str],
    smtp_host: Optional[str] = None,
    smtp_port: int = 587,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None,
    sender: Optional[str] = None,
    dry_run: bool = True,
) -> bool:
    """Send the Markdown report as a plain-text email.

    When ``dry_run`` is ``True`` (the default), the email is *not* actually
    sent – the content is logged instead, making it safe to run without real
    SMTP credentials.

    Returns ``True`` if the email was sent (or would have been sent in dry-run
    mode), ``False`` on error.
    """

    if dry_run:
        logger.info(
            "DRY-RUN – would send email\n"
            "  Subject   : %s\n"
            "  Recipients: %s\n"
            "  Body      :\n%s",
            subject,
            ", ".join(recipients),
            body_markdown,
        )
        return True

    # ── REAL SMTP send ─────────────────────────────────────────────────────────
    # TODO: Optionally convert Markdown to HTML using ``markdown`` package for
    #       a richer email body.
    if not smtp_host:
        logger.error("SMTP host is not configured.  Set SMTP_HOST in your .env file.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender or smtp_user or "reports@maritime-agents.local"
        msg["To"] = ", ".join(recipients)

        # Plain-text part
        msg.attach(MIMEText(body_markdown, "plain"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            if smtp_port == 587:
                server.starttls()
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(msg["From"], recipients, msg.as_string())

        logger.info("Report email sent to %s", ", ".join(recipients))
        return True

    except smtplib.SMTPException as exc:
        logger.error("Failed to send report email: %s", exc)
        return False
