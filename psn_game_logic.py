from psn_controller import *
from pynput import mouse,keyboard
from  behavior_tree import *
import time
import os
import subprocess
from cfg_helper import *
import yolo_helper

genshin_dungeon_num = 29
starrail_dungeon_type_num = 2 # 这个默认是0 0是内圈  1是经验本 2是各个职业的素材 3技能材料 4圣遗物
starrail_dungeon_num = 1 # 注意这两个数字从0开始数 你按了几下摇杆就是几

class BootPsn:
    def start_chiaki(self):
        #os.system("./bat/run_chiaki.bat")
        mouse_ctrl = BackgroundControllerSingleton.mouse_ctrl
        key_ctrl = BackgroundControllerSingleton.key_ctrl
        #mouse_ctrl.click
        # 打开chiaki
        exit_code = subprocess.call([".\\bat\\run_chiaki.bat"], shell=True)# boot chiaki
        time.sleep(1)
        # 发送ps5启动信号
        mouse_ctrl.position = (124,176)
        mouse_ctrl.click(mouse.Button.right, 1)
        time.sleep(0.2)
        mouse_ctrl.position = (141,211)
        mouse_ctrl.click(mouse.Button.left, 1)
        
        time.sleep(1)
        
        key_ctrl.press(keyboard.Key.enter)# 发完有个发送成功的弹窗要点掉
        time.sleep(0.1)
        key_ctrl.release(keyboard.Key.enter)
        time.sleep(0.1)

        mouse_ctrl.position = (124,176)
        mouse_ctrl.click(mouse.Button.right, 1)
        time.sleep(0.2)
        mouse_ctrl.position = (141,211)
        mouse_ctrl.click(mouse.Button.left, 1)
        
        time.sleep(1)
        
        key_ctrl.press(keyboard.Key.enter)
        time.sleep(0.1)
        key_ctrl.release(keyboard.Key.enter)
        time.sleep(0.1)

        
        time.sleep(10)
        # 打开psn
        mouse_ctrl.position = (124,176)
        mouse_ctrl.click(mouse.Button.left, 2)
        
        time.sleep(3)
        
        exit_code = subprocess.call([".\\bat\\run_chiaki_sub.bat"], shell=True)# boot chiaki
        time.sleep(1)
        return True
        pass
    def check_psn_boot_success(self):
        b = True
        count = 0
        while b:# 等到图片不是完全黑的 
            img = get_new_img()
            b = total_same(img,"00_chiaki_all_black")
            time.sleep(1)
            count = count + 1
            if count > 20:
                return False
        
        return True
        pass
    def stop_chiaki():
        exit_code = subprocess.call([".\\bat\\kill_chiaki.bat"], shell=True)# boot chiaki
        return BehaviorNode.success
    def boot_psn():
        boot = BootPsn()
        boot.start_chiaki()
        b = boot.check_psn_boot_success()
        print("psn boot finish ",b)
        if b == False:
            print("notify: if you loop here,you need to check your ps5 is power on and login")
        return b
    def close_game():
        
        psc = PsnController()
        BootPsn.go_home()
        time.sleep(1)
        psc.press("option")
        time.sleep(0.1)
        psc.release("option")
        
        time.sleep(0.5)
        for i in range(5):
            psc.press("circle")
            time.sleep(0.1)
            psc.release("circle")
            time.sleep(1)

        time.sleep(2)
    def go_home():
        # home ->up -> down -> x -> left 3sec -> check ->once again
        
        psc = PsnController()
        psc.press("home")
        time.sleep(0.1)
        psc.release("home")
        time.sleep(1)
        psc.press("l_up")
        time.sleep(0.1)
        psc.release("l_up")
        time.sleep(0.5)
        
        psc.press("l_down")
        time.sleep(0.1)
        psc.release("l_down")
        time.sleep(0.5)
        
        psc.press("l_left")
        time.sleep(2)
        psc.release("l_left")

        psc.press("cross")
        time.sleep(0.1)
        psc.release("cross")
        time.sleep(0.1)
        
        
        pass
    def check_home():
        img = get_new_img()
        b = avg_same(img,"00_go_psn_home")
        print("check home",b)
        return b
    def go_home_plus_check():
        BootPsn.go_home()
        
        psc = PsnController()
        psc.press("l_left")
        time.sleep(3)
        psc.release("l_left")
        
        b = BootPsn.check_home()
        #print(b)
        if b:
            return b
        
        BootPsn.go_home()
        b = BootPsn.check_home()
        return b
    def ln_boot_psn_block():
        # start_chiaki ->check_psn_boot_success
        # success: next
        # failed: stop_chiaki boot again
        # 现在的问题是回调不好加 脱裤子放屁     
        node = BehaviorNode(callback=BootPsn.boot_psn,name="boot_psn")
        #node.callback = BootPsn.boot_psn
        
        failed_node = BehaviorNode(callback=BootPsn.stop_chiaki,name="faild_stop_chiaki")
        #failed_node.callback = 
        link_node = LinkNode(node) 
        link_node.add_failed(failed_node)
        failed_node.add_node(link_node)
        return link_node,link_node
        pass
    pass 

