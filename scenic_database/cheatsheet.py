import sqlite3

conn = sqlite3.connect('tbl.db')

c = conn.cursor()

# create a table
"""
c.execute(create table tbl(name text, age integer, height_in_m real))
"""
# insert one record into table
"""
c.execute(insert into tbl values('Howard',26,1.73))
"""
# insert many records into table
"""
many_records = [
    ('Howard',26,1.73),
    ('John',25,1.67),
    ('Sara',51,1.56)
]

c.executemany("insert into tbl values(?,?,?)", many_records)
"""
# Query
"""
c.execute("select * from tbl")
# return a list of tuple
q = c.fetchall()
q = c.fetchone()
q = c.fetchmany(3)
"""
# Use where clause
"""
c.execute("select rowid, * from tbl where age = 25")
c.execute("select rowid, * from tbl where name like 'Ho%' ")
c.execute("select rowid, * from tbl where age between 24 and 26 ")
c.execute("select rowid, * from tbl where age in (12,56,24) ")
"""
# Update records
"""
c.execute("Update tbl set height_in_m = '1.83' where rowid = 2")
"""
# Delete records
"""
c.execute("delete from tbl where rowid = 3")
"""
# Order results
"""
c.execute("select rowid, * from tbl order by age")
print(c.fetchall())
"""
# AND/OR
"""
c.execute("select rowid, * from tbl where age <= 25 AND height_in_m >=1.6")
print(c.fetchall())
"""
# Limiting results
"""
c.execute("select rowid, * from tbl order by age limit 2")
print(c.fetchall())
"""
# Drop a table
"""
c.execute("drop table tbl2")
"""
# Copy (part of) a table
"""
c.execute("create table tbl2 as select * from tbl")
c.execute("create table tbl2 as select * from tbl where age <= 30")
"""
# Change table's structure
"""
1. create a new table
create table ntbl(name text, height real, email text);
2. insert data from old table
insert into ntbl(name,height) select name,height_in_m from tbl; 
3. drop old table and change new table's name to old table.
drop table tbl;
alter table ntbl rename to tbl;
"""
# Add columns
"""
alter table tbl add score integer;
"""
# frequently used functions
"""
avg(),count(),max(),min(),sum()
"""
"""
select avg(age) from tbl;
select rowid, name, max(age) from tbl;
"""
# Group by clause
"""
# row count for each class
select class,count(*) from tbl group by class;
# average score for each class
select class,avg(score) from tbl group by class;
# average class for class_A
select class,avg(score) from tbl where class='class_A' group by class;
"""
# Having clause (Note: a GROUP BY clause is required before HAVING)
"""
# average score for class which have average score >=90
select class,avg(score) from tbl group by class having avg(score)<80;
"""
# Sqlite constraints
"""
# NOT NULL Constraint: Ensures that a column cannot have NULL value.
CREATE TABLE COMPANY(
   ID INT PRIMARY KEY     NOT NULL,
   NAME           TEXT    NOT NULL,
   AGE            INT     NOT NULL,
   ADDRESS        CHAR(50),
   SALARY         REAL
);

# DEFAULT Constraint: Provides a default value for a column when none is specified.
CREATE TABLE COMPANY(
   ID INT PRIMARY KEY     NOT NULL,
   NAME           TEXT    NOT NULL,
   AGE            INT     NOT NULL,
   ADDRESS        CHAR(50),
   SALARY         REAL    DEFAULT 50000.00
);

# UNIQUE Constraint: Ensures that all values in a column are different.
CREATE TABLE COMPANY(
   ID INT PRIMARY KEY     NOT NULL,
   NAME           TEXT    NOT NULL,
   AGE            INT     NOT NULL UNIQUE,
   ADDRESS        CHAR(50),
   SALARY         REAL    DEFAULT 50000.00
);

# PRIMARY Key: Uniquely identifies each row/record in a database table.
CREATE TABLE COMPANY(
   ID INT PRIMARY KEY     NOT NULL,
   NAME           TEXT    NOT NULL,
   AGE            INT     NOT NULL,
   ADDRESS        CHAR(50),
   SALARY         REAL
);

# CHECK C  onstraint: Ensures that all values in a column satisfies certain conditions.
CREATE TABLE COMPANY3(
   ID INT PRIMARY KEY     NOT NULL,
   NAME           TEXT    NOT NULL,
   AGE            INT     NOT NULL,
   ADDRESS        CHAR(50),
   SALARY         REAL    CHECK(SALARY > 0)
);
"""


conn.commit()

conn.close()
