from asyncio.log import logger
import time
import io
import os
import cv2
import numpy as np
import math
#from torchvision.ops import box_iou
from tqdm import tqdm
import logging
import onnxruntime
#import torch
#import torchvision
#import config_triangle
import random
import datetime


# from algo.base import AlgoBase


class DetectorOnnxApi(object):

    def __init__(self, **kwargs):
        # self.device = kwargs.get('device') or None
        self.model_path = kwargs.get('model_path') or None
        self.img_size = kwargs.get('img_size') or 640
        # self.img_short_size = kwargs.get('img_short_size') or 640
        self.conf_thres = kwargs.get('conf_thres') or 0.05
        self.iou_thres = kwargs.get('iou_thres') or 0.5
        self.color_fill = [[4, 250, 7]]
        self.stride = 64

        # load model
        assert self.model_path.endswith('onnx'), "Not onnx model!"
        
        self.session = onnxruntime.InferenceSession(self.model_path, None)
        self.output_name = self.session.get_outputs()[0].name
        self.input_name = self.session.get_inputs()[0].name

        self.label_map = kwargs.get('label_map') or ['zytr','ng','wg']
        self.label_color = kwargs.get('label_color') or [(0, 0, 255),(0,0,255),(0,0,255)]
        self.cls_id_to_res = kwargs.get('cls_id_to_res') or dict({0 : 0, 1 : 1, 2: 2})

    @staticmethod
    def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
        # Resize and pad image while meeting stride-multiple constraints
        shape = im.shape[:2]  # current shape [height, width]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)

        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:  # only scale down, do not scale up (for better val mAP)
            r = min(r, 1.0)

        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        if auto:  # minimum rectangle
            dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
        elif scaleFill:  # stretch
            dw, dh = 0.0, 0.0
            new_unpad = (new_shape[1], new_shape[0])
            ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

        dw /= 2  # divide padding into 2 sides
        dh /= 2

        if shape[::-1] != new_unpad:  # resize
            im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
        return im, ratio, (dw, dh)

    def _pre_process(self, raw_img):
        img = self.letterbox(raw_img, self.img_size, stride=self.stride, auto=False)[0]
        img = img.astype('float32')
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        img = img.transpose(2, 0, 1)
        img = img[np.newaxis, ...]
        return img




    def non_max_suppression(self,prediction, conf_thres=0.25, iou_thres=0.45, classes=None, agnostic=False, multi_label=False, labels=(), max_det=300):
        """
        Runs Non-Maximum Suppression (NMS) on inference results using numpy.

        Returns:
            list of detections, on (n,6) array per image [xyxy, conf, cls]
        """
        nc = prediction.shape[2] - 5  # number of classes
        xc = prediction[..., 4] > conf_thres  # candidates
        assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
        assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'

        min_wh, max_wh = 2, 4096  # (pixels) minimum and maximum box width and height
        max_nms = 30000  # maximum number of boxes for NMS
        time_limit = 10.0  # seconds to quit after
        redundant = True  # require redundant detections
        multi_label &= nc > 1  # multiple labels per box
        merge = False  # use merge-NMS

        t = time.time()
        output = [np.zeros((0, 6)) for _ in range(prediction.shape[0])]
        
        for xi, x in enumerate(prediction):  # image index, image inference
            # Apply constraints
            x = x[xc[xi]]  # confidence filtering

            # Append labels to predictions if autolabelling
            if labels and len(labels[xi]):
                l = labels[xi]
                v = np.zeros((len(l), nc + 5))
                v[:, :4] = l[:, 1:5]  # box
                v[:, 4] = 1.0  # conf
                v[np.arange(len(l)), l[:, 0].astype(int) + 5] = 1.0  # cls
                x = np.concatenate((x, v), axis=0)

            # If none remain process next image
            if not x.shape[0]:
                continue

            # Compute conf
            x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf

            # Box (center x, center y, width, height) to (x1, y1, x2, y2)
            box = xywh2xyxy_numpy(x[:, :4])

            # Detections matrix nx6 (xyxy, conf, cls)
            if multi_label:
                i, j = np.nonzero(x[:, 5:] > conf_thres)
                x = np.concatenate((box[i], x[i, j + 5, None], j[:, None].astype(np.float32)), axis=1)
            else:  # best class only
                conf = x[:, 5:].max(1, keepdims=True)
                j = x[:, 5:].argmax(1)
                x = np.concatenate((box, conf, j[:, None].astype(np.float32)), axis=1)[conf.flatten() > conf_thres]

            # Filter by class
            if classes is not None:
                x = x[np.isin(x[:, 5], classes)]

            # Check shape
            n = x.shape[0]  # number of boxes
            if not n:  # no boxes
                continue
            elif n > max_nms:  # excess boxes
                x = x[x[:, 4].argsort()[::-1][:max_nms]]  # sort by confidence

            # Batched NMS
            c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
            boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
            i = nms_numpy(boxes, scores, iou_thres)  # NMS

            if i.shape[0] > max_det:  # limit detections
                i = i[:max_det]
            if merge and (1 < n < 3E3):  # Merge NMS (boxes merged using weighted mean)
                iou = box_iou_numpy(boxes[i], boxes) > iou_thres  # iou matrix
                weights = iou * scores[None]  # box weights
                x[i, :4] = np.dot(weights, x[:, :4]) / weights.sum(1, keepdims=True)  # merged boxes
                if redundant:
                    i = i[iou.sum(1) > 1]  # require redundancy

            output[xi] = x[i]
            if (time.time() - t) > time_limit:
                print(f'WARNING: NMS time limit {time_limit}s exceeded')
                break  # time limit exceeded

        return output
 
    @staticmethod
    def clip_coords(boxes, shape):
        # Clip bounding xyxy bounding boxes to image shape (height, width)
        #if isinstance(boxes, torch.Tensor):  # faster individually
        #    boxes[:, 0].clamp_(0, shape[1])  # x1
        #    boxes[:, 1].clamp_(0, shape[0])  # y1
        #    boxes[:, 2].clamp_(0, shape[1])  # x2
        #    boxes[:, 3].clamp_(0, shape[0])  # y2
        #else:  # np.array (faster grouped)
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2

    def scale_coords(self, img1_shape, coords, img0_shape, ratio_pad=None):
        # Rescale coords (xyxy) from img1_shape to img0_shape
        if ratio_pad is None:  # calculate from img0_shape
            gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
            pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
        else:
            gain = ratio_pad[0][0]
            pad = ratio_pad[1]

        coords[:, [0, 2]] -= pad[0]  # x padding
        coords[:, [1, 3]] -= pad[1]  # y padding
        coords[:, :4] /= gain
        self.clip_coords(coords, img0_shape)
        return coords

    def _show_objs(self, det, draw_img, show_names):
        if len(det) == 0:
            return draw_img
        det = det[0]
        show_det = np.zeros((1, 6))
        for name in show_names:
            show_index = self.label_map.index(name)
            filed_index = (det[:, -1] == show_index)
            m_det = det[filed_index]
            show_det = np.concatenate((show_det, m_det), axis=0)
        show_det = np.delete(show_det,0, axis = 0)
        for idx in range(show_det.shape[0]):
            box = show_det[idx, 0:4]
            text_name = self.label_map[int(show_det[idx, -1])]
            _color = self.label_color[int(show_det[idx, -1])]
            img = cv2.rectangle(draw_img, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])),
                                color=_color, thickness=10)
            cv2.putText(img, str(text_name),
                        (int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2) - 5), cv2.FONT_HERSHEY_SIMPLEX, 4,
                        _color, thickness=3, lineType=cv2.LINE_AA)

        return draw_img

    def exec(self, raw_img):
        """
        @type raw_img: np.array
        @type save_result: bool
        @type out_name:  str
        @type draw_img: np.array
        以字典的形式输出各个类别的相应数值
        """
        img = self._pre_process(raw_img)
        pred = np.array(self.session.run([self.output_name], {self.input_name: img}))
        pred = self.non_max_suppression(pred, self.conf_thres, self.iou_thres, None, True, max_det=2)
        # Process predictions
        dets = []
        for i, det in enumerate(pred):  # per image
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = self.scale_coords(img.shape[2:], det[:, :4], raw_img.shape).round()
                dets.append(det.numpy())

        # if draw_img is not None:
        #     draw_img = self._show_objs(dets, draw_img, self.label_map)
        # else:
        #     draw_img = self._show_objs(dets, raw_img, self.label_map)

        # if save_result:
        #     cv2.imwrite(out_name, draw_img)

        if len(dets) == 0:
            return dict({'res': None})
        dict_value = {}
        for i in range(len(dets[0])):
            cx = int((dets[0][i, 0] + dets[0][i, 2]) / 2)
            cy = int((dets[0][i, 1] + dets[0][i, 3]) / 2)
            cls_id = int(dets[0][i, -1])
            w = dets[0][i, 2] - dets[0][i, 0]
            h = dets[0][i, 3] - dets[0][i, 1]
            dict_value[self.label_map[cls_id]] = {'cls': self.cls_id_to_res[cls_id], 'cx': cx, 'cy': cy, 'w': w, 'h': h}
        return dict_value

