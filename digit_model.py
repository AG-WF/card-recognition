<<<<<<< HEAD
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers

def build_digit_model(input_shape=(28, 28, 1), num_classes=10):
    """带数据增强和正则化的 CNN 模型"""
    # ✅ 数据增强层（直接放在模型最前面）
    data_augmentation = tf.keras.Sequential([
        layers.RandomRotation(0.1),        # 随机旋转 ±10%
        layers.RandomTranslation(0.1, 0.1),# 平移
        layers.RandomZoom(0.1),            # 缩放
        layers.RandomContrast(0.1)         # 对比度扰动
    ])

    inputs = tf.keras.Input(shape=input_shape)
    x = data_augmentation(inputs)  # ← 增强输入

    # Block 1
    x = layers.Conv2D(32, (3, 3), padding='same', kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.1)(x)
    x = layers.MaxPooling2D((2, 2))(x)

    # Block 2
    x = layers.Conv2D(64, (3, 3), padding='same', kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.1)(x)
    x = layers.MaxPooling2D((2, 2))(x)

    # Block 3
    x = layers.Conv2D(128, (3, 3), padding='same', kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.1)(x)
    x = layers.GlobalAveragePooling2D()(x)

    # Dense
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu')(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = models.Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model
=======
import tensorflow as tf
from tensorflow.keras import layers, models, regularizers

def build_digit_model(input_shape=(28, 28, 1), num_classes=10):
    """带数据增强和正则化的 CNN 模型"""
    # ✅ 数据增强层（直接放在模型最前面）
    data_augmentation = tf.keras.Sequential([
        layers.RandomRotation(0.1),        # 随机旋转 ±10%
        layers.RandomTranslation(0.1, 0.1),# 平移
        layers.RandomZoom(0.1),            # 缩放
        layers.RandomContrast(0.1)         # 对比度扰动
    ])

    inputs = tf.keras.Input(shape=input_shape)
    x = data_augmentation(inputs)  # ← 增强输入

    # Block 1
    x = layers.Conv2D(32, (3, 3), padding='same', kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.1)(x)
    x = layers.MaxPooling2D((2, 2))(x)

    # Block 2
    x = layers.Conv2D(64, (3, 3), padding='same', kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.1)(x)
    x = layers.MaxPooling2D((2, 2))(x)

    # Block 3
    x = layers.Conv2D(128, (3, 3), padding='same', kernel_regularizer=regularizers.l2(1e-4))(x)
    x = layers.BatchNormalization()(x)
    x = layers.LeakyReLU(alpha=0.1)(x)
    x = layers.GlobalAveragePooling2D()(x)

    # Dense
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu')(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = models.Model(inputs, outputs)

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model
>>>>>>> 7c0d237040bb9cd6020f9c462b51475ec2f09b0d
