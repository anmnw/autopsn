'''
执行结点(execution node)：行为树的叶子结点，可以是动作结点(action node)或条件结点(condition node)。
对于条件结点(condition node)会在一次tick后立马返回成功或失败的状态信息。
对于动作结点(action node)则可以跨越多个tick执行，直到到达它的终结状态。一般来说，条件结点用于简单的判断(比如钳子是否打开?)，动作结点用于表示复杂的行为(比如打开房门)。

控制结点(control node)：控制结点是行为树的内部结点，它们定义了遍历其孩子结点的方式。控制结点的孩子可以是执行结点，也可以是控制结点。
顺序(Sequence)，备选(Fallback)，并行(Parallel)这3种类型的控制结点可以有任意数量的孩子结点，它们的区别在于对其孩子结点的处理方式。而装饰(Decorator)结点只能有一个孩子结点，用来对孩子结点的行为进行自定义修改

看着有点复杂 咱们整个简单的版本
1 第一版只有顺序 这不是树 这是链表 但是带回链 
2 一个节点只有三种模式 成功 失败 进行中；
3 失败可以返回之前的节点，但是之前的节点和其子树要重新初始化(即从success到ongoing)
4 维护一个公用的对象来存各种有的没有的东西 有个map来维护这些数据
''' 

class BehaviorNode:
    success = 0
    ongoing = 1
    failed = 2
    error = 99
    def default_callback():
        return BehaviorNode.success
        pass
    def boot_ret(b):
        if b:
            return BehaviorNode.success
        else: 
            return BehaviorNode.failed
        
    def __init__(self,callback=default_callback,name="",database={},):
        self.parent = None
        self.nodes = []
        self.database = database
        self.callback = callback
        self.state = BehaviorNode.ongoing
        self.name=name
        self.reset_node = None
        print("node init name ",name)
        pass
    def check_sub(self):
        if len(self.nodes) >0:
            return self.nodes 
        return [None]
    def add_node(self,node):
        self.nodes.append(node)
        node.parent = self
    def add_error_node(self,node):
        self.reset_node = node
    def reset(self):
        self.state = BehaviorNode.ongoing
        pass
    def run_callback(self):
        b = self.callback()
        #print(b,b==False)
        if b is True:
            return self.success
        if b is False:
            return self.failed
        if b is None:
            return self.success
        #print(b)
        if b == self.success or b == self.ongoing or b == self.failed or b == self.error:
            return b
        # now we get an bad callback,
        print("warning:unknow callback run")
        return b
    def tick(self):
        
        print("tick node name " ,self.name)
        if self.state != self.ongoing:
            return self.state
        
        if(self.name!=""):
            print(f"{self.name} tick once ")
            
        b = self.run_callback()
        #print(self.name,b)
        #print("tick answer is",b)
        if self.state != b and b == self.success:
            for node in self.nodes:
                print(f"node {node.name} reset")
                node.reset()

        self.state = b
        while self.state is False:
            print("here")
        return b
        pass
    def next_nodes(self):
        #if self.state == BehaviorNode.ongoing:
        #    return []
        if self.state == BehaviorNode.success:
            return self.nodes #nodes is list
        if self.state == BehaviorNode.error:
            return [self.reset_node]
        return []

class ExecutionNode(BehaviorNode):
    def __init__(self):
        pass
class ControlNode(BehaviorNode):
    def __init__(self):
        pass
# 连接节点是我加的一个逻辑节点，只有二分的逻辑，连接成功和失败两个节点。 跑当前节点的callback 成功去成功的节点 失败去失败的节点；当前节点已经有过值的话会清空状态
# 但是这块逻辑有点问题 我应该要有一个node controller来做这个的逻辑管理 不然会堆栈地狱
class NodeController():
    pass
def check_tree(root):
    buffer = [root]
    i = 0
    all_success = True
    while i<len(buffer):
        node = buffer[i] 
        print(f"run node {node.name}")
        sub = node.check_sub()
        for n in sub:
            if n == None:
                print("warning: node ",node.name," is not full construct!!!!!!!!!!!!!!!!")
            else:
                if not  n in buffer:
                    buffer.append(n)
        #buffer.extend(node.check_sub()) # 我希望广度优先，因此先更新下一层，再使用tick 免得每次都有
        
        i = i+1
    print("如果你发现节点没有打印完全 或者除了最后一个节点以外 存在为完全构造的节点，请检查代码逻辑。防止树枝断裂导致代码未执行")
def run_root_node_once(root):
    buffer = [root]
    i = 0
    all_success = True
    while i<len(buffer):
        #print(f"run node{i}")
        node = buffer[i]
        print("node name is",node.name)
        #print(buffer) 
        #node->tick =>success nextnode | 
        # ongoing x | 
        # failed goback
        
        buffer.extend(node.next_nodes()) # 我希望广度优先，因此先更新下一层，再使用tick 免得每次都有
        
        if node.state == BehaviorNode.ongoing:
            all_success = False
        b = node.tick()
        i = i+1
    print("tick finish")
    print("buffer size is",len(buffer))
    print([[node.name,node.state] for node in buffer])
    return all_success
