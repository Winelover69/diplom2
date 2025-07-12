import pytest
import allure
from api.client import ApiClient
from data.test_data import INVALID_INGREDIENT_HASHES

@allure.epic("API Stellar Burgers")
@allure.feature("Order Creation")
class TestOrderCreation:

    @allure.title("Создание заказа с авторизацией и ингредиентами")
    @allure.description("Проверяет успешное создание заказа авторизованным пользователем с корректными ингредиентами.")
    def test_create_order_authorized_with_ingredients_success(self, api_client, registered_user, get_some_ingredients_ids):
        email, password, name, token = registered_user
        ingredients_ids = get_some_ingredients_ids
        with allure.step("Создание заказа с авторизацией"):
            response = api_client.create_order(ingredients_ids, token=token)
        with allure.step("Проверка успешного ответа"):
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert "order" in response.json()
            assert "number" in response.json()["order"]
            assert response.json()["name"] is not None # Проверяем, что название заказа присутствует
            assert len(response.json()["order"]["ingredients"]) == len(ingredients_ids)


    @allure.title("Создание заказа без авторизации (анонимно) с ингредиентами")
    @allure.description("Проверяет успешное создание заказа неавторизованным пользователем с корректными ингредиентами.")
    def test_create_order_unauthorized_with_ingredients_success(self, api_client, get_some_ingredients_ids):
        ingredients_ids = get_some_ingredients_ids
        with allure.step("Создание заказа без авторизации"):
            response = api_client.create_order(ingredients_ids, token=None)
        with allure.step("Проверка успешного ответа"):
            assert response.status_code == 200
            assert response.json()["success"] is True
            assert "order" in response.json()
            assert "number" in response.json()["order"]
            assert response.json()["name"] is not None
            assert len(response.json()["order"]["ingredients"]) == len(ingredients_ids)


    @allure.title("Создание заказа с авторизацией, но без ингредиентов")
    @allure.description("Проверяет, что авторизованный пользователь не может создать заказ без ингредиентов.")
    def test_create_order_authorized_no_ingredients_fails(self, api_client, registered_user):
        email, password, name, token = registered_user
        with allure.step("Попытка создания заказа без ингредиентов"):
            response = api_client.create_order([], token=token) # Передаем пустой список ингредиентов
        with allure.step("Проверка ответа об ошибке"):
            assert response.status_code == 400
            assert response.json()["success"] is False
            assert response.json()["message"] == "Ingredient ids must be provided"

    @allure.title("Создание заказа без авторизации и без ингредиентов")
    @allure.description("Проверяет, что неавторизованный пользователь не может создать заказ без ингредиентов.")
    def test_create_order_unauthorized_no_ingredients_fails(self, api_client):
        with allure.step("Попытка создания заказа без ингредиентов и без авторизации"):
            response = api_client.create_order([], token=None)
        with allure.step("Проверка ответа об ошибке"):
            assert response.status_code == 400
            assert response.json()["success"] is False
            assert response.json()["message"] == "Ingredient ids must be provided"

    @allure.title("Создание заказа с неверным хешем ингредиентов")
    @allure.description("Проверяет, что заказ не может быть создан с некорректными ID ингредиентов (неверными хешами).")
    @pytest.mark.parametrize("invalid_hash", INVALID_INGREDIENT_HASHES)
    def test_create_order_with_invalid_ingredient_hash_fails(self, api_client, registered_user, invalid_hash):
        email, password, name, token = registered_user
        invalid_ingredients = [invalid_hash] # Используем один неверный хеш

        with allure.step(f"Попытка создания заказа с неверным хешем ингредиента: {invalid_hash}"):
            response = api_client.create_order(invalid_ingredients, token=token)

        with allure.step("Проверка ответа об ошибке"):
            # Согласно документации, если ID неверный, то должен быть статус 500
            # Однако, в реальных API могут быть и 400. Следуем документации.
            assert response.status_code == 500
            assert response.json()["success"] is False
            # Проверяем наличие ошибки, API может не возвращать сообщение об ошибке для 500
            assert "message" not in response.json() or response.json()["message"] == "Internal Server Error"