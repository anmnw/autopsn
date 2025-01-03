
from psn_controller import *
from pynput import mouse,keyboard
from  behavior_tree import *
import time
import os
import subprocess
from cfg_helper import *
import yolo_helper
import fgo_game_logic as fgo
from fgo_game_logic import FgoTurn
# fgo主要两种场景 1 日常白纸化三把 2 活动吃体力固定位置 3 无限池大刷特刷 
# 这个脚本适用于某个活动中 手动点到活动页面开始大刷特刷
def init_turns():
    turns = []
    turn = FgoTurn(clean=True)#0
    # 公主不重名 奥 爱 狐 t1 0 78 m123 加10np t2 34 t3 236
    turn.use_skill(0,target=1)
    turn.use_skill(7,target=1)
    turn.use_skill(8,target=1)
    turn.use_master_skill(1,target=1)
    turn.use_hougu(1)
    turns.append(turn)

    turn = FgoTurn(clean=True)#1
    turn.use_skill(3,target=1)
    turn.use_skill(4,target=1)
    turn.use_master_skill(0,target=1)
    turn.use_hougu(1)
    turns.append(turn)

    
    turn = FgoTurn(clean=True)#2
    turn.use_skill(2,target=1)
    turn.use_skill(3,target=1)
    turn.use_skill(6,target=1)
    turn.use_hougu(1)
    turns.append(turn)


    return 
    
    
if __name__ == "__main__":
    fgo.fgo_go_event = False #白纸化地球False 活动True 
    fgo.fgo_need_apple = 0
    fgo.eat_apple_num = 2 #012 金银蓝
    fgo.dungeon_num = 10 #从0开始 -1是最后一个 

    BackgroundControllerSingleton.datas["fgo_turns"] = init_turns()
    BackgroundControllerSingleton.wait_start()
    
    fgo.FgoLogic.dungeon_loop()
    pass