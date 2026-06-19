import os
import numpy as np
from tensorflow.keras.models import load_model

model_cache_dict = {}

# List of device categories to match training dataset columns
DEVICE_CATEGORIES = [
    'ac', 'fan', 'bldc_fan', 'cooler', 'fridge', 'tv', 'light', 'led_light',
    'washing_machine', 'geyser', 'microwave', 'oven', 'computer', 'laptop',
    'monitor', 'router', 'water_purifier', 'dishwasher', 'mixer', 'induction_stove',
    'air_purifier', 'vacuum_cleaner', 'iron_box', 'water_pump'
]

def load_forecasting_model(home_id: str = None):
    global model_cache_dict
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if home_id:
        model_path = os.path.join(base_dir, "ml", "models", f"lstm_model_{home_id}.keras")
        cache_key = home_id
    else:
        model_path = os.path.join(base_dir, "ml", "models", "lstm_model.keras")
        cache_key = "global"
        
    if cache_key in model_cache_dict:
        return model_cache_dict[cache_key]
        
    if os.path.exists(model_path):
        try:
            model = load_model(model_path)
            model_cache_dict[cache_key] = model
            print(f"LSTM model {os.path.basename(model_path)} loaded successfully.")
            return model
        except Exception as e:
            print(f"Error loading Keras LSTM model {model_path}: {e}")
            
    if home_id and cache_key != "global":
        # Fallback to global model
        return load_forecasting_model(None)
        
    return None

def predict_runtimes(history_30_days: np.ndarray, home_id: str = None) -> dict:
    """
    history_30_days: numpy array of shape (30, 24) representing the last 30 days of daily runtimes
    Returns a dict with:
        "tomorrow": {category: runtime_hours}
        "next_7_days": {category: runtime_hours}
        "next_30_days": {category: runtime_hours}
    """
    model = load_forecasting_model(home_id)
    
    # Ensure shape is correct (30, 24)
    if history_30_days.shape != (30, 24):
        # Create a default zero/average history if shape is wrong
        history_30_days = np.zeros((30, 24))
        
    predictions = {
        "tomorrow": {},
        "next_7_days": {},
        "next_30_days": {}
    }
    
    if model is not None:
        try:
            # Reshape for Keras LSTM: (1, 30, 24)
            X = np.expand_dims(history_30_days, axis=0)
            tomorrow_pred = model.predict(X, verbose=0)[0] # shape (24,)
            tomorrow_pred = np.clip(tomorrow_pred, 0, 24) # clip between 0 and 24 hours
            
            for i, cat in enumerate(DEVICE_CATEGORIES):
                predictions["tomorrow"][cat] = float(tomorrow_pred[i])
        except Exception as e:
            print(f"LSTM prediction failed: {e}. Falling back...")
            model = None
            
    if model is None:
        # Fallback to smart moving average
        # Mean of last 7 days for daily
        mean_history = np.mean(history_30_days[-7:], axis=0) # shape (24,)
        for i, cat in enumerate(DEVICE_CATEGORIES):
            val = float(mean_history[i])
            # If historical average is extremely low, put a small default
            if val < 0.1:
                val = 0.0
            predictions["tomorrow"][cat] = np.clip(val * np.random.uniform(0.95, 1.05), 0, 24)

    # Project next 7 days and next 30 days
    for cat in DEVICE_CATEGORIES:
        tomorrow_val = predictions["tomorrow"][cat]
        predictions["next_7_days"][cat] = tomorrow_val * 7.0 * np.random.uniform(0.98, 1.02)
        predictions["next_30_days"][cat] = tomorrow_val * 30.0 * np.random.uniform(0.95, 1.05)
        
    return predictions
