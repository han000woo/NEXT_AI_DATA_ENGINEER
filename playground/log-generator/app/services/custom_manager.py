from datetime import datetime, timedelta
import json
import os 
import random
from faker import Faker
from app.schemas.models import CustomColumnDefinition, SchemaConfig 

fake = Faker()
SCHEMA_DIR = "data/schemas"

os.makedirs(SCHEMA_DIR, exist_ok=True)

class SchemaManager : 
    @staticmethod
    def save_schema(config: SchemaConfig) :
        file_path = os.path.join(SCHEMA_DIR, f"{config.schema_name}.json")
        with open(file_path, "w", encoding="utf-8") as f :
            json.dump(config.model_dump(), f, ensure_ascii=False, indent=4)
        return {"message" : f"Schema '{config.schema_name}' saved successfully. "}
    
    @staticmethod
    def load_schemas() :
        schemas = []
        if not os.path.exists(SCHEMA_DIR) : 
            return []
        for f_name in os.listdir(SCHEMA_DIR) :
            if f_name.endswith(".json") :
                with open(os.path.join(SCHEMA_DIR, f_name),"r",encoding="utf-8") as f :
                    schemas.append(json.load(f))
        return schemas
    
class CustomLogGenerator : 

    @staticmethod
    def generate(config: SchemaConfig, count: int) : 
        logs = [] 
        for _ in range(count) : 
            row = {} 
            for col in config.columns : 
                row[col.name] = CustomLogGenerator._generate_value(col) 
            logs.append(row)
        return logs 
    
    @staticmethod

    def _generate_value(col: CustomColumnDefinition) :
        # 1. Integer
        if col.type == 'int':
            min_v = int(col.min_value) if col.min_value is not None else 0
            max_v = int(col.max_value) if col.max_value is not None else 1000
            return random.randint(min_v, max_v)
        
        # 2. Float
        elif col.type == 'float':
            min_v = col.min_value if col.min_value is not None else 0.0
            max_v = col.max_value if col.max_value is not None else 1000.0
            return round(random.uniform(min_v, max_v), 2)
        
        # 3. Category (ex: User Level, Region)
        elif col.type == 'category':
            opts = col.options if col.options else ['A', 'B', 'C']
            return random.choice(opts)
        
        # 4. Date
        elif col.type == 'date':
            # 기본값 설정 (입력이 없으면 최근 30일 ~ 오늘)
            default_start = datetime.now() - timedelta(days=30)
            default_end = datetime.now()

            # 시작일 파싱
            try:
                if col.min_value:
                    start_date = datetime.strptime(str(col.min_value), "%Y-%m-%d")
                else:
                    start_date = default_start
            except ValueError:
                start_date = default_start

            # 종료일 파싱
            try:
                if col.max_value:
                    end_date = datetime.strptime(str(col.max_value), "%Y-%m-%d")
                    # 종료일의 23:59:59까지 포함하고 싶다면 아래 주석 해제
                    # end_date = end_date.replace(hour=23, minute=59, second=59)
                else:
                    end_date = default_end
            except ValueError:
                end_date = default_end

            # 시작일이 종료일보다 늦으면 스왑
            if start_date > end_date:
                start_date, end_date = end_date, start_date

            # 두 날짜 사이의 총 초(seconds) 계산
            time_between_dates = end_date - start_date
            days_between_dates = time_between_dates.days
            
            if days_between_dates <= 0:
                 # 같은 날짜면 그냥 해당 날짜 반환 (시간만 랜덤)
                 random_seconds = random.randint(0, 86399)
                 random_date = start_date + timedelta(seconds=random_seconds)
            else:
                 # 날짜 차이만큼 랜덤 일수 + 랜덤 초 추가
                 random_days = random.randrange(days_between_dates + 1) # +1은 end_date 포함 위함
                 random_date = start_date + timedelta(days=random_days)
                 
                 # 시간까지 랜덤하게 하고 싶다면:
                 # random_seconds = random.randint(0, 86399) # 하루치 초
                 # random_date = random_date + timedelta(seconds=random_seconds)

            return random_date.isoformat() # "2024-05-21T14:30:00" 형식 반환
        
        # 5. UUID
        elif col.type == 'uuid':
            return fake.uuid4()
            
        # 6. String (Default)
        else:
            return fake.word()
        