import os
import sys

# Ensure root backend dir is in search path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
app_path = os.path.join(backend_path, "app")
if app_path not in sys.path:
    sys.path.insert(0, app_path)

import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.optimizers import Adam

def train_lstm():
    print("Loading training dataset from Supabase...")
    from app.db.connection import SessionLocal
    from app.db.models import TrainingRecord
    import json
    
    db = SessionLocal()
    try:
        records = db.query(TrainingRecord).order_by(TrainingRecord.date.asc()).all()
        if not records:
            print("Error: No training records found in database.")
            return
            
        print(f"Loaded {len(records)} training records from Supabase.")
        
        # Reconstruct DataFrame from database rows
        data = []
        for r in records:
            features = json.loads(r.features_json)
            targets = json.loads(r.targets_json)
            
            row = {
                "home_id": r.home_id,
                "date": r.date
            }
            row.update(features)
            row.update(targets)
            data.append(row)
            
        df = pd.DataFrame(data)
    finally:
        db.close()

    # Let's extract runtime columns
    runtime_cols = [col for col in df.columns if col.endswith('_runtime') and not col.startswith('next_day_')]
    print(f"Detected {len(runtime_cols)} device categories for forecasting.")

    # Prepare sequences (X: 30 days of history, y: next day runtime)
    # Since our training dataset is structured as: today's runtime + features -> next_day_runtime,
    # we can train a model to map the input features to the target values.
    # To satisfy the "previous 30 days runtime history" constraint, we can group by home_id
    # and create sliding window sequences of length 30.
    
    X = []
    y = []
    
    # Let's do a fast grouping to generate some training samples
    # We will sample sequence data for the LSTM
    print("Preparing sequence data for LSTM...")
    for home_id, group in df.groupby('home_id'):
        group = group.sort_values('date')
        runtimes = group[runtime_cols].values # shape (days, features)
        
        if len(runtimes) < 31:
            continue
            
        for i in range(len(runtimes) - 30):
            X.append(runtimes[i:i+30])
            y.append(runtimes[i+30])
            
    X = np.array(X)
    y = np.array(y)
    
    print(f"Prepared sequence data: X shape = {X.shape}, y shape = {y.shape}")

    # Build LSTM model
    # X shape: (samples, timesteps=30, features=len(runtime_cols))
    # y shape: (samples, features)
    model = Sequential([
        LSTM(64, input_shape=(30, len(runtime_cols)), return_sequences=False),
        Dense(64, activation='relu'),
        Dense(len(runtime_cols)) # predict next day runtimes for all device types
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
    
    # Train on a small number of epochs for speed and demo validation
    print("Training LSTM model (this may take a moment)...")
    epochs = 2
    batch_size = 64
    
    # Train on a slice of data to be fast and memory friendly
    if len(X) > 2000:
        indices = np.random.choice(len(X), 2000, replace=False)
        X_train = X[indices]
        y_train = y[indices]
    else:
        X_train = X
        y_train = y
        
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=1)
    
    # Save the model
    model_dir = os.path.join(backend_path, "ml", "models")
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "lstm_model.keras")
    model.save(model_path)
    print(f"Model saved successfully at {model_path}!")

def train_home_lstm(home_id: str):
    import pandas as pd
    import json
    from app.db.connection import SessionLocal
    from app.db.models import DeviceDailySummary, Device
    from ml.predict import DEVICE_CATEGORIES
    
    db = SessionLocal()
    try:
        # Get all devices in this home to map device_id to category
        devices = db.query(Device).filter(Device.home_id == home_id).all()
        if not devices:
            return {"success": False, "message": "No devices found for this home."}
            
        device_id_map = {d.id: d.device_type.lower().replace(" ", "_") for d in devices}
        
        # Get all daily summaries for this home
        summaries = db.query(DeviceDailySummary).filter(DeviceDailySummary.home_id == home_id).all()
        if not summaries:
            return {"success": False, "message": "No consumption history found for this home."}
            
        # Build list of rows
        data = []
        for s in summaries:
            cat = device_id_map.get(s.device_id)
            if cat:
                data.append({
                    "date": s.date,
                    "category": cat,
                    "runtime": s.runtime_hours
                })
        
        if not data:
            return {"success": False, "message": "No category-mapped runtime data found."}
            
        df = pd.DataFrame(data)
        # Pivot: index=date, columns=category, values=runtime
        df_pivot = df.pivot_table(index="date", columns="category", values="runtime", aggfunc="max").fillna(0.0)
        
        # Ensure all DEVICE_CATEGORIES are present in the columns
        for cat in DEVICE_CATEGORIES:
            if cat not in df_pivot.columns:
                df_pivot[cat] = 0.0
                
        # Keep columns in exact order of DEVICE_CATEGORIES
        df_pivot = df_pivot[DEVICE_CATEGORIES]
        
        # Convert to numpy array of shape (days, 24)
        runtimes = df_pivot.values
        
        if len(runtimes) < 31:
            return {"success": False, "message": f"Insufficient data: need at least 31 days of history, currently have {len(runtimes)} days."}
            
        # Prepare sequence windows of length 30
        X = []
        y = []
        for i in range(len(runtimes) - 30):
            X.append(runtimes[i:i+30])
            y.append(runtimes[i+30])
            
        X = np.array(X)
        y = np.array(y)
        
        # Build LSTM
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense
        from tensorflow.keras.optimizers import Adam
        
        model = Sequential([
            LSTM(32, input_shape=(30, len(DEVICE_CATEGORIES)), return_sequences=False),
            Dense(32, activation='relu'),
            Dense(len(DEVICE_CATEGORIES))
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        model.fit(X, y, epochs=5, batch_size=16, verbose=0)
        
        # Save model
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(base_dir, "ml", "models")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f"lstm_model_{home_id}.keras")
        model.save(model_path)
        
        return {"success": True, "message": f"Successfully trained personalized model for home {home_id} using {len(runtimes)} days of history."}
    except Exception as e:
        return {"success": False, "message": f"Training failed: {str(e)}"}
    finally:
        db.close()

if __name__ == "__main__":
    train_lstm()
