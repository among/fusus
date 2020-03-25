import cv2
import numpy as np
# from PIL import Image
import pytesseract
# import os


## (1) read
nameOfImage = "1000"
# img = cv2.imread("{0}/{0}.jpg".format(nameOfImage))
img = cv2.imread("qay_Page_1.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# (2) wipe out unimportant bits
findOrDestroy = "find"

def Find_And_Destroy(element, accuracy, findOrDestroy):
    if findOrDestroy == "find":
        color = (255,0,255)
        border = 3
    else:
        color = (255, 255, 255)
        border = -1
    elem = cv2.imread("elements/{0}.jpg".format(element))
    grayElem= cv2.cvtColor(elem, cv2.COLOR_BGR2GRAY)
    H,W= elem.shape[:2]
    result = cv2.matchTemplate(gray, grayElem, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= accuracy)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img, pt, (pt[0] + W, pt[1] + H), color, border)
        cv2.rectangle(gray, pt, (pt[0] + W, pt[1] + H), color, border)

# Put the cleaning into action
Find_And_Destroy("shadda",0.8, findOrDestroy)
Find_And_Destroy("shadda2",0.8, findOrDestroy)
Find_And_Destroy("shadda3",0.8, findOrDestroy)
Find_And_Destroy("semicolon",0.8, findOrDestroy)
Find_And_Destroy("colon",0.8, findOrDestroy)
Find_And_Destroy("period",0.9, findOrDestroy)
Find_And_Destroy("comma",0.6, findOrDestroy)
Find_And_Destroy("tanwin",0.7, findOrDestroy)
Find_And_Destroy("tanwin2",0.7, findOrDestroy)
Find_And_Destroy("longA",0.8, findOrDestroy)
Find_And_Destroy("doubleOpen",0.7, findOrDestroy)
Find_And_Destroy("doubleClose",0.7, findOrDestroy)
Find_And_Destroy("salla",0.75, findOrDestroy)
Find_And_Destroy("alayh",0.65, findOrDestroy)



# cv2.imwrite("1.selected.jpg", img)
# exit()
#
#
# To check if it is  found correctly change to "find" and uncomment the following lines
small = cv2.resize(img, (0,0), fx=0.3, fy=0.3)
cv2.imshow("find.jpg", small)
cv2.waitKey(0)
cv2.destroyAllWindows()
exit()

#Making lines more distinguished
blurred = cv2.GaussianBlur(gray, (21,21), 60,0)

## (2) threshold
th, threshed = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)

## (3) minAreaRect on the nozeros
pts = cv2.findNonZero(threshed)
ret = cv2.minAreaRect(pts)

(cx,cy), (w,h), ang = ret
if w>h:
    w,h = h,w
    ang += 90

## (4) Find rotated matrix, do rotation
M = cv2.getRotationMatrix2D((cx,cy), ang, 1.0)
rotated = cv2.warpAffine(threshed, M, (img.shape[1], img.shape[0]))
normalRotated = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

# cv2.imwrite("2a.rotated.jpg", rotated)
# cv2.imwrite("2b.normalRotated.jpg", normalRotated)
# exit()


## (5) Histogram to detect text block
histY = cv2.reduce(rotated,1, cv2.REDUCE_AVG).reshape(-1)
histX = cv2.reduce(rotated,0, cv2.REDUCE_AVG).reshape(-1)
i = 0
for value in histY:

    color = (int(value), int(2*value), int(value))
    cv2.line(normalRotated, (0, i), (value, i), color, 1)
    i = i+1
i = 0
for value in histX:

    color = (int(value), int(2*value), int(value))
    cv2.line(normalRotated, (i, 0), (i, value), color, 1)
    i = i+1
# cv2.imwrite("3.Histogram.jpg", normalRotated)
# exit()


## (6) Chop off left-right margins
threshhold = 5
H,W = img.shape[:2]
for pixel in range (0,W):
    if histX[pixel] < threshhold:
        cv2.line(normalRotated, (pixel, 0), (pixel, H), (255,255,255), 1)
# cv2.imwrite("4a.ChoppedLR.jpg", normalRotated)
# exit()



## (7) Chop off upper and lower. find and draw the upper and lower boundary of each lines

uppers = [y for y in range(H-1) if histY[y]<=threshhold and histY[y+1]>threshhold]
lowers = [y for y in range(H-1) if histY[y]>threshhold and histY[y+1]<=threshhold]

cv2.rectangle(normalRotated, (0,0), (W, lowers[0]), (255,255,255), -1)

line = cv2.imread("elements/division.jpg")
for i in range(1,len(uppers)):
    roi = normalRotated[uppers[i]-5:lowers[i]+4, 10:W-10]
    result = cv2.matchTemplate(roi, line, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= 0.5)
    if loc[0].size:
        cv2.rectangle(normalRotated, (0,uppers[i]), (W, H), (255,255,255), -1)
        break
    else:
        continue

#cv2.imwrite("4b.ChoppedUL.jpg", normalRotated)
# exit()


# (8) Let us try and find the footnotes and dagger alif - and wipe them out of existence

def Wiping_Footnotes(template, accuracy):
    fn= cv2.imread("elements/"+template+".jpg")
    widthFN, heigthFN = fn.shape[:2]
    bandwidthUp = 6
    bandwidthDown = 30
    for i in range(1,len(uppers)):
        roi = normalRotated[uppers[i]-bandwidthUp:uppers[i]+bandwidthDown, 10:W-10]
        result = cv2.matchTemplate(roi, fn, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > accuracy:
            cv2.rectangle(normalRotated, (10+max_loc[0], uppers[i]-bandwidthUp+max_loc[1]), (10+max_loc[0] + heigthFN, uppers[i]-bandwidthUp+max_loc[1] + widthFN), (255,255,255), -1)


for i in range(1,9):
    Wiping_Footnotes("note"+str(i), 0.7)
Wiping_Footnotes("notew", 0.7)
Wiping_Footnotes("note4b", 0.7)
Wiping_Footnotes("u", 0.75)
Wiping_Footnotes("a", 0.9)

# cv2.imwrite("5.cleaned.jpg", normalRotated)


## (9) Give the cleaned version to Tesseract


text = "\r\n" + "<pb n='{0}'/> \r\n".format(nameOfImage) + pytesseract.image_to_string(normalRotated, lang="ara")

with open("6.finalText.txt","a") as result:
    result.write(text)