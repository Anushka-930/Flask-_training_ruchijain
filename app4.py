import os
import sqlite3
from functools import wraps

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-before-deploying")
app.config["DATABASE"] = os.path.join(app.root_path, "library.db")


def get_db():
	if "db" not in g:
		g.db = sqlite3.connect(app.config["DATABASE"])
		g.db.row_factory = sqlite3.Row
	return g.db


@app.teardown_appcontext
def close_db(_error=None):
	database = g.pop("db", None)
	if database is not None:
		database.close()


def init_db():
	database = get_db()
	database.executescript(
		"""
		CREATE TABLE IF NOT EXISTS users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name TEXT NOT NULL,
			email TEXT NOT NULL UNIQUE,
			password_hash TEXT NOT NULL
		);
		CREATE TABLE IF NOT EXISTS books (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			user_id INTEGER NOT NULL REFERENCES users(id),
			book_number TEXT NOT NULL,
			name TEXT NOT NULL,
			author TEXT NOT NULL,
			book_type TEXT NOT NULL,
			issue_date TEXT NOT NULL,
			UNIQUE(user_id, book_number)
		);
		"""
	)
	database.commit()


def login_required(view):
	@wraps(view)
	def wrapped_view(**kwargs):
		if "user_id" not in session:
			flash("Please log in to continue.", "error")
			return redirect(url_for("login"))
		return view(**kwargs)

	return wrapped_view


@app.route("/")
def home():
	if "user_id" in session:
		return redirect(url_for("dashboard"))
	return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
	if request.method == "POST":
		name = request.form.get("name", "").strip()
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")

		if not name or not email or not password:
			flash("Please complete every field.", "error")
		elif len(password) < 8:
			flash("Use a password with at least 8 characters.", "error")
		else:
			database = get_db()
			try:
				cursor = database.execute(
					"INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
					(name, email, generate_password_hash(password)),
				)
				database.commit()
			except sqlite3.IntegrityError:
				flash("An account with that email already exists.", "error")
			else:
				session.clear()
				session["user_id"] = cursor.lastrowid
				session["user_name"] = name
				return redirect(url_for("dashboard"))

	return render_template("auth.html", mode="signup")


@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		email = request.form.get("email", "").strip().lower()
		password = request.form.get("password", "")
		user = get_db().execute(
			"SELECT id, name, password_hash FROM users WHERE email = ?", (email,)
		).fetchone()

		if user is None or not check_password_hash(user["password_hash"], password):
			flash("Email or password is incorrect.", "error")
		else:
			session.clear()
			session["user_id"] = user["id"]
			session["user_name"] = user["name"]
			return redirect(url_for("dashboard"))

	return render_template("auth.html", mode="login")


@app.route("/dashboard")
@login_required
def dashboard():
	return render_template("dashboard.html")


@app.route("/books/new", methods=["GET", "POST"])
@login_required
def add_book():
	if request.method == "POST":
		book_number = request.form.get("book_number", "").strip()
		name = request.form.get("name", "").strip()
		author = request.form.get("author", "").strip()
		book_type = request.form.get("book_type", "").strip()
		issue_date = request.form.get("issue_date", "").strip()

		if not all((book_number, name, author, book_type, issue_date)):
			flash("Please complete every book field.", "error")
		else:
			database = get_db()
			try:
				database.execute(
					"""INSERT INTO books
					   (user_id, book_number, name, author, book_type, issue_date)
					   VALUES (?, ?, ?, ?, ?, ?)""",
					(session["user_id"], book_number, name, author, book_type, issue_date),
				)
				database.commit()
			except sqlite3.IntegrityError:
				flash("You already have a book with that number.", "error")
			else:
				flash("Book saved successfully.", "success")
				return redirect(url_for("books"))

	return render_template("add_book.html")


@app.route("/books")
@login_required
def books():
	book_list = get_db().execute(
		"SELECT * FROM books WHERE user_id = ? ORDER BY id DESC", (session["user_id"],)
	).fetchall()
	return render_template("books.html", books=book_list)


@app.route("/logout", methods=["POST"])
def logout():
	session.clear()
	return redirect(url_for("home"))


with app.app_context():
	init_db()


if __name__ == "__main__":
	app.run(debug=True)
