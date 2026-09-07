class KafkaConsumer:
    def __init__(self, topic: str, group_id: str):
        self.topic = topic
        self.group_id = group_id

    def consume(self) -> None:
        print(
            f"Consuming from topic={self.topic}, "
            f"group={self.group_id}"
        )


consumer = KafkaConsumer(
    topic="notification-events",
    group_id="notification-workers",
)

consumer.consume()