class GenshinLogic():
# 写在最前
# 1 需要用芙+钟的队伍 不然打不过 (钟在左的位置)
# 2 包裹里必须有一个以上40树脂，并且不能有紫色的树脂
# 3 目前缺一个断点检测和重开的内容 先不管 能跑拉
    total_success_img_path = "genshin_daily.jpg"
    def __init__(self):
        pass
    def genshin_daily_total_success():
        if not os.path.exists(GenshinLogic.total_success_img_path):
            return False
        img = read_local_img(GenshinLogic.total_success_img_path)

        return avg_same(img,"01_genshin_all_done")
        return True
    pass
    def start_game():
        ctrl = GenshinController()
        count = 0
        for i in range(30):
            time.sleep(1)
            ctrl.click_once("select")
        while True:
            count = count + 1
            for i in range(10):
                time.sleep(1)
                ctrl.click_once("select")
            ctrl.click_once("option")
            time.sleep(1.5)
            if GenshinLogic.check_main_ui():
                return True
            if count > 5:
                return False
            for i in range(5):
                time.sleep(0.2)
                ctrl.click_once("cancel")
        return True
        pass
    def check_dungeon_timeout():
        timeout = 300
        ts = BackgroundControllerSingleton.datas["start_battle"]
        return True if time.time()-ts<timeout else False
    def start_battle(): 
        GenshinLogic.single_battle_loop0()
        ts = time.time()
        BackgroundControllerSingleton.datas["start_battle"] = ts
        ctrl = GenshinController()
        ctrl.press_once("move_up")
        for i in range(20):
            ctrl.click_once("select_object")
            time.sleep(0.2)
            if time.time()-ts > 4.7:
                break
        ctrl.release_once("move_up")

        pass
    def start_battle_second():
        GenshinLogic.single_battle_loop0()
        ts = time.time()
        BackgroundControllerSingleton.datas["start_battle"] = ts
        ctrl = GenshinController()
        ctrl.press_once("move_up")
        for i in range(20):
            ctrl.click_once("select_object")
            time.sleep(0.2)
            if time.time()-ts > 1.7:
                break
        ctrl.release_once("move_up")
        
        pass
    def check_main_ui():
        img = get_new_img()
        return avg_same(img,"01_main_ui")
        
        #return True
    def battle_loop():
        # 上下左右 水草岩雷
        # 行动逻辑 
        
        pass
    
    def single_battle_loop0():
        #battle prepare
        ctrl = GenshinController()

        ctrl.click_once("move_down")
        time.sleep(0.5)
        ctrl.click_once("left");
        time.sleep(0.3)
        ctrl.click_once("left");
        time.sleep(0.3)
        ctrl.press_once("skill1");
        time.sleep(1.1)
        ctrl.release_once("skill1")
        time.sleep(0.2)


    def single_battle_loop1():
        ctrl = GenshinController()
        ctrl.click_once("left");
        time.sleep(0.3)
        ctrl.click_once("select_object")
        ctrl.click_once("left");
        time.sleep(0.3)
        ctrl.press_once("skill1");
        time.sleep(0.3)
        ctrl.click_once("skill2");
        time.sleep(0.8)
        ctrl.release_once("skill1")
        time.sleep(0.1)
        time.sleep(0.1)
        #time.sleep(2)
        #ctrl.press_once("skill1");
        #time.sleep(1)
        #ctrl.release_once("skill1")
        #time.sleep(1)
    def single_battle_loop2():
        GenshinLogic.single_battle_loop1()
        ctrl = GenshinController()
        ctrl.click_once("up");
        time.sleep(0.3)
        ctrl.click_once("up");
        ctrl.click_once("skill1");
        time.sleep(0.3)
        ctrl.click_once("skill1");
        ctrl.click_once("select");
        time.sleep(0.3)
        ctrl.click_once("skill1");
        # 8sec
    
    def single_battle_loop4():
        
        GenshinLogic.single_battle_loop1()
        ctrl = GenshinController() 
        ctrl.click_once("right");
        time.sleep(0.3)
        ctrl.click_once("right");
        ctrl.click_once("skill1");
        time.sleep(0.3)
        ctrl.click_once("skill1");
        time.sleep(0.7)
        # 8sec


    def single_battle_loop3():
        
        GenshinLogic.single_battle_loop1()
        ctrl = GenshinController()
        ctrl.click_once("down");
        time.sleep(0.3)
        
        ctrl.click_once("down");
        ctrl.click_once("skill1");
        time.sleep(0.3)
        ctrl.click_once("skill1");
        time.sleep(0.3)
        ctrl.click_once("skill1");
        time.sleep(0.3) 
        
        #time.sleep(3)
    def single_battle_loop():
        GenshinLogic.single_battle_loop1()
        GenshinLogic.single_battle_loop2()
        GenshinLogic.single_battle_loop1()
        GenshinLogic.single_battle_loop3()
        
        
        
        pass
    def get_mission(self):
        pass
    def battle(self):
        pass
    def battle_finish(self):

        pass 
    def check_dungeon_reward(img = None):
        if img == None:
            
            img = get_new_img()
        b = avg_same(img,"01_dungen_touch_tree")
        if b: 
            return b
        
        b = avg_same(img,"01_dungeon_reward1")#没有体力的情况
        return b
        pass
    def check_dungeon_reward_ap_not_enought(img = None):
        if img == None:
            img = get_new_img()
        b = avg_same(img,"01_dungeon_reward2")
        return b
        pass

    def go_dungeon():
        b_go_dungeon_menu = False
        GenshinLogic.go_option()
        ctrl = GenshinController()
        l0 = [[(0,0),(0,3)]]
        if genshin_dungeon_num >=0:
                l = [
                     [(0,0),(0,2)],
                     [(0,0),(2,0)],
                     [(0,0),(0,genshin_dungeon_num)]
                ]
        else:
                l = [
                     [(0,0),(0,2)],
                     [(0,0),(2,0)],
                     [(0,0),(0,50)],
                     [(0,0),(0,genshin_dungeon_num+1)]# -2 +1 = -1,up one block
                ]

        if b_go_dungeon_menu:
            PsnController.go_block(l0[0])
        
            ctrl.click_once("select")
            time.sleep(0.5)
        else:
            psc = PsnController()
            for i in range(5):
                psc.click("circle")
                time.sleep(0.4)
            psc.press("l_1")
            time.sleep(1)
            psc.press("r_stick_right")
            psc.press("r_stick_up")
            time.sleep(1)
            
            psc.release("r_stick_right")
            psc.release("r_stick_up")
            time.sleep(0.1)
            psc.release("l_1")
            time.sleep(2)

            pass
        ctrl.press_once("move_up")
        time.sleep(2)
        ctrl.release_once("move_up")# 走到列表最上面 
        for ll in l:
            PsnController.go_block(ll)
        
        #PsnController.go_block(l[2])
        #PsnController.go_block(l[3])
        for i in range(5):
            ctrl.click_once("select")
            time.sleep(0.5)
        
        time.sleep(10)
        ctrl.press_once("move_up")
        time.sleep(2.5)
        ctrl.release_once("move_up")
        time.sleep(0.5)
        ctrl.click_once("select_object")
        
        # 20241025 这一段防止网络问题没进去，进到多人模式
        time.sleep(0.5)
        ctrl.click_once("select_object")
        
        time.sleep(0.5)
        ctrl.press_once("move_down")
        time.sleep(2)
        ctrl.release_once("move_down")
        #for i in range(5):
        #    ctrl.click_once("select_object")
        #    time.sleep(0.2)
        time.sleep(4)
        ctrl.click_once("select")# 选人
        
        time.sleep(2)
        ctrl.click_once("select_object")# 开始
        time.sleep(0.5)
        ctrl.click_once("select_object")# 开始
        
        time.sleep(0.5)
        
        ctrl.click_once("cancel")# 点一下取消，以防万一进了匹配，也能退出来
        time.sleep(10)
        
        ctrl.click_once("select")# 地脉异常
        time.sleep(0.5)
        pass
    def boot_genshin():
        psc = PsnController()
        print("boot genshin")
        for i in range(10):
            psc.press("l_right")
            time.sleep(0.1)
            psc.release("l_right")
            time.sleep(1)
            b = False
            for j in range(3):
                b = GenshinLogic.check_genshin_icon()
                if b:
                    break
                time.sleep(0.3)
            if b:
                return True
        return False
    def check_in_dungeon_option_ui():
        img = get_new_img()
        b = avg_same(img,"01_dungeon_exit_option")
        return b
        pass
    def check_genshin_icon():
        img = get_new_img()
        b = avg_same(img,"01_genshin_icon")
        return b
        pass
    def check_in_dungeon():
        
        ctrl = GenshinController()
        b = GenshinLogic.check_in_dungeon_option_ui()
        if  b: # need normal mode
            return False
        
        ctrl.click_once("option")
        time.sleep(1)
        
        b = GenshinLogic.check_in_dungeon_option_ui()
        if(b == False):
            time.sleep(0.5)
            
            b = GenshinLogic.check_in_dungeon_option_ui() # try again
        ctrl.click_once("cancel")
        return b


    def find_tree():
        print("======find tree=======")
        ts = time.time()
        timeout = 300
        ctrl = GenshinController()
        detector = yolo_helper.ObjectDetector(path="cfg.genshin_12")
        find_once = False
        last_move_right = True
        b = False
        for i in range(500):
            img = get_new_img()
            center = detector.detect_center(img,"tree")
            # 三种情况 找不到，找到 找错；假定不会找错 
            if center == None:# 找不到 
                if not find_once: # 没有找到过 
                    ctrl.press_once("camera_right")
                    time.sleep(0.5)
                    ctrl.release_once("camera_right")
                else: # 找到过 用上一回的反方向操作 
                    cmd = "camera_right" if last_move_right else "camera_left"
                    ctrl.click_once(cmd)
                pass
                continue
            # 找到了 只判断左右 左向左打方向 在中间10%跳出
            find_once = True
            x = center[0]
            if 0.475<x and x < 0.525:
                b = True
                break
            cmd = "camera_right" if x>0.5 else "camera_left" 
            last_move_right = True if x>0.5 else False
            # 这里最好是调个pid 我用映射的就好了 
            rotate_times = [0.3,0.2,0.1,0.05,0.01,
                            0.01,0.05,0.1,0.2,0.3]
            t = rotate_times[0]
            for i in range(len(rotate_times)):
                if x < i*0.1+0.1:
                    t = rotate_times[i]
            
            ctrl.press_once(cmd)
            time.sleep(t)
            ctrl.release_once(cmd)
            if(time.time()-ts>timeout): 
                return False
        # walk to tree
        ctrl.press_once("move_up")
        print("===========finded tree============")
        ts = time.time()
        timeout = 30 # 这边三十秒进不去基本也有问题了 
        for i in range(500):
            img = get_new_img()
            if(GenshinLogic.check_dungeon_reward()):
                b = True
                break
            ctrl.click_once("select_object")
            center = detector.detect_center(img,"tree")
            if center == None:# 靠近了可能就找不到了 不管他 
                continue
            x = center[0]
            if 0.475<x and x < 0.525:
                b = True
                continue
            cmd = "move_right" if x>0.5 else "move_left" 
            last_move_right = True if x>0.5 else False
            # 这里最好是调个pid 我用映射的就好了 
            
            ctrl.press_once(cmd)
            time.sleep(0.25)
            ctrl.release_once(cmd)
            
            if(time.time()-ts>timeout):
                ctrl.release_once("move_up")
                return False
            pass
        
        ctrl.release_once("move_up")
        return b
    def go_option():
        
        ctrl = GenshinController()
        for i in range(10):
            ctrl.click_once("cancel")
        time.sleep(1)
        ctrl.click_once("option")
        time.sleep(1)
        pass
    def go_map():
        GenshinLogic.go_option()
        ctrl = GenshinController()
        l0 = [[(0,0),(2,2)]]
        PsnController.go_block(l0[0])
        ctrl.click_once("select")
        time.sleep(1)
    def catherine_daily():
        
        ctrl = GenshinController()
        for i in range(5):
            ctrl.click_once("select_object")
            time.sleep(0.5)
        for i in range(10):
            ctrl.click_once("select")
            time.sleep(0.5)
        time.sleep(1)
    def     catherine_partner():
        
        l0 = [[(0,0),(0,2)]]#派遣委托
        ctrl = GenshinController()
        for i in range(5):
            ctrl.click_once("select_object")
            time.sleep(0.5)
        
        ctrl.click_once("select")
        time.sleep(0.5)
        PsnController.go_block(l0[0])# 枫丹 目前地图是5行2列的 这个改的倒是很频繁

        time.sleep(1)
        
        ctrl.click_once("select")
        
        time.sleep(1)
        
        ctrl.click_once("triangle")
        time.sleep(1)
        ctrl.click_once("select")
        time.sleep(1)
        for i in range(5):
        
            ctrl.click_once("cancel")
            time.sleep(0.3)

        pass
    def go_catherine():
        
        ctrl = GenshinController()
        l0 = [[(0,0),(0,2)]]#枫丹地图点
        
        GenshinLogic.go_map()

        ctrl.click_once("triangle")
        time.sleep(1)
        ctrl.press_once("move_up")
        
        time.sleep(2)
        ctrl.release_once("move_up")# 走到列表最上面 
        ctrl.press_once("move_left")
        time.sleep(1)
        ctrl.release_once("move_left")# 走到列表最上面 
        time.sleep(0.5)

        PsnController.go_block(l0[0])# 枫丹 目前地图是5行2列的 这个改的倒是很频繁
        ctrl.click_once("select")
        for i in range(10):#传送锚点等一系列操作 
            ctrl.click_once("select")
            time.sleep(0.3)
        
        pass
        time.sleep(10) # 加载枫丹 
        run_module_main("cfg.genshin_daily_record")



    def daily_quest():

        GenshinLogic.go_option()
        ctrl = GenshinController()
        l0 = [[(0,0),(0,3)]]
        l = [
             [(0,0),(0,1)],
             [(0,0),(1,0)],# 往右到任务部分
             
             [(0,0),(0,5)],# 往下到点x的部分 不然会出问题
        ]
        PsnController.go_block(l0[0])
        ctrl.click_once("select")
        time.sleep(0.5)
        ctrl.press_once("move_up")
        time.sleep(2)
        ctrl.release_once("move_up")# 走到列表最上面 
        for ll in l:
            PsnController.go_block(ll)
        ctrl.click_once("select")
        time.sleep(2)
        
        ctrl.click_once("select")
        
        ctrl.click_once("select")
        time.sleep(1)
        
        save_img(GenshinLogic.total_success_img_path)
        for i in range(10):
            ctrl.click_once("cancel")
            time.sleep(0.5)
        time.sleep(2)

    def ln_go_main_ui():
        pass
    def go_dungeon_block():
        GenshinLogic.go_dungeon()
        return GenshinLogic.check_in_dungeon()
        #for i in range(5):
        #    b = GenshinLogic.check_in_dungeon_option_ui() 
        #    if b == True:
        #        return b
        #return False
        pass 
    def battle_loop():
        pass
    def check_dungeon_finish():
        ts = time.time()
        detector = yolo_helper.ObjectDetector(path="cfg.genshin_12")
        img  = get_new_img()
        ret = detector.detect_center(img,"dungeon_final")
        print("detect block take: ",time.time()-ts)
        if(ret):
            return True
        return False
    def dungeon_block():

        GenshinLogic.start_battle()
        while not GenshinLogic.check_dungeon_finish():
            GenshinLogic.single_battle_loop()
            pass
        pass
    def get_dungeon_reward():
        # 继续挑战返回False 结束挑战返回True
        # 这块是最核心的找树、领奖励 
        # 找树用深度学习写，我标了100+张树，效果还可以，能往树的方向走；
        # 走的过程中按方块 截图 看是否触发了用树脂的界面(请常备一个以上的树脂)   find_tree函数只负责到这里
        # 找到之后按X 使用20树脂；如果没有20树脂 会跳到补充树脂的界面
        b_find_tree = GenshinLogic.find_tree()# 现在的逻辑timeout也是走到success里 好像也行


        time.sleep(2)
        
        ctrl = GenshinController()
        #ctrl.click_once("select_object")# 领取圣遗物 用不一样的树脂 没有原脆可能没有这一步 无所谓 
        ctrl.click_once("select")# 没有40可能就不会有那个界面..请保证有40的大树脂
        time.sleep(1)
        b = GenshinLogic.check_dungeon_reward_ap_not_enought()

        if True :#20250330 这里改下逻辑，找树找不到会退出地城
            print("===========ap not enought=========")
            for i in range(8):# 退出树脂界面
                time.sleep(0.25)
                ctrl.click_once("cancel")
            time.sleep(1)
            
            ctrl.click_once("option")
            time.sleep(1)
            ctrl.click_once("select")
            
            print("leave dungeon")
            time.sleep(5)
        if b: 
            return True
        
        time.sleep(4)#15-11=4
        ctrl.click_once("select")
        time.sleep(2)
        ctrl.click_once("cancel")
        
        time.sleep(10)
        print("========next turn========")
        ctrl.click_once("select")
        time.sleep(1)
        # 这块逻辑做简单一点，我同时做进下一关和退出的操作，然后按option 如果过了说明还在地牢 没过就没过
        if GenshinLogic.check_in_dungeon():
            return False
            #print("check success")
            #GenshinLogic.start_battle_second()
        
        return True
        pass
    def test():
        #GenshinLogic.go_option()
        GenshinLogic.go_dungeon_block()
        #GenshinLogic.start_battle()
        GenshinLogic.dungeon_block()
        GenshinLogic.find_tree()
        time.sleep(2)
        
        ctrl = GenshinController()
        #ctrl.click_once("select_object")# 领取圣遗物 用不一样的树脂 没有原脆可能没有这一步 无所谓 
        ctrl.click_once("select")# 不对 没有40可能就不会有那个界面..
        time.sleep(1)
        #if GenshinLogic.check_dungeon_reward:
            #we have not ap any more
        #    return False
        time.sleep(15)
        
        ctrl.click_once("select")
        time.sleep(2)
        ctrl.click_once("cancel")
        
        time.sleep(10)
        print("========next turn========")
        ctrl.click_once("select")
        time.sleep(1)
        if GenshinLogic.check_in_dungeon():
            
            print("check success")
            GenshinLogic.start_battle_second()
        pass
        pass
    def full_daily_quest():
        
        #GenshinLogic.daily_quest()
        GenshinLogic.go_catherine()
        GenshinLogic.catherine_daily()
        GenshinLogic.go_catherine()
        GenshinLogic.catherine_partner()

    def ln_daily_quest_block():
        #开书 拿每日奖励 
        node = BehaviorNode(callback=GenshinLogic.daily_quest,name="daily reward")# psn home page
        node0 = BehaviorNode(callback=GenshinLogic.go_catherine,name="go_catherine")# psn home page
        node1 = BehaviorNode(callback=GenshinLogic.catherine_daily,name="catherine_daily")# psn home page
        node2 = BehaviorNode(callback=GenshinLogic.catherine_partner,name="catherine_partner")# psn home page

        link_node0 = LinkNode(node0)
        
        link_node2 = LinkNode(node2)

        node.add_node(link_node0)
        link_node0.add_failed(link_node0)
        link_node0.add_success(node1)
        node1.add_node(link_node2)

        return node,link_node2
    
    def ln_dungeon_block():
        
        node00 = BehaviorNode(callback=GenshinLogic.go_dungeon_block,name="go dungeon")# 
        node0,_out,err = GenshinLogic.ln_simple_dungeon_block()
        
        link_node0 = LinkNode(node00) 
        
        link_node0.add_success(node0)
        link_node0.add_failed(link_node0)
        #node00.add_node(node0)
        return link_node0,_out,err
        pass
    def ln_simple_dungeon_block():
        
        #GenshinLogic.start_battle_second()

        
        node0 = BehaviorNode(callback=GenshinLogic.start_battle,name="open key")# psn home page
        node0_1 = BehaviorNode(callback=GenshinLogic.start_battle_second,name="open key second")# psn home page
        
        node1 = BehaviorNode(callback=GenshinLogic.check_dungeon_finish,name="dungeon_finish?")# psn home page
        
        node1_1 = BehaviorNode(callback=GenshinLogic.single_battle_loop2,name="single_battle_loop1")# failed route
        node1_2 = BehaviorNode(callback=GenshinLogic.single_battle_loop3,name="single_battle_loop2")# failed route
        node1_3 = BehaviorNode(callback=GenshinLogic.single_battle_loop4,name="single_battle_loop1")# 重复一次loop1 多开点蹲
        node1_4 = BehaviorNode(callback=GenshinLogic.single_battle_loop3,name="single_battle_loop3")# failed route

        
        node1_err = BehaviorNode(callback=GenshinLogic.check_dungeon_timeout,name="loop check timeout")# failed route

        #node2 = BehaviorNode(callback=GenshinLogic.find_tree,name="find tree")# psn home page
        node2 = BehaviorNode(callback=GenshinLogic.get_dungeon_reward,name="get reward and go next turn") # failed continue run,success go home
        
        node_err = BehaviorNode(callback=lambda:print("dungeon loop error"),name="dungeon failed,throw") # failed continue run,success go home
        
        link_node1 = LinkNode(node1) 
        link_node1_1 = LinkNode(node1) # 这里多搞几次检测所以多做几个节点 
        link_node1_2 = LinkNode(node1) # success连在一起 
        link_node1_3 = LinkNode(node1) 
        link_node1_4 = LinkNode(node1) 
        link_node1_err = LinkNode(node1_err) 
        link_node2 = LinkNode(node2) 
        
        #两个通路 分别是第一次摸红钥匙和第二次摸(距离短一点)
        # link_node1负责战斗检测和战斗自循环 
        # link_node2负责打完找树，跑过去拿圣遗物(这步可能出问题 目前看总是卡脚脚)
        # 体力耗尽输出成功(也有可能是通路出了问题) 否则自循环 进node0_1
        node0.add_node(link_node1)
        node0_1.add_node(link_node1)
        
        link_node1.add_failed(node1_1)
        node1_1.add_node(link_node1_1)
        link_node1_1.add_failed(node1_2)
        node1_2.add_node(link_node1_2)
        link_node1_2.add_failed(node1_3)
        node1_3.add_node(link_node1_3)
        link_node1_3.add_failed(node1_4)
        
        #node1_4.add_node(link_node1)
        node1_4.add_node(link_node1_err)
        link_node1_err.add_success(link_node1)
        link_node1_err.add_failed(node_err)# timeout,throw out.

        link_node1.add_success(link_node2)
        link_node1_1.add_success(link_node2)
        link_node1_2.add_success(link_node2)
        link_node1_3.add_success(link_node2)
        link_node1_4.add_success(link_node2)


        link_node2.add_failed(node0_1) # looping
        #link_node2.add_success(node2)
        return node0,link_node2,node_err
    def ln_boot_block():
        node0 = BehaviorNode(callback=BootPsn.go_home_plus_check,name="go_psn_home")# psn home page
        node1 = BehaviorNode(callback=GenshinLogic.boot_genshin,name="boot_genshin_game")# select game and boot up
        node2 = BehaviorNode(callback=GenshinLogic.start_game,name="go_main_ui")# open phone page failed close game and reboot it
        node20 = BehaviorNode(callback=BootPsn.close_game,name="close_game")# for reboot
        
        link_node0 = LinkNode(node0) 
        link_node1 = LinkNode(node1) 
        link_node2 = LinkNode(node2) 

        link_node0.add_success(link_node1)
        link_node0.add_failed(link_node0)
        link_node1.add_success(link_node2)
        link_node1.add_failed(link_node0)
        
        #link_node2.add_success(node2)
        link_node2.add_failed(node20)
        node20.add_node(link_node0)
        
        return link_node0,link_node2

        pass
    def ln_total_block():
        

        node_close = BehaviorNode(callback=BootPsn.close_game,name="close_game")# for reboot

        boot_block_in,boot_block_out = GenshinLogic.ln_boot_block()
        dungeon_block_in,dungeon_block_out,dungeon_block_err = GenshinLogic.ln_dungeon_block()
        daily_in,daily_out = GenshinLogic.ln_daily_quest_block()
        boot_block_out.add_success(dungeon_block_in)
        dungeon_block_out.add_success(daily_in)

        dungeon_block_err.add_node(node_close)# 发生错误 尝试重启游戏
        node_close.add_node(boot_block_in)# 重新进入循环
        #dungeon_block = BehaviorNode(callback=GenshinLogic.go_dungeon_block,name="go dungeon")# go dungeon
        
        #node.callback = BootPsn.boot_psn
        return boot_block_in,daily_out
        pass
    pass
