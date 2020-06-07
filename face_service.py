import os
from model.Model import Exam
from model.Model import Student
from model.Model import DetectionAlert
from model.Model import db
from model.Model import FrameData
from Facenet.face_recognizer import detectName as detect
from emailscript import sendMail
from sqlalchemy.sql import exists    

	
project_dir = os.path.dirname(os.path.abspath(__file__))
project_dir=os.path.join(project_dir, "action_model/database")
allExams = os.listdir(project_dir)

for individualExam in allExams:
	exam=Exam.query.filter_by(exam_id=individualExam).first()
	
	if exam.facenetStatus == 0 :
		

		ar=os.listdir(project_dir+'/'+individualExam)
		print(ar)
		for b in ar :
			print("*************"+project_dir+'/'+ individualExam +'/'+b+"*****************")
			
			
			result=detect(project_dir+'/'+ individualExam +'/'+b)
			for name in result:
				print(name)
				
				
				student = Student.query.filter_by(student_id=name).first()
				if student!=None:
					exists = DetectionAlert.query.filter_by(student_id=name,exam=exam).first()

					if(exists is not None):
						print("Already Exists")
						frame = FrameData(frameID = b,DetectionID=exists.id)
						db.session.add(frame)
						db.session.commit()
					
					else:
						print("DB updated")
						# frame_ID=(b.split('_')[1].split('.')[0])
						det = DetectionAlert(exam=exam,student=student,det_type=2,status="detected")
						db.session.add(det)
						db.session.commit()
						print(b)

						frame = FrameData(frameID = b ,DetectionID = det.id)
						db.session.add(frame)
						db.session.commit()

						if name == "unknown":
							c=exam.course.course_name
							sendMail("k163890@nu.edu.pk",examid=individualExam,examcode=c)
						else:
							c=exam.course.course_name
							sendMail(name+"@nu.edu.pk",detid=det.id,examcode=c)

					



		exam.facenetStatus = 1
		db.session.commit()









		
