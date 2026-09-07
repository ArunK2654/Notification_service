import json
from pathlib import Path
from typing import TypedDict


class NotificationRecord(TypedDict):
    channel: str
    status: str


def load_notifications(file_path: str) -> list[NotificationRecord]:
    with Path(file_path).open() as file:
        return json.load(file)


def main() -> None:
    notifications = load_notifications("notifications.json")

    for index, notification in enumerate(notifications, start=1):
        print(
            f"{index}. "
            f"channel={notification['channel']}, "
            f"status={notification['status']}"
        )

    has_failure = any(
        notification["status"] == "failed" for notification in notifications
    )

    all_successful = all(
        notification["status"] == "success" for notification in notifications
    )

    print(f"Has failure: {has_failure}")
    print(f"All successful: {all_successful}")


if __name__ == "__main__":
    main()
