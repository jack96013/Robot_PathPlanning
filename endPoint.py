import cv2


class EndPoint():
    def __init__(self):
        self.location = None
        pass


    def setLocation(self, cv_objects):
        
        contours_sorts = sorted(cv_objects, key=cv2.contourArea, reverse=True)
        
        if (len(contours_sorts) < 1):
            return None
        
        self.location = cv2.minAreaRect(contours_sorts[0])[0]

    def getLocation(self):
        return self.location


