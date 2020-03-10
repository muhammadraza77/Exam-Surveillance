from flask import Flask, render_template, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from model.Model import Course
from model.Model import Room
from model.Model import Student
from model.Model import Exam
from model.Model import DetectionAlert
# from model.Model import db
from sqlalchemy import text


project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)


@app.route('/')
@app.route('/login')
def hello():
    return render_template('login.html')


@app.route('/home')
def homescreen():
    detection=DetectionAlert.query.all()
    details = []
    for det in detection:
        myobj = {'s_name':det.student.name,'c_name':det.exam.course.course_name,'r_name':det.exam.room.room_code}
        details.append(myobj)
    return render_template('homescreen.html',details=details)


@app.route('/live_video/<string:video_id>')
def live_video(video_id):
    id = video_id
    Examdetails = Exam.query.filter_by(exam_id=id).first()
    coursedetails = Course.query.filter_by(
        course_id=Examdetails.course_id).first()
    roomdetails = Room.query.filter_by(room_id=Examdetails.room_id).first()
    OtherExam = Exam.query.filter(Exam.exam_id != id).all()
    temp = []
    for Examitration in OtherExam:
        temp.append({"href": "http://localhost:5000/live_video/" +
                     str(Examitration.exam_id), "id": Examitration.exam_id})

    return render_template('live_video.html', Examdetails=Examdetails, coursedetails=coursedetails, roomdetails=roomdetails, OtherExam=OtherExam, Examitration=Examitration, temp=temp, id=id)


@app.route("/exams", methods=["GET", "POST"])
def exams():
    if request.form:
        book = Exam(exam_id=request.form.get("exam_id"), time_slot=request.form.get("time_slot"),
                    room_id=request.form.get("room_id"), course_id=request.form.get("course_id"))
        db.session.add(book)
        db.session.commit()
    exams = Exam.query.all()
    return render_template("Examination.html", exams=exams)


if __name__ == '__main__':
    app.run(debug=True)



# from flask import Flask, render_template, url_for, request, flash, redirect
# from flask_sqlalchemy import SQLAlchemy
# import os 
# from model.Model import Course
# from model.Model import Room
# from model.Model import Student
# from model.Model import Exam
# # from model.Model import db


# project_dir = os.path.dirname(os.path.abspath(__file__))
# database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = database_file
# db = SQLAlchemy(app)


# @app.route('/')
# @app.route('/login')
# def hello():
#     return render_template('login.html')


# @app.route('/home')
# def homescreen():
#     return render_template('homescreen.html')


# @app.route('/live_video/<string:video_id>')
# def live_video(video_id):
#     print(video_id)
#     return render_template('live_video.html')


# @app.route('/exam_schedule', methods=['GET', 'POST'])
# def exam_schedule():
#     if request.method == 'POST':
#         studentDetails = request.form
#         name = studentDetails['name']
#         student_id = studentDetails['student_id']
#         contact = studentDetails['phone_no']
#         return 'success'
#     return render_template('temp.html')

# @app.route('/temp', methods=['GET', 'POST'])
# def temp():
#     if request.method == 'POST':
#         studentDetails = request.form
#         name = studentDetails['name']
#         student_id = studentDetails['student_id']
#         contact = studentDetails['phone_no']
#         return 'success'
#     return render_template('temp.html')


# @app.route('/index')
# def Index():
#     return render_template('AddDEl.html', student=data)


# @app.route("/exams",methods=["GET", "POST"])
# def exams():
#     if request.form:
#         book = Exam(exam_id=request.form.get("exam_id"),time_slot=request.form.get("time_slot"),
#         room_id=request.form.get("room_id"),course_id=request.form.get("course_id"))
#         db.session.add(book)
#         db.session.commit()
#     exams = Exam.query.all()


#     return render_template("Examination.html",exams=exams)    


# @app.route('/insert', methods=['POST'])
# def insert():

#     if request.method == "POST":
#         flash("Data ADDED Successfully")
#         name = request.form['name']
#         student_id = request.form['student_id']
#         phone_no = request.form['phone_no']
#         return redirect(url_for('Index'))


# @app.route('/delete/<string:id_data>', methods=['GET'])
# def delete(id_data):
#     return redirect(url_for('Index'))


# @app.route('/update', methods=['POST', 'GET'])
# def update():

#     if request.method == 'POST':
#         id_data = request.form['student_id']
#         name = request.form['name']
#         student_id = request.form['student_id']
#         phone_no = request.form['phone_no']
#         return redirect(url_for('Index'))


# if __name__ == '__main__':
#     app.run(debug=True)
