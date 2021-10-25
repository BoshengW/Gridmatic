import numpy as np
import pygrib


def extract_grib_temperature(filename):
    grbs = pygrib.open(filename)
    grb = grbs.select(shortName="2t")[0]
    return grb.data(lat1=41, lat2=41, lon1=254, lon2=254)[0][0][0]


def fit_model(past_temperature, past_load):
    """Fits a simple linear regression model using provided data."""
    x = np.array(past_temperature).reshape(-1, 1)
    y = np.array(past_load).reshape(-1)
    return np.linalg.solve(x.T @ x, x.T @ y)


def predict_model(future_temperature, theta):
    x = np.array(future_temperature).reshape(-1, 1)
    return x @ theta
