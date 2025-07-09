import unittest
from unittest.mock import Mock, patch

from src.auxiliary_functions import convert_salary


class TestConvertSalary(unittest.TestCase):

    @patch("requests.get")
    @patch("os.getenv", return_value="test_api_key")
    def test_convert_success(self, mock_getenv, mock_get):
        # Мокаем успешный ответ с ключом "result"
        mock_response = Mock()
        mock_response.json.return_value = {"result": 12345}
        mock_get.return_value = mock_response

        result = convert_salary(1000, 1)
        self.assertEqual(result, 12345)

        # Проверяем правильность вызова requests.get
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertIn("https://api.apilayer.com/exchangerates_data/convert", args[0])
        self.assertEqual(kwargs["headers"], {"apikey": "test_api_key"})

    @patch("requests.get")
    @patch("os.getenv", return_value="test_api_key")
    def test_convert_no_result_key(self, mock_getenv, mock_get):
        # Ответ без ключа "result"
        mock_response = Mock()
        mock_response.json.return_value = {"some_other_key": 999}
        mock_get.return_value = mock_response

        result = convert_salary(500, 2)
        self.assertIsNone(result)

    @patch("requests.get")
    @patch("os.getenv", return_value="test_api_key")
    def test_convert_empty_response(self, mock_getenv, mock_get):
        # Пустой JSON
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response

        result = convert_salary(2000, 3)
        self.assertIsNone(result)

    @patch("requests.get")
    @patch("os.getenv", return_value="test_api_key")
    def test_convert_request_exception(self, mock_getenv, mock_get):
        # Имитация исключения при запросе
        mock_get.side_effect = Exception("Network error")

        with self.assertRaises(Exception):
            convert_salary(1000, 1)

    @patch("requests.get")
    @patch("os.getenv", return_value="test_api_key")
    def test_convert_invalid_json(self, mock_getenv, mock_get):
        # Возвращает невалидный JSON (например, None или выбрасывает исключение)
        def raise_json_error():
            raise ValueError("Invalid JSON")

        mock_response = Mock()
        # Вызов json() вызывает исключение
        mock_response.json.side_effect = raise_json_error
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            convert_salary(1000, 1)
