from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import preprocess_input
from PIL import Image
import numpy as np
import io

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("loading model")
model = tf.keras.models.load_model("../model/cat_dog_resnet_model.keras")
print("모델 로딩 완료!")


def prepare_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    image = image.resize((224, 224))
    image = image.convert("RGB")
    image_array = np.array(image)
    image_array = np.expand_dims(image_array, axis=0)
    return image_array


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()

    processed_image = prepare_image(image_bytes)

    prediction = model.predict(processed_image)[0][0]

    if prediction < 0.5:
        confidence = (1 - prediction) * 100
        return {
            "result": "cat",
            "confidence": round(confidence, 2),
            "message": "고양이입니다!",
        }
    else:
        confidence = prediction * 100
        return {
            "result": "dog",
            "confidence": round(confidence, 2),
            "message": "강아지입니다!",
        }
