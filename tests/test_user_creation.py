import pytest
import allure
import logging

# api.client, random_user_data, registered_user, user_for_unique_creation_test
# все эти фикстуры становятся доступны автоматически благодаря conftest.py

logger = logging.getLogger(__name__)


@allure.epic("API Stellar Burgers")
@allure.feature("User Creation")
class TestUserCreation:

    @allure.title("Создание уникального пользователя")
    @allure.description("Проверяет успешное создание пользователя с уникальными данными.")
    # test_create_unique_user_success теперь принимает user_for_unique_creation_test
    def test_create_unique_user_success(self, api_client, user_for_unique_creation_test):
        # Получаем данные пользователя и функцию для установки токена из фикстуры
        email, password, name, set_access_token_for_deletion = user_for_unique_creation_test

        with allure.step("Отправка запроса на регистрацию"):
            response = api_client.register_user(
                email,
                password,
                name
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 200, f"Ожидался статус 200, получен: {response.status_code}"
            assert response.json()["success"] is True, "Поле 'success' должно быть True"
            assert "accessToken" in response.json(), "В ответе должен быть 'accessToken'"
            assert "refreshToken" in response.json(), "В ответе должен быть 'refreshToken'"
            assert response.json()["user"]["email"] == email, "Email пользователя в ответе не совпадает"
            assert response.json()["user"]["name"] == name, "Имя пользователя в ответе не совпадает"

        with allure.step("Передача токена в фикстуру для гарантированной очистки"):
            # Важно: вызываем функцию, предоставленную фикстурой, чтобы она могла удалить пользователя
            if response.json()["success"] and "accessToken" in response.json():
                set_access_token_for_deletion(response.json()["accessToken"])
                logger.info(
                    f"Тест 'create_unique_user_success': Токен для пользователя {email} передан фикстуре для очистки.")
            else:
                logger.error(
                    f"Тест 'create_unique_user_success': Токен не был получен для пользователя {email} после регистрации. Очистка может быть пропущена.")

    @allure.title("Создание пользователя, который уже зарегистрирован")
    @allure.description("Проверяет, что нельзя создать пользователя с уже существующим email.")
    def test_create_existing_user_fails(self, api_client, registered_user):
        email, password, name, _ = registered_user  # Пользователь уже зарегистрирован фикстурой

        with allure.step("Попытка повторной регистрации с тем же email"):
            response = api_client.register_user(email, password, name)

        with allure.step("Проверка ответа об ошибке"):
            # Исправлено: Добавлены полные утверждения для проверки ответа
            assert response.status_code == 403, f"Ожидался статус 403, получен: {response.status_code}"
            assert response.json()["success"] is False, "Поле 'success' должно быть False"
            assert response.json()[
                       "message"] == "User already exists", "Сообщение об ошибке не соответствует ожидаемому"

    @allure.title("Создание пользователя без заполнения обязательного поля")
    @allure.description(
        "Проверяет, что регистрация невозможна без одного из обязательных полей (email, password, name).")
    @pytest.mark.parametrize("missing_field", ["email", "password", "name"])
    def test_create_user_missing_required_field_fails(self, api_client, random_user_data, missing_field):
        user_data_copy = random_user_data.copy()
        user_data_copy.pop(missing_field)  # Удаляем одно из обязательных полей

        with allure.step(f"Попытка регистрации без поля: {missing_field}"):
            response = api_client.register_user(
                email=user_data_copy.get("email"),
                password=user_data_copy.get("password"),
                name=user_data_copy.get("name")
            )
        with allure.step("Проверка ответа об ошибке"):
            assert response.status_code == 403, f"Ожидался статус 403, получен: {response.status_code}"
            assert response.json()["success"] is False, "Поле 'success' должно быть False"
            assert response.json()[
                       "message"] == "Email, password and name are required fields", "Сообщение об ошибке не соответствует ожидаемому"