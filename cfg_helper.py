import importlib
import numpy as np
import pyautogui

import cv2

def load_datas(module_name):
    module = importlib.import_module(module_name)
    return module.point_data
def run_module_main(module_name):
    module = importlib.import_module(module_name)
    module.main()
def save_point_data(path,dic):
    with open(path, 'w') as file:
        file.write(f"origin_filename = '{path}'\n")
        file.write("point_data={\n")
        for k,v in dic.items():
            x,y,r,g,b = v
            print(k)
            file.write(f'"{k}":[{x},{y},{r},{g},{b}],\n')
            
        file.write("}")
    
def total_same(img,cfg):
    data = load_datas("cfg."+cfg)
    count = 0
    for k,v in data.items():
        x,y,r,g,b = v
        if(img[y][x][0] == r and img[y][x][1] == g and img[y][x][2] == b):
            count = count+1
    return True if count == len(data) else False
def save_img(path):
    img = get_new_img()
    img_rgb = img
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB) # 注意一下这里默认形式是rgb的 opencv需要bgr

    cv2.imwrite(path,img_bgr)
def search_jpg_files(directory):
    import os
    jpg_files = []
    for file in os.listdir(directory):  # 列出当前目录下的所有文件和文件夹
        if file.lower().endswith('.jpg'):  # 检查文件扩展名
            jpg_files.append(os.path.join(directory, file))  # 获取完整路径
    return jpg_files

def show_saved_img():
    image_paths = search_jpg_files("./")
    if len(image_paths)==0:
        return
    img = img = cv2.imread(image_paths[0])
    resize_height,resize_width,c = img.shape
    resize_height = int(resize_height/2)
    resize_width = int(resize_width/3)
    resized_images = []
    for path in image_paths:
        img = cv2.imread(path)
        if img is not None:
            resized_img = cv2.resize(img, (resize_width, resize_height))
            resized_images.append(resized_img)

    # 合并图片
    # 创建一个新画布，3列2行
    merged_image = np.zeros((resize_height * 2, resize_width * 3, 3), dtype=np.uint8)

    for index, img in enumerate(resized_images):
        x_offset = (index % 3) * resize_width
        y_offset = (index // 3) * resize_height
        merged_image[y_offset:y_offset + resize_height, x_offset:x_offset + resize_width] = img

    # 显示合并后的图像
    cv2.imshow('Merged Image', merged_image)
    cv2.waitKey(0)
def delete_jpg_files():
    directory = "./"
    import os
    for filename in os.listdir(directory):  # 列出当前目录下的所有文件
        if filename.lower().endswith('.jpg'):  # 检查文件扩展名
            file_path = os.path.join(directory, filename)  # 获取完整路径
            os.remove(file_path)  # 删除文件
            print(f"已删除: {file_path}")  # 打印删除的文件路径
def read_local_img(path):
    img_bgr = cv2.imread(path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_RGB2BGR)
    return img_rgb
    pass
def get_new_img(debug=True):
    if(debug == True):
        
        
        img = np.array(pyautogui.screenshot())
        img_rgb = img
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB) # 注意一下这里默认形式是rgb的 opencv需要bgr
        cv2.imwrite("tmp.jpg",img_bgr)# 只有保存的时候进行这个转换 默认处理都是用rgb通道逻辑
        
    return np.array(pyautogui.screenshot()) # x,y,w,h
def part_same(img,cfg,rate=0.8):
    count = 0
    data = load_datas("cfg."+cfg)
    for k,v in data.items():
        x,y,r,g,b = v
        if(img[y][x][0] == r and img[y][x][1] == g and img[y][x][2] == b):
            count = count+1
    return True if count >= (len(data)*rate) else False
def avg_same(img,cfg,diff=20):
    avg = 0.0
    data = load_datas("cfg."+cfg)
    for k,v in data.items():
        x,y,r,g,b = v
        rgb = np.array([r,g,b])
        rgbr = img[y][x][:]
        pix_diff = np.abs(rgb-rgbr).sum()
        avg = avg + pix_diff#.sum()
        #print(diff)

        #if(img[y][x][0] == r and img[y][x][1] == g and img[y][x][2] == b):
            #count = count+1

    return True if avg <= (len(data)*diff) else False # 这边直接返回 后面用 b is True捕获不到 不知道为啥 
if __name__ == "__main__":
    delete_jpg_files()
    save_img("2.jpg")
    show_saved_img()
    #data = load_datas("cfg.20241003_165239")
    #print(data)