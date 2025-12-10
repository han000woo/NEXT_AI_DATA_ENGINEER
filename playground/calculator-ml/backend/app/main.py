from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import io
from PIL import Image
import numpy as np
import tensorflow as tf

app = FastAPI()

# ⭐ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 모델 로드
model = tf.keras.models.load_model("../models/mnist_model.keras")


class ImageData(BaseModel):
    image: str


def preprocess_image(image: Image.Image):
    # 1) 흑백 변환
    img = image.convert("L")  
    
    # 2) 28x28로 리사이징
    img = img.resize((28, 28))
    
    # 3) numpy 배열로 변환
    img = np.array(img)
    
    # 4) 흰 배경 + 검정 글씨 형태 만들기 (MNIST 형태)
    img = 255 - img  
    
    # 5) 정규화 + CNN 입력 형태 reshape
    img = img.astype("float32") / 255.0
    
    # ★ CNN 입력 형태는 (batch, 28, 28, 1)
    img = img.reshape(1, 28, 28, 1)

    return img


@app.post("/predict")
def predict(data: ImageData):
    header, encoded = data.image.split(",", 1)
    decoded = base64.b64decode(encoded)

    image = Image.open(io.BytesIO(decoded))
    input_img = preprocess_image(image)

    pred = model.predict(input_img)
    result = int(np.argmax(pred))

    return {"prediction": result}
