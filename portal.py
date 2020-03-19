from flask import Flask, render_template, url_for, request, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from model.Model import Course
from model.Model import Room
from model.Model import Student
from model.Model import Exam
from model.Model import DetectionAlert

from flask import Response
import threading
import socket

from sqlalchemy import text

import cv2
import sys
import pickle
import numpy as np
import struct ## new
import zlib




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

@app.route("/changestatus", methods=["GET", "POST"])
def change():
    return render_template("changestatus.html")

def get_frame():
    PORT=8485

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('Socket created')
    s.bind((socket.gethostname(),PORT))
    print('Socket bind complete')
    s.listen(10)
    print('Socket now listening')

    conn,addr=s.accept()

    data = b""
    payload_size = struct.calcsize(">L")
    print("payload_size: {}".format(payload_size))

    while True:
        while len(data) < payload_size:
            print("Recv: {}".format(len(data)))
            data += conn.recv(4096)

        print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
        print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            data += conn.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        frame=pickle.loads(frame_data, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        imgencode=cv2.imencode('.jpg',frame)[1]
        stringData=imgencode.tostring()
        # print(b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
        yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

    del(camera)

@app.route('/video_feed')
def video_feed():
    return Response(get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # t = threading.Thread(target=capture_image)
    # t.daemon = True
    # t.start()
    app.run(host='localhost', debug=True, threaded=True )
