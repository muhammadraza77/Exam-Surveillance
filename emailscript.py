import smtplib, ssl




def sendMail(receiver,examid="",examcode="",detid=""):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "k163863@nu.edu.pk"  # Enter your address
    receiver_email = receiver  # Enter receiver address
    password = "mustafa123"
    message = """\
        Subject: Exam-Survillance Auto Generated Email

        Warning! This to inform you that you have been detected as cheating suspect in  current exam """+str(examcode)+"""review your case to exam coordinatior  using detection id  """+str(detid)+""" ."""
    if examid != "":
        message = """\
        Subject: Exam-Survillance Auto Generated Email Admin

        Warning! This to inform you that find unknown faces of  current exam """+str(examcode)+""" using exam id  """+str(examid)+""" ."""
          
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

