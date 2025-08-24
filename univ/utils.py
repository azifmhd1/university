import os
from twilio.rest import Client
from django.conf import settings


def send_whatsapp_message(to: str, message: str):
    """
    Send a WhatsApp message using Twilio.

    Args:
        to (str): Receiver phone number. Example: "+91xxxxxxxxxx" or "whatsapp:+91xxxxxxxxxx"
        message (str): The message text.

    Returns:
        str | None: The SID of the sent message if successful, otherwise None.
    """

    account_sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
    auth_token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
    from_whatsapp = getattr(settings, "TWILIO_WHATSAPP_FROM", None)

    if not all([account_sid, auth_token, from_whatsapp]):
        print("⚠️ Twilio settings are not configured properly in settings.py")
        return None

    client = Client(account_sid, auth_token)

    # Ensure number has whatsapp prefix
    to_number = to if to.startswith("whatsapp:") else f"whatsapp:{to}"

    try:
        msg = client.messages.create(
            from_=from_whatsapp,
            body=message,
            to=to_number
        )
        return msg.sid
    except Exception as e:
        print("❌ WhatsApp send error:", e)
        return None