class StarRailLogic(BootPsn):
    # 铁看着还好 完全可以用纯图像的方法来做 
    total_success_img_path = "starrail_daily.jpg"
    def boot_star_rail():
        psc = PsnController()
        for i in range(10):
            psc.press("l_right")
            time.sleep(0.1)
            psc.release("l_right")
            time.sleep(1)
            b = False
            for j in range(3):
                b = StarRailLogic.check_star_rail_icon()
                if b:
                    break
                time.sleep(0.3)
            if b:
                return True
        return False
    def star_rail_daily_total_success():
        if not os.path.exists(StarRailLogic.total_success_img_path):
            return False
        img = read_local_img(StarRailLogic.total_success_img_path)

        return avg_same(img,"02_starrail_all_done")
        return True
    pass
    def check_star_rail_icon():
        img = get_new_img()
        b = avg_same(img,"02_starrail_icon")
        return b
        pass
    def check_main_ui():
        b = avg_same(get_new_img(),"02_starrail_main_ui")
        return b
#        return part_same(get_new_img(),"02_starrail_main_ui")
        pass
    def check_phone_ui():
        return avg_same(get_new_img(),"02_starrail_phone_ui")
    def check_guild_book1():
        return avg_same(get_new_img(),"02_daily_box1")
    def check_guild_book2():
        return avg_same(get_new_img(),"02_daily_box2")
    def go_phone_ui(k=5):
        psc = PsnController()
        b = False
        for kk in range(k):
            for i in range(10):
                psc.click("circle")
                time.sleep(0.5)
            
            psc.click("option")
            time.sleep(2.5)
            if StarRailLogic.check_phone_ui():
                return True
            
                
        return False

    def go_main_phone_ui():
        
        psc = PsnController()
        b = False
        for i in range(10):
            psc.press("cross")
            time.sleep(0.1)
            psc.release("cross")
            time.sleep(3)
            b = StarRailLogic.check_main_ui()
            if b:
                break
        for i in range(5):
            b = StarRailLogic.go_phone_ui(k=2)
            if b:
                return True
            for j in range(10):
                psc.click("circle")
                time.sleep(0.3)
            for j in range(2):
                psc.click("cross")
                time.sleep(1)
            time.sleep(5) 
        return b
    
    
    def go_guild_book():
        b = StarRailLogic.go_phone_ui()
        if not b:
            return False
        
        b_go_menu = False
        l0 = [[(0,0),(0,3)]]
        if b_go_menu: 
            for ll in l0:
                PsnController.go_block(ll)
            psc.click("cross",t=0.3)
            time.sleep(2)
        else:
            psc = PsnController()
            for i in range(5):
                psc.click("circle")
                time.sleep(0.4)
            psc.press("l_1")
            time.sleep(1)
            psc.press("r_stick_right")
            psc.press("r_stick_up")
            time.sleep(1)
            
            psc.release("r_stick_right")
            psc.release("r_stick_up")
            time.sleep(0.1)
            psc.release("l_1") 
            time.sleep(1)
        return b
    
    def go_dungeon():
        b= StarRailLogic.go_guild_book()
        if not b:
            return False
        psc = PsnController()
        l0 = [[(0,0),(0,3)]]
        l = [
            # [(1,0),(0,0)],#here quest
            # [(0,0),(1,0)],
            
             [(1,0),(1,starrail_dungeon_type_num)],
             [(1,4),(2,4)],#右边走一格导选副本的地方
             
             [(0,0),(0,starrail_dungeon_num)],# 目前信使在这里第4个 往下10是风 #select
        ]
        

        b = False
        for i in range(10):
            b = StarRailLogic.check_guild_book2()
            if b:
                break
            psc.click("r_1",t=0.3)            
            time.sleep(2)
        if b == False:
            return False
        for ll in l:
            PsnController.go_block(ll)
        
        psc.click("cross",t=0.3)
        time.sleep(10)
        return True
    def check_party_ui():
        img = get_new_img()
        return avg_same(img,"02_choise_party")
        pass
    def before_start_dungeon():
        
        psc = PsnController()
        psc.click("triangle")
        time.sleep(2)#in dungeon
        return StarRailLogic.check_ap_not_enought()

    def start_dungeon():
        
        psc = PsnController()
        #psc.click("triangle")
        #time.sleep(2)#in dungeon
        b = False
        for i in range(3):
            
            time.sleep(1)
            b = StarRailLogic.check_party_ui()
            if b:
                b = True
                break
        if b == False:
            return False
        for i in range(5):
            psc.click("r_2")# select helper
            time.sleep(0.3)

        time.sleep(2) #wait helper
        for i in range(5):
            psc.click("triangle")
            time.sleep(0.3)
        
        #time.sleep(10)# wait dungeon stop.
    def check_ap_not_enought():
        img = get_new_img()
        return avg_same(img,"02_after_dungeon")
    def in_dungeon():
        psc = PsnController()
        for i in range(300):#3*100=300 正常5分钟怎么着都搞定了  没搞定说明哪里有问题 比如没开自动战斗 
            psc.click("triangle")
            time.sleep(3)
            if StarRailLogic.check_ap_not_enought():
                break
            if i > 200:# timeout时试着开一下自动战斗 
                time.sleep(1) 
                psc.click("r_1")
        
        pass
    def quit_dungeon():
        psc = PsnController()
        for i in range(10):
            psc.click("circle")
            time.sleep(0.5)
        
        time.sleep(10)
        return  StarRailLogic.go_phone_ui(1) 
    def daily_mission():
        
        StarRailLogic.go_phone_ui()
        psc = PsnController()
        l0 = [[(0,0),(2,0)]] 
        for ll in l0:
            PsnController.go_block(ll)
        pass
        
        psc.click("cross",t=0.3)
        time.sleep(2)
        
        psc.click("squre",t=0.3)
        time.sleep(1)
        psc.click("triangle",t=0.3)
        
        time.sleep(1)
        for i in range(10):# to home
            psc.click("circle")
            time.sleep(0.3)
    def make_item():
        
        StarRailLogic.go_phone_ui()
        psc = PsnController()
        l0 = [[(0,0),(1,1)]]
        for ll in l0:
            PsnController.go_block(ll)

        psc.click("cross",t=0.3)
        time.sleep(0.05)
        psc.click("cross")
        time.sleep(2)

        psc.click("triangle")
        time.sleep(2)
        psc.click("cross")
        time.sleep(1)
        for i in range(5):
            psc.click("circle")

    def daily_reward():
        StarRailLogic.go_guild_book()
        psc = PsnController()
        for i in range(10):
            b = StarRailLogic.check_guild_book1()
            if b:
                break
            psc.click("l_1",t=0.3)            
            time.sleep(2)
        if b == False:
            return False
        #psc.click("l_1")
        time.sleep(1)
        for i in range(5):# 这里不清楚每日奖励点完会不会消失 总之先放在这里 
            psc.click("cross")
            time.sleep(0.5)
        for i in range(5):
            psc.click("l_stick_right")
            time.sleep(0.5)
            psc.click("cross")
            time.sleep(0.5)
        
        
        psc.click("l_stick_up")
        time.sleep(1)
        
        psc.click("l_stick_up")
        time.sleep(0.1)
        psc.click("cross")
        time.sleep(1)
        psc.click("cross")
        time.sleep(1)
        psc.click("cross")
        time.sleep(1)
        save_img(StarRailLogic.total_success_img_path)
        pass

        pass
        
        pass
    def daily_score():
        b = StarRailLogic.go_phone_ui()
        psc = PsnController()
        for i in range(5):
            psc.click("circle")
            time.sleep(0.4)
        psc.press("l_1")
        time.sleep(1)
        psc.press("r_stick_left")
        psc.press("r_stick_up")
        time.sleep(1)
        
        psc.release("r_stick_left")
        psc.release("r_stick_up")
        time.sleep(0.1)
        psc.release("l_1") 
        time.sleep(1)

        psc.click("r_1")
        time.sleep(1)
        # get reward,i guess is squre or triangle
        for i in range(3):
            psc.click("triangle")
            #psc.click("squre")
            time.sleep(1)
            psc.click("l_stick_down")
            time.sleep(1)
            psc.click("triangle")
            time.sleep(1)
            psc.click("r_1")
            time.sleep(1)
        #return b
        return True #只试着拿一下纪行奖励 拿不到也无所谓。
        pass
    def full_dungeon_block():
        print("go_main_phone_ui")
        #StarRailLogic.go_main_phone_ui()
        #StarRailLogic.go_phone_ui()
        print("go_dungeon")
        StarRailLogic.go_dungeon()
        
        print("start_dungeon")
        #StarRailLogic.start_dungeon()
        
        print("in_dungeon")
        #StarRailLogic.in_dungeon()
        #StarRailLogic.quit_dungeon()
        
        print("daily_mission")
        StarRailLogic.daily_mission()
        StarRailLogic.daily_reward()
    def ln_dungeon_block():
        # 这里有两个检查点 1 开始副本的时候会跳一个ap检查出来，过了跳出，没过往下走；
        # 
        
        node0 = BehaviorNode(callback=StarRailLogic.go_dungeon,name="go_dungeon")# psn home page
        node0_3  = BehaviorNode(callback=StarRailLogic.before_start_dungeon,name="check ap")# psn home page
        node1 = BehaviorNode(callback=StarRailLogic.start_dungeon,name="start dungeon")# 这里会做一个选人界面的判断 成功往下走，失败回go dungeon 在里面可能能退到桌面
        #node1_0 = BehaviorNode(callback=StarRailLogic.go_phone_ui,name="start dungeon")# 
        node2 = BehaviorNode(callback=StarRailLogic.in_dungeon,name="on dungeon")# 
        node3 = BehaviorNode(callback=StarRailLogic.quit_dungeon,name="quit_dungeon")#  
        link_node0 = LinkNode(node0)
        link_node0_3 = LinkNode(node0_3)
        link_node1 = LinkNode(node1)
        link_node3 = LinkNode(node3) 

        #node0.add_node(link_node1)
        link_node0.add_success(link_node0_3)
        link_node0.add_failed(link_node0)
        link_node0_3.add_success(link_node3)#not ap  go out
        link_node0_3.add_failed(link_node1)#ap enough,go node1 
        link_node0.add_failed(link_node1)# ap enought 
        link_node1.add_success(node2)
        link_node1.add_failed(link_node0)
        node2.add_node(link_node3)
        link_node3.add_failed(link_node3)

        return link_node0,link_node3
        pass
    def ln_daily_reward_block():

        node3 = BehaviorNode(callback=StarRailLogic.make_item,name="daily make item")# 
        node4 = BehaviorNode(callback=StarRailLogic.daily_mission,name="daily mission")# 
        node5 = BehaviorNode(callback=StarRailLogic.daily_reward,name="daily reward")# 
        node6 = BehaviorNode(callback=StarRailLogic.daily_score,name="daily score")# 
        
        link_node5 = LinkNode(node5) 

        node3.add_node(node4)
        node4.add_node(node6)
        node6.add_node(link_node5)
        link_node5.add_failed(link_node5)# not work,only for tree check
        return node3, link_node5
        pass
    def ln_boot_starrail_block():
        # boot game

        node0 = BehaviorNode(callback=BootPsn.go_home_plus_check,name="go_psn_home")# psn home page
        node1 = BehaviorNode(callback=StarRailLogic.boot_star_rail,name="boot_starrail_game")# select game and boot up
        node2 = BehaviorNode(callback=StarRailLogic.go_main_phone_ui,name="go_main_phone_ui")# open phone page failed close game and reboot it
        node20 = BehaviorNode(callback=BootPsn.close_game,name="close_game")# for reboot
        #node.callback = BootPsn.boot_psn
        
        #failed_node = BehaviorNode(callback=BootPsn.stop_chiaki)
        #failed_node.callback = 
        link_node0 = LinkNode(node0) 
        link_node1 = LinkNode(node1) 
        link_node2 = LinkNode(node2) 
        
        link_node0.add_failed(link_node0)
        link_node0.add_success(link_node1)
        link_node1.add_failed(link_node0)
        link_node1.add_success(link_node2)
        
        #link_node2.add_success(link_node1)
        link_node2.add_failed(node20)
        node20.add_node(link_node0) 

        return link_node0,link_node2# not in out
        pass
    def ln_total_block():
        boot_in,boot_out = StarRailLogic.ln_boot_starrail_block()
        dungeon_in,dungeon_out = StarRailLogic.ln_dungeon_block()
        daily_in,daily_out = StarRailLogic.ln_daily_reward_block()   

        boot_out.add_success(dungeon_in)
        dungeon_out.add_success(daily_in)
        #return boot_in,daily_out
        return boot_in,daily_out
        pass
