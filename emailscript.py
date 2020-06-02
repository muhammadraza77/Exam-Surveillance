import smtplib, ssl




def sendMail(receiver):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "k163863@nu.edu.pk"  # Enter your address
    receiver_email = receiver  # Enter receiver address
    password = "mustafa123"
    message = """\
    Subject: Exam-Survillance Auto Generated Email

    Warning! This to inform you that Have been detected cheating in the Exam Kindly meet the Exam Coordinator within there days or Else Strict DC action would be taken and you would be BLACKLISTED ."""
    
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

