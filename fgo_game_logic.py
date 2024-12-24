from psn_controller import *
from pynput import mouse,keyboard
from  behavior_tree import *
import time
import os
import subprocess
from cfg_helper import *
import yolo_helper
# fgo主要两种场景 1 日常白纸化三把 2 活动吃体力固定位置 3 无限池大刷特刷 
fgo_go_event = False #白纸化地球False 活动True 
fgo_need_apple = 0
eat_apple_num = 2 #012 金银蓝
dungeon_num = 10 #从0开始 -1是最后一个 
class FgoTurn:
    def __init__(self,clean=False):
        self.skill1 = [False]*9
        self.skill_target1 = [1]*9
        self.master_skill = [False]*3
        self.master_skill_target = [1]*3
        self.skill2 = [False]*9
        self.skill_target2 = [1]*9
        self.hougu = [True] * 3
        self.card = [True]*5
        self.change_person = False
        self.change_person_target1 = 2
        self.change_person_target2 = 3
        if clean:
            self.clear_skill()
            self.clear_hougu()
    # turn里所有的使用都是从0开始的 
    # 但是battle里的所有下标是从1开始 要注意
    def use_all_skill(self):
        self.skill1 = [True]*9
    def clear_skill(self):
        self.skill1 = [False]*9
        self.master_skill = [False]*3
    def clear_hougu(self):
        self.hougu = [False] * 3
    def use_skill(self,i,target=1):
        self.skill1[i] = True
        self.skill_target1[i] = target
    def use_master_skill(self,i,target=1):
        self.master_skill[i] = True
        self.master_skill_target[i] = target
    def use_hougu(self,i):
        self.hougu[i] = True
        pass
    def is_change_person(self):
        self.change_person = True
    def use_skill2(self,i,target=2):
        self.skill2[i] = True
        self.skill_target2[i] = target
    def use_change_person(self,t1,t2):
        self.change_person = True
        self.change_person_target1 = t1
        self.change_person_target2 = t2
