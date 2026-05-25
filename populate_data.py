import os
from mysql_connection import create_db_connection
from mysql.connector import Error

def populate_dummy_data():
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Dbroot123$")
    DB_NAME = os.getenv("DB_NAME", "financial_db")

    print(f"Connecting to '{DB_NAME}' on '{DB_HOST}' to populate exact dummy data...")
    connection = create_db_connection(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

    if not connection:
        print("Failed to connect to database. Please make sure the MySQL server is running and credentials are correct.")
        return

    cursor = connection.cursor()

    try:
        # Disable foreign key checks to safely truncate existing tables
        print("Clearing existing data...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        tables_to_truncate = [
            "Tb_use_rate",
            "Tb_TP_rate",
            "Tb_ticket_balance",
            "Tb_contract_balance",
            "Tb_LE_code",
            "Tb_ccy_master"
        ]
        for table in tables_to_truncate:
            cursor.execute(f"TRUNCATE TABLE {table};")
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Existing data cleared.")

        # 1. Populate Tb_ccy_master with random currency codes and day counts
        print("Inserting Currency Master data...")
        ccy_query = "INSERT INTO Tb_ccy_master (Currency_code, Day_count) VALUES (%s, %s);"
        ccy_data = [
            ('USD', 'Actual/360'),
            ('EUR', '30/360'),
            ('GBP', 'Actual/365'),
            ('JPY', 'Actual/365'),
            ('CAD', 'Actual/365')
        ]
        cursor.executemany(ccy_query, ccy_data)

        # 2. Populate Tb_LE_code with legal entities
        print("Inserting Legal Entity codes...")
        le_query = "INSERT INTO Tb_LE_code (LE_code, LE_desc) VALUES (%s, %s);"
        le_data = [
            ('LE001', 'Acme Financial Services US'),
            ('LE002', 'Global Banking Corp UK'),
            ('LE003', 'Enterprise Solutions India'),
            ('LE004', 'Pacific Holdings Japan')
        ]
        cursor.executemany(le_query, le_data)

        # 3. Populate Tb_contract_balance (Exactly 2 records with specific math constraints)
        # Record 1 (April): Amt = 1,000,000.0000, PnL = 55,000.0000
        # Record 2 (May):   Amt = 1,100,000.0000 (+10%), PnL = 88,000.0000 (+60%)
        print("Inserting 2 Contract Balance records...")
        contract_query = """
            INSERT INTO Tb_contract_balance (As_of_date, Start_date, End_date, Amt, Cust_rate, PnL, Currency) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        contract_data = [
            ('2026-04-15', '2026-04-01', '2026-10-01', 1000000.0000, 0.050000, 55000.0000, 'USD'),
            ('2026-05-15', '2026-04-01', '2026-10-01', 1100000.0000, 0.050000, 88000.0000, 'USD')
        ]
        cursor.executemany(contract_query, contract_data)

        # 4. Populate Tb_use_rate (Adjusted bid rates based on: Amt * Bid_rate = PnL)
        # April Record: Bid_rate = PnL_1 / Amt_1 = 55,000 / 1,000,000 = 0.055000
        # May Record:   Bid_rate = PnL_2 / Amt_2 = 88,000 / 1,100,000 = 0.080000
        print("Inserting matching Use Rates...")
        use_rate_query = """
            INSERT INTO Tb_use_rate (As_of_rate, yc_code, Bid_rate, Offer_rate, Tenure, Currency)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        use_rate_data = [
            ('2026-04-15', 'SOFR', 0.055000, 0.056000, '6M', 'USD'),
            ('2026-05-15', 'SOFR', 0.080000, 0.081000, '6M', 'USD')
        ]
        cursor.executemany(use_rate_query, use_rate_data)

        # 5. Populate Tb_ticket_balance (Exactly 2 records, PnL differing by 8%)
        # April Record: PnL = 10,000.00
        # May Record:   PnL = 10,800.00 (8% increase)
        print("Inserting Ticket Balances...")
        ticket_query = """
            INSERT INTO Tb_ticket_balance (As_of_date, Start_date, End_date, Amt, TP_rate, PnL, Currency)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        ticket_data = [
            ('2026-04-15', '2026-04-15', '2026-05-15', 100000.0000, 0.040000, 10000.0000, 'USD'),
            ('2026-05-15', '2026-04-15', '2026-05-15', 100000.0000, 0.040000, 10800.0000, 'USD')
        ]
        cursor.executemany(ticket_query, ticket_data)

        # 6. Populate Tb_TP_rate with random TP rates matching currencies and tenures
        print("Inserting TP Rates...")
        tp_rate_query = """
            INSERT INTO Tb_TP_rate (As_of_date, Start_date, End_date, Bid_rate, Offer_rate, Tenure, Currency)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        tp_rate_data = [
            # April TP Rates
            ('2026-04-15', '2026-04-15', '2026-05-15', 0.038000, 0.039000, '1M', 'USD'),
            ('2026-04-15', '2026-04-15', '2026-07-15', 0.041000, 0.042500, '3M', 'USD'),
            ('2026-04-15', '2026-04-15', '2026-05-15', 0.029000, 0.030500, '1M', 'EUR'),
            ('2026-04-15', '2026-04-15', '2026-07-15', 0.031000, 0.032500, '3M', 'EUR'),
            # May TP Rates
            ('2026-05-15', '2026-05-15', '2026-06-15', 0.039000, 0.040000, '1M', 'USD'),
            ('2026-05-15', '2026-05-15', '2026-08-15', 0.042000, 0.043500, '3M', 'USD'),
            ('2026-05-15', '2026-05-15', '2026-06-15', 0.029500, 0.031000, '1M', 'EUR'),
            ('2026-05-15', '2026-05-15', '2026-08-15', 0.032000, 0.033500, '3M', 'EUR')
        ]
        cursor.executemany(tp_rate_query, tp_rate_data)

        connection.commit()
        print("\nAll dummy data populated successfully with precise math and random support data!")

    except Error as err:
        print(f"Error populating data: {err}")
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    populate_dummy_data()
