import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Course(db.Model):
    course_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    course_name = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    cr_hours = db.Column(db.Integer, unique=False, nullable=False, primary_key=False)
    exam = db.relationship('Exam', backref='course', lazy=True)
    
    def __repr__(self):
        return "<Title: {}>".format(self.course_name)

class Student(db.Model):
    student_id = db.Column(db.String(50), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    ph_number = db.Column(db.String(80), unique=True, nullable=False, primary_key=False)

    def __repr__(self):
        return "<Title: {}>".format(self.name)

class Room(db.Model):
    room_id = db.Column(db.Integer, unique=True, nullable=False, primary_key=True)
    room_code = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    capacity = db.Column(db.Integer, unique=True, nullable=False, primary_key=False)
    exams = db.relationship('Exam', backref='room', lazy=True)
    stream_address = db.Column(db.String(200), unique=False, nullable=False, primary_key=False)
    

    def __repr__(self):
        return "<Title: {}>".format(self.room_code)

class Exam(db.Model):
    exam_id = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    time_slot = db.Column(db.String(80), unique=False, nullable=False, primary_key=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'),nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'),nullable=False)
    duration = db.Column(db.Integer,nullable=True)

		

def init_db():
	db.create_all()

# if __name__ == '__main__':
#     init_db()