class Fgo:
    # 有了奏章1之后白纸化地球也有了稳定的锚点，可以定位进去；标题画面也可以定位；就是中间更新的按钮可能需要点一下。(不过这个可以用实验的 实在不行整个随机数)
    def boot_fgo():
        pass
    pass

if __name__ == "__main__":
    BackgroundControllerSingleton.wait_start()
    #gl = GenshinLogic()
    #while BackgroundControllerSingleton.is_running():
    #    gl.single_battle_loop()
    
    root,_ = BootPsn.ln_boot_psn_block()
    rail_in,rail_out = StarRailLogic.ln_total_block()
    genshin_in,genshin_out = GenshinLogic.ln_total_block()
    close_psn_node = BehaviorNode(BootPsn.stop_chiaki)
    success_node = BehaviorNode(lambda:print("all done,good job!"),"final_block")

    root.add_success(rail_in)
    rail_out.add_success(success_node)
    genshin_out.add_success(close_psn_node)
    close_psn_node.add_node(success_node)
    run_root_node(root)
    #run_root_node(rail_in)

    run_root_node(genshin_in)


    #StarRailLogic.full_dungeon_block()
    #GenshinLogic.go_dungeon()
    #print(GenshinLogic.check_dungeon_reward())
    #GenshinLogic.test()
    #GenshinLogic.full_daily_quest()
    #GenshinLogic.find_tree()
    pass