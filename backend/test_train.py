import os
import sys

backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
app_path = os.path.join(backend_path, "app")
if app_path not in sys.path:
    sys.path.insert(0, app_path)

from ml.train import train_home_lstm

res = train_home_lstm("home_shivani_1")
print(res)
