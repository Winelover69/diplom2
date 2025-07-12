import pytest
import allure
import logging
from api.client import ApiClient
from data.test_data import generate_random_email, generate_random_password, \
    generate_random_name
from config import BASE_URL

# --- Настройка логирования ---
# Создаем и настраиваем корневой логгер
logger = logging.getLogger(__name__)  # Можно использовать __name__ или просто 'root'
logger.setLevel(logging.INFO)  # Устанавливаем уровень логирования (INFO, DEBUG, WARNING, ERROR)

# Создаем обработчик для вывода в консоль
handler = logging.StreamHandler()
# Создаем форматтер для красивого вывода логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Добавляем обработчик к логгеру, если он еще не добавлен, чтобы избежать дублирования
if not logger.handlers:
    logger.addHandler(handler)


# --- Конец настройки логирования ---


@pytest.fixture(scope="session")
def api_client():
    """
    Фикстура, предоставляющая экземпляр ApiClient для всех тестов в рамках сессии.
    Это гарантирует, что HTTP-сессия переиспользуется, что эффективно для API-тестов.
    """
    logger.info("Фикстура 'api_client': Инициализация ApiClient.")
    return ApiClient(base_url=BASE_URL)


@pytest.fixture
def random_user_data():
    """
    Фикстура, генерирующая случайные данные для регистрации пользователя
    (email, пароль, имя). Данные уникальны для каждого вызова фикстуры.
    """
    email = generate_random_email()
    password = generate_random_password()
    name = generate_random_name()
    logger.info(f"Фикстура 'random_user_data': Сгенерированы данные: email={email}, name={name}")
    return {"email": email, "password": password, "name": name}


@pytest.fixture
def registered_user(api_client, random_user_data):
    """
    Фикстура: регистрирует нового пользователя перед выполнением теста
    и гарантированно удаляет его после завершения теста.
    Возвращает кортеж: (email, password, name, accessToken).
    """
    email = random_user_data["email"]
    password = random_user_data["password"]
    name = random_user_data["name"]
    access_token = None

    with allure.step(f"Фикстура 'registered_user': Регистрация пользователя {email}"):
        response = api_client.register_user(email, password, name)

        if response.status_code == 200 and response.json().get("success"):
            access_token = response.json().get("accessToken")
            logger.info(f"Фикстура 'registered_user': Пользователь {email} успешно зарегистрирован. Токен получен.")
        else:
            logger.error(
                f"Фикстура 'registered_user': Ошибка при регистрации пользователя {email}. "
                f"Статус: {response.status_code}, Ответ: {response.text}"
            )
            pytest.fail(f"Фикстура 'registered_user': Не удалось зарегистрировать пользователя через API.")

    if not access_token:
        pytest.fail(f"Фикстура 'registered_user': Токен не был получен после регистрации пользователя {email}.")

    # --- Yield: Возвращаем данные для теста ---
    yield email, password, name, access_token

    # --- Финализатор: Код после yield выполняется после завершения теста ---
    with allure.step(f"Финализатор 'registered_user': Удаление пользователя {email}"):
        if access_token:
            delete_response = api_client.delete_user(access_token)
            if delete_response.status_code == 202 and delete_response.json().get("success"):
                logger.info(f"Финализатор 'registered_user': Пользователь {email} успешно удален.")
            else:
                logger.warning(
                    f"Финализатор 'registered_user': Не удалось удалить пользователя {email}. "
                    f"Статус: {delete_response.status_code}, Ответ: {delete_response.text}"
                )
        else:
            logger.warning(
                f"Финализатор 'registered_user': Токен для удаления пользователя {email} отсутствует. Удаление пропущено.")


