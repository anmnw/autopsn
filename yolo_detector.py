from detect_triangle_fix import DetectorOnnxApi
#from config_triangle import cfg
#import torch
import numpy as np
import cv2
import os
import tqdm

class mTimer():
    #log = True
    log = False
    #打印代码块的执行时间
    def __init__(self,name, t=0.0):
        self.t = t
        self.start = 0
        self.end = 0
        self.name = name
    def __enter__(self):
        self.start = self.time()
        return self
    def __exit__(self,type, value, traceback):
        self.dt = self.time() - self.start  # delta-time
        self.t += self.dt  # accumulate dt
        if mTimer.log:
            print("{} use {:.4f}ms".format(self.name,self.dt*1000))
    def time(self):
        import time
        return time.perf_counter()

class YoloDetector(DetectorOnnxApi):
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
    def exec(self, raw_img):
        """
        @type raw_img: np.array
        @type save_result: bool
        @type out_name:  str
        @type draw_img: np.array
        以字典的形式输出各个类别的相应数值
        """
        
        with mTimer("__pre process"):
            img = self._pre_process(raw_img)
        with mTimer("__onnx run"):
            pred = np.array(self.session.run([self.output_name], {self.input_name: img}))
            print(pred.shape)
        with mTimer("__post process nms"):
            pred = self.non_max_suppression(pred, self.conf_thres, self.iou_thres, None, True, max_det=20)#先定20个框 
            
            print("number after nms",len(pred[0]))
            # Process predictions
            dets = []
            for i, det in enumerate(pred):  # per image
                if len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = self.scale_coords(img.shape[2:], det[:, :4], raw_img.shape).round()
                    dets.append(det)
            print(dets)
            if len(dets) == 0:
                return None
            dict_value = {}
            bbox = []
            for i in range(len(dets[0])):
                cx = int((dets[0][i, 0] + dets[0][i, 2]) / 2)
                cy = int((dets[0][i, 1] + dets[0][i, 3]) / 2)
                cls_id = int(dets[0][i, -1])
                w = int(dets[0][i, 2] - dets[0][i, 0])
                h = int(dets[0][i, 3] - dets[0][i, 1])
                print(dets[0][i,4])
                print(self.label_map[cls_id])
                print(self.cls_id_to_res[cls_id])
                bbox.append({"label":self.label_map[cls_id], 'cls': self.cls_id_to_res[cls_id],"id":cls_id, 'cx': cx, 'cy': cy, 'w': w, 'h': h,"conf": dets[0][i,4]})
            
        return bbox
    def drawbox(self,img_data,bboxs):
        """
        图片路径函数：
        输入-图片对应的numpy数组，[类别：{label:"label name",cls:0,cx:0,cy:0,h:0,w:0},............,{label,cls,cx...}]
        输出-添加目标框、类别和向量箭头的图片numpy数组
        """
        if not bboxs:
            return img_data
        for i,bbox in enumerate(bboxs):
            print("--------",bbox)
            x1 = bbox['cx'] - 0.5 * bbox['w']
            y1 = bbox['cy'] - 0.5 * bbox['h']
            x2 = bbox['cx'] + 0.5 * bbox['w']
            y2 = bbox['cy'] + 0.5 * bbox['h']
            box = [x1,y1,x2,y2]
            text_name = bbox["label"]
            _color = self.label_color[int( self.label_map.index(text_name)%3)]
            draw_size = min(img_data.shape[0:2])/500
            img_data = cv2.rectangle(img_data, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])),
                                color=_color, thickness=int(draw_size*2))
            
            cv2.putText(img_data, ("{} {:.2f}".format(text_name,bbox["conf"]*100)),
                        (int(x1), int(y1 - draw_size)), cv2.FONT_HERSHEY_PLAIN, draw_size,
                        _color, thickness=int(draw_size), lineType=cv2.LINE_AA)

        return img_data
 
        

def detect(img,detector):
    
    bboxs = detector.exec(img)#[{label,cls,cx,cy,h,w},{}]] 
    save = detector.drawbox(img,bboxs)
    return bboxs,save

def main(**args):
    print(args)
    detector = YoloDetector(**args)
    for p in tqdm.tqdm(os.listdir(args["test_img_dir"])):
        with mTimer("one detect"):
            if p.endswith(".jpg") or p.endswith(".png"):
                
                with mTimer("_img read"):
                    img = cv2.imread(os.path.join(args['test_img_dir'],p))
                
                with mTimer("_detect"):
                    result,save = detect(img,detector=detector)
                #print(result)
                with mTimer("_img write"):
                    cv2.imwrite(os.path.join(args['output_dir'],p),save)
    #cv2.imshow("a",save)
    #cv2.waitKey(0)
def camera_main1(**args):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2448)  # 设置图像宽度 ##注意下这里需要匹配相机一帧数据尺寸，相机端可能没有做opencv的适配
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2048)  # 设置图像高度
    cap.set(cv2.CAP_PROP_FPS , 20)   # 设置帧率
    ret, frame = cap.read()
    detector = YoloDetector(**args)
    while(1):
        # get a frame
        ret, img = cap.read()
        img = cv2.resize(img , (612 , 512))
        # show a frame
        result,labelimg = detect(img,detector=detector)
        cv2.imshow("show", labelimg)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows() 
    pass


if __name__ == "__main__":
    #camera_main(**cfg)
    main(**cfg)
