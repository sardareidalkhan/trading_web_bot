# train_model.py

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Flatten, Concatenate, Conv2D, MaxPooling2D
from tensorflow.keras.optimizers import Adam
from docx import Document
from PIL import Image
import io

# 📁 Input datasets and output model folder
DATASET_ROOT = "dataset"
MODEL_OUTPUT_DIR = "EXTRA_THINGS/all_dataset"
os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)

# 🏷️ Labels used for classification
CLASSES = ["UP", "DOWN", "NO_SIGNAL"]

# 📐 All images will be resized to this size
IMG_SIZE = (128, 128)


def extract_image_pairs_from_docx(docx_path):
    try:
        doc = Document(docx_path)
    except Exception as e:
        print(f"❌ Error reading {docx_path}: {e}")
        return []

    image_pairs = []
    full_img = None

    for rel in doc.part._rels:
        rel = doc.part._rels[rel]
        if "image" in rel.target_ref:
            try:
                img_data = rel.target_part.blob
                img = Image.open(io.BytesIO(img_data)).convert('RGB')
                img = img.resize(IMG_SIZE)
                img = np.array(img) / 255.0

                if full_img is None:
                    full_img = img
                else:
                    image_pairs.append((full_img, img))  # (full, cropped)
                    full_img = None
            except Exception as e:
                print(f"⚠️ Skipping invalid image in {docx_path}: {e}")
                continue

    return image_pairs


def load_data_for_timeframe(timeframe):
    folder_path = os.path.join(DATASET_ROOT, f"{timeframe}_dataset")
    X_full, X_cropped, y = [], [], []

    for class_idx, label in enumerate(CLASSES):
        doc_path = os.path.join(folder_path, f"{timeframe}_{label}.docx")
        if not os.path.exists(doc_path):
            print(f"⚠️ File not found: {doc_path}")
            continue

        pairs = extract_image_pairs_from_docx(doc_path)
        if not pairs:
            print(f"⚠️ No valid image pairs in {doc_path}")
            continue

        for full_img, cropped_img in pairs:
            X_full.append(full_img)
            X_cropped.append(cropped_img)
            y.append(class_idx)

    if not X_full:
        return None, None, None

    return (
        np.array(X_full),
        np.array(X_cropped),
        tf.keras.utils.to_categorical(y, num_classes=3)
    )


def build_hybrid_model():
    def cnn_branch():
        input_layer = Input(shape=(128, 128, 3))
        x = Conv2D(32, (3, 3), activation='relu')(input_layer)
        x = MaxPooling2D((2, 2))(x)
        x = Conv2D(64, (3, 3), activation='relu')(x)
        x = MaxPooling2D((2, 2))(x)
        x = Flatten()(x)
        return input_layer, x

    input_full, encoded_full = cnn_branch()
    input_crop, encoded_crop = cnn_branch()

    combined = Concatenate()([encoded_full, encoded_crop])
    dense = Dense(128, activation='relu')(combined)
    output = Dense(3, activation='softmax')(dense)

    model = Model(inputs=[input_full, input_crop], outputs=output)
    model.compile(optimizer=Adam(1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
    return model


def train_models_for_all_timeframes():
    timeframes = [
        "5s", "10s", "15s", "30s", "1m", "2m", "3m", "5m",
        "10m", "15m", "30m", "1h", "4h", "1d"
    ]

    for tf_str in timeframes:
        print(f"\n🧠 Training model for timeframe: {tf_str}")
        X_full, X_cropped, y = load_data_for_timeframe(tf_str)

        if X_full is None or len(X_full) == 0:
            print(f"⛔ Skipped {tf_str}: No training data.")
            continue

        model = build_hybrid_model()
        model.fit([X_full, X_cropped], y, epochs=10, batch_size=8)

        model_path = os.path.join(MODEL_OUTPUT_DIR, f"model_{tf_str}.h5")
        model.save(model_path)
        print(f"✅ Model saved to: {model_path}")


if __name__ == "__main__":
    train_models_for_all_timeframes()
