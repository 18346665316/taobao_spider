import time
from threading import Thread
def timeoutfunc(timeout, pythoncode, self):
    #一个简单的超时函数
    code = [0]
    self = self
    text = None
    code.append(text)
    def get_result_parent(self=self):
        def get_rusult(self=self):
            try:
                text = eval(pythoncode)
                code[1] = text
                code[0] = 1
            except:
                print('页面加载超时')
                return
        t1 = Thread(target=get_rusult, name='get_result')
        t1.setDaemon(True)
        t1.start()
        if code[1] != None:
            return
        for i in range(timeout):
            time.sleep(1)
            if i == (timeout-1) and code[0] == 0:
                #页面还未打开
                pass
            elif code[0] == 1:
            #页面打开成功
                return
    t2 = Thread(target=get_result_parent, )
    t2.start()
    for i in range(timeout):
        time.sleep(1)
        print('waiting loaded------', i , '秒')
        if i == (timeout - 1) and code[0] == 0:
            # 页面还未打开
            pass
        elif code[0] == 1:
            # 页面打开成功
            return code[1]