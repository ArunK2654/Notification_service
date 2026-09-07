class KafkaProducer:
    def publish(
        self,
        topic: str,
        key: str,
        value: str,
    ) -> None:
        print(
            f"Publishing to topic={topic}, "
            f"key={key}, "
            f"value={value}"
        )

producer = KafkaProducer()

producer.publish(
    topic="notification-events",
    key="42",
    value='{"channel": "email"}',
)