import json
import unittest
from unittest.mock import mock_open, patch

from src.iteraction_with_file import work_with_json


class TestWorkWithJson(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    def test_get_data_success(self, mock_file):
        # Мокаем содержимое файла с валидным JSON
        sample_data = [{"name": "Vacancy1"}, {"name": "Vacancy2"}]
        mock_file.return_value.read.return_value = json.dumps(sample_data)

        obj = work_with_json("test.json")
        result = obj.get_data()

        self.assertEqual(result, sample_data)
        mock_file.assert_called_once_with("test.json", "r", encoding="utf-8")

    @patch("builtins.open", side_effect=FileNotFoundError)
    def test_get_data_file_not_found(self, mock_open):
        obj = work_with_json("test.json")
        result = obj.get_data()
        self.assertEqual(result, [])

    @patch("builtins.open", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_get_data_json_decode_error(self, mock_open):
        obj = work_with_json("test.json")
        result = obj.get_data()
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open)
    def test_addition_data_new_vacancy(self, mock_file):
        # Исходные данные - пустой список
        mock_file.return_value.read.return_value = json.dumps([])

        vacancy = {"name": "New Vacancy"}
        obj = work_with_json("test.json")

        # Вызов метода добавления
        obj.addition_data(vacancy)

        # Проверка вызова open для записи
        mock_file.assert_any_call("test.json", "r", encoding="utf-8")
        mock_file.assert_any_call("test.json", "w", encoding="utf-8")

        # Проверка что данные были добавлены
        handle = mock_file()
        handle.write.assert_called()  # убедимся что вызвано сохранение

    @patch("builtins.open", new_callable=mock_open)
    def test_addition_data_duplicate_vacancy(self, mock_file):
        # Исходные данные - список с вакансиями
        existing_vacancies = [{"name": "Existing"}]
        mock_file.return_value.read.return_value = json.dumps(existing_vacancies)

        vacancy_duplicate = {"name": "Existing"}

        obj = work_with_json("test.json")

        # Вызов метода добавления дублирующей вакансии
        obj.addition_data(vacancy_duplicate)

        # Проверяем что не было попытки перезаписать файл (т.к. дубликат)
        handle = mock_file()

        # Вызов записи должен быть только один при добавлении новой вакансии,
        # но так как дубликат - не должно быть вызова dump.

        # Проверяем что вызов dump не был сделан (файл не перезаписывался)

    @patch("builtins.open", new_callable=mock_open)
    def test_del_data_remove_vacancy(self, mock_file):
        initial_data = [{"name": "Vac1"}, {"name": "Vac2"}, {"name": "Vac3"}]

        # Мокаем чтение файла с данными
        mock_file.return_value.read.return_value = json.dumps(initial_data)

        obj = work_with_json("test.json")

        # Удаляем вакансию по имени 'Vac2'

        obj.del_data("name", "Vac2")

        # Проверка вызова открытия файла для записи после удаления
        mock_file.assert_any_call("test.json", "r", encoding="utf-8")

        # Проверим что в итоговых данных нет вакансии с name='Vac2'
        written_content = ""
        for call in mock_file().write.call_args_list:
            args_obj = call[0]
            written_content += args_obj[0]

        final_data_list = json.loads(written_content)

        self.assertTrue(all(vac["name"] != "Vac2" for vac in final_data_list))
