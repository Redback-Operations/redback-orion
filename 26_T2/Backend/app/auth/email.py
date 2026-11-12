import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_password_reset_email(
    email: str,
    reset_link: str,
):
    message = MIMEMultipart("alternative")

    message["Subject"] = "Reset your password"
    message["From"] = SMTP_USERNAME
    message["To"] = email

    html = f"""
    <html>
        <body>
            <h2>Reset your password</h2>

            <p>
                We received a request to reset your password.
            </p>

            <p>
                Click the button below to create a new password.
            </p>

            <p>
                <a
                    href="{reset_link}"
                    style="
                        background: #2563eb;
                        color: white;
                        padding: 12px 20px;
                        text-decoration: none;
                        border-radius: 5px;
                        display: inline-block;
                    "
                >
                    Reset Password
                </a>
            </p>

            <p>
                This link expires in 15 minutes.
            </p>

            <p>
                If you didn't request this password reset,
                you can ignore this email.
            </p>
        </body>
    </html>
    """

    message.attach(
        MIMEText(
            html,
            "html",
        )
    )

    with smtplib.SMTP(
        SMTP_SERVER,
        SMTP_PORT,
    ) as server:

        server.starttls()

        server.login(
            SMTP_USERNAME,
            SMTP_PASSWORD,
        )

        server.sendmail(
            SMTP_USERNAME,
            email,
            message.as_string(),
        )