import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')

if gpus:
    print(f"Num GPUs Available: {len(gpus)}")
    print(gpus)
    # 메모리 사용을 유연하게 설정 (선택 사항, 충돌 방지)
    tf.config.experimental.set_memory_growth(gpus[0], True)
else:
    print("Num GPUs Available: 0. GPU is still not detected.")