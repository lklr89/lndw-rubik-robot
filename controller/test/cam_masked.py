import cv2
import numpy as np
cam = cv2.VideoCapture(4)
#frame = cv2.imread('rubiks-side-F.png')
cv2.namedWindow("img")
cv2.namedWindow("mask")
img_counter = 0
mask_top = 100
mask_bottom = 110
mask_right = 180
mask_left = 180
ret,frame = cam.read()
#ret = True
height,width,depth=frame.shape
print height,width
mask = np.full((height,width),255,np.uint8)
while True:
    ret, frame = cam.read()
    cv2.imshow("img", frame)
    height,width,depth=frame.shape
    mask[0:mask_top,:] = 0
    mask[180:195,:] = 0
    mask[270:285,:] = 0
    mask[:,265:280] = 0
    mask[:,370:385] = 0
    mask[-mask_bottom:height,:] = 0
    mask[:,0:mask_right] = 0
    mask[:,-mask_left:width] = 0
    img_masked = cv2.bitwise_and(frame,frame,mask=mask)
    m = cv2.getRotationMatrix2D((width/2,height/2),180,1)
    img_masked = cv2.warpAffine(frame,m,(width,height))
    cv2.imshow("mask",img_masked)
    # print mask
    # print mask[:,0]
    # print len(mask[:,0])
    # break
    if not ret:
        break
    k = (cv2.waitKey(1))%256

    if k == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k == 32:
        # SPACE pressed
        img_name = "opencv_frame_{}.png".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
        break
    elif k == ord('A'): #A - decrease RIGHT
        break
    elif k == ord('D'):
        break
    elif k == ord('W'):
        break
    elif k == ord('S'):
        break
    elif k == ord('a'): #A - increase RIGHT
        break
    elif k == ord('d'):
        break
    elif k == ord('w'):
        break
    elif k == ord('s'):
        break

cam.release()

cv2.destroyAllWindows()
