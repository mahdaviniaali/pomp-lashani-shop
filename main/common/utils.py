import re
from sms_ir import SmsIr
from django.conf import settings


class SmsIrR(SmsIr):
    def send_sms(self, number: str, message: str, linenumber=None):

        modified_message = f"{message} \n\n waterrisen.com"

        return super().send_sms(
            number=number,
            message=modified_message,
            linenumber=linenumber
        )

SendSMS = SmsIrR(
api_key=settings.SMSIR_API_KEY,
linenumber=settings.SMSIR_LINE_NUMBER,
)




def generate_farsi_slug(text: str) -> str:
    """تولید slug از متن فارسی"""
    text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text.strip('-')