import bcrypt

# Шаг 1: Хешируем пароль (как в get_password_hash)
password = "321"
password_bytes = password.encode('utf-8')[:72]
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
print("Хеш:", hashed)

# Шаг 2: Проверяем (как в verify_password)
plain_bytes = password.encode('utf-8')[:72]
hashed_bytes = hashed.encode('utf-8')
is_valid = bcrypt.checkpw(plain_bytes, hashed_bytes)
print("Проверка:", is_valid)  # Должно быть True

print(hashed_bytes)