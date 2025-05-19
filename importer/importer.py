import sys
from typing import Dict, Any
from pathlib import Path

# Add the parent directory to the Python path so that 'importer' can be found as a package
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from loguru import logger

from importer.config import Config

# Configure loguru to write to standard output
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="{time} | {level} | {message}")


class PriceImporter:
    """Class to handle the price import process."""

    def __init__(self, config: Config):
        """
        Initialize the price importer with configuration.

        Args:
            config (Config): Configuration object
        """
        self.config = config
        self.influx_client = None
        self.write_api = None

    @staticmethod
    def get_bucket_for_timeframe(timeframe: str) -> str:
        """
        Map a timeframe to its corresponding InfluxDB bucket name.

        Args:
            timeframe (str): The timeframe identifier

        Returns:
            str: The corresponding bucket name
        """
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

    @staticmethod
    def process_price_data(item: Dict[str, Any], bucket: str, write_api) -> None:
        """
        Process a single price data item and write it to InfluxDB.

        Args:
            item (dict): The price data item to process
            bucket (str): The InfluxDB bucket to write to
            write_api: The InfluxDB write API client
        """
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

        logger.debug(f"Writing price data to InfluxDB bucket: {bucket}")
        write_api.write(bucket=bucket, record=p)
        logger.success(f"Successfully wrote price data to InfluxDB bucket: {bucket}")

    def connect_to_influxdb(self, token: str) -> None:
        """
        Connect to InfluxDB using the provided token.

        Args:
            token (str): InfluxDB authentication token

        Raises:
            SystemExit: If connection fails
        """
        logger.info(f"Connecting to InfluxDB at {self.config.influx_url} with organization {self.config.influx_org}")
        try:
            self.influx_client = InfluxDBClient(
                url=self.config.influx_url,
                token=token,
                org=self.config.influx_org
            )
            self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
            logger.success(f"Connected to InfluxDB: {str(self.write_api)}")
        except Exception as if_exc:
            logger.error(f"Error connecting to InfluxDB: {if_exc}")
            raise SystemExit(1)

    def fetch_and_store_prices(self) -> None:
        """Fetch prices for all configured tickers and timeframes and store them in InfluxDB."""
        for ticker_entry in self.config.tickers:
            # Parse BROKER:TICKER format
            parts = ticker_entry.split(":", 1)
            if len(parts) != 2:
                logger.warning(f"Invalid ticker format '{ticker_entry}', skipping")
                continue

            broker, ticker = parts

            for tf in self.config.timeframes:
                self._process_ticker_timeframe(broker, ticker, tf)

    def _process_ticker_timeframe(self, broker: str, ticker: str, timeframe: str) -> None:
        """
        Process a single ticker and timeframe combination.

        Args:
            broker (str): The broker identifier
            ticker (str): The ticker symbol
            timeframe (str): The timeframe identifier
        """
        bucket = self.get_bucket_for_timeframe(timeframe)
        url = self.config.url_template.format(
            base=self.config.datasource_url,
            ticker=ticker,
            broker=broker,
            tf=timeframe
        )

        try:
            resp = requests.get(url)
            resp.raise_for_status()  # Raise exception for HTTP errors
            data = resp.json()["result"]["prices"]

            for item in data:
                self.process_price_data(item, bucket, self.write_api)
        except requests.RequestException as e:
            logger.error(f"Error fetching data for {broker}:{ticker} at timeframe {timeframe}: {e}")
        except (KeyError, ValueError) as e:
            logger.error(f"Error processing data for {broker}:{ticker} at timeframe {timeframe}: {e}")

    def close(self) -> None:
        """Close the InfluxDB client connection."""
        if self.influx_client:
            self.influx_client.close()
            logger.info("Closed InfluxDB connection")
