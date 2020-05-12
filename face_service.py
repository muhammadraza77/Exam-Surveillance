import os
from model.Model import Exam
from model.Model import Student
from model.Model import DetectionAlert
from model.Model import db
# from facenet.detect import detect
def detect(s):
	return 'k16-3890'

	
project_dir = os.path.dirname(os.path.abspath(__file__))
project_dir=os.path.join(project_dir, "action_model\\database")
arr = os.listdir(project_dir)

for a in arr:
	exam=Exam.query.filter_by(exam_id=a).first()
	if exam.facenetStatus == 0 :
		ar=os.listdir(project_dir+'\\'+a)
		print(ar)
		for b in ar :
			result=detect(project_dir+'\\'+b)
			student=Student.query.filter_by(student_id=result).first()
			if student!=None:
				det = DetectionAlert(exam=exam,student=student,det_type=2,status="detected")
				db.session.add(det)
				db.session.commit()


		exam.facenetStatus = 1
		db.session.commit()









		