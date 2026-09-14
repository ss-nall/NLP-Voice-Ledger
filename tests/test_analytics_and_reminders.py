import pytest
from backend.app.services.reminder_service import reminder_service

def test_reminder_generation():
    res = reminder_service.generate_reminders(
        customer_name="Ramesh",
        amount=3000.0,
        due_date="2026-09-15",
        phone="+919848012345",
        store_name="Sri Lakshmi Kirana"
    )
    assert res["customer_name"] == "Ramesh"
    assert "₹3,000.00" in res["templates"]["telugu_script"]
    assert "₹3,000.00" in res["templates"]["romanized_telugu"]
    assert "₹3,000.00" in res["templates"]["english"]
    assert "whatsapp.com/send" in res["whatsapp_url"]
