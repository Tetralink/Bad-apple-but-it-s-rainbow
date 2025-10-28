import os, sys
import numpy as np
import cv2
import re
from PIL import Image
import time

print()
os.chdir(os.path.dirname(sys.argv[0])) #path
print("Current folder:", os.getcwd()) #verification
print()
print("Do you want to create frames from the video?")
demandeframe = input("(yes/no; yes by default): ")

if demandeframe == "no":  
    print("Make sure all frames are in a folder named \"frameIn\" at the root of the program")
else:
    print("Only supports mp4 (I think)")
    vidnom = input("Choose the video name (must be in the same directory as the program): ")
    if ".mp4" not in vidnom:
        vidnom = vidnom + ".mp4"
    cap = cv2.VideoCapture(vidnom)

    os.makedirs("frameIn", exist_ok=True)
    frames = []

    if cap.isOpened():
        current_frame = 0
        while True:
            ret, frame = cap.read()
            if ret:
                name = f'frameIn/frame{current_frame}.jpg'
                print(f"Creating file... {name}")
                cv2.imwrite(name, frame)
                frames.append(name)
                current_frame += 1
            else: break
        cap.release()
    cv2.destroyAllWindows()

folder = "frameIn"
files = sorted([f for f in os.listdir(folder) 
               if f.lower().endswith(".jpg")])
files = sorted(files, key=lambda n: int(re.search(r'\d+', n).group()))

print("Do you want to load an existing save of the images?")
charrep = input("(yes/no); no by default: ")

filecreated = 1
if charrep == "yes":
    if os.path.exists("allframe.npy"):
        allframe = np.load("allframe.npy", allow_pickle=True).item()
    else: print("Save not found (\"allframe.npy\")")
    filecreated = 0
else:
    allframe = {}

    for i, name in enumerate(files, 1):
        path = os.path.join(folder, name)
        frameconversion = Image.open(path).convert("L") #L for black and white

        arr = np.array(frameconversion) 
        #Convert to array
        threshold = 127
        #No need to explain
        TrueFalse = arr > threshold
        #Set True if above threshold
        pixels_flat = TrueFalse.astype(np.uint8).flatten() 
        #Convert True/False to 0/1 (uint8)
        #Then put in order, from what I understood
        allframe[name] = pixels_flat 
        #store it
        print(f"[{i}/{len(files)}] {name} processed ({pixels_flat.size} pixels)") 
        #show progress
        
    print("Do you want to save?")
    saverep = input("(yes/no); no by default: ")
    if saverep == "yes":
        np.save("allframe.npy", allframe) 

print("Creating animation...")

#EFFECT TIME!
COLOR_0 = [80, 40, 220]
COLOR_1 = [220, 180, 30]

speeds_0 = [2, 4, 6]
speeds_1 = [7, 3, 5]

directions_0 = [1, 1, 1]
directions_1 = [1, 1, 1]

#huuuu chatgpt, I admit
print("Creating MP4 video...")
first_frame = Image.open(os.path.join(folder, files[0])).convert("L")
frame_shape = np.array(first_frame).shape
first_frame.close()

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('animation.mp4', fourcc, 30.0, (frame_shape[1], frame_shape[0]), isColor=True)

i = 0

for name in files:
    if name in allframe:
        pixels_flat = allframe[name]
        
        # Replace values
        img_binary = pixels_flat.reshape(frame_shape)
        img_color = np.zeros((frame_shape[0], frame_shape[1], 3), dtype=np.uint8)

        if i % 3 == 0:
            #this part
            for j in range(3):
                COLOR_0[j] += speeds_0[j] * directions_0[j]
                if COLOR_0[j] >= 255:
                    COLOR_0[j] = 255
                    directions_0[j] = -1
                elif COLOR_0[j] <= 0:
                    COLOR_0[j] = 0
                    directions_0[j] = 1
            
            for j in range(3):
                COLOR_1[j] += speeds_1[j] * directions_1[j]
                if COLOR_1[j] >= 255:
                    COLOR_1[j] = 255
                    directions_1[j] = -1
                elif COLOR_1[j] <= 0:
                    COLOR_1[j] = 0
                    directions_1[j] = 1
        
        i += 1

        img_color[img_binary == 0] = [COLOR_0[2], COLOR_0[1], COLOR_0[0]]
        img_color[img_binary == 1] = [COLOR_1[2], COLOR_1[1], COLOR_1[0]]
        out.write(img_color)

out.release()
print("Video saved as 'animation.mp4'")

#Launch the video
capcap = cv2.VideoCapture("animation.mp4")
while(capcap.isOpened()):
    resu, fr = capcap.read()
    if resu == True:
        cv2.imshow('VIDEO', fr)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break
    else:
        break
capcap.release()
cv2.destroyAllWindows()