import os
import sys
import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

TASK_API_BASE_URL = os.environ.get("DATASOURCE_URL", "http://localhost:3000")
INFLUX_URL = os.environ["INFLUX_URL"]
INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]
ORG = os.environ["INFLUX_ORG"]
URL_TEMPLATE = "{base}/api/v1/prices?ticker={ticker}&amount=10&broker=FX&timeframe={tf}"

tickers = ["GBPUSD", "EURUSD"]
timeframes = ["4H", "1D"]


def get_bucket_for_timeframe(timeframe: str) -> str:
    mapping = {
        "1": "prices_1m",
        "5": "prices_5m",
        "15": "prices_15m",
        "30": "prices_30m",
        "45": "prices_45m",
        "60": "prices_1h",
        "120": "prices_2h",
        "180": "prices_3h",
        "240": "prices_4h",
        "4H": "prices_4h",
        "1D": "prices_1d",
        "1W": "prices_1w"
    }
    return mapping.get(timeframe, "prices_default")

print("Connecting to InfluxDB...", INFLUX_URL, INFLUX_TOKEN, ORG, sep="\n")
try:
    client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=ORG)
except Exception as e:
    print(f"Error connecting to InfluxDB: {e}")
    sys.exit(1)

write_api = client.write_api(write_options=SYNCHRONOUS)
print("Connected to InfluxDB:", str(write_api))

for ticker in tickers:
    for tf in timeframes:
        url = URL_TEMPLATE.format(base=TASK_API_BASE_URL, ticker=ticker, tf=tf)
        resp = requests.get(url)
        data = resp.json()["result"]["prices"]

        bucket = get_bucket_for_timeframe(tf)

        for item in data:
            p = Point(item["measurement"]) \
                .tag("ticker", item["ticker"]) \
                .tag("broker", item["broker"]) \
                .tag("timeframe", item["timeframe"]) \
                .field("open", item["open"]) \
                .field("high", item["high"]) \
                .field("low", item["low"]) \
                .field("close", item["close"]) \
                .field("volume", item["volume"]) \
                .time(item["timestamp"], WritePrecision.S)

            write_api.write(bucket=bucket, record=p)
client.close()
