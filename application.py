from flask import Flask, render_template, request, session,redirect,url_for,jsonify
import os
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from signuppy import sigunupvaildr
import requests
# import mediaClass

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)
app.secret_key=os.urandom(24)
userinf0={'sreejith':'password','subash':'pass'}
notes={'sreejith':[],'subash':[]}

@app.route("/", methods=["GET", "POST"])
def index():
	users1 = db.execute("SELECT password FROM userinfo WHERE username = :username", {"username": "sreejith"}).fetchone()


	if 'id' not in session:
		#Comment following line
		#session['id']=1

		return redirect(url_for('login'))
	if request.method == 'POST':
		search_text = request.form.get("search_text")
		search_type = request.form.get("search_type")
		search_text ="%"+search_text+"%"
		if search_type=="title":
			search_result=db.execute("SELECT * FROM books_main WHERE title LIKE  :search_text", {"search_text": search_text}).fetchall()
		elif search_type=="author":
			search_result=db.execute("SELECT * FROM books_main WHERE author LIKE  :search_text", {"search_text": search_text}).fetchall()
		else:
			search_result=db.execute("SELECT * FROM books_main WHERE isbn LIKE  :search_text", {"search_text": search_text}).fetchall()	
		
		if search_result:
			m1=str(len(search_result))+" results found"
			return render_template('index.html',message=m1,search_results=search_result)
		else:
			m1="No results found."
		return render_template('index.html',message='No results')

	return render_template('index.html')

@app.route("/login",methods=["GET", "POST"])
def login():
	if request.method == 'POST':
		input_username=request.form['username']
		input_password=request.form['password']
		dbpassword = db.execute("SELECT password FROM userinfo WHERE username = :username", {"username": input_username}).fetchone()
		if dbpassword:
			if dbpassword[0]==input_password:
				user_id=db.execute("SELECT id FROM userinfo WHERE username = :username", {"username": input_username}).fetchone().id
				session['id']=user_id
				return redirect(url_for('index'))
		return 'Enter valid Login Details'
		
		# if usr1 in userinf0:
		# 	if userinf0[usr1]==pass1:
		# 		session['id']=usr1
		# 		return redirect(url_for('index'))
		# return 'Hey you are trying to login'

	else:
		if 'id' in session:
			return redirect(url_for('dropsession'))
		return render_template("login.html")
@app.route("/logout",methods=["GET"])
def dropsession():
	session.pop('id',None)
	return redirect(url_for('login'))
@app.route("/signup",methods=["GET","POST"])
def signup(message=None):
	if request.method == 'POST':
		input_username=request.form['username']
		input_password1=request.form['password1']
		input_password2=request.form['password2']
		input_email=request.form['email']
		signup_status=sigunupvaildr(input_username,input_password1,input_password2,input_email)
		if signup_status[1]!= 0:
			return render_template('signup.html',message=signup_status[0])
		else:
			if db.execute("SELECT * FROM userinfo WHERE username = :username", {"username": input_username}).rowcount == 0:
				if db.execute("SELECT * FROM userinfo WHERE email = :email", {"email": input_email}).rowcount == 0:
					try:
						db.execute("INSERT INTO userinfo (username,password,email) VALUES (:username, :password, :email)",{"username": input_username, "password": input_password1, "email":input_email})
						db.commit()
						return render_template('signup.html',success_message='success',dbld='disabled')
					except:
						return render_template('signup.html',message='Oops.Something went wrong. Try again')	
				else:
					return render_template('signup.html',message='You have already registered with this email. Try loggin in.')
			else:
				return render_template('signup.html',message='Username already exists. Try another one') 
	else:
		if 'id' in session:
			return redirect(url_for('dropsession'))
		return render_template('signup.html')

@app.route("/book/<int:book_id>",methods=["GET","POST"])
def bookpage(book_id):
	if 'id' not in session:
		#Comment following line
		#session['id']=1

		return redirect(url_for('login'))
	if (db.execute("SELECT * FROM books_main WHERE id = :id", {"id": book_id}).rowcount == 0):
		return render_template('error.html',message="Book not Found")
	try:
		goodreadskey=os.getenv("goodreads_key")
		isbn=db.execute("SELECT * FROM books_main WHERE  id= :book_id",{"book_id":book_id}).fetchone().isbn
		res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": goodreadskey, "isbns": isbn})
		if res.status_code != 200:
			raise KeyError('book not found')
		gdvalues=(res.json())
		gdvalues=gdvalues['books'][0]
	except KeyError:
		gdvalues={}
	reviewed=True
	if 'id' in session and db.execute("SELECT * FROM books_review WHERE  user_id = :user_id AND book_id= :book_id",{"user_id":session["id"],"book_id":book_id}).rowcount == 0:
		
		reviewed=False
	if request.method == 'POST' and reviewed==False:

	
		input_rating=request.form['rating']
		input_user_review=request.form['usertext']

		try:
			db.execute("INSERT INTO books_review (book_id,user_id,user_rating,review_text) VALUES (:book_id, :user_id, :user_rating, :review_text)",{"book_id": book_id, "user_id": session["id"], "user_rating":input_rating,"review_text":input_user_review})
			db.commit()
			reviewed=True
			total_rating=db.execute("SELECT SUM(user_rating) AS total FROM books_review WHERE book_id= :book_id",{"book_id":book_id}).fetchone().total
			no_of_ratings=db.execute("SELECT COUNT(*) FROM books_review WHERE book_id=:book_id",{"book_id":book_id}).fetchone().count
			new_Rating=round(total_rating/no_of_ratings,2)
			db.execute("UPDATE books_main set ratings=:new_Rating ,reviews=:no_of_ratings WHERE id=:id",{"new_Rating":new_Rating,"no_of_ratings":no_of_ratings,"id":book_id})
			db.commit()	
		except:
			db.rollback()
			return render_template('error.html',message="Oops! Something unexpected happend")


	book=db.execute("SELECT * FROM books_main WHERE id = :id", {"id": book_id}).fetchone()
	reviews=db.execute("SELECT username,review_text,user_rating FROM userinfo JOIN books_review ON books_review.user_id = userinfo.id WHERE book_id= :book_id", {"book_id": book_id}).fetchall()

	return render_template('book.html',book=book,reviews=reviews,reviewed=reviewed,gdvalues=gdvalues)
@app.route("/api/<string:isbn>",methods=["GET"])
def bookapi(isbn):

	if (db.execute("SELECT * FROM books_main WHERE isbn = :isbn", {"isbn": isbn}).rowcount == 0):
		return  jsonify({"error": "Invalid isbn"}), 404
	book=db.execute("SELECT * FROM books_main WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
	return jsonify({
    "title": book.title,
    "author": book.author,
    "year": book.year,
    "isbn": isbn,
    "review_count": int(book.reviews),
    "average_score":round(float(book.ratings),2)
})