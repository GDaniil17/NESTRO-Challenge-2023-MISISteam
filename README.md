# NESTRO-Challenge-2023-MISISteam

Код на Python / Flask

### Чтобы запустить это приложение локально:

1. Клонируйте репозиторий.
2. Убедитесь, что у вас установлен Python 3.6+ и Flask.

Установите Flask с помощью команды:

```
pip install -U Flask
```

3. Убедитесь, что вы находитесь в каталоге /marketplace и выполните следующие команды в терминале:

Для Mac/Linux:

```
export FLASK_APP=marketplace

export FLASK_ENV=development

flask run
```

Для Windows:

```
set FLASK_APP=marketplace

set FLASK_ENV=development

flask run
```

4. Перейдите по URL-адресу, указанному в терминале, чтобы увидеть веб-приложение.

# Hack_MISUISSERS

#### Создание приложения Flask

Функция `create_app` создает экземпляр приложения Flask и настраивает его.

```python
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'marketplace.sqlite'),
    )
```

#### Роуты и шаблоны

##### `hello`

- URL: `/hello`
- Метод: `GET`
- Описание: Приветственный эндпоинт.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: Строка "Hello World!!"

##### `table`

- URL: `/table/<path>`
- Метод: `GET`
- Описание: Отображает таблицу из файла CSV.
- Параметры URL:
  - `path` (строка, обязательно): Путь к файлу CSV.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница с отображением таблицы.

##### `item_path`

- URL: `/item`
- Метод: `GET`
- Описание: Отображает список элементов.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница с отображением списка элементов.

##### `get_columns`

- URL: `/columns`
- Метод: `GET`
- Описание: Возвращает страницу с отображением столбцов.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница с отображением столбцов.

##### `loader`

- URL: `/loader`
- Метод: `GET`
- Описание: Возвращает страницу загрузчика.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница загрузчика.

##### `upload_file`

- URL: `/upload_file`
- Методы: `GET`, `POST`
- Описание: Загружает файл на сервер.
- Запросы:
  - GET: Возвращает страницу загрузки файла.
  - POST: Загружает выбранный файл на сервер.
- Ответ:
  - Код состояния: `302 Found` (при успешной загрузке файла)
  - Перенаправляет на страницу загрузки файла.

#### Обработчик ошибок

##### `too_large`

- Код ошибки: `413 Request Entity Too Large`
- Описание: Обработчик ошибки, который возвращает сообщение "File is too large" при загрузке слишком большого файла.

## Аутентификационное API

Это API предоставляет конечные точки для регистрации, входа и выхода пользователя.

### Конечные точки

#### Регистрация

- URL: `/auth/register`
- Метод: `POST`
- Описание: Зарегистрировать нового пользователя.
- Тело запроса:
  - `name` (строка, обязательно): Имя пользователя.
  - `username` (строка, обязательно): Имя пользователя или электронная почта.
  - `password` (строка, обязательно): Пароль пользователя.
  - `isAdmin` (логическое значение, опционально): Установите `true`, если пользователь должен иметь права администратора.
- Ответ:
  - Успех:
    - Код состояния: `302 Found`
    - Перенаправляет на страницу входа.
  - Ошибки:
    - Код состояния: `200 OK`
    - Тело ответа: JSON-объект с полем `error`, содержащим массив сообщений об ошибках.

#### Вход

- URL: `/auth/login`
- Метод: `POST`
- Описание: Аутентифицировать пользователя и создать сессию.
- Тело запроса:
  - `username` (строка, обязательно): Имя пользователя или электронная почта.
  - `password` (строка, обязательно): Пароль пользователя.
- Ответ:
  - Успех:
    - Код состояния: `302 Found`
    - Перенаправляет на домашнюю страницу.
  - Ошибки:
    - Код состояния: `200 OK`
    - Тело ответа: JSON-объект с полем `error`, содержащим массив сообщений об ошибках.

#### Выход

- URL: `/auth/logout`
- Метод: `GET`
- Описание: Завершить сеанс аутентифицированного пользователя.
- Ответ:
  - Успех:
    - Код состояния: `302 Found`
    - Перенаправляет на домашнюю страницу.

### Декораторы аутентификации

#### `login_required`

Декоратор, который может использоваться для защиты маршрутов, требующих аутентификации.

Использование:

```python
@app.route('/protected')
@login_required
def protected():
    # Доступно только аутентифицированным пользователям
    return 'Защищенная страница'
```

#### `admin_only`

