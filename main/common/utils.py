import re
from sms_ir import SmsIr
from django.conf import settings


SendSMS = SmsIr(
api_key=settings.SMSIR_API_KEY,
linenumber=settings.SMSIR_LINE_NUMBER,
)




def generate_farsi_slug(text: str) -> str:
    """تولید slug از متن فارسی"""
    text = re.sub(r'[^\w\s\u0600-\u06FF]', '', text)
    text = re.sub(r'\s+', '-', text)
    return text.strip('-')