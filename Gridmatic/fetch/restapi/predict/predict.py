from flask import Blueprint
from flask import Response
from flask import request
from . import BP_predict
from flask import current_app
from .. import app

import os
import numpy as np
import pandas as pd
from ..util.data_util import fit_model, predict_model
from ..util.data_util import extract_grib_temperature

import datetime
from datetime import datetime as DT
from bson.json_util import dumps


@BP_predict.route("/train", methods=["GET"])
def train():
    df = pd.read_csv("./DB/TrainData/2021-10-24.csv")
    x = df["temperature"].tolist()
    y = df["Load"].tolist()

    model = fit_model(x, y)
    os.makedirs("./DB/model", exist_ok=True)
    np.save(os.path.join("./DB/model", "model.npy"), model)

    return "Done"

@BP_predict.route("/predict", methods=["POST"])
def predict():
    request_json = request.get_json()
    start = request_json["start"]
    end = request_json["end"]

    start_dt = DT.fromtimestamp(start)
    start_dt -= datetime.timedelta(hours=start_dt.hour - start_dt.hour // 3 * 3)

    end_dt = DT.fromtimestamp(end)
    end_dt -= datetime.timedelta(hours=end_dt.hour - end_dt.hour // 3 * 3)

    dataArr = []

    for _d in range(int((end_dt - start_dt).total_seconds() // 3600 // 3)):
        curr_dt = start_dt + datetime.timedelta(hours=_d * 3)
        filename = os.path.join("./DB/NOAA/", curr_dt.strftime("%Y-%m-%d-%H") + ".grb2")
        dataArr.append(extract_grib_temperature(filename))

    prediction = predict_model(dataArr, app.model)

    response = {}
    response["prediction"] = prediction.tolist()

    return response, 200

