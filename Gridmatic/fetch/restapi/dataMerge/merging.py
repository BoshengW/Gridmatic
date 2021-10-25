import os.path

from flask import Blueprint
from flask import Response
from flask import request
from . import BP_merge
from flask import current_app

import pandas as pd
from ..util.data_util import extract_grib_temperature

import datetime
from datetime import date
from datetime import datetime as DT

from bson.json_util import dumps

@BP_merge.route("/mergeByTS", methods=["POST"])
def mergeNOAAByTS():
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

    response = {}
    response["NOAA"] = dataArr

    return dumps(response)

def cvtHour(hour):
    digit = ""
    while(len(digit)<2):
        digit += str(hour%10);
        hour = hour // 10
    return digit[::-1]

@BP_merge.route("/mergeTwoData/<setdate>", methods=["GET"])
def mergeTwoData(setdate):
    dateRange = setdate
    if dateRange == "current":
        today = date.today()
        curr = today.strftime("%Y%m%d")
        curr2 = today.strftime("%Y-%m-%d")
    else:
        curr = dateRange.replace("-","")
        curr2 = dateRange
        print(curr2)

    ## each time merge NYISO and NOAA into one dateframe and load into csv
    df_loaddata = pd.read_csv("./DB/NYISO/load_date" + curr +".csv")
    df_nyc = df_loaddata[df_loaddata.Name == "N.Y.C."]

    tempurList = []
    for idx in range(df_nyc.shape[0]):
        hr = int(df_nyc["Time Stamp"].iloc[idx].split(" ")[1].split(":")[0])//3*3
        filename = "./DB/NOAA/" + curr2 + "-" + cvtHour(hr) + ".grb2"
        tempurList.append(extract_grib_temperature(filename))


    df_nyc["temperature"] = tempurList
    # filename = os.path.join("./DB/NOAA/", curr_dt.strftime("%Y-%m-%d-%H") + ".grb2")
    os.makedirs("./DB/TrainData/", exist_ok=True)
    df_nyc.to_csv(os.path.join("./DB/TrainData/", curr2 +".csv"))

    return "Merged NYISO + NOAA Dataset -> Date: " + curr2