def  run_root_node(root,max_time=1500):
    import time
    ts = time.time()
    tick = 0
    
    check_tree(root)
    root.reset()# start new loop 
    while True:
        tick = tick+1
        print(f"======run tick {tick}=========")
        b = run_root_node_once(root)
        #print(b)
        if b:
            break
        print(f"timeout:{time.time()-ts}/{max_time}")
        if (time.time()-ts)>max_time:
            print(root.name," not success,timeout")
            import cfg_helper
            cfg_helper.save_img(f"{root.name}_timeout.jpg")
            break
        #root.name = f"name{i}"
        #if b :
            #print("all done")
            #root.reset()
    pass 
    print("all_tick finish")
class LinkNode(BehaviorNode):
    def __init__(self,node,name=""):
        self.success_node = None
        self.failed_node = None
        self.node = node
        self.state = BehaviorNode.ongoing
        self.name = name
        if name=="":
            self.name="ln_"+self.node.name
        print("linknode init name ",name)
    def check_sub(self):
        return [self.success_node,self.failed_node]
    def add_success(self,node):
        self.success_node = node
    def add_failed(self,node):
        self.failed_node = node
    def reset(self):
        self.state = BehaviorNode.ongoing
        #if not self.node == self:
        self.node.reset()
    def tick(self):
        ret = self.state
        print("tick in state ",ret)
        if self.state == BehaviorNode.ongoing:
            if(self.name!=""):
                print(f"{self.name} tick once ")
            ret = self.node.tick()
            print(self.node.name," tick ",ret)
            self.state = ret
            if ret == BehaviorNode.failed and self.failed_node!=None:
                self.failed_node.reset()
            elif ret == BehaviorNode.success and self.success_node!=None:
                self.success_node.reset()
        #else :
        #    if self.state == BehaviorNode.success and self.success_node!=None:
        #        ret = self.success_node.tick()
        #    elif  self.state == BehaviorNode.failed and self.failed_node!=None:
        #        ret = self.failed_node.tick()
        print("linknode ret",ret) 
        return ret
        pass
    
    def next_nodes(self):
        if self.state == BehaviorNode.ongoing:
            return []
        if self.state == BehaviorNode.success and self.success_node!=None:
            return [self.success_node]
        if self.state == BehaviorNode.failed and self.failed_node!=None:
            return [self.failed_node]
        if self.state == BehaviorNode.error and self.reset_node!=None:
            return [self.reset_node]
        return []

    pass 
# class SingleNode(BehaviorNode):
#     def __init__(self,node,name=""):
#         self.node = node
#         self.state = BehaviorNode.ongoing
#         self.name = name
#     def reset(self):
#         self.state = BehaviorNode.ongoing
#         #if not self.node == self:
#         self.node.reset()
#     def tick(self):
#         if self.state == BehaviorNode.ongoing:
#             ret = self.node.tick()
#             if ret == BehaviorNode.success and self.success_node!=None:
#                 for node in self.nodes:
#                     node.reset()
#         else :
#             if self.state == BehaviorNode.success and self.success_node!=None:
#                 ret = self.success_node.tick()
#             elif  self.state == BehaviorNode.failed and self.failed_node!=None:
#                 ret = self.failed_node.tick()
#         return ret
#         pass
#     pass
# 这个东西他没有callback 他只是维护一个顺序的逻辑 
# 单一个顺序是一个完整的节点，也就是说外面还要套一层成功和失败的方法,里面要套一整条的基础节点
class SequenceNode(ControlNode):
    def __init__(self,database={}):
        self.database = database 
        self.count = 0
        
        pass
    def reset(self):
        self.count = 0
    def tick(self):
        if(self.count < len(self.nodes)):
            state = self.nodes[self.count].tick()
            if(state == self.success):
                self.count = self.count+1
            return state
        return self.success
        pass
class FallbackNode(ControlNode):
    def __init__(self):
        pass
class PrallelNode(ControlNode):
    def __init__(self):
        pass
    def tick(self):
        for node in self.nodes:
            node.tick()
        pass
def cb():
    print("cb")
    return BehaviorNode.success

if __name__ == "__main__":
    root = BehaviorNode()
    node1 = BehaviorNode(callback=lambda :print("callback node1"))
    node2 = BehaviorNode(callback=lambda :print("callback node2"))
    
    node21 = BehaviorNode(callback=lambda :print("callback node21"))
    ln2 = LinkNode(node2)
    root.add_node(node1)
    root.add_node(ln2)
    ln2.add_success(node21)
    run_root_node(root)
    
    pass