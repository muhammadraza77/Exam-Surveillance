import cv2
import io
import socket
import struct
import time
import pickle
import zlib

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(), 8485))
# give ip here
connection = client_socket.makefile('wb')

#ip camera
cap = cv2.VideoCapture(cap = cv2.VideoCapture('http://192.168.1.2:5001/video'))
img_counter = 0

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

while(True):
    ret, frame = cap.read()

    result, frame = cv2.imencode('.jpg', frame, encode_param)
    data = pickle.dumps(frame, 0)
    size = len(data)


    print("{}: {}".format(img_counter, size))
    client_socket.sendall(struct.pack(">L", size) + data)
    img_counter += 1

cam.release()
    