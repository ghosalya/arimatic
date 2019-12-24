import io
import base64
import numpy as np
import pandas as pd

# taken from
# https://towardsdatascience.com/machine-learning-part-19-time-series-and-autoregressive-integrated-moving-average-model-arima-c1005347b0d7
from statsmodels.tsa.stattools import adfuller
# from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA


def read_data_file(contents, filename):
    _, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)

    if "csv" in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
    elif "xls" in filename:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded))

    # for now, assume columns[-1] as y_column
    y_column = df.columns[-1]
    df, form = get_most_stationary(df, y_column)
    arima_df = get_arima_prediction(df, y_column, form)
    return arima_df


def get_most_stationary(df, y_column):
    if check_stationary(df, y_column):
        return (df, "original")

    df_log = df[:]
    df_log[y_column] = np.log(df[y_column])
    if check_stationary(df_log, y_column):
        return (df_log, "log")

    print("No stationary, returning original")
    return (df, "original")


def check_stationary(df, y_column):
    # Using Dickey-Fuller test
    result = adfuller(df[y_column])
    adf = result[0]
    print(f"ADF: {adf}")
    return adf < 0.05


def get_arima_prediction(df, y_column, form):
    model = ARIMA(df[y_column], order=(2, 0, 1))
    results = model.fit(disp=-1)

    if form == "original":
        pred = results.predict(1, len(df)*2)
        print(pred)
        return pred
    elif form == "log":
        return np.exp(results.predict(1, len(df)*2))
