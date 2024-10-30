# 11 12 13 好像是另外三个图标 先不要；
cfg = {
    'model_path': "./cfg/genshin_12.onnx", # 模型路径
    #'model_path': "./model/yolov5n_sim.onnx", # 模型路径
    #'model_path': r"C:\Users\Zha Zha\Desktop\dq_deploy\dq_detect\model\dq_best.onnx", # 模型路径
    #'img_size': [2048,2464], # 图片尺寸 ##原图2048x2448 2448不能被32整除 padding一格
    'img_size': [512,512], # 图片尺寸 ##原图2048x2448 2448不能被32整除 padding一格
    'conf_thres':0.65,#非极大值抑制的参数 
    'iou_thres':0.5,#同上
    #"label_map":["0","1","2","3","04","05","06","07","08","09","10","0","0","0","0","0","0","0","0","0","0","0","0"],
    "label_map" : [
        "map_center",
        "dungeon_icon",
        "island_with_dungenon",
        "gate_mark",
        "paimon_icon",
        "squre_icon",
        "?",
        "center_red_key",
        "tree",
        "dungeon_final",
    ],
    "cls_id_to_res":[0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2,0,1,2],
    #'test_img_dir':"../datasets/dq/images",#测试文件路径
    'test_img_dir':"./model",#测试文件路径
    'output_dir':"./output",#输出文件路径
}
