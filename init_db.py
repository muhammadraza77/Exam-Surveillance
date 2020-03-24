from model.Model import db
from model.Model import Course
from model.Model import Room
from model.Model import Student
from model.Model import Exam
from model.Model import DetectionAlert


db.drop_all()
db.create_all()
# ******************************************************************************************
course = Course(course_id = 0,course_name = 'Computer Vision',cr_hours = 3) 
db.session.add(course)

course = Course(course_id = 1,course_name = 'Programming Fundamentals',cr_hours = 3) 
db.session.add(course)

course = Course(course_id = 2,course_name = 'Computer Networking',cr_hours = 3) 
db.session.add(course)
# ******************************************************************************************
room = Room(room_id = 1,room_code = 'R-11',capacity = 50,stream_address = 'http://192.168.1.2:5001/video')
db.session.add(room)

room = Room(room_id = 2,room_code = 'R-12',capacity = 45,stream_address = 'http://192.168.1.2:5001/video')
db.session.add(room)

room = Room(room_id = 3,room_code = 'S-1',capacity = 65,stream_address = 'http://192.168.1.2:5001/video')
db.session.add(room)
# ******************************************************************************************
student = Student(student_id='k16-3890',name='Muhammad Raza',ph_number='03452445249')
db.session.add(student)

student1 = Student(student_id='k16-3886',name='Mustafa Irfan',ph_number='03256899947')
db.session.add(student1)

student2 = Student(student_id='k16-3863',name='Mujtaba Bawani',ph_number='0325587555')
db.session.add(student2)
# ******************************************************************************************
exam1 = Exam(exam_id = 1,time_slot = '10-11',room_id = 1,course_id = 2,duration = 1)
db.session.add(exam1)

exam = Exam(exam_id = 2,time_slot = '12-1',room_id = 2,course_id = 1,duration = 1)
db.session.add(exam)

exam = Exam(exam_id = 3,time_slot = '1-2',room_id = 3,course_id = 0,duration = 1)
db.session.add(exam)
# ******************************************************************************************
det = DetectionAlert(exam=exam,student=student,det_type=1,status="detected")
db.session.add(det)

det = DetectionAlert(exam=exam,student=student1,det_type=3,status="detected")
db.session.add(det)

det = DetectionAlert(exam=exam1,student=student1,det_type=2,status="detected")
db.session.add(det)
# ******************************************************************************************

db.session.commit()
