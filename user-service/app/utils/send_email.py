import smtplib
from email.message import EmailMessage


def send_verification_email(
    user_email: str, verification_link: str,
):
    sender_email = "saadkamran6ft@gmail.com"
    sender_password = "tvracfxubghzlflh"

    mail = EmailMessage()
    mail["From"] = sender_email
    mail["To"] = user_email
    mail["Subject"] = "Email Verification"

    # Plain text and HTML content
    # mail.set_content(
    #     f"Please verify your email by clicking on the following link: {verification_link}"
    # )
    html_content = f"""
    <html>
    <body>
        <p>Please verify your email by clicking on the following link:</p>
        <a href="{verification_link}">Verify Email</a>
    </body>
    </html>
    """
    mail.set_content(html_content, subtype="html")

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        return server.send_message(mail)
        # print("Verification email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()


# def send_verification_email(email: str):
#     sender_email = "saadkamran6ft@gmail.com"
#     text = f"dear {email} this is a newwwwww....... verification email"
#     server = smtplib.SMTP("smtp.gmail.com", 587)
#     server.starttls()
#     server.login(sender_email, "tvracfxubghzlflh")
#     return server.sendmail(sender_email, email, text)
