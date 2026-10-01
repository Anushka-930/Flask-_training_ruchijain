from flask import Flask,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---

# Option A: SQLite (Creates a local file named 'project.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/flaskproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("anushka")
db = SQLAlchemy(app)

#database model
class user(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80),nullable=True)
    email=db.Column(db.String(20),nullable=True)
    phone_num=db.Column(db.String(12),nullable=True)
    meg=db.Column(db.String(80),nullable=True)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)