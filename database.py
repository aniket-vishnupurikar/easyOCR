import mysql.connector
import pandas as pd
mydb = mysql.connector.connect(host="localhost", user="root", password="mysql", database="ocr")
mycursor = mydb.cursor(buffered=True)
mycursor.execute(f"CREATE DATABASE ocr")
mycursor.execute(f"USE ocr")
mycursor.execute(f'''CREATE TABLE ocr_data_2
                   (id INTEGER PRIMARY KEY AUTO_INCREMENT,
                   card_holder_name TEXT,
                   designation TEXT,
                   company_name TEXT,
                   email_address TEXT,
                   mobile_number VARCHAR(50),
                   website_url TEXT,
                   area TEXT,
                   city TEXT,
                   state TEXT,
                   pin_code VARCHAR(10),
                   image LONGBLOB
                    )''')