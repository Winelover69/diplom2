import requests
import allure
import logging

logger = logging.getLogger(__name__)

class ApiClient:
    def __init__(self, base_url="https://stellarburgers.nomoreparties.site/api/"):
        self.base_url = base_url
        self.session = requests.Session() # Используем сессию для сохранения куков и заголовков

    @allure.step("Отправка GET запроса на {endpoint}")
    def _get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"GET: {url}, Params: {params}, Headers: {headers}")
        response = self.session.get(url, params=params, headers=headers)
        logger.info(f"Response: Status={response.status_code}, Body={response.text}")
        return response

    @allure.step("Отправка POST запроса на {endpoint}")
    def _post(self, endpoint, json=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"POST: {url}, Body: {json}, Headers: {headers}")
        response = self.session.post(url, json=json, headers=headers)
        logger.info(f"Response: Status={response.status_code}, Body={response.text}")
        return response

    @allure.step("Отправка PATCH запроса на {endpoint}")
    def _patch(self, endpoint, json=None, headers=None):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"PATCH: {url}, Body: {json}, Headers: {headers}")
        response = self.session.patch(url, json=json, headers=headers)
        logger.info(f"Response: Status={response.status_code}, Body={response.text}")
        return response

    @allure.step("Отправка DELETE запроса на {endpoint}")
    def _delete(self, endpoint, headers=None):
        url = f"{self.base_url}{endpoint}"
        logger.info(f"DELETE: {url}, Headers: {headers}")
        response = self.session.delete(url, headers=headers)
        logger.info(f"Response: Status={response.status_code}, Body={response.text}")
        return response

    # --- Методы для работы с пользователем ---
    @allure.step("Регистрация пользователя")
    def register_user(self, email, password, name):
        data = {"email": email, "password": password, "name": name}
        return self._post("auth/register", json=data)

    @allure.step("Логин пользователя")
    def login_user(self, email, password):
        data = {"email": email, "password": password}
        return self._post("auth/login", json=data)

    @allure.step("Удаление пользователя")
    def delete_user(self, token):
        headers = {"Authorization": token}
        return self._delete("auth/user", headers=headers)

    @allure.step("Получение данных пользователя")
    def get_user_data(self, token):
        headers = {"Authorization": token}
        return self._get("auth/user", headers=headers)

    @allure.step("Обновление данных пользователя")
    def update_user_data(self, token, email=None, password=None, name=None):
        headers = {"Authorization": token}
        data = {}
        if email: data["email"] = email
        if password: data["password"] = password
        if name: data["name"] = name
        return self._patch("auth/user", json=data, headers=headers)

    # --- Методы для работы с ингредиентами и заказами ---
    @allure.step("Получение списка ингредиентов")
    def get_ingredients(self):
        return self._get("ingredients")

    @allure.step("Создание заказа")
    def create_order(self, ingredients_ids, token=None):
        headers = {}
        if token:
            headers["Authorization"] = token
        data = {"ingredients": ingredients_ids}
        return self._post("orders", json=data, headers=headers)

    @allure.step("Получение заказов пользователя")
    def get_user_orders(self, token):
        headers = {"Authorization": token}
        return self._get("orders", headers=headers)