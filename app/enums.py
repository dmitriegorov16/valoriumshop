import enum


class AccountType(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class DeliveryType(enum.Enum):
    AUTO = "auto"
    MANUAL = "manual"


class OrderStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"


class PaymentMethod(enum.Enum):
    CRYPTO_BOT = "crypto_bot"
    STARS = "stars"


class PaymentStatus(enum.Enum):
    DRAFT = "draft"
    PAID = "paid"
    CANCELED = "canceled"
