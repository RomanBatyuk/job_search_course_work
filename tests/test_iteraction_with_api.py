import unittest
from unittest.mock import Mock, patch

from src.iteraction_with_api import MyCustomError, hh_ru  # замените на актуальный путь


class Test_hh_Ru(unittest.TestCase):

    @patch("requests.get")
    def test_connect_apy_success(self, mock_get):
        # Мокаем успешный ответ с ключом 'items'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"items": [{"id": 1}]}'
        mock_response.json.return_value = {"items": [{"id": 1}]}
        mock_get.return_value = mock_response

        api = hh_ru()
        result = api._connect_apy("Python")

        # Проверяем, что результат содержит ожидаемый элемент
        self.assertIn({"id": 1}, result)
        # Проверяем, что page увеличился до 20 или больше (зависит от логики)
        self.assertTrue(api._hh_ru__params["page"] >= 1)

    @patch("requests.get")
    def test_connect_apy_http_error(self, mock_get):
        # Мокаем ответ с ошибкой статуса
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response

        api = hh_ru()
        with self.assertRaises(MyCustomError) as context:
            api._connect_apy("Python")
        self.assertIn("Ошибка! Запрос не выполнен", str(context.exception))

    @patch("requests.get")
    def test_connect_apy_invalid_json(self, mock_get):
        # Мокаем ответ с некорректным JSON
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Invalid JSON"
        mock_response.json.side_effect = ValueError
        mock_get.return_value = mock_response

        api = hh_ru()
        with self.assertRaises(MyCustomError) as context:
            api._connect_apy("Python")
        self.assertIn("Ошибка парсинга JSON", str(context.exception))

    @patch("requests.get")
    def test_connect_apy_missing_items_key(self, mock_get):
        # Мокаем ответ без ключа 'items'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"not_items": []}'
        mock_response.json.return_value = {"not_items": []}
        mock_get.return_value = mock_response

        api = hh_ru()
        with self.assertRaises(MyCustomError) as context:
            api._connect_apy("Python")
        self.assertIn("Ключ 'items' отсутствует", str(context.exception))

    @patch("requests.get")
    def test_get_vacancies_returns_first_vacancy(self, mock_get):
        # Мокаем несколько страниц с вакансиями
        first_page_data = {"items": [{"id": 1}], "page": 0, "per_page": 100, "total": 1}

        second_page_data = {
            "items": [{"id": 2}],
            "page": 1,
            "per_page": 100,
            "total": 2,
        }

        # Настраиваем последовательность вызовов requests.get
        def side_effect(*args, **kwargs):
            if kwargs["params"]["page"] == 0:
                resp = Mock()
                resp.status_code = 200
                resp.text = '{"items": [{"id": 1}]}'
                resp.json.return_value = first_page_data
                return resp
            elif kwargs["params"]["page"] == 1:
                resp = Mock()
                resp.status_code = 200
                resp.text = '{"items": [{"id": 2}]}'
                resp.json.return_value = second_page_data
                return resp
            else:
                resp = Mock()
                resp.status_code = 200
                resp.text = '{"items": []}'
                resp.json.return_value = {"items": []}
                return resp

        mock_get.side_effect = side_effect

        api = hh_ru()

        # Запускаем подключение (собирает вакансии)
        vacancies_list = api._connect_apy("Python")

        # Проверяем, что вакансии собраны корректно
        self.assertTrue(any(vac["id"] == 1 for vac in vacancies_list))

    def test_get_vacancies_returns_first_element(self):
        api_instance = hh_ru()
        api_instance._HeadHunterAPI__vacancies = None
        result = api_instance.get_vacancies()
        self.assertEqual(result, None)


if __name__ == "__main__":
    unittest.main()
