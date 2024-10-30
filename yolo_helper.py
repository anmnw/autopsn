from yolo_detector import YoloDetector
import time
import cv2
import importlib
def load_cfg(module_name):
    module = importlib.import_module(module_name)
    return module.cfg

class ObjectDetector(YoloDetector):
    def __init__(self,path,**kwargs):

        #from config_triangle import cfg
        cfg = load_cfg(path)
        super().__init__(**kwargs,**cfg)
        self.bboxs = {} 
        self.w = 1
        self.h = 1
#    def __del__(self):
#    	if self.cap:
#             self.cap.release()   
    def test_once(self,path):
        import os
        img = cv2.imread(path)
        #img = cv2.resize(img , (2448,2048))# resize only for show image 
        #ret, img = self.cap.read()
        bboxs = self.exec(img)
        print(bboxs)
        save = self.drawbox(img,bboxs)
        #save = cv2.resize(600,500)
        cv2.imshow("GasketDetector", save)
        
        cv2.waitKey(0) 

    def test_video(self,path):
        cap = cv2.VideoCapture(path)
        ret, frame = cap.read()
        jump_frame = 25
        count = 0
        while(1):
            # get a frame
            count = count + 1
            ret, img = cap.read()
            if count % jump_frame > 0:
                continue
            img = cv2.resize(img , (512 , 512))
            # show a frame
                    #ret, img = self.cap.read()
            bboxs = self.exec(img)
            print(bboxs)
            save = self.drawbox(img,bboxs)

            cv2.imshow("show", img)
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break
        cap.release()
    def search(self,cls_name):
        bboxs = self.bboxs
        w,h = self.w,self.h
        if not bboxs:
            return None
        ret = []
        for bbox in bboxs:
            #cls = bbox["id"]
            cls = bbox["label"]
            if cls == cls_name:
                ret.append([bbox["cx"]/w,bbox["cy"]/h])
        return ret
    def detect_center(self,img,cls_name):
        bboxs = self.exec(img)
        self.bboxs = bboxs
        ret = []
        if not bboxs:
            return None
        h,w,c = img.shape
        self.w = w
        self.h = h
        for bbox in bboxs:
            #cls = bbox["id"]
            cls = bbox["label"]
            if cls == cls_name:
                ret.append([bbox["cx"]/w,bbox["cy"]/h])
        if len(ret)==0:
            return None
        return ret[0]


if __name__ == "__main__":
    detector = ObjectDetector(path="cfg.genshin_12") 
    detector.test_video("2024-10-05 21-29-28.mkv")
    #img = cv2.imread("./cfg/20241005_015656.jpg")
    #ret = detector.detect_center(img,"tree")
    #print(ret)
    # 树是08 钥匙是07 看着树还好，钥匙不行；可能要用瞄准的方法，靠近了也看不到。
#     while(1):
        
#         #detector.test()
#         l,timestamp = detector.get_gaskets()
#         print("============timestamp",timestamp,"============") 
#         #for points in l:
#         #    print("x:",points[0]," y:",points[1])
#         if len(l)>0:
#              print(l[0][0],"x:",l[0][1]," y:",l[0][2])#类型 x y
#         else:
#              print("not found")
#         #detector.test()