Декоратор, который может использоваться для защиты маршрутов, требующих прав администратора.

Использование:

```python
@app.route('/admin')
@admin_only
def admin():
    # Доступно только пользователям с правами администратора
    return 'Страница администратора'
```

#### `add_cart`

- URL: `/add_cart/<int:item_id>`
- Метод: `POST`
- Описание: Добавляет товар в корзину пользователя.
- Параметры URL:
  - `item_id` (целое число, обязательно): Идентификатор товара.
- Ответ:
  - Код состояния: `302 Found`
  - Перенаправляет на домашнюю страницу магазина.

#### `read_file`

- Описание: Функция для чтения файла CSV.
- Параметры:
  - `path` (строка, обязательно): Путь к файлу CSV.
- Возвращает:
  - Кортеж `headers` - заголовки столбцов
  - Список `rows` - данные строк

#### `table`

- Описание: Функция для отображения таблицы из файла CSV.
- Параметры:
  - `path` (строка, обязательно): Путь к файлу CSV.
- Возвращает:
  - Ответ:
    - Код состояния: `200 OK`
    - Тело ответа: HTML-страница с отображением таблицы.

#### `preview`

- URL: `/preview/<int:item_id>`
- Методы: `POST`, `GET`
- Описание: Отображает предварительный просмотр товара.
- Параметры URL:
  - `item_id` (целое число, обязательно): Идентификатор товара.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница с предварительным просмотром таблицы.

#### `checkout`

- URL: `/checkout`
- Метод: `GET`
- Описание: Отображает страницу оформления заказа.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница с формой оформления заказа.

#### `tag`

- URL: `/tag/<item_dataset_author>`
- Метод: `GET`
- Описание: Фильтрует товары по автору датасета.
- Параметры URL:
  - `item_dataset_author` (строка, обязательно): Имя автора датасета.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница с отфильтрованными товарами.

#### `delete_item`

- URL: `/delete/<cart_item_id>`
- Метод: `POST`
- Описание: Удаляет товар из корзины пользователя.
- Параметры URL:
  - `cart_item_id` (строка, обязательно): Идентификатор товара в корзине.
- Ответ:
  - Код состояния: `302 Found`
  - Перенаправляет на страницу оформления заказа.

#### `create_zip_archive`

- Описание: Функция для создания zip-архива из списка файлов.
- Параметры:
  - `file_list` (список, обязательно): Список файлов для архивации.
  - `archive_name` (строка, обязательно): Имя zip-архива.
- Возвращает: Ничего.

#### `download_zip`

- URL: `/download_zip`
- Метод: `POST`
- Описание: Скачивает zip-архив с товарами из корзины пользователя.
- Ответ:
  - Код состояния: `200 OK`
  - Файловый ответ: Zip-архив с товарами.

#### `get_PATH_by_item_id`

- Описание: Функция для получения пути к файлу по идентификатору товара.
- Параметры:
  - `item_id` (целое число, обязательно): Идентификатор товара.
- Возвращает: Путь к файлу.

#### `download_item`

- URL: `/download/<int:item_id>`
- Метод: `POST`
- Описание: Скчивает выбранный товар.
- Параметры URL:
  - `item_id` (целое число, обязательно): Идентификатор товара.
- Ответ:
  - Код состояния: `200 OK`
  - Файловый ответ: Выбранный товар.

#### `mail_item`

- URL: `/mail/<int:item_id>`
- Метод: `POST`
- Описание: Отправляет товар по электронной почте.
- Параметры URL:
  - `item_id` (целое число, обязательно): Идентификатор товара.
- Ответ:
  - Код состояния: `302 Found`
  - Перенаправляет на почтовый клиент с предзаполненным письмом и вложением товара.

#### Главная страница

- URL: `/`
- Метод: `GET`
- Описание: Отображает главную страницу магазина со списком товаров.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница с отображением списка товаров.

#### Создание товара

- URL: `/create`
- Методы: `GET`, `POST`
- Описание: Создает новый товар в магазине.
- Запросы:
  - GET: Возвращает страницу создания товара.
  - POST: Создает новый товар на основе данных из формы.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница с формой создания товара или перенаправление на главную страницу магазина.

#### Удаление товара

- URL: `/delete_cart_item/<int:item_id>`
- Метод: `POST`
- Описание: Удаляет товар из магазина.
- Параметры URL:
  - `item_id` (целое число, обязательно): Идентификатор товара.
