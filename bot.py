import os
import imaplib
import email
import requests

# إعدادات البريد الإلكتروني وتليجرام
EMAIL_USER = "mohamad.abdulbaset@suezsteel.com"
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
# ضع هنا معرف محادثة تليجرام الخاص بك (Chat ID)
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID" 

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending telegram message: {e}")

def check_email():
    try:
        # الاتصال بخادم البريد (IMAP لنطاق الشركة أو السيرفر الخاص بكم)
        mail = imaplib.IMAP4_SSL("imap.suezsteel.com") # يمكنك تعديل السيرفر إذا لزم الأمر
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # البحث عن الرسائل غير المنقروة التي تحتوي على كلمة check reply
        status, messages = mail.search(None, '(UNSEEN BODY "check reply")')
        
        if status == "OK":
            for num in messages[0].split():
                res, msg_data = mail.fetch(num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg["Subject"]
                        sender = msg["From"]
                        
                        notification = f"⚠️ تم استلام إيميل جديد يطابق الشروط!\n\nمن: {sender}\nالموضوع: {subject}"
                        send_telegram_message(notification)
                        
        mail.logout()
    except Exception as e:
        print(f"Error checking email:
