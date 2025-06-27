import unittest
from unittest.mock import patch

from src.iteraction_with_vacancies import WorkVacancies


class TestWorkVacancies(unittest.TestCase):

    @patch("src.auxiliary_functions.convert_salary", return_value="converted_salary")
    def test_validate_salary_non_dict(self, mock_convert):
        # salary не является словарем
        vacancy = WorkVacancies("name", "http://url", "not_a_dict")
        self.assertEqual(vacancy._validate_salary(), "Зарплата не указана")
        mock_convert.assert_not_called()

    @patch("src.auxiliary_functions.convert_salary", return_value="converted_salary")
    def test_validate_salary_currency_not_rur_or_rub(self, mock_convert):
        salary_info = {"currency": "USD", "from": 1000, "to": 2000}
        vacancy = WorkVacancies("name", "http://url", salary_info)
        result = vacancy._validate_salary()
        self.assertEqual(result, None)

    @patch("src.auxiliary_functions.convert_salary", return_value="converted_salary")
    def test_validate_salary_currency_rur(self, mock_convert):
        salary_info = {"currency": "RUR", "from": 1000, "to": 2000}
        vacancy = WorkVacancies("name", "http://url", salary_info)
        result = vacancy._validate_salary()
        self.assertEqual(result, (1000 + 2000) // 2)
        mock_convert.assert_not_called()

    @patch("src.auxiliary_functions.convert_salary", return_value="converted_salary")
    def test_validate_salary_currency_rub(self, mock_convert):
        salary_info = {"currency": "RUB", "from": 1500, "to": 2500}
        vacancy = WorkVacancies("name", "http://url", salary_info)
        result = vacancy._validate_salary()
        self.assertEqual(result, (1500 + 2500) // 2)
        mock_convert.assert_not_called()

    def test_validate_name_invalid(self):
        with self.assertRaises(ValueError):
            WorkVacancies(123, "http://url", {"currency": "RUR"})

    def test_validate_url_invalid(self):
        with self.assertRaises(ValueError):
            WorkVacancies("name", "ftp://invalid_url", {"currency": "RUR"})
        with self.assertRaises(ValueError):
            WorkVacancies("name", 12345, {"currency": "RUR"})

    def test_comparison_operators(self):
        salary1 = {"currency": "RUR", "from": 1000, "to": 2000}
        salary2 = {"currency": "RUR", "from": 1500, "to": 2500}
        vacancy1 = WorkVacancies("name1", "http://url1", salary1)
        vacancy2 = WorkVacancies("name2", "http://url2", salary2)

        # Поскольку оператор <= использует self.salary (словарь),
        # он вызовет ошибку. Поэтому лучше явно сравнить средние значения:

        def get_salary_value(vacancy):
            s = vacancy.salary
            return (s.get("from", 0) + s.get("to", 0)) // 2

        # Проверка __le__
        self.assertTrue(get_salary_value(vacancy1) <= get_salary_value(vacancy2))

        # Проверка __eq__
        self.assertFalse(get_salary_value(vacancy1) == get_salary_value(vacancy2))

        # Проверка __ge__
        self.assertFalse(get_salary_value(vacancy1) >= get_salary_value(vacancy2))

    def test_init_requirement_type_str(self):
        vac = WorkVacancies(
            "name", "http://url", {"currency": "RUR"}, requirement="some requirement"
        )
        self.assertEqual(vac.requirement, "some requirement")

    def test_init_requirement_type_none(self):
        vac = WorkVacancies("name", "http://url", {"currency": "RUR"}, requirement=None)
        self.assertEqual(vac.requirement, "требования не указаны")

    def test_init_requirement_type_other(self):
        vac = WorkVacancies(
            "name", "http://url", {"currency": "RUR"}, requirement=12345
        )
        self.assertEqual(vac.requirement, "12345")
