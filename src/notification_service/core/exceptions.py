class NotificationError(Exception):
    pass


class EmailDeliveryError(NotificationError):
    pass


class SMSDeliveryError(NotificationError):
    pass


class PushDeliveryError(NotificationError):
    pass
