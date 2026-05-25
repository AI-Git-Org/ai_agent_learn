import os
import mysql.connector
from mysql.connector import Error


def create_db_connection(
        host_name,
        user_name,
        user_password,
        db_name=None):

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

        return connection

    except Error as err:

        print(f"Connection error: {err}")

        return None


def execute_single_query(connection, query, message=None):

    cursor = connection.cursor()

    try:

        cursor.execute(query)

        connection.commit()

        if message:
            print(message)

    except Error as err:

        connection.rollback()

        print(f"Query execution error: {err}")

    finally:

        cursor.close()


def initialize_schema(connection, schema_file_path):

    if not os.path.exists(schema_file_path):

        print(f"Schema file not found: {schema_file_path}")

        return False

    print(f"Loading schema from '{schema_file_path}'")

    with open(schema_file_path, "r", encoding="utf-8") as file:

        sql_script = file.read()

    cursor = connection.cursor()

    try:

        statements = sql_script.split(";")

        for statement in statements:

            statement = statement.strip()

            if statement:

                print(f"\nExecuting:\n{statement[:100]}...")

                cursor.execute(statement)

        connection.commit()

        print("\nDatabase schema initialized successfully")

        return True

    except Error as err:

        connection.rollback()

        print(f"\nSchema initialization error: {err}")

        return False

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

    DB_PASSWORD = os.getenv(
        "DB_PASSWORD",
        "Dbroot123$"
    )

    DB_NAME = os.getenv(
        "DB_NAME",
        "financial_db"
    )

    SCHEMA_FILE = "init.sql"

    print("\nConnecting to MySQL server...\n")

    server_connection = create_db_connection(
        DB_HOST,
        DB_USER,
        DB_PASSWORD
    )

    if not server_connection:

        print("Unable to connect to MySQL server")

        exit(1)

    print(f"\nDropping database '{DB_NAME}' if it exists...\n")

    execute_single_query(
        server_connection,
        f"DROP DATABASE IF EXISTS {DB_NAME}",
        f"Database '{DB_NAME}' dropped"
    )

    print(f"\nCreating database '{DB_NAME}'...\n")

    execute_single_query(
        server_connection,
        f"CREATE DATABASE {DB_NAME}",
        f"Database '{DB_NAME}' created"
    )

    server_connection.close()

    print(f"\nConnecting to '{DB_NAME}'...\n")

    connection = create_db_connection(
        DB_HOST,
        DB_USER,
        DB_PASSWORD,
        DB_NAME
    )

    if not connection:

        print(f"Failed to connect to '{DB_NAME}'")

        exit(1)

    schema_success = initialize_schema(
        connection,
        SCHEMA_FILE
    )

    if schema_success:

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

    connection.close()

    print("\nMySQL connection closed")