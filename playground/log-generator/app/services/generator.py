from faker import Faker
import random
from datetime import datetime
from app.schemas.dynamic_models import DynamicLogRequest
from app.schemas.models import LogSchema

fake = Faker()


class LogGeneratorService:
    @staticmethod
    def generate_dynamic_logs(schema: DynamicLogRequest):
        logs = []
        
        for _ in range(schema.count):
            row = {}
            for col in schema.columns:
                # LLM이 정해준 타입에 따라 Faker 함수 매핑
                if col.data_type == 'name':
                    row[col.name] = fake.name()
                elif col.data_type == 'email':
                    row[col.name] = fake.email()
                elif col.data_type == 'date':
                    row[col.name] = fake.iso8601()
                elif col.data_type == 'uuid':
                    row[col.name] = fake.uuid4()
                elif col.data_type == 'int':
                    row[col.name] = fake.random_int(min=1, max=1000)
                elif col.data_type == 'float':
                    row[col.name] = round(random.uniform(10.0, 1000.0), 2)
                elif col.data_type == 'city':
                    row[col.name] = fake.city()
                elif col.data_type == 'country':
                    row[col.name] = fake.country_code()
                elif col.data_type == 'category':
                    # 옵션이 있으면 그 중에서 선택, 없으면 임의 문자열
                    options = col.options if col.options else ['A', 'B', 'C']
                    row[col.name] = random.choice(options)
                else:
                    row[col.name] = fake.word()
            
            logs.append(row)
        
        return {
            "table_name": schema.table_name,
            "data": logs
        }
