from unittest.mock import patch, MagicMock

import pytest
import requests
from influxdb_client import Point

from importer.importer import PriceImporter


class TestPriceImporter:
    """Test cases for the PriceImporter class."""

    def test_init(self, mock_config):
        """Test initialization of PriceImporter."""
        importer = PriceImporter(mock_config)
        assert importer.config == mock_config
        assert importer.influx_client is None
        assert importer.write_api is None

    def test_get_bucket_for_timeframe(self):
        """Test mapping of timeframes to bucket names."""
        # Test known timeframes
        assert PriceImporter.get_bucket_for_timeframe("1") == "prices_1m"
        assert PriceImporter.get_bucket_for_timeframe("5") == "prices_5m"
        assert PriceImporter.get_bucket_for_timeframe("15") == "prices_15m"
        assert PriceImporter.get_bucket_for_timeframe("30") == "prices_30m"
        assert PriceImporter.get_bucket_for_timeframe("45") == "prices_45m"
        assert PriceImporter.get_bucket_for_timeframe("60") == "prices_1h"
        assert PriceImporter.get_bucket_for_timeframe("120") == "prices_2h"
        assert PriceImporter.get_bucket_for_timeframe("180") == "prices_3h"
        assert PriceImporter.get_bucket_for_timeframe("240") == "prices_4h"
        assert PriceImporter.get_bucket_for_timeframe("4H") == "prices_4h"
        assert PriceImporter.get_bucket_for_timeframe("1D") == "prices_1d"
        assert PriceImporter.get_bucket_for_timeframe("1W") == "prices_1w"

        # Test unknown timeframe
        assert PriceImporter.get_bucket_for_timeframe("unknown") == "prices_default"

    def test_process_price_data(self, mock_write_api):
        """Test processing of price data."""
        # Setup test data
        item = {
            "measurement": "price",
            "ticker": "GBPUSD",
            "broker": "FX",
            "timeframe": "4H",
            "open": 1.2345,
            "high": 1.2456,
            "low": 1.2234,
            "close": 1.2400,
            "volume": 1000,
            "timestamp": 1609459200
        }
        bucket = "prices_4h"

        with patch('importer.importer.Point') as mock_point:
            # Create a mock Point instance
            mock_point_instance = MagicMock()
            mock_point.return_value = mock_point_instance
            mock_point_instance.tag.return_value = mock_point_instance
            mock_point_instance.field.return_value = mock_point_instance
            mock_point_instance.time.return_value = mock_point_instance

            # Call the method
            PriceImporter.process_price_data(item, bucket, mock_write_api)

            # Verify Point was created correctly
            mock_point.assert_called_once_with(item["measurement"])

            # Verify tags were set
            mock_point_instance.tag.assert_any_call("ticker", item["ticker"])
            mock_point_instance.tag.assert_any_call("broker", item["broker"])
            mock_point_instance.tag.assert_any_call("timeframe", item["timeframe"])

            # Verify fields were set
            mock_point_instance.field.assert_any_call("open", item["open"])
            mock_point_instance.field.assert_any_call("high", item["high"])
            mock_point_instance.field.assert_any_call("low", item["low"])
            mock_point_instance.field.assert_any_call("close", item["close"])
            mock_point_instance.field.assert_any_call("volume", item["volume"])

            # Verify write_api was called
            mock_write_api.write.assert_called_once_with(bucket=bucket, record=mock_point_instance)

    def test_connect_to_influxdb(self, mock_config, mock_influxdb_client):
        """Test connection to InfluxDB."""
        with patch('importer.importer.InfluxDBClient', return_value=mock_influxdb_client):
            importer = PriceImporter(mock_config)
            importer.connect_to_influxdb("test_token")

            # Verify InfluxDBClient was created with correct parameters
            assert importer.influx_client == mock_influxdb_client
            assert importer.write_api == mock_influxdb_client.write_api.return_value

    def test_connect_to_influxdb_failure(self, mock_config):
        """Test handling of InfluxDB connection failure."""
        with patch('importer.importer.InfluxDBClient', side_effect=Exception("Connection failed")):
            importer = PriceImporter(mock_config)

            # Verify that SystemExit is raised
            with pytest.raises(SystemExit):
                importer.connect_to_influxdb("test_token")

    def test_process_ticker_timeframe(self, mock_config, mock_requests_get, mock_write_api):
        """Test processing of a single ticker and timeframe."""
        with patch('importer.importer.PriceImporter.get_bucket_for_timeframe', return_value="prices_4h"):
            importer = PriceImporter(mock_config)
            importer.write_api = mock_write_api

            # Call the method
            importer._process_ticker_timeframe("FX", "GBPUSD", "4H")

            # Verify requests.get was called with the correct URL
            expected_url = f"{mock_config.datasource_url}/api/v1/prices?ticker=GBPUSD&amount=10&broker=FX&timeframe=4H"
            mock_requests_get.assert_called_once_with(expected_url)

            # Verify process_price_data was called for each price item
            assert mock_write_api.write.call_count == 1

    def test_process_ticker_timeframe_request_exception(self, mock_config, mock_write_api):
        """Test handling of request exception in _process_ticker_timeframe."""
        with patch('requests.get', side_effect=requests.RequestException("Request failed")):
            importer = PriceImporter(mock_config)
            importer.write_api = mock_write_api

            # Call the method - should not raise an exception
            importer._process_ticker_timeframe("FX", "GBPUSD", "4H")

            # Verify write_api.write was not called
            mock_write_api.write.assert_not_called()

    def test_fetch_and_store_prices(self, mock_config, mock_requests_get):
        """Test fetching and storing prices for all tickers and timeframes."""
        with patch('importer.importer.PriceImporter._process_ticker_timeframe') as mock_process:
            importer = PriceImporter(mock_config)

            # Call the method
            importer.fetch_and_store_prices()

            # Verify _process_ticker_timeframe was called for each ticker and timeframe
            expected_calls = len(mock_config.tickers) * len(mock_config.timeframes)
            assert mock_process.call_count == expected_calls

    def test_fetch_and_store_prices_invalid_ticker(self, mock_config):
        """Test handling of invalid ticker format."""
        # Set an invalid ticker format
        mock_config.tickers = ["InvalidFormat"]

        with patch('importer.importer.PriceImporter._process_ticker_timeframe') as mock_process:
            importer = PriceImporter(mock_config)

            # Call the method
            importer.fetch_and_store_prices()

            # Verify _process_ticker_timeframe was not called
            mock_process.assert_not_called()

    def test_close(self, mock_config, mock_influxdb_client):
        """Test closing the InfluxDB client connection."""
        importer = PriceImporter(mock_config)
        importer.influx_client = mock_influxdb_client

        # Call the method
        importer.close()

        # Verify influx_client.close was called
        mock_influxdb_client.close.assert_called_once()

    def test_close_no_client(self, mock_config):
        """Test closing when no client exists."""
        importer = PriceImporter(mock_config)
        importer.influx_client = None

        # Call the method - should not raise an exception
        importer.close()
