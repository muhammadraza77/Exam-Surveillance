from __future__ import division
import time
import os
import torch 
import torch.nn as nn
from torch.autograd import Variable
import numpy as np
import cv2 
from action_model.util import *
from action_model.darknet import Darknet
from action_model.preprocess import prep_image, inp_to_image, letterbox_image
import pandas as pd
import random 
import pickle as pkl
import argparse

import socket
import struct
import math


def get_test_input(input_dim, CUDA):
    img = cv2.imread("action_model//"+"dog-cycle-car.png")
    img = cv2.resize(img, (input_dim, input_dim)) 
    img_ =  img[:,:,::-1].transpose((2,0,1))
    img_ = img_[np.newaxis,:,:,:]/255.0
    img_ = torch.from_numpy(img_).float()
    img_ = Variable(img_)
    
    if CUDA:
        img_ = img_.cuda()
    
    return img_

def prep_image(img, inp_dim):
    """
    Prepare image for inputting to the neural network. 
    
    Returns a Variable 
    """

    orig_im = img
    dim = orig_im.shape[1], orig_im.shape[0]
    img = (letterbox_image(orig_im, (inp_dim, inp_dim)))
    img_ = img[:,:,::-1].transpose((2,0,1)).copy()
    img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)
    return img_, orig_im, dim

def write(x, img,classes,colors,frameNumber,examid,fs):
    c1 = tuple(x[1:3].int())
    c2 = tuple(x[3:5].int())
    cls = int(x[-1])
    # print(cls)
    # print(x)
    # print("########")
    if int(x[0])==0:
        label = "{0}".format(classes[cls])
        label = label + "==" + str(x[5])
    
        color = random.choice(colors)

        cv2.rectangle(img, c1, c2,color, 1)
        t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]

    # //******************crop culprits***********************************//
#    if int(x[0])==0:
        cropped=img[c1[1]:c2[1], c1[0]:c2[0], :]
        print('detected')
#        cropped=cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR)
        cv2.imwrite("action_model//"+"database//"+examid+"//frame_"+str(frameNumber)+".png",cropped)
    # cv2.imwrite("frame_"+str(frameNumber)+".png",cropped)    
    # //*******************************************************************//

        c2 = c1[0] + t_size[0] + 3, c1[1] + t_size[1] + 4
        cv2.rectangle(img, c1, c2,color, -1)
    
        cv2.putText(img, label, (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [225,255,255], 1);
    
    fs.udp_frame(img)
    return img

class Arguments():
    def __init__(self, examid,streamAddress):
        self.video = streamAddress
        self.examid = examid
        self.dataset = "pascal"
        self.confidence = 0.5
        self.nms_thresh= 0.4
        self.cfgfile = "cfg/yolov3.cfg"
        self.weightsfile = "yolov3_6000_3classes.weights"
        self.reso = "416"

class FrameSegment(object):
    """ 
    Object to break down image frame segment
    if the size of image exceed maximum datagram size 
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64 # extract 64 bytes in case UDP frame overflown
    def __init__(self, sock, port, addr="127.0.0.1"):
        self.s = sock
        self.port = port
        self.addr = addr

    def udp_frame(self, img):
        """ 
        Compress image and Break down
        into data segments 
        """
        compress_img = cv2.imencode('.jpg', img)[1]
        dat = compress_img.tostring()
        size = len(dat)
        count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
        array_pos_start = 0
        while count:
            array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
            self.s.sendto(struct.pack("B", count) +
                dat[array_pos_start:array_pos_end], 
                (self.addr, self.port)
                )
            array_pos_start = array_pos_end
            count -= 1
 
def startModel(paramerter):
    # args = arg_parse()
    args = Arguments(str(paramerter['exam_id']),paramerter['stream_address'])
    confidence = float(args.confidence)
    nms_thesh = float(args.nms_thresh)
    start = 0
    
    frameNumber = 0
    #//**********create folder for info related to specfici exam**********************//
    project_dir = os.path.dirname(os.path.abspath(__file__))
    print(project_dir)
    path = os.path.join(project_dir, 'database//'+args.examid) 
    try: 
        os.makedirs(path,exist_ok = True) 
        print("Directory  created successfully") 
    except OSError as error: 
        print("Directory can not be created") 

    # //******************************************************************************//    
    
    # *****************************udp socket creation*******************************
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = paramerter['port']

    fs = FrameSegment(s, port)

    # ************************************************************************************
    CUDA = torch.cuda.is_available()

    num_classes = 3

    CUDA = torch.cuda.is_available()
    
    bbox_attrs = 5 + num_classes
    
    print("Loading network.....")
    model = Darknet("action_model//"+args.cfgfile)
    model.load_weights("action_model//"+args.weightsfile)
    print("Network successfully loaded")

    model.net_info["height"] = args.reso
    inp_dim = int(model.net_info["height"])
    assert inp_dim % 32 == 0 
    assert inp_dim > 32
    
    if CUDA:
        model.cuda()
        
    model(get_test_input(inp_dim, CUDA), CUDA)

    model.eval()
    
    videofile = args.video
    
    cap = cv2.VideoCapture(videofile)
    # /////////////////
    sz = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
#    fourcc = cv2.CV_FOURCC('m', 'p', '4', 'v')

    
    vout = cv2.VideoWriter()
    vout.open(os.path.join("imgs", "res", "test11.avi"), fourcc, 20, sz, True)
    # ////////////////////


    assert cap.isOpened(), 'Cannot capture source'
    
    frames = 0
    start = time.time()    
    while cap.isOpened():
        print('\n\n********************************\n')
        frameNumber+=1
        ret, frame = cap.read()
        if ret:
            img, orig_im, dim = prep_image(frame, inp_dim)
            
            im_dim = torch.FloatTensor(dim).repeat(1,2)                        
            
            
            if CUDA:
                im_dim = im_dim.cuda()
                img = img.cuda()
            
            with torch.no_grad():   
                output = model(Variable(img), CUDA)
            output = write_results(output, confidence, num_classes, nms = True, nms_conf = nms_thesh)

            if type(output) == int:
                frames += 1
                print("FPS of the video is {:5.2f}".format( frames / (time.time() - start)))
                #cv2.imshow("frame", orig_im)
                vout.write(orig_im)
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    break
                continue
            
            

            
            im_dim = im_dim.repeat(output.size(0), 1)
            scaling_factor = torch.min(inp_dim/im_dim,1)[0].view(-1,1)
            
            output[:,[1,3]] -= (inp_dim - scaling_factor*im_dim[:,0].view(-1,1))/2
            output[:,[2,4]] -= (inp_dim - scaling_factor*im_dim[:,1].view(-1,1))/2
            
            output[:,1:5] /= scaling_factor
    
            for i in range(output.shape[0]):
                output[i, [1,3]] = torch.clamp(output[i, [1,3]], 0.0, im_dim[i,0])
                output[i, [2,4]] = torch.clamp(output[i, [2,4]], 0.0, im_dim[i,1])
            
            classes = load_classes("action_model//"+'data/coco.names')
            # print(classes)
            colors = pkl.load(open("action_model//"+"pallete", "rb"))
            
            list(map(lambda x: write(x, orig_im,classes,colors,frameNumber,args.examid,fs), output))
            
            
            #cv2.imshow("frame", orig_im)
            vout.write(orig_im)
            key = cv2.waitKey(1)
            if key & 0xFF == ord('q'):
                break
            frames += 1
            print("FPS of the video is {:5.2f}".format( frames / (time.time() - start)))

            
        else:
            break
    
    s.close()
    
    

# startModel(paramerter)
