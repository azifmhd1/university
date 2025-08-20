from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

@receiver(user_logged_in)
def send_login_email(sender, request, user, **kwargs):
    ts = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
    subject = "Login Alert - University Portal"
    message = f"Hi {user.username}, you just logged in at {ts}."
    recipient = [user.email]   # student’s email (must be filled in DB)

    try:
        send_mail(subject, message, None, recipient)
    except Exception as e:
        print("Email error:", e)