class FgoLogic: 
    total_success_img_path = "fgo_daily.jpg"
    def check_fgo_info():
        return avg_same(get_new_img(),"03_fgo_info_ui")
        pass
    
    def boot_game():
        psc = PsnController()
        
        exit_code = subprocess.call([".\\bat\\run_fgo.bat"], shell=True)# boot fgo
        #psc.click()
        pass
    def go_main_ui_normal():
        # 这里的想法是大版本更新主界面也会变 但是通知栏那边我是没见过变过 
        # 开机点左上角和返回 一直点到看到info栏
        ts = time.time()
        ps = PointData("03_home_mark_point")
        ps1 = PointData("03_startup_button")
        for i in range(100):
            ps.move_click("1")
            time.sleep(2)
            if i > 30:
                b = FgoLogic.check_update_button()
                if b:
                    ps1.move_click("2")# 点右边 更新
                    ts = time.time()# 再拿120s出来更新
            b = FgoLogic.check_fgo_info()
            if b :
                break
            if i == 40:
                ps1.move_click("1") # 点左边 
            if ts-time.time()>120:
                return False
            
        pass
        return True
    def go_main_ui_ng():
        # 服务器升级等因素需要等待mainui打开 
        # 这里不更新在左边 更新在右边；不开始游戏在左边 开始在右边 就纠结
        # 简单版本就是先不管他 过1分钟以上，点左边，
        # ongoing
        pass
    def click_bar_zero():
        bar = PointData("03_bar_mark_point")
        
        bar.move_click("1")# 返回按钮
        pass
    #从0开始算副本
    def click_bar_dungeon(num):
        
        bar = PointData("03_bar_mark_point")
        bar.move_click(f"{num+2}")# 1是bar的头 从0开始
    def click_bar_last_dungeon():
        
        bar = PointData("03_bar_mark_point")
        
        bar.move_click("0")# 1是bar的头 0是bar的尾巴
        time.sleep(1)
        bar.move_click("2")# 1是bar的头 从0开始
    def drag_two():
        bar = PointData("03_bar_mark_point")
        p1 = bar.p("6")# 下面的点
        p2 = bar.p("7")# 下面的点
        ps = p1+p2
        bar.psc.drag(ps,t=5,step=100)# 这个拖多了会有一点点拉过头 尽量控制在3以内 
        pass
    def click_return():
        
        ps = PointData("03_home_mark_point")
        ps.move_click("0")
        pass
    def go_home(step=4): 
        
        ps = PointData("03_home_mark_point")
        for i in range(step):
            if i >= 0:
                for i in range(3):
                    ps.move_click("0")# 返回按钮
                    time.sleep(0.3)
                
            ps.move_click("1")# 左上角的info
            
            time.sleep(2)
            b = FgoLogic.check_fgo_info()
            
            if b :
                FgoLogic.click_return()
                time.sleep(0.5)
                #FgoLogic.click_return()
                time.sleep(0.5)
                return True 
        pass
        return False
    def route_event():
        return fgo_go_event
            
    def go_event():
        FgoLogic.go_home()
        ps = PointData("03_home_mark_point")
        bar = PointData("03_bar_mark_point")
        time.sleep(1)
        FgoLogic.click_bar_zero()
        time.sleep(0.5)
        ps.move_click("3")
        time.sleep(3)
    def select_dungeon():
        tmp_num = dungeon_num
        FgoLogic.click_bar_zero()
        if tmp_num == -1:
            FgoLogic.click_bar_last_dungeon()
            return
        while tmp_num>3:
            FgoLogic.drag_two()
            tmp_num = tmp_num-2
        time.sleep(1)
        FgoLogic.click_bar_dungeon(tmp_num)
        time.sleep(1)
    def try_eat_apple():
        time.sleep(1)
        b = False
        for i in range(5):
            time.sleep(0.5)
            b = FgoLogic.check_need_apple()
            if b:
                print("check need apple success")
                break
            pass
        if b == True:
            b = FgoLogic.eat_apple() # 失败则不继续 
            # 白纸化地球吃完还要回去点一下框框的确定按钮 不会直接进去 
            #time.sleep(2)
            #ps.move_click("2")# 弹出框框的确定按钮 普通模式没有这个框框
            return b # 失败说明补充体力失败 无法继续 返回false；往下走的情况是正常的 不用管这个b
        return True
        pass
    def go_white_earth():
        for jj in range(3):
            FgoLogic.go_home()
            ps = PointData("03_home_mark_point")
            # 3 4 5 是右边的三个基础点位 
            # 5是活动点位3 有活动的时候是日常本
            # 4活动点位2 有活动的时候是周常本
            b = False
            p_cmd = ["5","4" ]
            # 考虑到正常多数都是有活动的 所以先走5点
            for cmd in p_cmd:
                FgoLogic.click_bar_zero()
                time.sleep(0.5)
                ps.move_click(cmd)

                time.sleep(2)
                for i in range(10):
                    b = FgoLogic.check_white_earth()
                    if b:
                        return True
                    time.sleep(1)
                if b:
                    break
                #走到这里说明不是白纸化地球  回桌面再来一次
                FgoLogic.go_home()
            return b
        return False
    def check_white_earth():
        return avg_same(get_new_img(),"03_white_earth")
    def check_event():
        pass
    def go_earth_dungeon():
        ps = PointData("03_white_earth_mark")
        
        p_cmd = ["5","6"]
        ts =    [2, 0.5]
        ps.go_block(p_cmd,ts)
        #time.sleep(1)
        b = False
        for i in range(5):
            time.sleep(0.5)
            b = FgoLogic.check_white_earth()
            if b:
                break
        if b == False:
            return b
        time.sleep(2)
        p_cmd = ["4","4","4","4"]
        ps.go_block(p_cmd,t=[2])
        p1 = ps.p("7")
        p2 = ps.p("8")
        #print(p1,p2)
        psc = PsnController()
        psc.line_click(p1+p2)# 这里点的位置会点到右边开始关卡的部分 不过问题不大 先不管他 
        time.sleep(1)
        return True
        pass
    # 补充体力 如果不需要或者补充失败了(如点击后没有补充 )
    def eat_apple():
        #on going
        global fgo_need_apple # for set this value
        if fgo_need_apple<=0:
        #if fgo_need_apple == False:
            return False
        fgo_need_apple = fgo_need_apple - 1
        #eat_apple_num = 0 #0123 金银蓝铜 现在不支持铜
        ps0 = PointData("03_eat_apple_mark")
        ps1 = PointData("03_apple_mark") # 4 point
        
        if eat_apple_num < 3:
            ps1.move_click(f"{eat_apple_num+1}")
            time.sleep(2)
            ps0.move_click("1")
        return True
    def fgo_daily_total_success():
        if not os.path.exists(FgoLogic.total_success_img_path):
            return False
        img = read_local_img(FgoLogic.total_success_img_path)
        
        b1 = FgoLogic.check_out_of_jar(img)
        b2 = FgoLogic.check_need_apple(img)
        return (b1 == True) or (b2 == True)
        pass
    def select_earth_dungeon():
        FgoLogic.click_bar_dungeon(0)
        time.sleep(2)
        ps = PointData("03_white_dungeon_mark")
        
        ps.move_click("2")# 弹出框框的确定按钮
        time.sleep(1)
        b = False
        for i in range(5):
            time.sleep(0.5)
            b = FgoLogic.check_need_apple()
            if b:
                print("check need apple success")
                break
            pass


        save_img(FgoLogic.total_success_img_path)

        if b == True:
            b = FgoLogic.eat_apple() # 失败则不继续 
            # 白纸化地球吃完还要回去点一下框框的确定按钮 不会直接进去 
            time.sleep(2)
            ps.move_click("2")# 弹出框框的确定按钮
            return b # 失败说明补充体力失败 无法继续 返回false；往下走的情况是正常的 不用管这个b
        
        for i in range(5):
            time.sleep(0.2)
            b = FgoLogic.check_out_of_jar()
            if b:
                print("check out of jar")
                return False
                
            pass



        return True
    def check_helper_ui():
        return avg_same(get_new_img(),"03_helper_select")
        pass
    def check_dungeon_party_ui():
        
        return avg_same(get_new_img(),"03_member_select")
        pass
    def select_helper():
        b  = False
        for i in range(10):
            b = FgoLogic.check_helper_ui()
            time.sleep(0.1)
            b = FgoLogic.check_helper_ui()
            time.sleep(1)
            if(b):
                break
        ps = PointData("03_helper_select")
        ps.move_click("e")# 找第一个人点一下  这边可以加更复杂的逻辑 先不管 
        
        
        for i in range(10):
            b = FgoLogic.check_dungeon_party_ui()
            time.sleep(1)
            if(b):
                break
        ps = PointData("03_member_select_mark")
        ps.move_click("1")# 开始按钮
        time.sleep(0.5)
        ps.move_click("1")# 开始按钮
        return True
        #return b
        
        pass
    class FgoBattle:
        # 所有的标签从1开始计数 
        p1_cmd = "03_1_fgo_skill_mark_point"
        p1 = {
            "enemy1":"1",
            "enemy2":"2",
            "enemy3":"3",
            "skill1":"4",
            "skill2":"5",
            "skill3":"6",
            "skill4":"7",
            "skill5":"8",
            "skill6":"9",
            "skill7":"q",
            "skill8":"w",
            "skill9":"e",
            "master_skill":"r",
            "master_skill1":"t",
            "master_skill2":"y",
            "master_skill3":"u",
            "start":"i"
        }
        p2_cmd = "03_1_person_change_mark"
        p2 = {
            "p1":"1",
            "p2":"2",
            "p3":"3",
            "p4":"4",
            "p5":"5",
            "p6":"6",
            "change_select":"7"
        }
        p3_cmd = "03_1_skill3_mark"

        p3 = {
            "member1":"1",
            "member2":"2",
            "member3":"3",
        }
        
        p4_cmd = "03_01_card_mark"
        p4 = {
            "card1":"4",
            "card2":"5",
            "card3":"6",
            "card4":"7",
            "card5":"8",
            "hcard1":"1",
            "hcard2":"2",
            "hcard3":"3",
        }
        def __init__(self):
            self.p = [self.p1,self.p2,self.p3,self.p4]
            self.ps1 = PointData(self.p1_cmd)
            self.ps2 = PointData(self.p2_cmd)
            self.ps3 = PointData(self.p3_cmd)
            self.ps4 = PointData(self.p4_cmd)
            self.pss = [self.ps1,
                        self.ps2,
                        self.ps3,
                        self.ps4]
        # 单纯一次技能使用 多种技能的话会比较麻烦 
        # 注意所有的标签、人从1开始计数 
        def move_click(self,s):
            for i in range(len(self.p)):
                pi = self.p[i]
                if s in pi.keys():
                    cmd = pi[s]
                    self.pss[i].move_click(cmd)
                    return 
            print("error: key not found ",s)
        def click_other(self):
            ps = PointData("03_save_point_mark")
            time.sleep(0.2)
            ps.move_click("1")# click outer
            time.sleep(0.2)
        def use_skill(self,num,target=2):
            cmd = f"skill{num}"
            tgt = f"member{target}"
            self.move_click(cmd)
            time.sleep(0.3)
            self.move_click(tgt)
            self.click_other()
            # self.ps1.move_click(cmd)
            # time.sleep(0.5)
            # self.ps3.move_click(tgt)

            pass
        def use_master_skill(self,num,target=2):
            
            cmd = f"master_skill{num}"
            tgt = f"member{target}"
            
            # self.ps1.move_click("master_skill")
            # time.sleep(0.5)
            # self.ps1.move_click(cmd)
            # time.sleep(0.5)
            # self.ps3.move_click(tgt)
            self.move_click("master_skill")
            time.sleep(0.5)
            self.move_click(cmd)
            time.sleep(0.5)
            self.move_click(tgt)
            self.click_other()
            pass
        def use_change_person(self,p1=3,p2=4): 
            cmd = "master_skill3"
            target1 = f"p{p1}"
            target2 = f"p{p2}"
            # self.ps1.move_click("master_skill")
            # time.sleep(1) 
            # self.ps1.move_click("master_skill3")
            # time.sleep(1)
            # self.ps2.move_click(target1)
            # time.sleep(0.5)
            # self.ps2.move_click(target2)
            # time.sleep(0.5)
            # self.ps2.move_click("change_select")
            # time.sleep(0.5)
            
            self.move_click("master_skill")
            time.sleep(1) 
            self.move_click("master_skill3")
            time.sleep(1)
            self.move_click(target1)
            time.sleep(0.5)
            self.move_click(target2)
            time.sleep(0.5)
            self.move_click("change_select")
            time.sleep(0.5)
            
            self.click_other()
            pass
        def select_card(self,num):
            cmd = f"card{num}"
            #self.ps4.move_click(cmd)
            self.move_click(cmd)
            time.sleep(0.5)
        def use_skill_card(self,num):
            
            cmd = f"hcard{num}"
            #self.ps4.move_click(cmd)
            self.move_click(cmd)
            time.sleep(0.5)
        


    def in_dungeon():
        ps = PointData("03_member_select_mark")
        time.sleep(3)
        ps.move_click("1")
        pass
    def check_update_button():
        b =  avg_same(get_new_img(),"03_startup_button",diff=20)
        return b
    def check_skill_phase():
        b =  avg_same(get_new_img(),"03_1_start_button",diff=20)
        #print(b)
        return b
    
    def wait_start_button(timeout = 3):
        b = False
        t = timeout/20
        for i in range(20):# 找蓝色按钮
            b = FgoLogic.check_skill_phase()
            if b:
                break
            time.sleep(t)
        if b == False:
            print("wait_start_button timeout")
        return b
    def click_start_button():
        # 等4秒找蓝色按钮 找到后点一下 接着找蓝色按钮  蹲到蓝色消失 
        b = FgoLogic.wait_start_button(timeout = 4)
        if b == False:
            return False
        fb =FgoLogic.FgoBattle()
        fb.move_click("start")
        time.sleep(0.1)
        fb.move_click("start")
        time.sleep(0.1) 
        fb.click_other()
        count = 0
        for i in range(25):
            b = FgoLogic.check_skill_phase()
            if b == False:
                count = count + 1
            if count > 5:
                break
            time.sleep(0.2)
        if count < 5:
            print("click_start_button not find once")
            return False
        return True
    def try_click_start_button(step=4):
        b = False
        for i in range(step):
            b = FgoLogic.click_start_button()
            if b:
                return True
            FgoLogic.click_return()
            time.sleep(0.3)
            FgoLogic.click_return()
            time.sleep(0.3)
            
            fb = FgoLogic.FgoBattle()
            fb.click_other()
            #fb.move_click("enemy1")#这是个左上角的点 点一下消返回的框框 
        print("try_click_start_button timeout")
        return b
    def single_turn_skill(turn):
        fb =FgoLogic.FgoBattle()
        for i in range(len(turn.skill1)):
            k = i+1
            skill = turn.skill1[i]
            target = turn.skill_target1[i] +1
            print(f"use skill {i}{skill}")
            if skill:
                fb.use_skill(k,target)
                time.sleep(1)
        if turn.change_person:
            fb.use_change_person(turn.change_person_target1+1,turn.change_person_target2+1) 
            FgoLogic.wait_start_button(timeout=60)
            
        for i in range(len(turn.master_skill)):
            k = i+1
            skill = turn.master_skill[i]
            target = turn.master_skill_target[i] +1
            if skill:
                fb.use_master_skill(k,target)
                time.sleep(1)
        
        
        for i in range(len(turn.skill2)):
            k = i+1
            skill = turn.skill2[i]
            target = turn.skill_target2[i] +1
            if skill:
                fb.use_skill(k,target)
                time.sleep(1)
        pass
    def single_turn_card(turn):
        
        fb =FgoLogic.FgoBattle()
        for i in range(len(turn.hougu)):
            k = i+1
            skill = turn.hougu[i]
            if skill:
                fb.use_skill_card(k)
                time.sleep(1)
        
        time.sleep(0.5)
        for i in range(5):
            k = i+1
            fb.select_card(k)
            time.sleep(0.2)
        
        for i in range(5):
            k = i+1
            fb.select_card(k)
            time.sleep(0.2)
        
    def single_turn(turn=FgoTurn()):
        #流程
        # 找开始图标
        # 1 放一轮技能
        # 2 放一轮御主技能
        # 3 放一轮技能
        # 4 点开始
        # 找开始图标 
        # 5 点宝具
        # 6 点指令卡 (指令卡插宝具太复杂 先不管他 )
        # 其中最重要的是开始图标的识别 识别不到都完蛋 
        FgoLogic.single_turn_skill(turn)
        b = FgoLogic.try_click_start_button()#FgoLogic.click_start_button()
        print(f"==================start button success{b}===========")
        FgoLogic.single_turn_card(turn)
        
        pass
    def dungeon_loop():
        # timeout 返回failed
        # 
        
        default_timeout = 160
        turns = BackgroundControllerSingleton.datas["fgo_turns"]
        print(f"======all turns{len(turns)}==========")
        count = 0
        ts_first = time.time()
        while True: # wait in first stage
            print(f"dungeon loop timeout {default_timeout-(time.time()-ts_first)}")
            if ( time.time()-ts_first )>default_timeout:
                return False
            
            b = FgoLogic.wait_start_button()
            if b : 
                break
            time.sleep(0.5)
            #break
            pass
        time.sleep(3)# here 20240910 上面的start button有误识别 难受
        while True:
            print(f"dungeon loop turn{count}")
            ts_turn = time.time()
            turn = FgoTurn()
            turn.clear_skill()
            if count < len(turns):
                turn = turns[count]
            
            FgoLogic.single_turn(turn)
            print(f"wait next turn {default_timeout}")
            while True:
                b = FgoLogic.check_success()
                if b :
                    return True
                b = FgoLogic.check_skill_phase()#20241010 here 公主本这个不太好用 不知道为啥  我改了20可以开起来再跑一把 
                if b : 
                    break
                if (time.time()-ts_turn) > default_timeout:
                    return False
            count = count + 1



        return BehaviorNode.ongoing



    def check_success():
        b = False
        b = avg_same(get_new_img(),"03_dungeon_end")
        if b == False:
            return False
        count = 0 # 这个不好使的话可以改2 然后改03_dungeon_end的点
        l = ["03_dungeon_end1","03_dungeon_end2","03_dungeon_end3","03_dungeon_end4"]
        for s in l:
            b = avg_same(get_new_img(),s)
            if b:
                count = count +1
        print("check success count",count)
        return  True if count>1 else False
        
    def skill_phase():
        pass
    def check_need_apple(img=None):
        if img is None:
            img = get_new_img()
        return avg_same(img,"03_apple_mark")
        pass 
    def check_out_of_jar(img=None):
        if img is None:
            img = get_new_img()
        return avg_same(img,"03_out_of_jar")
        pass
    def quit_dungeon():
        ts = time.time()
        ps1 = PointData("03_dungeon_get_item_mark")
        ps2 = PointData("03_dungeon_quit_mark_point2")
        get_all_black = False
        count = 0
        while True:
            count = count + 1
            b = FgoLogic.check_all_black()
            if b == True and count > 10:# 先点个一轮把东西都点掉 
                get_all_black = True
            if get_all_black and (b == False):
                time.sleep(5)# 等完全亮起来
                return True
            if count %10 == 0:
                ps1.move_click("1")
                time.sleep(0.2)
                ps2.move_click("1")
                time.sleep(1.8)
            if time.time()-ts>60:#timeout 60s
                return False
            time.sleep(0.1)
        
        pass
    def check_all_black():
        return avg_same(get_new_img(),"03_dungeon_quit_all_black",diff=10)
    def stop_game():
        
        exit_code = subprocess.call([".\\bat\\kill_fgo.bat"], shell=True)# boot fgo
        time.sleep(2)
    
    def total(): 
        #FgoLogic.boot_game()
        #FgoLogic.go_main_ui_normal()
        FgoLogic.go_event()
        FgoLogic.select_dungeon()
        FgoLogic.select_helper()
        #FgoLogic.go_white_earth()
        #FgoLogic.go_earth_dungeon()
        #FgoLogic.select_earth_dungeon()
        # 往下的逻辑就是通用的战斗逻辑了 ongoing
        pass
    def ln_event_block():
        
        node1 = BehaviorNode(FgoLogic.go_event,"go_event")
        ln1 = LinkNode(node1)
        ln1.add_failed(ln1)# for complie check
        return ln1,ln1
        pass
    def ln_event_in_dungeon_block():
        node1 = BehaviorNode(FgoLogic.select_dungeon,"select_dungeon")
        node2 = BehaviorNode(FgoLogic.try_eat_apple,"try eat apple")
        
        node4 = BehaviorNode(FgoLogic.stop_game,"not ap,stop game,not return")
        
        ln2 = LinkNode(node2)
        #ln1 = LinkNode(node1)
        node1.add_node(ln2)
        ln2.add_failed(node4)#for complie
        
        return node1,ln2,node4
        pass
    def ln_boot_game_block():
        node1 = BehaviorNode(FgoLogic.boot_game,"boot_game")
        node2 = BehaviorNode(FgoLogic.go_main_ui_normal,"go main")
        node2_1 = BehaviorNode(FgoLogic.stop_game,"stop")
        #ln1 = LinkNode(node1)
        ln2 = LinkNode(node2)

        node1.add_node(ln2)
        ln2.add_failed(node2_1)
        node2_1.add_node(node1)
        return node2_1,ln2
    def ln_earth_block():
        # 这里两条通路 不行的通路重启游戏；可以的通路往下走 还有一条ap不足的通路直接结束
        node1 = BehaviorNode(FgoLogic.go_white_earth,"go earth")
        node2 = BehaviorNode(FgoLogic.go_earth_dungeon,"select dungeon")

        node_failed = BehaviorNode(lambda:print("need reboot"),"failed node ,for reboot")
        ln1 = LinkNode(node1)
        ln2 = LinkNode(node2)

        ln1.add_success(ln2)
        ln1.add_failed(node_failed)

        ln2.add_failed(node_failed)
        return ln1,ln2,node_failed
        pass
    def ln_daily_in_dungeon_block():

        node3 = BehaviorNode(FgoLogic.select_earth_dungeon,"in dungeon")# 苹果逻辑
        node4 = BehaviorNode(FgoLogic.stop_game,"not ap,stop game,not return")

        ln3 = LinkNode(node3)
        ln3.add_failed(node4)# end  if not ap. 
        return ln3,ln3,node4# node4 是整个程序的唯一出口 
    
    def ln_dungeon_block():
        node0 = BehaviorNode(FgoLogic.select_helper,"select_helper")

        node1 = BehaviorNode(FgoLogic.dungeon_loop,"loop")
        node2 = BehaviorNode(FgoLogic.quit_dungeon,"quit_dungeon")
        
        node_failed = BehaviorNode(lambda:print("need reboot"),"failed node ,for reboot")
        
        ln1 = LinkNode(node1)
        ln2 = LinkNode(node2)
        
        node0.add_node(ln1)
        ln1.add_failed(node_failed)
        ln1.add_success(ln2)
        ln2.add_failed(node_failed)
        return node0,ln2,node_failed
    

    def ln_total_daily_block():
        boot_in,boot_out = FgoLogic.ln_boot_game_block()
        earth_in,earth_out,earth_failed = FgoLogic.ln_earth_block()
        daily_in,daily_out,daily_total = FgoLogic.ln_daily_in_dungeon_block()
        dungeon_in,dungeon_out,dungeon_failed = FgoLogic.ln_dungeon_block()

        node_stop = BehaviorNode(FgoLogic.stop_game,"reset game")
        node_stop.add_node(boot_in)
        boot_out.add_success(earth_in)
        earth_out.add_success(daily_in)
        daily_out.add_success(dungeon_in)
        dungeon_out.add_success(daily_in)# here loop

        earth_failed.add_node(node_stop)
        dungeon_failed.add_node(node_stop)

        return boot_in,daily_total

        pass
    def ln_total_event_block():
        
        boot_in,boot_out = FgoLogic.ln_boot_game_block()
        earth_in,earth_out = FgoLogic.ln_event_block()
        daily_in,daily_out,daily_total = FgoLogic.ln_event_in_dungeon_block()
        dungeon_in,dungeon_out,dungeon_failed = FgoLogic.ln_dungeon_block()

        node_stop = BehaviorNode(FgoLogic.stop_game,"reset game")
        node_stop.add_node(boot_in)
        boot_out.add_success(earth_in)
        earth_out.add_success(daily_in)
        daily_out.add_success(dungeon_in)
        dungeon_out.add_success(daily_in)# here loop

        #earth_failed.add_node(node_stop)
        dungeon_failed.add_node(node_stop)

        return boot_in,daily_total
def init_turns():
    turn0 = FgoTurn(clean=True)
    # 白纸化地球 梅利 尼禄 尼托 t1 012 456 h2 t2  h3 t3 7 h13
    turn0.use_skill(0,target=1)
    turn0.use_skill(1,target=1)
    turn0.use_skill(2,target=1)
    turn0.use_skill(3,target=1)
    turn0.use_skill(4,target=1)
    turn0.use_skill(5,target=1)
    turn0.use_skill(6,target=1)
    
    turn0.use_hougu(1)
    
    
    turn1 = FgoTurn(clean=True)
    #turn1.use_skill(7,target=1)
    turn1.use_hougu(2)

    turn2 = FgoTurn(clean=True)
    turn2.use_skill(2,target=1)
    turn2.use_skill(7,target=1)
    turn2.use_hougu(0)
    turn2.use_hougu(2)

    turns = [turn0,turn1,turn2]
    return turns
    pass

if __name__ == "__main__":
    BackgroundControllerSingleton.datas["fgo_turns"] = init_turns()
    BackgroundControllerSingleton.wait_start() 
    root,_ = FgoLogic.ln_total_event_block()
    run_root_node(root)
    pass