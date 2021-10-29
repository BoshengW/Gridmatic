import os
from flask import Flask
from flask_cors import CORS
from logging.config import fileConfig
from .dataFetch import BP_fetch
from .dataMerge import BP_merge
from .predict import BP_predict
import numpy as np

import time
import atexit
import requests

from .util.data_util import fit_model
import pandas as pd

from apscheduler.schedulers.background import BackgroundScheduler
## Schedulor
def daily_train_job():
    df = pd.read_csv("./DB/TrainData/2021-10-24.csv")
    x = df["temperature"].tolist()
    y = df["Load"].tolist()

    model = fit_model(x, y)
    os.makedirs("./DB/model", exist_ok=True)
    np.save(os.path.join("./DB/model", "model.npy"), model)

def daily_merge_job():
    try:
        print("daily dataset merging start ---")
        requests.get("http://localhost:5050/mergeTwoData/current/")
        print("daily dataset merging finish ---")
    except Exception as e:
        print("job failed: " + e)

def daily_NYISO_download_job():
    try:
        print("daily NYISO download job start ---")
        requests.get("http://localhost:5050/downloadNYISO/current/")
        print("daily NYISO download job finish ---")
    except Exception as e:
        print("job failed: " + e)

# scheduler = BackgroundScheduler()
# scheduler.add_job(func=daily_train_job, trigger="interval", hours=24)
# scheduler.add_job(func=daily_merge_job, trigger="interval", hours=24)
# scheduler.start()

### config init for logging
# fileConfig('./config/logging.conf')

### load model
model = np.load("./DB/model/model.npy")

def create_app():
    try:
        app = Flask(__name__)
        app.config.from_pyfile("settings.py")
        CORS(app)  ## cross region 跨域处理
        register_blueprint(app)
        app.logger.info('DataFetch Service Initialize Successfully!')

    except Exception as e:
        app.logger.error(e)

    return app

def register_blueprint(app):
    try:
        app.register_blueprint(BP_fetch)
        app.register_blueprint(BP_merge)
        app.register_blueprint(BP_predict)
    except Exception as e:
        app.logger.error(e)

app = create_app()
# atexit.register(lambda: scheduler.shutdown())