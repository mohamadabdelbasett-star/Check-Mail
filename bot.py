import os
import imaplib
import email
import requests
from email.header import decode_header
from email.utils import parsedate_to_datetime
import zoneinfo

# الإعدادات
EMAIL_USER = "mohamad.abdulbaset@gmail.com" 
EMAIL_PASS = os.environ.get("EMAIL_PASS")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def decode_mime_header(header_value):
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
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        requests.post(url, json=payload, timeout=10)
        print("Telegram sent ✔")
    except Exception as e:
        print(f"Telegram error: {e}")

def generate_report():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com") 
        mail.login(EMAIL_USER, EMAIL_PASS)
        
        status, response = mail.select('"Check Reply"')
        if status != "OK":
            send_telegram_message("❌ لم يتم العثور على فولدر 'Check Reply'.")
            return
        
        # بندور على الإيميلات اللي مأخدتش رد
        status, messages = mail.search(None, 'UNANSWERED')
        ids = messages[0].split()
        
        if len(ids) == 0:
            send_telegram_message("✅ <b>كل الإيميلات في (Check Reply) تم الرد عليها!</b>")
            mail.close()
            mail.logout()
            return

        message_text = f"⚠️ <b>إيميلات تنتظر الرد (Check Reply):</b>\n(عددهم: {len(ids)})\n\n"
        
        for num in ids:
            res, msg_data = mail.fetch(num, "(RFC822)")
            for part in msg_data:
                if isinstance(part, tuple):
                    msg = email.message_from_bytes(part[1])
                    subject = decode_mime_header(msg["Subject"])
                    date_str = msg["Date"]
                    
                    formatted_date = "غير معروف"
                    if date_str:
                        try:
                            parsed_date = parsedate_to_datetime(date_str)
                            cairo_tz = zoneinfo.ZoneInfo("Africa/Cairo")
                            formatted_date = parsed_date.astimezone(cairo_tz).strftime("%Y-%m-%d %I:%M %p")
                        except:
                            formatted_date = date_str

                    message_text += f"📧 <b>الموضوع:</b> {subject}\n"
                    message_text += f"📅 <b>التاريخ:</b> {formatted_date}\n"
                    message_text += "➖➖➖➖➖➖➖➖\n"

        send_telegram_message(message_text)
        mail.close()
        mail.logout()
        print("Report sent successfully.")

    except Exception as e:
        print(f"Error checking email: {e}")
        send_telegram_message(f"❌ حدث خطأ:\n{e}")

if __name__ == "__main__":
    # البوت دلوقتي بيشتغل علطول لما يتشغل (سواء يدوي أو الساعة 12)
    generate_report()
