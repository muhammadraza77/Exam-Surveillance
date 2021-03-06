from __future__ import division

from flask import Flask, render_template, url_for, request, flash, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from model.Model import Course
from model.Model import Room
from model.Model import Student
from model.Model import Exam
from model.Model import DetectionAlert
from model.Model import FrameData

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
import time
from flask import send_from_directory
from datetime import datetime


MAX_DGRAM = 2**16
pp = 0

def dump_buffer(s):
    start = time.time()
    """ Emptying buffer frame """
    while True:
        if (time.time()-start == 15):
            s.close()
            return False
        seg, addr = s.recvfrom(MAX_DGRAM)
        print(seg[0])
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("finish emptying buffer")
            break
    return True

project_dir = os.path.dirname(os.path.abspath(__file__))
#project_dir = "C:\\Users\\User\\OneDrive\\Desktop\\Exam-Surveillance"
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
assets_folder = os.path.join(app.root_path, 'action_model//database//1')
print(assets_folder)
# app.add_url_rule('../action_model/<path:filename>', endpoint='attachments', build_only=True)
db = SQLAlchemy(app)


@app.route('/')
@app.route('/login')
def hello():
    return render_template('login.html')


@app.route('/home')
def homescreen():
    print("f") 
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
    global pp
    pp = roomdetails.output_port
    print("*1*************$$$$$$$$$$$$$$$$$$")
    print(pp)
    temp = []
    for Examitration in OtherExam:
        temp.append({"href": "/live_video/" +
                     str(Examitration.exam_id), "id": Examitration.exam_id})
    
    return render_template('live_video.html', Examdetails=Examdetails, coursedetails=coursedetails, roomdetails=roomdetails, OtherExam=OtherExam, Examitration=Examitration, temp=temp, id=id)


@app.route("/exams", methods=["GET", "POST"])
def exams():
    allCourses =(Course.query.all())
    allRooms = Room.query.all()

    if request.form:
        DTime = request.form.get("time_slot")
        
        objDate = datetime.strptime(DTime, '%Y-%m-%dT%H:%M')
        convertedDate=datetime.strftime(objDate,'%a %b %d %X %Y')

        book = Exam(duration=request.form.get("dur"), time_slot=convertedDate,
                    room_id=request.form.get("room_id"), course_id=request.form.get("course_id"),
                     facenetStatus=0)
        db.session.add(book)
        db.session.commit()
    exams = Exam.query.all()
    return render_template("Examination.html", exams=exams,allCourses=allCourses,allRooms =allRooms)

@app.route("/changestatus", methods=["GET", "POST"])
def change():
    detected = None
    exam_detected =None
    course_detected = None
    frame1 = []
    if request.method == "POST" :
        det_id = request.form.get("detection_id")
        exam_id = request.form.get("exam_id")
        print("detID"+ str(det_id))
        print("examID"+ str(exam_id))
        if exam_id!="":
            detected=DetectionAlert.query.filter_by(exam_id = exam_id,student_id='unknown').first()
            
        else:
            detected = DetectionAlert.query.filter_by(id = det_id).first()
        
        exam_detected = Exam.query.filter_by(exam_id=detected.exam_id).first()
        course_detected = Course.query.filter_by(course_id=exam_detected.course_id).first()
        frame1 =(FrameData.query.filter_by(DetectionID = detected.id).all())
        # print(detected.status)
    else:
        print("here")
        print(request.form)
    return render_template('changestatus.html',detected=detected,exam_detected=exam_detected,course_detected=course_detected,frame=frame1)

@app.route("/updateDatabase",methods=['POST'])
def updateDatabase():
    x = (request.form['value'])
    did = (request.form['did'])
    db.session.query(DetectionAlert).filter_by(id=did).update({DetectionAlert.status:x})
    # detect = DetectionAlert.query.filter_by(id=did).first()
    # detect.status = x

    db.session.commit()

    return jsonify({'value': x })

def get_frame():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', int(pp)))
    dat = b''
    flag=dump_buffer(s)

    while flag:
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

@app.route('/action_model/database/<string:name>/<path:filename>')
def Custom_Static(name,filename):
	assets_folder = os.path.join(app.root_path, 'action_model//database')
    assets_folder = assets_folder +'//'+name
    return send_from_directory(assets_folder, filename)

if __name__ == '__main__':
    # t = threading.Thread(target=capture_image)
    # t.daemon = True
    # t.start()
    app.run(host='0.0.0.0', debug=True, threaded=True )
