
from psn_controller import *
from pynput import mouse,keyboard
from  behavior_tree import *
import time
import os
import subprocess
from cfg_helper import *
import yolo_helper
import fgo_game_logic as fgo
import psn_game_logic as psn
from fgo_game_logic import FgoTurn,init_turns
# 当前配置：1 白纸化地球的qp本 不吃苹果 使用fgo_game_logic中的战斗逻辑 尼托即死队 2 星铁的智识材料 3 原刷4.0新副本 
if __name__ == "__main__":
    fgo.fgo_go_event = False #白纸化地球False 活动True 
    fgo.fgo_need_apple = 0
    fgo.eat_apple_num = 2 #012 金银蓝
    fgo.dungeon_num = 0 #从0开始 -1是最后一个 
    psn.starrail_dungeon_type_num = 2
    psn.starrail_dungeon_num = 1 # 圣遗物是4-3 智识材料2-9
    psn.genshin_dungeon_num = 29 # 4.0圣遗物本 
    delete_jpg_files()

    BackgroundControllerSingleton.datas["fgo_turns"] = init_turns()
    #BackgroundControllerSingleton.wait_start()
    node_stop = BehaviorNode(fgo.FgoLogic.stop_game,"stop fgo ")

    root_fgo,fgo_out = fgo.FgoLogic.ln_total_daily_block()
    fgo_out.add_node(node_stop)


    root_psn,_ = psn.BootPsn.ln_boot_psn_block()
    root_psn_genshin,_ = psn.BootPsn.ln_boot_psn_block()
    rail_in,rail_out = psn.StarRailLogic.ln_total_block()
    genshin_in,genshin_out = psn.GenshinLogic.ln_total_block()
    close_psn_node = BehaviorNode(psn.BootPsn.stop_chiaki)
    success_node = BehaviorNode(lambda:print("all done,good job!"),"final_block")

    root_psn.add_success(rail_in)
    rail_out.add_success(close_psn_node)
    
    root_psn_genshin.add_success(genshin_in)
    genshin_out.add_success(close_psn_node)
    close_psn_node.add_node(success_node)

    for i in range(10):
        if not fgo.FgoLogic.fgo_daily_total_success():
            run_root_node(root_fgo)

        if not psn.StarRailLogic.star_rail_daily_total_success():
            run_root_node(root_psn)
        #run_root_node(rail_in)
        if not psn.GenshinLogic.genshin_daily_total_success():
            run_root_node(root_psn_genshin)
        print(f"============turn stop{i}============")
        print("========================")
        print("========================")
        print("========================")
        print("========================")
    show_saved_img()
    #fgo.FgoLogic.dungeon_loop()
    pass