@pytest.fixture
def user_for_unique_creation_test(api_client, random_user_data, request):
    """
    Фикстура для сценария "создание уникального пользователя".
    Предоставляет данные для создания, а тест сам регистрирует пользователя.
    Затем тест передает полученный токен обратно в эту фикстуру для гарантированного удаления.
    Возвращает (email, password, name, set_token_callback_function).
    """
    email = random_user_data["email"]
    password = random_user_data["password"]
    name = random_user_data["name"]

    # Замыкание для хранения токена, который тест передаст для удаления
    token_to_delete = {"value": None}

    def finalizer():
        """Функция-финализатор для удаления пользователя, созданного в тесте."""
        if token_to_delete["value"]:
            with allure.step(f"Финализатор 'user_for_unique_creation_test': Удаление пользователя {email}"):
                delete_response = api_client.delete_user(token_to_delete["value"])
                if delete_response.status_code == 202 and delete_response.json().get("success"):
                    logger.info(f"Финализатор 'user_for_unique_creation_test': Пользователь {email} успешно удален.")
                else:
                    logger.warning(
                        f"Финализатор 'user_for_unique_creation_test': Не удалось удалить пользователя {email}. "
                        f"Статус: {delete_response.status_code}, Ответ: {delete_response.text}"
                    )
        else:
            logger.info(
                f"Финализатор 'user_for_unique_creation_test': Токен для пользователя {email} не был установлен. Удаление пропущено.")

    # Добавляем финализатор, который будет вызван после завершения теста
    request.addfinalizer(finalizer)

    # Функция-callback, которую тест будет вызывать для передачи токена
    def set_access_token_for_deletion(token):
        token_to_delete["value"] = token
        logger.debug(f"Фикстура 'user_for_unique_creation_test': Токен для удаления пользователя {email} установлен.")

    logger.info(f"Фикстура 'user_for_unique_creation_test': Предоставлены данные для создания пользователя {email}.")
    yield email, password, name, set_access_token_for_deletion


@pytest.fixture(scope="session")
def get_some_ingredients_ids(api_client):
    """
    Фикстура (session-scope): получает ID нескольких ингредиентов (булка, соус, начинка)
    для создания заказа. Выполняется один раз за всю тестовую сессию,
    чтобы избежать лишних вызовов API.
    Возвращает словарь с ID булки, соуса и начинки.
    """
    bun_id = None
    sauce_id = None
    main_id = None

    with allure.step("Фикстура 'get_some_ingredients_ids': Получение ID ингредиентов через API"):
        response = api_client.get_ingredients()

        if response.status_code != 200 or not response.json().get("success"):
            logger.error(
                f"Фикстура 'get_some_ingredients_ids': Ошибка при получении ингредиентов. "
                f"Статус: {response.status_code}, Ответ: {response.text}"
            )
            pytest.fail(f"Фикстура 'get_some_ingredients_ids': Не удалось получить список ингредиентов через API.")

        ingredients = response.json().get("data", [])

        buns = [ing for ing in ingredients if ing.get("type") == "bun"]
        sauces = [ing for ing in ingredients if ing.get("type") == "sauce"]
        mains = [ing for ing in ingredients if ing.get("type") == "main"]

        # Берем первый попавшийся ID для каждого типа
        if buns:
            bun_id = buns[0].get("_id")
        if sauces:
            sauce_id = sauces[0].get("_id")
        if mains:
            main_id = mains[0].get("_id")

        if not all([bun_id, sauce_id, main_id]):
            missing_items = []
            if not bun_id: missing_items.append("булки")
            if not sauce_id: missing_items.append("соуса")
            if not main_id: missing_items.append("начинки")
            pytest.fail(
                f"Фикстура 'get_some_ingredients_ids': Не удалось найти все необходимые типы ингредиентов: {', '.join(missing_items)}.")

        logger.info(
            f"Фикстура 'get_some_ingredients_ids': Получены ID: Булка={bun_id}, Соус={sauce_id}, Начинка={main_id}")

    yield {"bun_id": bun_id, "sauce_id": sauce_id, "main_id": main_id}