# generator by gpt

def xywh2xyxy_numpy(x):
    """Convert nx4 boxes from [x_center, y_center, w, h] to [x1, y1, x2, y2] format using numpy"""
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top-left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top-left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom-right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom-right y
    return y

def nms_numpy(boxes, scores, iou_thres):
    """Pure numpy NMS implementation."""
    x1, y1, x2, y2 = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= iou_thres)[0]
        order = order[inds + 1]

    return np.array(keep, dtype=np.int32)

def box_iou_numpy(box1, box2):
    """Compute IoU between boxes using numpy."""
    def box_area(box):
        return (box[:, 2] - box[:, 0]) * (box[:, 3] - box[:, 1])

    area1 = box_area(box1)
    area2 = box_area(box2)

    inter = (np.minimum(box1[:, None, 2], box2[:, 2]) - np.maximum(box1[:, None, 0], box2[:, 0])).clip(0) * \
            (np.minimum(box1[:, None, 3], box2[:, 3]) - np.maximum(box1[:, None, 1], box2[:, 1])).clip(0)

    return inter / (area1[:, None] + area2 - inter)


class Triangle(object):
    def __init__(self, **kwargs):
        self.infer_handle = DetectorOnnxApi(**kwargs)
        self.debug = kwargs.get('debug') or True
        self.status = 0
        self.count = 0
        self.label_map = kwargs.get('label_map') or ['zytr','ng','wg']
        self.label_color = kwargs.get('label_color') or [(0, 0, 255),(0,0,255),(0,0,255)]
        self.angle = kwargs.get('angle')
        self.debug = kwargs.get('debug')
        self.test_img_dir = kwargs.get('test_img_dir')
        self.out_dir = kwargs.get('out_dir')
    
    def log_print(self):
        """
        日志文件初始化函数
        """
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        log_path = self.out_dir
        log_name = os.path.join(log_path,rq) + '.txt'
        logfile = log_name
        fh = logging.FileHandler(logfile, mode='w') 
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        logger.addHandler(fh)


    def imgs_path(self):
        """
        图片路径函数：
        输出-（包含测试图片路径的列表，保存路径）
        """
        if not os.path.exists(self.out_dir):
            os.mkdir(self.out_dir)
        test_img_list = [os.path.join(self.test_img_dir, ele) for ele in os.listdir(self.test_img_dir) if ele.endswith('.jpg')]
        return (test_img_list,self.out_dir)

    def show_object(self,img_data,out_det,dict_value):
        """
        图片路径函数：
        输入-图片对应的numpy数组，{类别：{cls:0,cx:0,cy:0,h:0,w:0,h:0}............}，{类别：[cx,cy]........}
        输出-添加目标框、类别和向量箭头的图片numpy数组
        """
        det_list = list(out_det.keys())
        for i in range(len(out_det)):
            x1 = out_det[det_list[i]]['cx'] - 0.5 * out_det[det_list[i]]['w']
            y1 = out_det[det_list[i]]['cy'] - 0.5 * out_det[det_list[i]]['h']
            x2 = out_det[det_list[i]]['cx'] + 0.5 * out_det[det_list[i]]['w']
            y2 = out_det[det_list[i]]['cy'] + 0.5 * out_det[det_list[i]]['h']
            box = [x1,y1,x2,y2]
            text_name = det_list[i]
            _color = self.label_color[int( self.label_map.index(det_list[i]))]
            img_data = cv2.rectangle(img_data, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])),
                                color=_color, thickness=10)
            cv2.putText(img_data, str(text_name),
                        (int((box[0] + box[2]) / 2), int((box[1] + box[3]) / 2) - 5), cv2.FONT_HERSHEY_SIMPLEX, 4,
                        _color, thickness=3, lineType=cv2.LINE_AA)

        dict_name = list(dict_value.keys())
        p1 = np.array(dict_value[dict_name[1]])
        p2 = np.array(dict_value[dict_name[0]])  
        cv2.arrowedLine(img_data, p2, p1, (255, 0, 255), thickness=10, line_type=cv2.LINE_4, shift=0, tipLength=0.3)
        return img_data

    def object_cat(self,img,date_time,information):
        """
        图片的拼接函数：
        输入-information指代information_extraction()函数输出的结果
        输出-日志信息：不同时刻图片的配对情况，目前已经配对成功的图片对数
            -根据self.debug的值来确定要不要保存图片之间的配对情况图
        """
        name1 = os.path.split(self.history[1])[1].split('.')[0]
        name2 = os.path.split(information[1])[1].split('.')[0]
        status_name={1:'_are_matched',-1:'_category_mismatch',-2:'_point_mismatch'}
        logger.info('{'+name1+'_and_'+name2+status_name[self.status]+'}'+'   {} pairs of matched hubs'.format(self.count))
        if self.debug == True:
            cv2.putText(img, str(date_time),
                (int(img.shape[1]/2),int(img.shape[0]/2)), cv2.FONT_HERSHEY_SIMPLEX, 6,
                (0,255,0), thickness=8, lineType=cv2.LINE_AA)
            cv2.imwrite(os.path.join(os.path.split(information[1])[0],name1+'_and_'+name2+status_name[self.status]+'.jpg'),img)
        else:
            return 0

    def vector_calculation(self,dict_value):
        """
        向量计算函数:
        输入-{类别名：[cx,cy]........}
        输出-(类别名,numpy向量)
        """
        dict_name = list(dict_value.keys())
        p1 = np.array(dict_value[dict_name[1]])
        p2 = np.array(dict_value[dict_name[0]])
        vector = p1-p2
        return (dict_name[0],vector)

    def dot_product_angle(self,v1, v2):
        """
        角度计算函数:
        输入-两个numpy向量
        输出-角度值
        """
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            print("Zero magnitude vector!")
        else:
            vector_dot_product = np.dot(v1, v2)
            arccos = np.arccos(vector_dot_product / (np.linalg.norm(v1) * np.linalg.norm(v2)))
            angle = np.degrees(arccos)
            return angle
        return 0   


    def information_extraction(self, img_data, out_name):
        """
        信息提取函数:
        输入-图片numpy数组、保存路径
        输出-向量、保存路径、经过处理后的图片numpy数组
        """
        out_det = self.infer_handle.exec(img_data)#{类别：{cls:0,cx:0,cy:0,h:0,w:0,h:0}............}
        if out_det is not None:
            dict_value = {}
            out_det = dict(sorted(out_det.items(), key=lambda x: x[0]))# 按键值为字典排序,旨在确定最重点和轮毂中心的先后顺序，统一向量的指向。
            key_list = list(out_det.keys())
            for i in range(len(key_list)):
                cx1 = out_det[key_list[i]]['cx']
                cy1 = out_det[key_list[i]]['cy']
                dict_value[key_list[i]]=[cx1, cy1] # dict_value = {类别：[cx,cy].........}
            vector = self.vector_calculation(dict_value) # 计算向量
            img = self.show_object(img_data,out_det,dict_value) # 对图片的向量
            
            return [vector,out_name,img]

    def picture_matching(self,information):
        """
        图片匹配:输入-[(类别名,numpy向量)...............]、测试路径
                输出-status=0 目前存储的只有一张图片的信息,只有一个工件
                            1 图片匹配，两个轮毂符合要求可以配对
                           -1 类别不匹配，两个相同的轮毂，不配对
                           -2 最重点不匹配，两个不同的轮毂，最重点位置小于30度，不配对
        """
        if not hasattr(self,'history'): # 判断类中是否存有history这个类，若没有则将t时刻的图片信息赋值为history
            self.history = information
            self.status = 0
        else:
            if self.history[0][0]!=information[0][0]: # 判断t-1时刻（上一时刻）和t时刻（当前时刻）的类别是否匹配
                angle = self.dot_product_angle( self.history[0][1],information[0][1])
                if angle>=self.angle: # 判断t-1时刻（上一时刻）和t时刻（当前时刻）的最重点是否匹配
                    self.status = 1
                    self.count +=1
                    img1 = self.history[2]
                    img2 = information[2]
                    img = np.hstack((img1,img2))
                    datetime_object = datetime.datetime.now()
                    self.object_cat(img,datetime_object,information)
                    del self.history # 配对成功后删除history，将t+1时刻的信息赋值给history而后与t+2时刻的图片信息进行配对
                else:
                    self.status = -2
                    img1 = self.history[2]
                    img2 = information[2]
                    img = np.hstack((img1,img2))
                    datetime_object = datetime.datetime.now()
                    self.object_cat(img,datetime_object,information)
                    self.history = information # 配对不成功后，将t时刻的信息赋值为history，而后与t+1时刻的图片信息进行配对
            else:
                self.status = -1
                img1 = self.history[2]
                img2 = information[2]
                img = np.hstack((img1,img2))
                datetime_object = datetime.datetime.now()
                self.object_cat(img,datetime_object,information)
                self.history = information
        return self.status


if __name__ == '__main__':
    # my_detector =  Triangle(**config_triangle.triangle_status) # 类的实例化，具体传入内容见配置文件config_triangle.py
    # test_img_list,out_dir = my_detector.imgs_path() # 测试图片文件夹以及保存路径的获取

    # # random.shuffle(test_img_list) # 打乱顺序便于测试

    # my_detector.log_print() # 日志文件的初始化
    # for img_path in tqdm(test_img_list):
    #     img_data = cv2.imread(img_path) # img_data为numpy数组
    #     img_name = os.path.split(img_path)[1]
    #     out_name = os.path.join(out_dir, img_name) # out_dir为保存的路径
    #     information = my_detector.information_extraction(img_data, out_name) # 图片信息的提取
    #     result = my_detector.picture_matching(information) # 图片匹配，返回状态值，并生成中间结果

        # print('status:',result)
    
    pass







