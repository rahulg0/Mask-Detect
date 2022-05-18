from django.shortcuts import render

from django.http import HttpResponse
# from django.views.decorators import gzip
from django.http import StreamingHttpResponse
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import os
import threading


# Create your views here.

# def home(request):
#     return render (request , 'homepage.html')
    

def home(request):

    if request.method== 'POST':

        def detect_and_predict_mask(frame, faceNet, maskNet):
        # grab the dimensions of the frame and then construct a blob
        # from it
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(frame, 1.0, (224, 224),
                (104.0, 177.0, 123.0))

            # pass the blob through the network and obtain the face detections
            faceNet.setInput(blob)
            detections = faceNet.forward()
            print(detections.shape)

            # initialize our list of faces, their corresponding locations,
            # and the list of predictions from our face mask network
            faces = []
            locs = []
            preds = []

            for i in range(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated with
            # the detection
                confidence = detections[0, 0, i, 2]

                # filter out weak detections by ensuring the confidence is
                # greater than the minimum confidence
                if confidence > 0.5:
                    # compute the (x, y)-coordinates of the bounding box for
                    # the object
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    (startX, startY) = (max(0, startX), max(0, startY))
                    (endX, endY) = (min(w - 1, endX), min(h - 1, endY))

                    # extract the face ROI, convert it from BGR to RGB channel
                    # ordering, resize it to 224x224, and preprocess it
                    face = frame[startY:endY, startX:endX]
                    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                    face = cv2.resize(face, (224, 224))
                    face = img_to_array(face)
                    face = preprocess_input(face)

                    # add the face and bounding boxes to their respective
                    # lists
                    faces.append(face)
                    locs.append((startX, startY, endX, endY))
            
            if len(faces) > 0:

                faces = np.array(faces, dtype="float32")
                preds = maskNet.predict(faces, batch_size=32)
            return (locs, preds)
        
        prototxtPath = r"W:\CODING(prac)\Django\mask-detect\face_detector\_deploy.prototxt"
        weightsPath = r"W:\CODING(prac)\Django\mask-detect\face_detector\_res10_300x300_ssd_iter_140000.caffemodel"
        faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

        maskNet = load_model(r"W:\CODING(prac)\Django\mask-detect\mask_detector.model")
        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()
        t1=10 

        while True:
            # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
            frame = vs.read()
            frame = imutils.resize(frame, width=400)

            # detect faces in the frame and determine if they are wearing a
            # face mask or not
            (locs, preds) = detect_and_predict_mask(frame, faceNet, maskNet)

            # loop over the detected face locations and their corresponding
            # locations
            for (box, pred) in zip(locs, preds):
                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred

                label = "Mask" if mask > withoutMask else "No Mask"
                color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                if label != "Mask":
                    t1-=1
                else:
                    t1=120
                
                label = "{}: {: .2f}%".format(label , max(mask , withoutMask) * 100)

                if t1<1:
                    cv2.putText(frame , "Please Wear Your Mask" , (startX-70 , startY -10), cv2.FONT_HERSHEY_COMPLEX , 0.60 , color ,2)
                    cv2.rectangle(frame , (startX , startY) , (endX ,endY), color ,2 )

                else:
                    cv2.putText(frame , label , (startX , startY - 10),cv2.FONT_HERSHEY_SIMPLEX , 0.45 , color , 2)

                    cv2.rectangle (frame ,(startX , startY) , (endX ,endY), color , 2) 

               
            cv2.imshow("Frame" , frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("x"):
                break

            

        # if request.method == 'POST':

        #     while True:

        #         key = cv2.waitKey(1) & 0xFF
        #         if key == ord("x"):
        #             break

        cv2.destroyAllWindows()
        vs.stop()

    return render(request , 'homepage.html')

def about(request):
    return render(request , 'about.html')
    

# # @gzip.gzip_page

# def Home(request):
#     try:
#         cam = VideoCamera()
#         return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
#     except:
#         pass
#     return render(request, 'app1.html')

# #to capture video class
# class VideoCamera(object):
#     def __init__(self):
#         self.video = cv2.VideoCapture(0)
#         (self.grabbed, self.frame) = self.video.read()
#         threading.Thread(target=self.update, args=()).start()

#     def __del__(self):
#         self.video.release()

#     def get_frame(self):
#         image = self.frame
#         _, jpeg = cv2.imencode('.jpg', image)
#         return jpeg.tobytes()

#     def update(self):
#         while True:
#             (self.grabbed, self.frame) = self.video.read()

# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')