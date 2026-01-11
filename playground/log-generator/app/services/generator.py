from faker import Faker
import random
from datetime import datetime
from app.schemas.models import LogSchema

fake = Faker()


class LogGeneratorService:
    @staticmethod
    def generate_random_logs(count: int):
        logs = []
        for _ in range(count):
            log = LogSchema(
                event_id=fake.uuid4(),
                timestamp=datetime.now().isoformat(),
                user_id=fake.random_int(min=1000, max=9999),
                user_region=fake.country_code(),
                event_type=random.choice(["click", "view", "purchase", "cart_add"]),
                item_id=f"ITEM-{fake.random_int(min=1, max=100)}",
                price=round(random.uniform(10.0, 500.0), 2),
            )
            logs.append(log)
        return logs
