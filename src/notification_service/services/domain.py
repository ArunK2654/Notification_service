"""Domain objects used by the application"""

from dataclasses import dataclass


@dataclass
class Notification:
    subject: str
    message: str
