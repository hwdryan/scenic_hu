import sqlite3

# Connect to database
conn = sqlite3.connect('customer.db')

# Create a cursor
c = conn.cursor()

# Create a table
c.execute("""INSERT INTo customers VALUES ('Weidong', 'Hu','weidong@x.com')
""")


conn.commit()
conn.close()