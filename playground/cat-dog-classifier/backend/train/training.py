# 1. 필수 라이브러리 설치
!pip install gradio -q

import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import BatchNormalization
import numpy as np
import os
import zipfile
import gradio as gr

# ==========================================
# [중요] 여기에 내 ZIP 파일 이름을 적어주세요
# ==========================================
local_zip_filename = 'cats_and_dogs_filtered.zip'  # 예: 'my_data.zip'

# 2. 압축 해제 (이미 풀려있으면 건너뜀)
base_dir = '/content/dataset' # 압축을 풀 폴더 경로

if not os.path.exists(base_dir):
    print(f"'{local_zip_filename}' 압축 해제 중...")
    with zipfile.ZipFile(local_zip_filename, 'r') as zip_ref:
        zip_ref.extractall(base_dir)
    print("압축 해제 완료!")
else:
    print("이미 압축이 해제된 폴더가 있습니다.")

# 3. 데이터 경로 설정
# 주의: 압축 파일 내부 구조에 따라 경로를 수정해야 할 수 있습니다.
# 보통 압축을 풀면 최상위 폴더가 하나 더 생기는 경우가 많습니다.
# 확인을 위해 폴더 구조를 출력해봅니다.
print(f"폴더 구조 확인: {os.listdir(base_dir)}")

# 만약 압축 풀린 폴더 안에 'cats_and_dogs_filtered' 같은 폴더가 또 있다면 아래 경로에 추가해야 합니다.
# 예: os.path.join(base_dir, 'cats_and_dogs_filtered', 'train')
train_dir = os.path.join(base_dir, 'cats_and_dogs_filtered', 'train')
validation_dir = os.path.join(base_dir, 'cats_and_dogs_filtered', 'validation')

# 4. 데이터 전처리 (ResNet 전용)
IMG_HEIGHT = 224
IMG_WIDTH = 224
batch_size = 32

train_image_generator = ImageDataGenerator(
    preprocessing_function=preprocess_input,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

validation_image_generator = ImageDataGenerator(
    preprocessing_function=preprocess_input
)

# 데이터 로딩 시도 (경로 에러 방지용 try-except)
try:
    train_data_gen = train_image_generator.flow_from_directory(
        batch_size=batch_size,
        directory=train_dir,
        shuffle=True,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        class_mode='binary'
    )

    val_data_gen = validation_image_generator.flow_from_directory(
        batch_size=batch_size,
        directory=validation_dir,
        target_size=(IMG_HEIGHT, IMG_WIDTH),
        class_mode='binary'
    )
except FileNotFoundError:
    print("❌ 오류: 'train' 또는 'validation' 폴더를 찾을 수 없습니다.")
    print(f"현재 '{base_dir}' 안에 있는 폴더 목록: {os.listdir(base_dir)}")
    print("경로 설정 부분(train_dir, validation_dir)을 실제 폴더 구조에 맞게 수정해주세요.")
    raise # 코드 실행 중단

# 5. ResNet50 모델 생성
base_model = ResNet50(input_shape=(IMG_HEIGHT, IMG_WIDTH, 3),
                      include_top=False,
                      weights='imagenet')
base_model.trainable = False

model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    BatchNormalization(),
    Dense(256, activation='relu'),
    Dropout(0.4),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              loss='binary_crossentropy',
              metrics=['accuracy'])

# 6. 학습 시작
print("학습을 시작합니다...")
history = model.fit(
    train_data_gen,
    steps_per_epoch=len(train_data_gen),
    epochs=10,
    validation_data=val_data_gen,
    validation_steps=len(val_data_gen)
)

# 1. 모델 저장 (.keras 형식 권장)
save_path = 'cat_dog_resnet_model.keras'
model.save(save_path)

print(f"모델이 '{save_path}'로 저장되었습니다.")

# 7. Gradio 인터페이스
def classify_image(image):
    image = image.resize((IMG_WIDTH, IMG_HEIGHT))
    img_array = np.array(image)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)
    prediction = model.predict(img_array)[0][0]
    if prediction < 0.5:
        return f"🐱 고양이 ({ (1-prediction)*100:.1f}% )"
    else:
        return f"🐶 강아지 ({ prediction*100:.1f}% )"

interface = gr.Interface(fn=classify_image, inputs=gr.Image(type="pil"), outputs="text")
interface.launch(share=True)