- Ответ:
  - Код состояния: `302 Found`
  - Перенаправляет на главную страницу магазина.

#### Просмотр товара

- URL: `/store/item/<int:item_id>`
- Метод: `GET`
- Описание: Отображает информацию о товаре.
- Параметры URL:
  - `item_id` (целое число, обязательно): Идентификатор товара.
- Ответ:
  - Код состояния: `200 OK`
  - Тело ответа: HTML-страница с информацией о товаре.

### Аутентификация и авторизация

Для доступа к некоторым конечным точкам магазина требуется аутентификация пользователя и наличие прав администратора.

### Шаблоны и статические файлы

Для работы магазина требуется следующая структура файлов и папок:

```
├── marketplace/
│   ├── static/
│   │   ├── img/
│   │   │   └── [item_image_files]
│   │   └── files/
│   │       └── [item_file_files]
│   └── templates/
│       └── store/
│           ├── index.html
│           ├── create.html
│           └── item.html
├── marketplace.py
└── ...
```

### Аутентификация и авторизация

Для доступа к некоторым конечным точкам магазина требуется аутентификация пользователя и наличие прав администратора.

Для аутентификации используется пакет `flask-login`, который обеспечивает хранение и проверку данных пользователя.

Для авторизации администратора используется декоратор `admin_only`, который проверяет наличие прав администратора у пользователя перед выполнением функции.

### База данных

Для работы магазина требуется наличие базы данных SQLite. База данных должна содержать таблицы `item` и `cart`.

Таблица `item` содержит следующие поля:

- `id` (целое число, первичный ключ): Идентификатор товара.
- `item_name` (строка, обязательно): Название товара.
- `item_description` (строка): Описание товара.
- `item_image` (строка): Имя файла изображения товара.
- `dataset_author` (строка, обязательно): Автор датасета.
- `file_name` (строка, обязательно): Имя файла товара.
- `secured_name` (строка, обязательно):
- `id` (целое число, первичный ключ): Идентификатор товара.
- `item_name` (строка, обязательно): Название товара.
- `item_description` (строка): Описание товара.
- `item_image` (строка): Имя файла изображения товара.
- `dataset_author` (строка, обязательно): Автор датасета.
- `file_name` (строка, обязательно): Имя файла товара.
- `secured_name` (строка, обязательно): Защищенное имя файла товара.
- `original_file_name` (строка, обязательно): Оригинальное имя файла товара.

Таблица `cart` содержит следующие поля:

- `cart_id` (целое число, первичный ключ): Идентификатор элемента корзины.
- `user_id` (целое число, обязательно): Идентификатор пользователя.
- `item_id` (целое число, обязательно): Идентификатор товара.
- `FOREIGN KEY (user_id) REFERENCES user (id)`: Внешний ключ на таблицу пользователей.
- `FOREIGN KEY (item_id) REFERENCES item (id)`: Внешний ключ на таблицу товаров.

### Декораторы

#### `login_required`

Декоратор, который может использоваться для защиты маршрутов, требующих аутентификации пользователя.

#### `admin_only`

Декоратор, который может использоваться для защиты маршрутов, требующих прав администратора.

### Статические файлы

Магазин использует следующие папки для хранения статических файлов:

- `img/`: Папка для хранения изображений товаров.
- `files/`: Папка для хранения файлов товаров.

### Шаблоны

Магазин использует следующие HTML-шаблоны:

- `index.html`: Шаблон главной страницы магазина со списком товаров.
- `create.html`: Шаблон страницы создания нового товара.
- `item.html`: Шаблон страницы с информацией о товаре.

### Формат файлов

Магазин поддерживает загрузку файлов в следующих форматах:

- Изображения: `png`, `jpg`, `jpeg`, `gif`
- Документы: `txt`, `pdf`
- Таблицы: `xlsx`

### Зависимости

Для работы магазина требуются следующие зависимости:

- Flask
- Werkzeug
- pandas

### Конфигурация

Для настройки магазина можно использовать следующую конфигурацию:

```python
SECRET_KEY = 'your_secret_key'
DATABASE = '/path/to/database.sqlite'
IMG_FOLDER = '/path/to/img_folder'
FILE_FOLDER = '/path/to/file_folder'
```

Где:

- `SECRET_KEY`: Секретный ключ для Flask.
- `DATABASE`: Путь к файлу базы данных SQLite.
- `IMG_FOLDER`: Путь к папке для хранения изображений товаров.
- `FILE_FOLDER`: Путь к папке для хранения файлов товаров.
