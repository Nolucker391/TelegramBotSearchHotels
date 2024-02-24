import sqlite3
from loguru import logger

connection_string = "database/history.db"


def create_table_user() -> None:
    """
    Создает пустую таблицу с параметрами:
    id, username, chat_id, full_name
    , если бота запускает новый пользователь.

    Данная таблица не участвует в выдаче сохраненной
    информации. Она просто хранит данные пользователя.

    : param chat_id : int
    : param username : str
    : param full_name : str
    : return : None
    """

    with sqlite3.connect(connection_string) as connect:
        cursor = connect.cursor()
        cursor.execute(
            "SELECT CASE WHEN tbl_name = 'user' THEN 1 ELSE 0 END FROM sqlite_master WHERE tbl_name = 'user' AND type = 'table'"
        )

        records = cursor.fetchall()

        try:
            if records[0][0] == 1:
                pass

        except IndexError:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS user(
                                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                chat_id INTEGER UNIQUE,
                                username STRING,
                                full_name TEXT
                            );
                            """
            )
            connect.commit()


def add_user(chat_id: int, username: str, full_name: str) -> None:
    """
    Добавляет в таблицу данные пользователя:
    id, username, chat_id, full_name

    Данная таблица не участвует в выдаче сохраненной
    информации. Она просто хранит данные пользователя.

    : param chat_id : int
    : param username : str
    : param full_name : str
    : return : None
    """
    with sqlite3.connect(connection_string) as connection:
        cursor = connection.cursor()

        try:
            cursor.execute(
                "INSERT INTO user (chat_id, username, full_name) VALUES (?, ?, ?)",
                (chat_id, username, full_name),
            )
            logger.info("Добавлен новый пользователь.")
            connection.commit()

        except sqlite3.IntegrityError:
            logger.info("Данный пользователь уже существует")


def add_query(query_data: dict) -> None:
    """
    Создаёт таблицу, если она ещё не создавалась и добавляет туда данные,
    которые ввел пользователь для поиска
    : param query_data : dict
    : return : None
    """
    with sqlite3.connect(connection_string) as connection:
        cursor = connection.cursor()

        user_id = query_data["chat_id"]
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS query(
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER,
            date_time STRING, 
            input_city STRING,
            destination_id STRING,
            photo_need STRING,
            response_id INTEGER,
            FOREIGN KEY (response_id) REFERENCES response(id) ON DELETE CASCADE ON UPDATE CASCADE
        );    
        """
        )

        try:
            cursor.execute(
                "INSERT INTO query(user_id, input_city, photo_need, destination_id, date_time) VALUES (?, ?, ?, ?, ?)",
                (
                    user_id,
                    query_data["input_city"],
                    query_data["photo_need"],
                    query_data["destination_id"],
                    query_data["date_time"],
                ),
            )
            logger.info("Добавлен в БД новый запрос.")

            # Нам не нужно очень много записей историй поиска, поэтому для каждого пользователя
            # будем хранить только 5 последних записей, лишние - удалим.
            cursor.execute(
                f"""
                    DELETE FROM query WHERE query.[date_time]=
                    (SELECT MIN([date_time]) FROM query WHERE `user_id` = '{user_id}' )
                    AND
                    ((SELECT COUNT(*) FROM query WHERE `user_id` = '{user_id}' ) > 5 ) 
                """
            )
            connection.commit()
        except sqlite3.IntegrityError:
            print("Запрос с такой датой и временем уже существует")


def add_response(search_result: dict) -> None:
    """
    Создаёт таблицу, если она ещё не создавалась и добавляет туда данные,
    которые бот получил в результате запросов к серверу.
    : param search_result : dict
    : return : None
    """
    with sqlite3.connect(connection_string) as connection:
        cursor = connection.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS response(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
                query_id INTEGER,
                hotel_id STRING,
                name STRING,
                address STRING, 
                price REAL,
                total REAL,
                distance REAL,
                FOREIGN KEY (hotel_id) REFERENCES images(hotel_id) ON DELETE CASCADE ON UPDATE CASCADE
            );
            """
        )

        for item in search_result.items():
            cursor.execute(
                f"SELECT `id` FROM query WHERE `date_time` = ?", (item[1]["date_time"],)
            )
            query_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO response(query_id, hotel_id, name, address, price, total, distance) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    query_id,
                    item[0],
                    item[1]["name"],
                    item[1]["address"],
                    item[1]["price"],
                    item[1]["total"],
                    item[1]["distance"],
                ),
            )
            logger.info("Добавлены в БД данные отеля.")

            for link in item[1]["images"]:
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS images(
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    hotel_id INTEGER REFERENCES response (id),
                    link TEXT     
                    );"""
                )
                cursor.execute(
                    "INSERT INTO images (hotel_id, link) VALUES (?, ?)", (item[0], link)
                )

            logger.info("Добавлены в БД ссылки на фотографии отеля.")
            connection.commit()
