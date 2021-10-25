from flask import Blueprint
from flask import Response
from flask import request

import os
from os.path import join
import requests
from . import BP_fetch
from flask import current_app

import datetime
from datetime import date
from datetime import datetime as DT

def diffHrs(date1, date2):
    diff = date2 - date1
    hours = diff.days * 24 + diff.seconds // 3600
    return hours

def cvtInt2Str(cvtHour):
    digit = ""
    while(len(digit)<3):
        digit += str(cvtHour%10)
        cvtHour = cvtHour//10
    return digit[::-1]

def download_file(url, filename, dataset):
    # check if file exist
    if not os.path.isfile(filename):
        print('Downloading File...')
        response = requests.get(url)

        storage_dir = join("./DB/", dataset)
        os.makedirs(storage_dir, exist_ok=True)

        # check response status
        if response.status_code == 200:
            # open file and write the content
            filename = join(storage_dir, filename)
            with open(filename, 'wb') as file:
                # A chunk of 128 bytes
                for chunk in response:
                    file.write(chunk)
            print("File - " + filename + " downloaded")
        else:
            print('Error for download caused by File not exist or Connection, plz check' + url)
    else:
        print('File exists')

def findLatestData():
    ## get today 00:00
    ## latest data should be from 2 lag
    for lag in [2,3]:
        startTList = ["_0000_", "_0600_", "_1200_", "_1800_"]

        lagDate = date.today() - datetime.timedelta(lag)
        latestFilePath = str(lagDate.year) + str(lagDate.month) + "/" + lagDate.strftime("%Y%m%d") + "/"
        cvtHour = 6 + (lag-1)*24 ## firstly check 1800 init time if not then +6
        ## check if file exist
        url = "https://www.ncei.noaa.gov/data/global-forecast-system/access/grid-003-1.0-degree/forecast/" + latestFilePath
        i = 3
        while(i>=0):
            filename = "gfs_3_" + lagDate.strftime("%Y%m%d") + startTList[i] + cvtInt2Str(cvtHour) + ".grb2"
            response = requests.get(url + filename)
            # check response status
            if response.status_code == 200:
                # open file and write the content
                print("Lastest dataset file found, start downloading")
                print(url + filename)
                path = url + "gfs_3_" + lagDate.strftime("%Y%m%d") + startTList[i]

                ## convert reference date into real date (20211021 1800 +6 -> 20211022 0000)
                realdateRef = datetime.datetime(lagDate.year, lagDate.month, lagDate.day, i*6, 0)
                print(realdateRef)
                return [path, realdateRef, cvtHour]
            else:
                pass
            i-=1
            cvtHour+=6
    return None

@BP_fetch.route("/health")
def fetch():
    return "Fetching Service is Runing"

@BP_fetch.route("/downloadNYISO/<setdate>", methods=["GET"])
def dailyNYISODownloadJob(setdate):
    dateRange = setdate
    if dateRange=="current":
        today = date.today()
        curr = today.strftime("%Y%m%d")
    else:
        curr = dateRange

    url = current_app.config["NYISO_URL"] + curr + "pal.csv"
    filename = "load_date" + curr + ".csv"
    response = Response(status=200)

    try:
        download_file(url, filename, "NYISO")
    except Exception as e:
        print(e)
        print("Download Failed, URL: " + url)

    return "response", 200

@BP_fetch.route("/downloadNOAA", methods=["POST"])
def dailyNOAADownloadJob():
    try:
        request_json = request.get_json()
        start = request_json["start"]
        end = request_json["end"]

        ## first find the latest dataset grsb reference
        path, realtimeRef, cvtHour = findLatestData()

        ## cvtHour is the hour (+3/+6/..) from reference (0000/0600/1200/1800)

        start_obj = DT.fromtimestamp(start)
        end_obj = DT.fromtimestamp(end)

        midnight = DT.combine(date.today(), DT.min.time())
        start_diff_hrs = diffHrs(midnight, start_obj)
        end_diff_hrs = diffHrs(midnight, end_obj)

        ## get current diff hour
        start_hrs = (midnight.hour + start_diff_hrs) // 3 * 3
        end_hrs = (midnight.hour + end_diff_hrs) // 3 * 3

        for hrs in range(start_hrs, end_hrs + 1, 3):
            curr_hrs = cvtHour + hrs
            print("ref:" + str(cvtHour) + "hrs: " + str(hrs))
            url = path + cvtInt2Str(curr_hrs) + ".grb2"

            ## use real time after conversion as filename
            realtime = realtimeRef + datetime.timedelta(hours=curr_hrs)
            filename = realtime.strftime("%Y-%m-%d-%H") + ".grb2"
            print(realtime.strftime("%Y-%m-%d-%H") + ".grb2")
            download_file(url, filename, "NOAA")

        return Response(status=200)

    except Exception as e:
        print(e)
        print("download failed")
        return Response(status=400)