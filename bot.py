import os
import imaplib
import email
import requests
from email.header import decode_header

# الإعدادات (بتتقرأ من الـ Secrets اللي أنت ضفتها في جيتهاب)
EMAIL_USER = "mohamad.abdulbaset@suezsteel.com"
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# شرط البحث (بيدور على إيميلات غير مقروءة في الموضوع بتاعها "check reply")
# لو عايز تدور في محتوى الإيميل نفسه، غير SUBJECT وخليها TEXT
SEARCH_QUERY = '(UNSEEN SUBJECT "check reply")'

def decode_mime_header(header_value):
    """دالة عشان تفك تشفير عناوين الإيميلات (زي العربي أو الرموز الغريبة)"""
    if not header_value:
        return ""
    try:
        parts = decode_header(header_value)
        return "".join(
            p.decode(enc or "utf-8") if isinstance(p, bytes) else p
            for p, enc in parts
        )
    except Exception:
        return str(header_value)

def send_telegram_message(message):
    """دالة إرسال الرسالة على تليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": True,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        print("Telegram sent ✔")
    except Exception as e:
        print(f"Telegram error: {e}")

def check_email():
    """الدالة الرئيسية لفحص الإيميل"""
    try:
        # الاتصال بسيرفر الشركة
        mail = imaplib.IMAP4_SSL("imap.suezsteel.com")
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # البحث عن الإيميلات المطابقة
        status, messages = mail.search(None, SEARCH_QUERY)
        if status != "OK":
            print("Search failed.")
            return

        ids = messages[0].split()
        print(f"Found {len(ids)} matching email(s).")

        # اللف على كل إيميل لقاه
        for num in ids:
            res, msg_data = mail.fetch(num, "(RFC822)")
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    
                    # فك تشفير الموضوع والمرسل
                    subject = decode_mime_header(msg["Subject"])
                    sender = decode_mime_header(msg["From"])

                    # تجهيز نص الرسالة
                    notification = (
                        "⚠️ <b>إيميل جديد يطابق الشروط</b>\n\n"
                        f"👤 <b>من:</b> {sender}\n"
                        f"📧 <b>الموضوع:</b> {subject}"
                    )
                    send_telegram_message(notification)

            # مهم جداً: تعليم الإيميل كـ "مقروء" عشان البوت ميبعتوش تاني في التشغيل اللي بعده
            mail.store(num, '+FLAGS', '\\Seen')

        # قفل الاتصال بالسيرفر
        mail.close()
        mail.logout()
        print("Email check completed successfully.")

    except Exception as e:
        print(f"Error checking email: {e}")

if __name__ == "__main__":
    check_email()
