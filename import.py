#! /usr/bin/python
import os
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def create_Table0():
	sql_command="""CREATE TABLE userinfo (
	id SERIAL PRIMARY KEY,
	username VARCHAR NOT NULL,
	email VARCHAR NOT NULL,
	password VARCHAR NOT NULL,
	UNIQUE(username,email)
	);
	"""

	db.execute(sql_command)
	db.commit()


# create_Table0()
def create_Table1():
	sql_command="""CREATE TABLE books_main (
	id SERIAL PRIMARY KEY,
	isbn VARCHAR NOT NULL,
	title VARCHAR NOT NULL,
	author VARCHAR NOT NULL,
	year INTEGER NOT NULL,
	ratings NUMERIC DEFAULT 0.0,
	reviews INTEGER DEFAULT 0,
	UNIQUE(isbn)
	);
	"""

	db.execute(sql_command)
	db.commit()
# create_Table1()

def add_values1():
	f1=open('books.csv')
	reader=csv.reader(f1)
	skip_first=0
	for isbn,title,author,year in reader:
		if skip_first != 0:
			db.execute("INSERT INTO books_main (isbn,title,author,year) VALUES (:isbn, :title, :author,:year)",{"isbn": isbn, "title": title, "author": author, "year":year})
			db.commit()
		skip_first=1

# add_values1()
def create_Table2():
	sql_command="""CREATE TABLE books_review (
	id SERIAL PRIMARY KEY,
	book_id INTEGER REFERENCES books_main(id) NOT NULL,
	user_id INTEGER REFERENCES userinfo(id) NOT NULL,
	user_rating NUMERIC DEFAULT 0.0,
	review_text TEXT
	);
	"""

	db.execute(sql_command)
	db.commit()
# create_Table2()