import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("NU_NOTIFICATION_SERVICE")

class NotificationService:
    """
    Abstract notification dispatcher supporting Email, SMS, Webhooks, and internal logging.
    Designed for pluggable future integration with Twilio, Sonali Seba SMS, or SMTP.
    """
    def send_notification(
        self,
        event_type: str,
        recipient: str,
        message: str,
        token_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        logger.info(f"[NOTIFICATION] Event={event_type} | To={recipient} | Token={token_id} | Message='{message}'")
        return True

_notification_service_instance: Optional[NotificationService] = None

def get_notification_service() -> NotificationService:
    global _notification_service_instance
    if _notification_service_instance is None:
        _notification_service_instance = NotificationService()
    return _notification_service_instance
