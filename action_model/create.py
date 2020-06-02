import numpy as np
import cv2

cap = cv2.VideoCapture('v3short.mp4')
cap2 = cv2.VideoCapture('v43.mp4')
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
width = 1370
height = 480
video=cv2.VideoWriter('video.mp4', fourcc, 20,(width,height))

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    ret2, frame2 = cap2.read()

    # Our operations on the frame come here
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Display the resulting fram
#     if not ret :
#         cap = cv2.VideoCapture('v3short.mp4')
#         ret, frame = cap.read()
    if ret and ret2:
        frame2=frame2[:,100:700]
        frame=frame[:,50:820]
        vis = np.concatenate((frame, frame2), axis=1)
#         cv2.imshow('frame',vis)
        video.write(vis)
    else:
        break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
video.release()
cv2.destroyAllWindows()

