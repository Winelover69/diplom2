import pytest
import allure
from api.client import ApiClient
from data.test_data import generate_random_email, generate_random_password

@allure.epic("API Stellar Burgers")
@allure.feature("User Login")
class TestUserLogin:

    @allure.title("Вход под существующим пользователем")
    @allure.description("Проверяет успешный вход в систему для зарегистрированного пользователя.")
    def test_login_existing_user_success(self, api_client, registered_user):
        email, password, _, _ = registered_user
        with allure.step(f"Попытка входа для пользователя: {email}"):
            response = api_client.login_user(email, password)
        with allure.step("Проверка успешного ответа"):
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert "accessToken" in response.json()
            assert "refreshToken" in response.json()
            assert response.json()["user"]["email"] == email

    @allure.title("Вход с неверным логином и паролем")
    @allure.description("Проверяет, что вход невозможен с некорректными учетными данными.")
    @pytest.mark.parametrize("invalid_email, invalid_password", [
        ("wrong@example.com", "wrongpass"),
        (generate_random_email(), generate_random_password()) # Полностью случайные данные
    ])
    def test_login_with_incorrect_credentials_fails(self, api_client, invalid_email, invalid_password):
        with allure.step(f"Попытка входа с неверными данными: {invalid_email}/{invalid_password}"):
            response = api_client.login_user(invalid_email, invalid_password)
        with allure.step("Проверка ответа об ошибке"):
            assert response.status_code == 401
            assert response.json()["success"] is False
            assert response.json()["message"] == "Email or password are incorrect"