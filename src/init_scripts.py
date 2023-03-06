import psycopg2

conn = psycopg2.connect(
    host="localhost", database="scrapDb", user="scrapReality", password="Password001+"
)

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a command: this creates a new table
cur.execute(
    "CREATE TABLE IF NOT EXISTS flat (id int PRIMARY KEY,"
    "title varchar (150) NOT NULL,"
    "place varchar (150) NOT NULL,"
    "price varchar (20) NOT NULL,"
    "url varchar (100) NOT NULL,"
    "date_added date DEFAULT CURRENT_TIMESTAMP);"
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS  media (id int PRIMARY KEY,"
    "video boolean NOT NULL,"
    "url varchar (150) NOT NULL,"
    "flat_id int,"
    "FOREIGN KEY (flat_id) REFERENCES flat (id))"
)

cur.execute(
    "CREATE TABLE IF NOT EXISTS attribute (id int PRIMARY KEY,"
    "text varchar(100) NOT NULL)"
)

cur.execute(
    "CREATE TABLE IF NOT EXISTS attribute_flat (attribute_id int,"
    "flat_id int, FOREIGN KEY (flat_id) REFERENCES flat (id),"
    "FOREIGN KEY (attribute_id) REFERENCES attribute (id))"
)
conn.commit()

cur.close()
conn.close()
