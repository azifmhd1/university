from django.core.mail import send_mail
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from .utils import send_whatsapp_message
from .models import Student

@receiver(user_logged_in)
def send_login_alert(sender, request, user, **kwargs):
    ts = timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")
    subject = "Login Alert - University Portal"
    message = f"Hi {user.username}, you just logged in at {ts}."
    recipient = [user.email]

    # ---- Email ----
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient)
    except Exception as e:
        print("❌ Email error:", e)

    # ---- WhatsApp ----
    try:
        student = Student.objects.filter(user=user).first()
        if student and student.phone:
            whatsapp_to = f"+91{student.phone}"  # adjust country code
            send_whatsapp_message(whatsapp_to, message)
    except Exception as e:
        print("❌ WhatsApp error:", e)
