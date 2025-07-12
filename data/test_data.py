import random
import string

def generate_random_email():
    return f"test_user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}@example.com"

def generate_random_password():
    return "password" + ''.join(random.choices(string.digits, k=4))

def generate_random_name():
    return "Name" + ''.join(random.choices(string.ascii_letters, k=5))

# Пример невалидных хешей ингредиентов
INVALID_INGREDIENT_HASHES = [
    "invalid_hash_12345",
    "another_bad_hash",
    "00000000000000000000000" # Пример слишком короткого или невалидного формата
]