from __future__ import division

from flask import Flask, render_template, url_for, request, flash, redirect, jsonify
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


MAX_DGRAM = 2**16

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finish emptying buffer")
            break

project_dir = os.path.dirname(os.path.abspath(__file__))
#project_dir = "C:\\Users\\User\\OneDrive\\Desktop\\Exam-Surveillance"
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
    coursedetails = Course.query.filter_by(course_id=Examdetails.course_id).first()
    roomdetails = Room.query.filter_by(room_id=Examdetails.room_id).first()
    OtherExam = Exam.query.filter(Exam.exam_id != id).all()
    temp = []
    for Examitration in OtherExam:
        temp.append({"href": "/live_video/" +
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
    detected = None
    exam_detected =None
    course_detected = None

    if request.method == "POST" :
        det_id = request.form.get("detection_id")
        exam_id = request.form.get("exam_id")
        # print("detID"+ str(det_id))
        detected = DetectionAlert.query.filter_by(id = det_id).first()
        exam_detected = Exam.query.filter_by(exam_id=detected.exam_id).first()
        course_detected = Course.query.filter_by(course_id=exam_detected.course_id).first()
    else:
        print("here")
        print(request.form)
    return render_template('changestatus.html',detected=detected,exam_detected=exam_detected,course_detected=course_detected)

@app.route("/updateDatabase",methods=['POST'])
def updateDatabase():
    x = (request.form['value'])
    print(x)
    return jsonify({'value': x })

def get_frame():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', 12345))
    dat = b''
    dump_buffer(s)

    while True:
        print("hey")
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] > 1:
            dat += seg[1:]
        else:
            dat += seg[1:]
            img = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), 1)
            
            imgencode=cv2.imencode('.jpg',img)[1]
            stringData=imgencode.tostring()
            # cv2.imshow(img)
            # print(b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')
            yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    # cap.release()
    cv2.destroyAllWindows()

    del(camera)


@app.route('/video_feed')
def video_feed():
    return Response(get_frame(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    # t = threading.Thread(target=capture_image)
    # t.daemon = True
    # t.start()
    app.run(host='0.0.0.0', debug=True, threaded=True )
