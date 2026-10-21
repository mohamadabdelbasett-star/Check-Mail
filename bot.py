import os
import imaplib
import email
from email.header import decode_header
import requests

# إعدادات البريد الإلكتروني وتليجرام
IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = "mohamad.abdulbaset@suezsteel.com"
# ملاحظة: سيتم استخدام App Password لتسجيل الدخول بأمان
EMAIL_PASS = os.environ.get("EMAIL_PASS") 

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = "7533781687"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

def check_emails():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # البحث عن الإيميلات غير المقروءة التي تحتوي على كلمة check reply أو ردود
        status, messages = mail.search(None, '(UNSEEN)')
        
        if status != 'OK':
            print("خطأ في البحث عن الرسائل.")
            return

        for num in messages[0].split():
            res, msg_data = mail.fetch(num, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # قراءة عنوان الإيميل والرسالة المرسلة
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                        
                    sender = msg.get("From")
                    
                    # تصفية أو التحقق من الكلمة المطلوبة (مثلاً check reply)
                    if "check reply" in subject.lower():
                        alert_text = f"🚨 *إشعار إيميل جديد!*\n\n📩 *الموضوع:* {subject}\n👤 *من:* {sender}"
                        send_telegram_message(alert_text)

        mail.logout()
    except Exception as e:
        print(f حدث خطأ أثناء فحص البريد: {e}")

if __name__ == "__main__":
    check_emails()
