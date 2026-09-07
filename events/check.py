import json
from dataclasses import asdict
from uuid import uuid4

from notification_service.events.notification import NotificationEvent

event = NotificationEvent(
    event_id=str(uuid4()),
    notification_id=42,
    channel="email",
    recipient="arun@example.com",
    message="Your order has been shipped",
)

payload = asdict(event)

print(type(event))
print(type(payload))
print(type(json.dumps(payload)))
