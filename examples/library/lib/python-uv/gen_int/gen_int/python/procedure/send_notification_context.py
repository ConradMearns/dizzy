# AUTO-GENERATED — do not edit
from dataclasses import dataclass
from typing import Callable

from gen_def.pydantic.events import PatronNotified


@dataclass
class send_notification_emitters:
    patron_notified: Callable[[PatronNotified], None]


@dataclass
class send_notification_context:
    emit: send_notification_emitters
