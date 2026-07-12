<<<<<<< HEAD
# file: train_digit_model.py
import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

DATASET_DIR = "dataset"
MODEL_PATH = "digit_recognizer.h5"
IMG_SIZE = 28

def load_dataset(dataset_dir=DATASET_DIR):
    X, y = [], []
    for label in range(10):
        folder = os.path.join(dataset_dir, str(label))
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            path = os.path.join(folder, fname)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            X.append(img)
            y.append(label)
    X = np.array(X, dtype="float32") / 255.0
    X = np.expand_dims(X, -1)
    y = np.array(y, dtype="int32")
    print(f"✅ 加载完成: {len(X)} 张数字样本")
    return X, y


def build_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation="relu", input_shape=(IMG_SIZE, IMG_SIZE, 1)),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Conv2D(64, (3, 3), activation="relu"),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Conv2D(128, (3, 3), activation="relu"),
        BatchNormalization(),
        Flatten(),

        Dense(256, activation="relu"),
        Dropout(0.5),
        Dense(10, activation="softmax")
    ])
    model.compile(optimizer=Adam(1e-3),
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])
    return model


def train_model():
    X, y = load_dataset()
    y_cat = to_categorical(y, 10)
    X_train, X_val, y_train, y_val = train_test_split(X, y_cat, test_size=0.2, random_state=42)

    # 数据增强：轻微旋转、亮度扰动
    datagen = ImageDataGenerator(
        rotation_range=5,
        width_shift_range=0.05,
        height_shift_range=0.05,
        brightness_range=[0.7, 1.3]
    )
    datagen.fit(X_train)

    model = build_model()
    print("🚀 开始训练模型...")

    history = model.fit(
        datagen.flow(X_train, y_train, batch_size=64),
        epochs=1000,
        validation_data=(X_val, y_val)
    )

    model.save(MODEL_PATH)
    print(f"✅ 模型已保存: {MODEL_PATH}")

    acc = history.history["val_accuracy"][-1]
    print(f"📈 最终验证准确率: {acc*100:.2f}%")

    return model


if __name__ == "__main__":
    train_model()
=======
# file: train_digit_model.py
import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split

DATASET_DIR = "dataset"
MODEL_PATH = "digit_recognizer.h5"
IMG_SIZE = 28

def load_dataset(dataset_dir=DATASET_DIR):
    X, y = [], []
    for label in range(10):
        folder = os.path.join(dataset_dir, str(label))
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            path = os.path.join(folder, fname)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
            X.append(img)
            y.append(label)
    X = np.array(X, dtype="float32") / 255.0
    X = np.expand_dims(X, -1)
    y = np.array(y, dtype="int32")
    print(f"✅ 加载完成: {len(X)} 张数字样本")
    return X, y


def build_model():
    model = Sequential([
        Conv2D(32, (3, 3), activation="relu", input_shape=(IMG_SIZE, IMG_SIZE, 1)),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Conv2D(64, (3, 3), activation="relu"),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Conv2D(128, (3, 3), activation="relu"),
        BatchNormalization(),
        Flatten(),

        Dense(256, activation="relu"),
        Dropout(0.5),
        Dense(10, activation="softmax")
    ])
    model.compile(optimizer=Adam(1e-3),
                  loss="categorical_crossentropy",
                  metrics=["accuracy"])
    return model


def train_model():
    X, y = load_dataset()
    y_cat = to_categorical(y, 10)
    X_train, X_val, y_train, y_val = train_test_split(X, y_cat, test_size=0.2, random_state=42)

    # 数据增强：轻微旋转、亮度扰动
    datagen = ImageDataGenerator(
        rotation_range=5,
        width_shift_range=0.05,
        height_shift_range=0.05,
        brightness_range=[0.7, 1.3]
    )
    datagen.fit(X_train)

    model = build_model()
    print("🚀 开始训练模型...")

    history = model.fit(
        datagen.flow(X_train, y_train, batch_size=64),
        epochs=1000,
        validation_data=(X_val, y_val)
    )

    model.save(MODEL_PATH)
    print(f"✅ 模型已保存: {MODEL_PATH}")

    acc = history.history["val_accuracy"][-1]
    print(f"📈 最终验证准确率: {acc*100:.2f}%")

    return model


if __name__ == "__main__":
    train_model()
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
