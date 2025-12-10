import tensorflow as tf
from tensorflow import keras 
from keras.utils import to_categorical
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import numpy as np

np.random.seed(0)
tf.random.set_seed(0)

(X_train, Y_train), (X_test, Y_test) = tf.keras.datasets.mnist.load_data()

# ★ CNN 입력 형태에 맞게 reshape
X_train = X_train.reshape(-1, 28, 28, 1).astype('float32') / 255
X_test = X_test.reshape(-1, 28, 28, 1).astype('float32') / 255

Y_train = to_categorical(Y_train, 10)
Y_test = to_categorical(Y_test, 10)

# 모델 - 아키텍쳐 
model = Sequential()

# dense랑 비슷함, 커널이라는 개념 추가, 
# cnn구조를 tensorflow에서 구현 

# 32 - 입력 노드, (3,3) 커널의 크기 - 보고 줄이고
model.add(Conv2D(32, (3,3), activation='relu', input_shape=(28,28,1)))
# MaxPooling2D - 차원 축소 - 이미지 하나만 봤을때 0과 1로 나눠짐, 특징을 뽑기위해 강제로 늘림 - 과적합 방지 
model.add(MaxPooling2D(2,2))

# 64 - 입력 노드
model.add(Conv2D(64, (3,3), activation='relu'))
model.add(MaxPooling2D(2,2))

# 32 - 입력 노드
model.add(Conv2D(32, (3,3), activation='relu'))
model.add(MaxPooling2D(2,2))

# flatten - 일렬로 한다. reshape랑 비슷함 
model.add(Flatten())
model.add(Dense(128, activation='relu'))   # 노드 128
model.add(Dropout(0.5)) 
model.add(Dense(10, activation='softmax')) # 보통 소프트 맥스로 마무리 
#
model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

# checkpoint_cb = keras.callbacks.ModelCheckpoint('best-cnn-model.keras', save_best_only=True)
# early_stopping_cb = keras.callbacks.EarlyStopping(patience=4, restore_best_weights = True) 

model.fit(
    X_train, Y_train,
    validation_data=(X_test, Y_test),
    epochs=15,
    batch_size=128,
    verbose=2,
    # callbacks=[checkpoint_cb, early_stopping_cb]
)

print("\nTrain Acc: ", model.evaluate(X_train, Y_train)[1])
print("Test Acc: ", model.evaluate(X_test, Y_test)[1])
# Train Acc:  0.9941666722297668
# 313/313 ━━━━━━━━━━━━━━━━━━━━ 1s 2ms/step - accuracy: 0.9865 - loss: 0.0524     
# Test Acc:  0.9865000247955322
model.save("../models/mnist_model.keras")
