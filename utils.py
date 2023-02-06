import json
import os

import numpy as np
import pandas as pd


# Custom json Encoder
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)

        if isinstance(obj, np.floating):
            return float(obj)

        if isinstance(obj, np.ndarray):
            return obj.tolist()

        return super(NpEncoder, self).default(obj)


def create_dataframe_from_json(
    filepath: str, is_hist: bool = False, is_signal: bool = False
) -> pd.DataFrame:

    if not os.path.exists(filepath):
        raise RuntimeError(f"Filepath {filepath} doesn't exist!")

    # Create dataframe from the provided filepath
    df = pd.read_json(filepath)

    # Create historical data df if is_hist flag is true
    if is_hist:
        hist_df = pd.DataFrame(index=pd.to_datetime(df["data"]["time"], unit="s"))
        hist_df["Open"] = df["data"]["olhc"]["open"]
        hist_df["Low"] = df["data"]["olhc"]["low"]
        hist_df["High"] = df["data"]["olhc"]["high"]
        hist_df["Close"] = df["data"]["olhc"]["close"]
        hist_df["Volume"] = df["data"]["olhc"]["volume"]
        return hist_df

    # Create signal data df if is_signal flag is true
    elif is_signal:
        signal_df = pd.DataFrame.from_dict(df["payload"][0]["signals"]).T
        signal_df.index = pd.to_datetime(signal_df.index, unit="s")
        return signal_df

    return df


def avg_volume(
    signal_df: pd.DataFrame, historical_df: pd.DataFrame, no_of_candles: int
):
    volume = []
    for idx in signal_df.index:
        try:
            hist_idx = historical_df.index.get_loc(idx)
        except:
            continue
        rows_before_idx = historical_df[hist_idx - no_of_candles : hist_idx]
        max, min = rows_before_idx["Volume"].max(), rows_before_idx["Volume"].min()
        volume.append([min, max])

    return volume


def signal_occurred_range(
    signal_df: pd.DataFrame, historical_df: pd.DataFrame, no_of_candles: int
):
    volume = avg_volume(signal_df, historical_df, no_of_candles)
    return volume


def profit_occurred_range(
    signal_df: pd.DataFrame, historical_df: pd.DataFrame, no_of_candles: int
):
    profit_occured_signal_df = signal_df[signal_df["result"] == "P"]
    volume = avg_volume(profit_occured_signal_df, historical_df, no_of_candles)

    return volume


def loss_occurred_range(
    signal_df: pd.DataFrame, historical_df: pd.DataFrame, no_of_candles: int
):
    loss_occured_signal_df = signal_df[signal_df["result"] == "L"]
    volume = avg_volume(loss_occured_signal_df, historical_df, no_of_candles)

    return volume
