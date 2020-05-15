from scipy.spatial.distance import cosine
import numpy as np
import cv2
import mtcnn
from keras.models import load_model
from Facenet.utils import get_face, plt_show, get_encode, load_pickle, l2_normalizer

encoder_model = 'Facenet/facenet_keras.h5'
people_dir = 'Facenet/data/StudentsData'
encodings_path = 'Facenet/data/StudentsEncodings/encodings.pkl'


recognition_t = 0.3
required_size = (160, 160)
encoding_dict = load_pickle(encodings_path)
face_detector = mtcnn.MTCNN()
face_encoder = load_model(encoder_model)

def detectName(test_img_path , test_res_path="data/results/test.jpg"):
	names =[]
	img = cv2.imread(test_img_path)
		# plt_show(img)
	img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	results = face_detector.detect_faces(img_rgb)
	for res in results:
		face, pt_1, pt_2 = get_face(img_rgb, res['box'])
		encode = get_encode(face_encoder, face, required_size)
		encode = l2_normalizer.transform(np.expand_dims(encode, axis=0))[0]

		name = 'unknown'
		distance = float("inf")

		for db_name, db_encode in encoding_dict.items():
			dist = cosine(db_encode, encode)
			if dist < recognition_t and dist < distance:
				name = db_name
				distance = dist

		if name == 'unknown':
			cv2.rectangle(img, pt_1, pt_2, (0, 0, 255), 2)
			cv2.putText(img, name, pt_1, cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
		else:
			cv2.rectangle(img, pt_1, pt_2, (0, 255, 0), 2)
			cv2.putText(img, name + f'__{distance:.2f}', pt_1, cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
		names.append(name)
				
	cv2.imwrite(test_res_path, img)
	return names 
	