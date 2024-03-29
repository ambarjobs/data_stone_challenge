from typing import Any
from unittest import mock

import httpx
import pytest
import rest_framework.status as status
from django.urls import reverse
from rest_framework.test import APIClient

from .logic import ExchangeApi


client = APIClient()


# ==================================================================================================
#   External API access entity
# ==================================================================================================
class TestExchangeApi:
    # ----------------------------------------------------------------------------------------------
    #   `get_exchange_rates()`
    # ----------------------------------------------------------------------------------------------
    def test_get_exchange_rates__general_case(
        self,
        currency_list: list[str],
        exchange_api_result: dict[str, Any],
        expected_rates: dict[str, Any],
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            mock_get_api.return_value.json.return_value = exchange_api_result

            exchange_api = ExchangeApi()
            exchange_rates_status = exchange_api.get_exchange_rates()

            assert not exchange_rates_status.error
            assert exchange_rates_status.status == 'ok'

            assert exchange_rates_status.data == {
                'exchange_rates': expected_rates, 'updated': exchange_api_result['lastupdate']}

    def test_get_exchange_rates__invalid_json(
        self,
        httpx_get_request: httpx.Request,
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            mock_get_api.return_value = httpx.Response(
                content='invalid json',
                status_code=status.HTTP_200_OK,
                request=httpx_get_request
            )

            exchange_api = ExchangeApi()
            exchange_rates_status = exchange_api.get_exchange_rates()

            assert exchange_rates_status.error
            assert exchange_rates_status.status == 'json_data_error'

            assert 'error' in exchange_rates_status.data
            assert 'Invalid JSON' in exchange_rates_status.data['error']

    def test_get_exchange_rates__invalid_last_update(
        self,
        exchange_api_result: dict[str, Any]
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            exchange_api_result['lastupdate'] = ''
            mock_get_api.return_value.json.return_value = exchange_api_result

            exchange_api = ExchangeApi()
            exchange_rates_status = exchange_api.get_exchange_rates()

            assert exchange_rates_status.error
            assert exchange_rates_status.status == 'invalid_api_data_error'

            assert 'error' in exchange_rates_status.data
            assert 'Invalid API response' in exchange_rates_status.data['error']
            assert 'lastupdate' in exchange_rates_status.data['error']['Invalid API response']
            assert (
                'Datetime has wrong format.' in
                str(exchange_rates_status.data['error']['Invalid API response']['lastupdate'])
            )

    def test_get_exchange_rates__rate_invalid_value(
        self,
        exchange_api_result: dict[str, Any]
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            exchange_api_result['rates']['BRL'] = 'invalid float'
            mock_get_api.return_value.json.return_value = exchange_api_result

            exchange_api = ExchangeApi()
            exchange_rates_status = exchange_api.get_exchange_rates()

            assert exchange_rates_status.error
            assert exchange_rates_status.status == 'invalid_api_data_error'

            assert 'error' in exchange_rates_status.data
            assert 'Invalid API response' in exchange_rates_status.data['error']
            assert 'rates' in exchange_rates_status.data['error']['Invalid API response']
            assert 'BRL' in exchange_rates_status.data['error']['Invalid API response']['rates']
            assert (
                'A valid number is required.' in
                str(exchange_rates_status.data['error']['Invalid API response']['rates']['BRL'])
            )

    def test_get_exchange_rates__negative_rate(
        self,
        exchange_api_result: dict[str, Any]
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            exchange_api_result['rates']['BRL'] = -1.23
            mock_get_api.return_value.json.return_value = exchange_api_result

            exchange_api = ExchangeApi()
            exchange_rates_status = exchange_api.get_exchange_rates()

            assert exchange_rates_status.error
            assert exchange_rates_status.status == 'invalid_api_data_error'

            assert 'error' in exchange_rates_status.data
            assert 'Invalid API response' in exchange_rates_status.data['error']
            assert 'rates' in exchange_rates_status.data['error']['Invalid API response']
            assert 'BRL' in exchange_rates_status.data['error']['Invalid API response']['rates']
            assert (
                'Invalid rate: must be > 0.0' in
                str(exchange_rates_status.data['error']['Invalid API response']['rates']['BRL'])
            )

    def test_get_exchange_rates__zero_rate(
        self,
        exchange_api_result: dict[str, Any]
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            exchange_api_result['rates']['BRL'] = 0
            mock_get_api.return_value.json.return_value = exchange_api_result

            exchange_api = ExchangeApi()
            exchange_rates_status = exchange_api.get_exchange_rates()

            assert exchange_rates_status.error
            assert exchange_rates_status.status == 'invalid_api_data_error'

            assert 'error' in exchange_rates_status.data
            assert 'Invalid API response' in exchange_rates_status.data['error']
            assert 'rates' in exchange_rates_status.data['error']['Invalid API response']
            assert 'BRL' in exchange_rates_status.data['error']['Invalid API response']['rates']
            assert (
                'Invalid rate: must be > 0.0' in
                str(exchange_rates_status.data['error']['Invalid API response']['rates']['BRL'])
            )

class TestConversion:
    # ----------------------------------------------------------------------------------------------
    #   /conversion endpoint (GET)
    # ----------------------------------------------------------------------------------------------
    @pytest.mark.parametrize(
        'from_currency,to_currency, amount, converted_value',
        [
            ('USD', 'BRL', 2.0, 10.026532),
            ('BTC', 'EUR', 3.0, 196705.8257921073),
            ('ETH', 'USD', 4.0, 14252.759868789093),
        ]
    )
    def test_get_conversion__general_case(
        self,
        exchange_api_result: dict[str, Any],
        from_currency: str,
        to_currency: str,
        amount: float,
        converted_value: float,
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            mock_get_api.return_value.json.return_value = exchange_api_result

            result = client.get(
                path=reverse('api.currency_conversion'),
                data={'from': from_currency, 'to': to_currency, 'amount': amount}
            )
            assert result.status_code == status.HTTP_200_OK

            expected_result = {
                'from_currency': from_currency,
                'to_currency': to_currency,
                'amount': amount,
                'converted_value': converted_value,
                'last_update': exchange_api_result['lastupdate'],
            }
            assert result.json() == expected_result

    @pytest.mark.parametrize(
        'from_currency,to_currency, amount',
        [
            (None, 'BRL', 2.0),
            ('USD', None, 3.0),
            ('USD', 'BRL', None),
        ]
    )
    def test_get_conversion__missing_parameters(
        self,
        exchange_api_result: dict[str, Any],
        from_currency: str | None,
        to_currency: str | None,
        amount: float | None,
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            mock_get_api.return_value.json.return_value = exchange_api_result

            params = [
                param for param in zip(
                    ['from', 'to', 'amount'], [from_currency, to_currency, amount])
                if param[1] is not None
            ]
            result = client.get(
                path=reverse('api.currency_conversion'),
                data=dict(params)

            )
            assert result.status_code == status.HTTP_400_BAD_REQUEST

            expected_result = {'error': 'There are missing parameters on query string.'}
            assert result.json() == expected_result

    @pytest.mark.parametrize(
        'from_currency,to_currency',
        [
            ('INEXISTENT', 'BRL'),
            ('BTC', 'INEXISTENT'),
        ]
    )
    def test_get_conversion__inexistent_currency(
        self,
        exchange_api_result: dict[str, Any],
        from_currency: str,
        to_currency: str,
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            mock_get_api.return_value.json.return_value = exchange_api_result

            result = client.get(
                path=reverse('api.currency_conversion'),
                data={'from': from_currency, 'to': to_currency, 'amount': 1.0}

            )
            assert result.status_code == status.HTTP_400_BAD_REQUEST

            expected_result = {'error': 'The currency [INEXISTENT] is not available for conversion.'}
            assert result.json() == expected_result

    @pytest.mark.parametrize(
        'from_currency,to_currency',
        [
            ('', 'BRL'),
            ('BTC', ''),
        ]
    )
    def test_get_conversion__empty_currency(
        self,
        exchange_api_result: dict[str, Any],
        from_currency: str,
        to_currency: str,
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            mock_get_api.return_value.json.return_value = exchange_api_result

            result = client.get(
                path=reverse('api.currency_conversion'),
                data={'from': from_currency, 'to': to_currency, 'amount': 1.0}

            )
            assert result.status_code == status.HTTP_400_BAD_REQUEST

            expected_result = {'error': 'The currency [] is not available for conversion.'}
            assert result.json() == expected_result

    def test_get_conversion__external_api_error(
        self,
        exchange_api_result: dict[str, Any],
    ) -> None:
        with mock.patch.object(target=httpx, attribute='get', autospec=True) as mock_get_api:
            exchange_api_result['rates']['BRL'] = 'invalid float'
            mock_get_api.return_value.json.return_value = exchange_api_result

            result = client.get(
                path=reverse('api.currency_conversion'),
                data={'from': 'USD', 'to': 'BRL', 'amount': 1.0}

            )
            assert result.status_code == status.HTTP_400_BAD_REQUEST

            result_json = result.json()

            assert 'error' in result_json
            assert 'Invalid API response' in result_json['error']
            assert 'rates' in result_json['error']['Invalid API response']
            assert 'BRL' in result_json['error']['Invalid API response']['rates']
            assert (
                'A valid number is required.' in
                str(result_json['error']['Invalid API response']['rates']['BRL'])
            )
