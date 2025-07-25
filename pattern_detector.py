# ✅ pattern_detector.py (Multi-user Safe Version)

import os
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# Constants
MODEL_DIR = os.path.join("EXTRA_THINGS", "all_dataset")
LABELS = ["DOWN", "NO_SIGNAL", "UP"]
LOADED_MODELS = {}  # Model cache

def preprocess_image(path, target_size=(128, 128)):
    print(f"📸 Loading image: {path}")
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return None
    try:
        img = load_img(path, target_size=target_size)
        img = img_to_array(img) / 255.0
        print(f"✅ Image loaded & resized to {target_size}")
        return img
    except Exception as e:
        print(f"❌ Error loading image {path}: {e}")
        return None

def load_timeframe_model(timeframe):
    model_path = os.path.join(MODEL_DIR, f"model_{timeframe}.h5")
    if model_path in LOADED_MODELS:
        return LOADED_MODELS[model_path]

    print(f"📦 Loading model from: {model_path}")
    if not os.path.exists(model_path):
        print(f"❌ Model not found for timeframe '{timeframe}'")
        return None
    try:
        model = load_model(model_path)
        LOADED_MODELS[model_path] = model
        print("✅ Model loaded successfully & cached")
        return model
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return None

def predict(timeframe="1m", image_dir="."):
    print("\n🔍 Starting Prediction Process")

    model = load_timeframe_model(timeframe)
    if model is None:
        print("🚫 No model available. Cannot continue.")
        return "NO_SIGNAL"

    full_path = os.path.join(image_dir, "chart.png")
    crop_path = os.path.join(image_dir, "cropped_chart.png")

    print("🗼 Preparing images...")
    full_img = preprocess_image(full_path)
    cropped_img = preprocess_image(crop_path)

    if full_img is None or cropped_img is None:
        print("🚫 Missing images. Cannot continue.")
        return "NO_SIGNAL"

    input_data = [
        np.expand_dims(full_img, axis=0),
        np.expand_dims(cropped_img, axis=0)
    ]

    print("🤖 Making prediction...")
    try:
        preds = model.predict(input_data, verbose=0)
        print(f"📊 Raw prediction output: {preds}")
        label_index = np.argmax(preds[0])
        prediction = LABELS[label_index]
        confidence = float(np.max(preds[0])) * 100

        print(f"✅ Final Prediction: {prediction}")
        print(f"🎯 Confidence: {confidence:.2f}%")
        return prediction
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        return "NO_SIGNAL"

# For manual test
if __name__ == "__main__":
    result = predict(timeframe="1m", image_dir="temp_data")
    print(f"\n🎉 Prediction result: {result}")
