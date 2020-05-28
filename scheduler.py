import schedule
import time
import threading

from model.Model import Course
from model.Model import Room
from model.Model import Student
from model.Model import Exam
from action_model.CheatingDetection import startModel

def startDetection(examDetails):
    room = Room.query.filter_by(room_id=examDetails.room_id).first()
    streamAddress=room.stream_address
    port=room.output_port
    obj_to_be_sent_to_model = {'stream_address':streamAddress,'exam_id':examDetails.exam_id,'port':int(port)}
    startModel(obj_to_be_sent_to_model)

def checktime(t):

	allExams=Exam.query.filter_by(time_slot='Wed Apr  8 03:24:00 2020').all()
	# allExams=Exam.query.filter_by(time_slot=time.ctime()).all()	
	if len(allExams)>0:
		for i in range(0,len(allExams)):
			threading.Thread(target=startDetection,kwargs={"examDetails": allExams[i]}).start()

# schedule.every().second.do(checktime,'It is 01:00')

# while True:
#     schedule.run_pending()
#     time.sleep(1)


checktime(55)
