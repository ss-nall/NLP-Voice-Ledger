"""
Automated Bilingual Payment Reminder Message Generator.
Creates personalized WhatsApp and SMS payment reminders in Telugu Script,
Romanized Telugu, and English with dynamic amounts, due dates, and UPI links.
"""

from typing import Dict, Any
import urllib.parse

class ReminderService:
    """
    Generates polite and professional payment reminders for customers.
    """
    
    @staticmethod
    def generate_reminders(
        customer_name: str,
        amount: float,
        due_date: str,
        phone: str = "",
        store_name: str = "Sri Lakshmi Kirana"
    ) -> Dict[str, Any]:
        formatted_amount = f"₹{amount:,.2f}"
        
        # 1. Telugu Script Template
        telugu_script = (
            f"నమస్కారం {customer_name} గారు,\n"
            f"{store_name} నుండి మెసేజ్. మీ ఖాతాలో పెండింగ్ మొత్తం {formatted_amount} "
            f"{due_date} తేదీ లోపు చెల్లించవలసిందిగా కోరుతున్నాము.\n"
            f"ధన్యవాదాలు!"
        )
        
        # 2. Romanized Telugu Template
        romanized_telugu = (
            f"Namaskaram {customer_name} garu,\n"
            f"{store_name} nundi message. Mee khata lo pending amount {formatted_amount} "
            f"{due_date} lopala pay cheyandi.\n"
            f"UPI / Cash dwara pay cheyavachhu. Dhanyavaadhalu!"
        )
        
        # 3. English Template
        english = (
            f"Dear {customer_name},\n"
            f"Greetings from {store_name}. This is a gentle reminder that your pending balance "
            f"of {formatted_amount} is due by {due_date}.\n"
            f"Please settle via UPI or visit the store. Thank you!"
        )
        
        # Generate WhatsApp Click-to-Chat URL
        encoded_msg = urllib.parse.quote(romanized_telugu)
        clean_phone = phone.replace("+", "").replace(" ", "").replace("-", "") if phone else "919876543210"
        whatsapp_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
        
        return {
            "customer_name": customer_name,
            "amount": amount,
            "due_date": due_date,
            "phone": phone,
            "templates": {
                "telugu_script": telugu_script,
                "romanized_telugu": romanized_telugu,
                "english": english
            },
            "whatsapp_url": whatsapp_url
        }

# Global singleton
reminder_service = ReminderService()
