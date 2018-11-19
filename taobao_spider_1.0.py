# -*- coding:utf-8 -*-
from selenium import webdriver
import json
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from multiprocessing import Process
from timeou_test import timeoutfunc
import sys


class Taobao_spider():
    def __init__(self, start_page, end_page):
        self.start_page = start_page
        self.end_page = end_page
        url = 'https://login.taobao.com/member/login.jhtml?redirectURL=http://s.taobao.com/search'
        self.f = open('%s-%s.txt'%(self.start_page, self.end_page), 'a', encoding='utf-8')
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        self.driver.maximize_window()
        script = "(function(){ if(!window.jQuery){ var s = document.createElement('script'); s.type = 'text/javascript'; s.src = 'http://code.jquery.com/jquery-1.10.2.min.js'; document.body.appendChild(s); } } )(); "
        # js.executeScript(script);
        self.driver.execute_script(script)
        self.page_num = self.start_page
        self.f_1 = open('taobao.txt', 'a', encoding='utf-8')
        time.sleep(7)
        input_ele = self.driver.find_element_by_xpath('//*[@id="q"]')
        input_ele.send_keys('T恤')
        submit_btn = self.driver.find_elements_by_class_name('icon-btn-search')[0]
        submit_btn.click()

    def get_firstpage_good_list(self):
        goods_list = self.driver.find_elements_by_xpath("//img[@class='J_ItemPic img']")
        return goods_list

    def get_goods_list(self):
        print('get_goods_list')
        # try:
        if self.page_num == 1:
            index = 0
        else:
            index = 1
        next_page_btn = self.driver.find_elements_by_class_name("J_Pager")[index]
        action = ActionChains(self.driver)
        action.move_to_element(next_page_btn).perform()
        self.driver.execute_script('window.scrollTo(0, 0)')
        print('等待页面跳转')
        for i in range(1):
            print(i)
            time.sleep(1)
        next_page_btn = self.driver.find_elements_by_class_name("J_Pager")[index]
        next_page_btn.click()
        goods_list = self.driver.find_elements_by_xpath("//img[@class='J_ItemPic img']")
        self.page_num += 1
        return goods_list
        # except:
        #     self.driver.refresh()
        #     print('刷新页面')
        #     return self.get_goods_list()

    def get_detail_page(self, goods_list):
        print('get_detail_page')
        # try:
        for goods in range(goods_list[:20].__len__()):
            self.driver.execute_script('document.getElementsByClassName("J_ItemPic img")[%s].click()'%goods)
            handles = self.driver.window_handles
            origin_window = self.driver.current_window_handle
            for i in handles:
                if i != self.driver.current_window_handle:
                    print('切换窗口')
                    self.driver.switch_to.window(i)
                    print('进入加载页面')
                    pythoncode = 'self.driver.page_source'
                    text = timeoutfunc(10, pythoncode, self)
                    if text:
                        print('加载完毕')
                        self.parse_page(text)
                        self.driver.close()
                        if self.driver.window_handles.__len__() == 1:
                            break
                    else:
                        print('加载失败')
                        # self.driver.refresh()
                        # pythoncode = 'self.driver.page_source'
                        # text = timeoutfunc(10, pythoncode, self)

                        break
                    # try:
                    # self.parse_page(text)
                    # except Exception as e:
                    #     print(e)
                    # break
            self.driver.switch_to.window(origin_window)
        # except:
        #     self.get_detail_page(goods_list)

    def taobao_goods_parse(self, text):
        li_ele_list = self.driver.find_elements_by_xpath("//ul[@class='J_TSaleProp tb-clearfix']//li")
        span_ele_list = self.driver.find_elements_by_xpath("//ul[@class='J_TSaleProp tb-clearfix']//span")
        dict_chima = dict()
        print('提取尺码')
        if li_ele_list.__len__() != span_ele_list.__len__():
            return 0
        for i in range(li_ele_list.__len__()):
            dict_chima[li_ele_list[i].text] = span_ele_list[i].text
        str_chima = json.dumps(dict_chima)
        print(str_chima)
        print('1')
        text = re.search(r"valItemInfo      : (\{[^)]*)", text, re.S)
        print('2')
        json_text = json.dumps(text.group(1)[:-1])
        print('3')
        content = json_text[:-1] + str_chima + '}'
        print(content)
        print(content, file=self.f_1)
        print('结束')

    def parse_page(self, text):
        print('进去解析页面parse_page')
        try:
            text = re.search(r"TShop.Setup\(([^\<]*)", text, re.S)
            text = text.group(1)[:-6].strip()[:-2].strip()
        except:
            # raise Exception('正则匹配错误, 页面为淘宝页面')
            return print('正则匹配错误, 页面为淘宝页面')
        dict_new = json.loads(text)
        action = ActionChains(self.driver)
        #第一次进入详情页面展示出来的促销价格
        if self.driver.find_element_by_id('J_PromoPrice').get_attribute('style') == 'display: none;':
            js_python = 'print()'
            price_all = '原价'
        else:
            try:
                price_all = self.driver.find_element_by_xpath('//div[@class="tm-promo-price"]//span[1]').text
            except:
                time.sleep(2)
                price_all = self.driver.find_element_by_xpath('//div[@class="tm-promo-price"]//span[1]').text
            if '-' not in self.driver.find_element_by_xpath('//div[@class="tm-promo-price"]//span[1]').text:
                    js_python = 'print()'
            else:
                js_python = """action.move_to_element(self.driver.find_element_by_partial_link_text('立即购买')).perform()"""
                print('需要每次点击之前都重新定位')
        li_xpath_str = '//ul[@class="tm-clear J_TSaleProp tb-img"]//li'
        li_ele_list = self.driver.find_elements_by_xpath(li_xpath_str)
        #showif标识是否全部商品全都在页面上展示了出来
        show_if = True
        should_click = True
        for li_ele in li_ele_list:
            if li_ele.get_attribute('@class') == 'tb-out-of-stock':
                show_if = False
        if js_python == 'print()' and show_if:
            #标识是否符合跳过点击的商品
            should_click = False
        for key_demo in dict_new["propertyPics"].keys():
            print(key_demo)
            if key_demo != "default":
                if should_click == False:
                    dict_new["propertyPics"][key_demo].append({'discount_price': price_all})
                    print(price_all)
                    break
                key = key_demo.strip(';')
                #selenium实现
                # xpath_str = '//li[@data-value="%s"]/a' % key
                # btn = self.driver.find_element_by_xpath(xpath_str)
                # js = "document.getElementsByClassName('tm-clear J_TSaleProp tb-img')[0].getElementsByTagName('li')"
                #js实现
                # js = """$('[data-value="%s"]').children[0].click()"""% key
                js = """
                alist = document.querySelectorAll("li[data-value]");
                for(i=0;i<alist.length;i++){
                    if(alist[i].getAttribute('data-value')=='%s')
                        {alist[i].children[0].click()}
                        }
                """ % key
                if self.driver.find_element_by_xpath('//li[@data-value="%s"]'%key).get_attribute('class') == 'tb-out-of-stock':
                    dict_new["propertyPics"][key_demo].append({'discount_price': ''})
                # try:
                # eval(js_python)
                self.driver.execute_script(js)
                discount_price = self.driver.find_element_by_xpath(
                    '//div[@class="tm-promo-price"]/span[1]').text
                dict_new["propertyPics"][key_demo].append({'discount_price':discount_price})
                print(discount_price)
                # except:
                #     print('商品style点击错误')
                #     raise Exception('商品style点击错误')
        text = json.dumps(dict_new)
        print(text, file=self.f)
        # except AttributeError as e:
        #     print('正则匹配为None', '原因可能是淘宝页面')
        # except Exception as e:
        #     print(e)
        #     self.taobao_goods_parse(self.driver.page_source)

    def run(self):
        #num 为页数
        if self.start_page == 1:
            first_goods_list = self.get_firstpage_good_list()
            self.get_detail_page(goods_list=first_goods_list)
            print('第1页爬取成功')
        else:
            #跳转页面
            print('跳转到第', self.start_page, '页')
            js = 'window.scrollTo(0,document.body.scrollHeight)'
            # self.driver.execute_script(js)
            # action = ActionChains(self.driver)
            # action.move_to_element(self.driver.find_element_by_xpath('//a[@text()="掌柜热卖"'))
            # action.move_to_element(self.driver.find_element_by_xpath("//span[@class='btn J_Submit']")).perform()
            input_ele = self.driver.find_element_by_xpath('//input[@aria-label="页码输入框"]')
            input_ele.clear()
            input_ele.send_keys(str(self.start_page))
            # submit_ele = self.driver.find_element_by_xpath("//span[@class='btn J_Submit']")
            # submit_ele.click()
            js_submit = "var q = document.getElementsByClassName('J_Submit')[0];q.click()"
            # js_submit = '$(".J_Submit").click()'
            self.driver.execute_script(js_submit)
            first_goods_list = self.get_firstpage_good_list()
            self.get_detail_page(goods_list=first_goods_list)
        k = 1
        for i in range(self.start_page, self.end_page):
            k += 1
            goods_list = self.get_goods_list()
            self.get_detail_page(goods_list=goods_list)
            print('第%s页爬取成功' % k)
        self.f.close()
        print('爬取结束')
def run_spider(start_page, end_page):
    tao_spider = Taobao_spider(start_page, end_page)
    tao_spider.run()
def main():
    page_cout = 2
    for i in range(1,10,step=page_cout):
        print('新进程启动')
        p = Process(target=run_spider, args=(i, i+2))
        p.start()
        for j in range(15,1,-1):
            print('等待', j, '秒')
            time.sleep(1)
params_list = sys.argv()
run_spider(params_list[1],params_list[2])





