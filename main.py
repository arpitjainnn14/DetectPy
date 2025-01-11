import cv2
import time
import glob
from send_emails import send_email
import os
from threading import Thread

#enter the value 1 if the external webcam is connected
video=cv2.VideoCapture(0)
"""
this allows the delay in execution of the program which helps in avoiding black screen when the camera starts 
"""
time.sleep(1)

#cleans the image folder after sending the successful image via email
def clean_folder():
    print("Cleaning Process Started")
    images=glob.glob("images/*.png")
    for image in images:
        os.remove(image)
    print("Cleaning Process Ended!")


first_frame=None
status_list=[]
count=1
while True:
    status=0
    check,frame=video.read()
    
    #change the pixel color to gray
    gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    #add blur to the background(tuple contains the blur value)
    gray_frame_gau=cv2.GaussianBlur(gray_frame,(21,21),0)
    
    #avoid mirrored video
    mirrored_frame=cv2.flip(gray_frame_gau,1)

    #this checks if the first_frame is none, then it will add the first frame that will be captured by the webcam will be stored in the first_name.
    if first_frame is None:
        first_frame=mirrored_frame
     
    #this finds the difference between the first frame and the rest of the frames.
    delta_frame=cv2.absdiff(first_frame,mirrored_frame)
    
    thresh_frame=cv2.threshold(delta_frame,60,255,cv2.THRESH_BINARY)[1]
    dil_frame=cv2.dilate(thresh_frame,None,iterations=2)
    
    cv2.imshow("My video",dil_frame)
    
    contours,check=cv2.findContours(dil_frame,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour)<10000:
            continue
        x,y,w,h=cv2.boundingRect(contour)
        rectangle=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
        #if object is detected and rectangle is formed,then execute this:
        if rectangle.any():
            status=1
            
            cv2.imwrite(f"images/{count}.png",frame)
            count+=1
            allImages=glob.glob("images/*.png")  
            index=int(len(allImages)/2)
            image=allImages[index]   
        
    status_list.append(status)
    status_list=status_list[-2:]
    
    if status_list[0]==1 and status_list[1]==0:
        #creating thread to avoid freezing up of video
        email_thread=Thread(target=send_email,args=(image, ))
        email_thread.daemon=True
        email_thread.start()
    

    cv2.imshow("Video",frame)
    
    #this allows the termination of program when the key is pressed.
    key=cv2.waitKey(1)
    
    if key==ord("q"):
        break

clean_folder()
video.release()
""" 
What we want to achieve here is that, we want to check if there is any difference between the frames,
we want to compare the the first frame with the rest of the frames, as the first frame should be complete black to make this project work.
"""