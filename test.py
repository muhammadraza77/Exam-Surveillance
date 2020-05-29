import os
from model.Model import DetectionAlert
from model.Model import Exam

from model.Model import db
# from sqlalchemy.sql import exists



def testfunc(name):
    exists= DetectionAlert.query.filter_by(student_id=name,exam_id=3).first()
    if (exists is not None):
        print("Already Exists")
    else:
        # sendMail(name+"@nu.edu.pk")
        print("hello")
    



testfunc("k163890")