from face_recognizer import detectName


names = detectName("data/test/test.jpg")


for name in names:
    print(name)