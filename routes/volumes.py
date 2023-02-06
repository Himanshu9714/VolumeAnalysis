import json
import os
import tempfile

from flask import Blueprint, abort, current_app, request
from flask.views import MethodView

from ..utils import (
    NpEncoder,
    create_dataframe_from_json,
    loss_occurred_range,
    profit_occurred_range,
    signal_occurred_range,
)

# Create blueprint for the volumes
api = Blueprint("volumes", __name__)


class VolumeAvg(MethodView):
    def post(self):

        # Get the signal data json file
        file1 = request.files["signal_data"]
        # Get the historical data json file
        file2 = request.files["historical_data"]
        # Get no. of candle for which range should be find
        no_of_candles = request.args.get("candle")

        # If no. of candle is not passed in the request, get from the app configuration
        if not no_of_candles:
            no_of_candles = current_app.config["NO_OF_CANDLES"]

        # Check if both files are passed or not.
        if file1.filename == "":
            abort(400, message=f"You must select the file!")
        if file2.filename == "":
            abort(400, message=f"You must select the file!")

        # Create temporary directory
        tmpdir = tempfile.mkdtemp()

        # Store signal data and historical data files in the tempdir
        file1_path = os.path.join(tmpdir, file1.filename)
        file1.save(file1_path)
        file2_path = os.path.join(tmpdir, file2.filename)
        file2.save(file2_path)

        # Create signal and historical data dataframe
        historical_df = create_dataframe_from_json(file1_path, is_hist=True)
        signal_df = create_dataframe_from_json(file2_path, is_signal=True)

        # Calculate the avg of volume and returns the response
        volumes = {
            "volume1": signal_occurred_range(signal_df, historical_df, no_of_candles),
            "volume2": profit_occurred_range(signal_df, historical_df, no_of_candles),
            "volume3": loss_occurred_range(signal_df, historical_df, no_of_candles),
        }

        # Dump the result
        return json.dumps(volumes, cls=NpEncoder)


class IndexView(MethodView):
    pass


api.add_url_rule("/volumes", view_func=VolumeAvg.as_view("Volumes"))
api.add_url_rule("/", view_func=IndexView.as_view("Index"))
