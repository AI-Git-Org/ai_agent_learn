import os
import mysql.connector
from mysql.connector import Error


def create_db_connection(
        host_name,
        user_name,
        user_password,
        db_name=None):

    connection = None

    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name
        )

        print(
            f"MySQL connection to "
            f"'{db_name if db_name else 'server'}' successful"
        )

    except Error as err:
        print(f"Connection error: {err}")

    return connection


def initialize_schema(connection, schema_file_path):

    if not os.path.exists(schema_file_path):
        print(f"Schema file not found: {schema_file_path}")
        return

    print(f"Loading schema from {schema_file_path}")

    with open(schema_file_path, "r", encoding="utf-8") as file:
        sql_script = file.read()

    cursor = connection.cursor()

    try:

        statements = sql_script.split(";")

        for statement in statements:

            statement = statement.strip()

            if statement:
                cursor.execute(statement)

        connection.commit()

        print("Database initialized successfully")

    except Error as err:
        print(f"Schema initialization error: {err}")

    finally:
        cursor.close()


def execute_query(connection, query):

    cursor = connection.cursor()

    try:
        cursor.execute(query)
        connection.commit()

        print("Query executed successfully")

    except Error as err:
        print(f"Query error: {err}")

    finally:
        cursor.close()


def read_query(connection, query):

    cursor = connection.cursor()

    try:

        cursor.execute(query)

        result = cursor.fetchall()

        return result

    except Error as err:

        print(f"Read error: {err}")

        return None

    finally:
        cursor.close()


if __name__ == "__main__":

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")

    # replace with your MySQL password
    DB_PASSWORD = os.getenv(
        "DB_PASSWORD",
        "root"
    )

    DB_NAME = os.getenv(
        "DB_NAME",
        "financial_db"
    )

    SCHEMA_FILE = "init.sql"


    print(
        f"Attempting to connect to "
        f"'{DB_NAME}'"
    )

    connection = create_db_connection(
        DB_HOST,
        DB_USER,
        DB_PASSWORD,
        DB_NAME
    )


    if connection is None:

        print(
            "Database does not exist. "
            "Creating..."
        )

        server_connection = create_db_connection(
            DB_HOST,
            DB_USER,
            DB_PASSWORD
        )

        if server_connection:

            initialize_schema(
                server_connection,
                SCHEMA_FILE
            )

            server_connection.close()

            print(
                "Reconnecting to created database..."
            )

            connection = create_db_connection(
                DB_HOST,
                DB_USER,
                DB_PASSWORD,
                DB_NAME
            )

    else:

        print(
            "Database exists."
        )


    if connection:

        try:

            print("\nCurrent tables:\n")

            tables = read_query(
                connection,
                "SHOW TABLES"
            )

            if tables:

                for table in tables:
                    print(f"- {table[0]}")

            else:
                print("No tables found")

        finally:

            connection.close()

            print(
                "\nMySQL connection closed"
            )