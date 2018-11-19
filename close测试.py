from selenium import webdriver
from threading import Thread
driver = webdriver.Chrome()
# driver.set_page_load_timeout(3)
def a1(driver):
    print('a1')
    try:
        driver.get('https://chrome.google.com/webstore?utm_source=chrome-ntp-icon')
    except:
        pass

def a2(driver):
    print('a2')
    print(driver.title)
    # driver.stop_client()
    import time
    time.sleep(1)
    driver.stop_client()
    js = 'window.stop()'
    driver.execute_script(js)
    driver.close()
    import time
    time.sleep(3)
    driver.get('http://www.baidu.com')
    print('百度加载完成')
    time.sleep(10)
    # driver.close()
t1 = Thread(target=a1, args=(driver,))
t2 = Thread(target=a2, args=(driver,))
t1.setDaemon(True)
t1.start()
t2.start()
print('推出')
