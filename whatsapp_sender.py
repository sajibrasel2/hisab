"""
WhatsApp automation module for Amar Hisab Billing Software.
Uses pywhatkit to send automated professional due billing messages
with graceful fallback to WhatsApp Web API.
"""

import threading
import urllib.parse
import webbrowser
from typing import Tuple, Callable, Optional


def format_phone_number(phone: str, default_country_code: str = "+880") -> str:
    """
    Formats a raw phone number into standard international E.164 format.
    Example: '01711223344' -> '+8801711223344'
             '+8801711223344' -> '+8801711223344'
    """
    if not phone:
        return ""

    # Keep only digits and plus sign
    clean = "".join(c for c in phone.strip() if c.isdigit() or c == "+")

    if not clean:
        return ""

    # If it starts with '+', it already has country code
    if clean.startswith("+"):
        return clean

    # If starts with '00', replace with '+'
    if clean.startswith("00"):
        return "+" + clean[2:]

    # If starts with '880' without '+', add '+'
    if clean.startswith("880"):
        return "+" + clean

    # If starts with local '0', replace with country code
    if clean.startswith("0"):
        return default_country_code + clean[1:]

    # Default fallback
    return default_country_code + clean


def create_professional_due_message(client_name: str, due_amount: float, shop_name: str = "আমার হিসাব") -> str:
    """
    Generates a professional Bengali billing reminder message.
    """
    clean_name = client_name.strip() if client_name else "সম্মানিত গ্রাহক"
    message = (
        f"আসসালামু আলাইকুম {clean_name},\n\n"
        f"'{shop_name}' বিলিং সিস্টেম থেকে শুভেচ্ছা।\n"
        f"আপনার বর্তমান হিসাব অনুযায়ী সর্বশেষ বকেয়া (Due Amount): ৳ {due_amount:,.2f}।\n\n"
        f"অনুগ্রহ করে সুবিধাজনক সময়ে বকেয়া পরিশোধ করার জন্য বিনীত অনুরোধ করা হলো।\n\n"
        f"যেকোনো তথ্যের জন্য আমাদের সাথে যোগাযোগ করতে পারেন।\n"
        f"ধন্যবাদ!"
    )
    return message


def send_whatsapp_message(phone: str, client_name: str, due_amount: float,
                          on_success: Optional[Callable[[str], None]] = None,
                          on_error: Optional[Callable[[str], None]] = None):
    """
    Sends WhatsApp message in a background thread to prevent Tkinter UI freeze.
    Uses pywhatkit, with fallback to WhatsApp Web if needed.
    """
    def _worker():
        formatted_phone = format_phone_number(phone)
        if not formatted_phone or len(formatted_phone) < 10:
            if on_error:
                on_error("অনুগ্রহ করে সঠিক WhatsApp নম্বর প্রদান করুন (যেমন: 01711223344)।")
            return

        message = create_professional_due_message(client_name, due_amount)

        # Attempt sending with pywhatkit
        try:
            import pywhatkit
            # pywhatkit.sendwhatmsg_instantly opens WhatsApp Web, types message, and presses Enter
            pywhatkit.sendwhatmsg_instantly(
                phone_no=formatted_phone,
                message=message,
                wait_time=12,
                tab_close=False
            )
            if on_success:
                on_success(f"'{client_name}' ({formatted_phone})-কে pywhatkit এর মাধ্যমে সফলভাবে WhatsApp মেসেজ পাঠানো হয়েছে!")
            return
        except Exception as pywhatkit_err:
            # Graceful browser fallback if pywhatkit hits driver or screen automation limitation
            try:
                encoded_msg = urllib.parse.quote(message)
                web_url = f"https://web.whatsapp.com/send?phone={formatted_phone}&text={encoded_msg}"
                webbrowser.open(web_url)
                if on_success:
                    on_success(
                        f"WhatsApp Web ওপেন হয়েছে ({formatted_phone})!\n"
                        f"বকেয়া: ৳ {due_amount:,.2f}"
                    )
            except Exception as fallback_err:
                if on_error:
                    on_error(f"WhatsApp মেসেজ পাঠানো সম্ভব হয়নি: {str(fallback_err)}")

    # Start non-blocking daemon thread
    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
