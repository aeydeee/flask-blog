import mysql.connector

# Connect to MySQL server
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
)

my_cursor = mydb.cursor()

# Check if the database already exists
my_cursor.execute("SHOW DATABASES")
databases = my_cursor.fetchall()

database_name = "users"

if (database_name,) not in databases:
    my_cursor.execute(f"CREATE DATABASE {database_name}")
    print(f"Database '{database_name}' created successfully.")
else:
    print(f"Database '{database_name}' already exists.")

# List all databases
my_cursor.execute("SHOW DATABASES")
for db in my_cursor:
    print(db)
