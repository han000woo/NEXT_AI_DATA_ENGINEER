import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
import os

print("Num GPUs Available: ", len(tf.config.experimental.list_physical_devices('GPU')))
print(tf.config.experimental.list_physical_devices('GPU'))
exit()

# ==============================
# ✅ 경로 설정
# ==============================
base_dir = "../data/cats_and_dogs_filtered"

train_dir = os.path.join(base_dir, "train")
validation_dir = os.path.join(base_dir, "validation")

# ==============================
# ✅ 하이퍼파라미터
# ==============================
img_size = 224
batch_size = 32
epochs = 10

# ==============================
# ✅ 데이터 전처리
# ==============================
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.1,
    zoom_range=0.1,
    horizontal_flip=True
)

validation_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_size, img_size),
    batch_size=batch_size,
    class_mode="binary"
)

validation_generator = validation_datagen.flow_from_directory(
    validation_dir,
    target_size=(img_size, img_size),
    batch_size=batch_size,
    class_mode="binary"
)

# ==============================
# ✅ ResNet50 불러오기 (전이학습)
# ==============================
base_model = ResNet50(
    weights="imagenet",
    include_top=False,
    input_shape=(img_size, img_size, 3) # 색상채널 RGB의 수 
)

# ✅ 기존 가중치 동결 (중요)
for layer in base_model.layers:
    layer.trainable = False

# ==============================
# ✅ 커스텀 분류기 추가
# ==============================
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation="relu")(x)
output = Dense(1, activation="sigmoid")(x)

model = Model(inputs=base_model.input, outputs=output)

# ==============================
# ✅ 컴파일
# ==============================
model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss="binary_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ==============================
# ✅ 학습
# ==============================
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // batch_size,
    epochs=epochs
)

# ==============================
# ✅ 모델 저장 (FastAPI에서 사용할 모델)
# ==============================
os.makedirs("../model", exist_ok=True)
model.save("../model/model.keras")

print("✅ 모델 저장 완료: ../model/model.keras")
