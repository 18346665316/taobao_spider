#-*-coding:utf-8 -*-
#对taobao_spider_1.0 文件进行整理封装,注释的添加等等
from selenium import webdriver
import selenium
import json
import time
import re
from selenium.webdriver.common.action_chains import ActionChains
from multiprocessing import Process
from timeou_test import timeoutfunc
from retry import retry


class Taobao_spider():
    #对淘宝天猫进行数据爬取,全代码利用selenium,配合js代码进行实现
    def __init__(self, start_page, end_page, keywords):
        """
        对爬虫程序进行初始化
        :param start_page: 要爬取的起始页面的页数
        :param end_page: 　要爬取的结尾页面的页数,包括结尾页面的商品信息
        :param keywords: 要爬取的商品的搜索关键字
        """
        self.start_page = start_page
        self.end_page = end_page
        self.keywords = keywords
        url = 'https://login.taobao.com/member/login.jhtml?redirectURL=http://s.taobao.com/search'
        #获得一个数据保存的文件对象
        self.f = open('%s-%s.txt'%(self.start_page, self.end_page), 'a', encoding='utf-8')
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        self.driver.maximize_window()
        #建立一个页码游标
        self.page_num = self.start_page
        self.f_1 = open('taobao.txt', 'a', encoding='utf-8')
        #调用扫淘宝二维码登陆函数
        try:
            self.login_taobao()
        except:
            print('扫码超时, 退出程序')
        self.send_keywords()
    @retry(tries=3)
    def login_taobao(self):
        #堵塞相应的时间,进行淘宝扫码登陆
        print('请扫码登陆淘宝')
        time.sleep(7)
        self.input_ele = self.driver.find_element_by_xpath('//*[@id="q"]')

    def send_keywords(self):
        #传入关键字, 进行淘宝搜索
        self.input_ele.send_keys(self.keywords)
        submit_btn = self.driver.find_elements_by_class_name('icon-btn-search')[0]
        submit_btn.click()

    def get_goods_count(self):
        #获取列表页商品数量
        print('获取列表页商品数量')
        goods_count = self.driver.find_elements_by_xpath("//img[@class='J_ItemPic img']").__len__()
        return [i for i in range(goods_count)]

    # def get_detail_page(self, goods_list):
    #     #进入详情页面, 对详情页面数据进行解析
    #     print('进入get_detail_page函数')
    #     # 创立一个列表,为了对timeout时间内加载未成功的页面进行重新加载
    #     goods_load_failed_list = list()
    #     origin_window = self.driver.current_window_handle
    #     for goods in goods_list[:10]:
    #         #遍历点击列表页面的每个商品
    #         self.driver.execute_script('document.getElementsByClassName("J_ItemPic img")[%s].click()' % goods)
    #         #获取当前浏览器所有打开的窗口列表
    #         handles = self.driver.window_handles
    #         #origin_window列表页面的窗口
    #         for i in handles:
    #             #进行判断是否为详情页面
    #             if i != origin_window:
    #                 print('切换窗口')
    #                 #把webdriver 切换到详情页面
    #                 self.driver.switch_to.window(i)
    #                 print('进入加载页面')
    #                 pythoncode = 'self.driver.page_source'
    #                 #调用超时函数
    #                 text = timeoutfunc(10, pythoncode, self)
    #                 if text:
    #                     # 页面正常时间内加载成功
    #                     print('加载完毕')
    #                    #调用数据解析提取函数进行数据的解析提取
    #                     self.parse_page(text)
    #                     #提取成功关闭当前窗口
    #                     self.driver.close()
    #                 else:
    #                     print('加载失败')
    #                     #timeout 时间内加载未完成,将商品序号加入到失败的队列
    #                     goods_load_failed_list.append(goods)
    #                     self.driver.close()
    #                     print('成功关闭')
    #         self.driver.switch_to.window(origin_window)
    #     self.get_detail_page(goods_load_failed_list)
    def get_detail_page(self, goods_list):
        #进入详情页面, 对详情页面数据进行解析
        print('进入get_detail_page函数')
        # 创立一个列表,为了对timeout时间内加载未成功的页面进行重新加载
        goods_load_failed_list = list()
        origin_window = self.driver.current_window_handle
        for goods in goods_list[:10]:
            #遍历点击列表页面的每个商品
            self.driver.execute_script('document.getElementsByClassName("J_ItemPic img")[%s].click()' % goods)
            #获取当前浏览器所有打开的窗口列表
            handles = self.driver.window_handles
            #origin_window列表页面的窗口
            for i in handles:
                #进行判断是否为详情页面
                if i != origin_window:
                    print('切换窗口')
                    #把webdriver 切换到详情页面
                    self.driver.switch_to.window(i)
                    print('进入加载页面')
                    pythoncode = 'self.driver.page_source'
                    #调用超时函数driver.stop_client()
                    text = timeoutfunc(7, pythoncode, self)
                    if text:
                        # 页面正常时间内加载成功
                        print('加载完毕')
                       #调用数据解析提取函数进行数据的解析提取
                        self.parse_page(text)
                        #提取成功关闭当前窗口
                        self.driver.close()
                    else:
                        print('加载失败')
                        #timeout 时间内加载未完成,将商品序号加入到失败的队列
                        goods_load_failed_list.append(goods)
                        self.driver.close()
                        # time.sleep(1)

                        print('成功关闭')
            self.driver.switch_to.window(origin_window)
        if goods_load_failed_list != []:
            self.get_detail_page(goods_load_failed_list)
    def parse_page(self, text):
        print('进去解析页面parse_page')
        json_text = re.search(r"TShop.Setup\(([^\<]*)", text, re.S)
        #判断是否符合正则, 符合则该商品属于天猫商城商品,反之为淘宝商城商品
        if json_text is None:
            # raise Exception('正则匹配错误, 页面为淘宝页面')
            print('页面为淘宝页面')
            return
        json_text = json_text.group(1)[:-6].strip()[:-2].strip()
        #将匹配到的json转换为python的字典
        dict_new = json.loads(json_text)
        #调用函数获取到需要的data
        parse_data = self.get_discount_price(dict_new)
        print(parse_data, file=self.f)

    def get_discount_price(self, dict_new):
        # 以下代码为获取促销价格
        #定义sign, 用来判断商品是否有促销价, 不同的sku之间价格是否会发生变化, 页面是否有隐藏商品.判断每个ｓｋｕ是否需要点击
        have_discount = True
        is_pricechange_of_spu = True
        is_all_show = True
        should_click = True
        # 第一次进入详情页面展示出来的促销价格, 少数商品并没有促销价, 只有价格一栏, 但要考虑页面隐藏商品
        if self.driver.find_element_by_id('J_PromoPrice').get_attribute('style'):# == 'display: none;'

            # js_python = 'print()'
            # price_all = '原价'
            have_discount = False
            price_all = self.driver.find_element_by_xpath("//dl[@id='J_StrPriceModBox']//span").text
        else:
            #促销价js延迟加载问题, 有待解决, 可利用超时函数
            #todo
            try:
                price_all = self.driver.find_element_by_xpath('//div[@class="tm-promo-price"]//span[1]').text
            except:
                time.sleep(1)
                price_all = self.driver.find_element_by_xpath('//div[@class="tm-promo-price"]//span[1]').text
            #判断价格是否有变动
            if '-' not in self.driver.find_element_by_xpath('//div[@class="tm-promo-price"]//span[1]').text:
                    # js_python = 'print()'
                is_pricechange_of_spu = False
            else:
                # js_python = """action.move_to_element(self.driver.find_element_by_partial_link_text('立即购买')).perform()"""
                is_pricechange_of_spu = True
        #获取所有图片标签,包括隐藏
        li_xpath_str = '//ul[@class="tm-clear J_TSaleProp tb-img"]//li'
        li_ele_list = self.driver.find_elements_by_xpath(li_xpath_str)
        #showif标识是否全部商品全都在页面上展示了出来
        # show_if = True
        # should_click = True
        for li_ele in li_ele_list:
            if li_ele.get_attribute('@class') == 'tb-out-of-stock':
                is_all_show = False
        # if js_python == 'print()' and show_if:
            #标识是否符合跳过点击的商品
        if (is_all_show and is_pricechange_of_spu==False) or (is_all_show and have_discount==False):
            should_click = False

        for key_demo in dict_new["propertyPics"].keys():
            print(key_demo)
            if key_demo != "default":
                #1,商品全部展示, 并且有促销价格, 但是促销价没发生变化,2, 商品全部展示,无促销价
                if should_click == False:
                    dict_new["propertyPics"][key_demo].append({'discount_price': price_all, 'on_sale':'true'})
                    print(price_all)
                    continue
                #获取style编码
                key = key_demo.strip(';')
                #用js进行遍历,从而进行点击
                js = """
                alist = document.querySelectorAll("li[data-value]");
                for(i=0;i<alist.length;i++){
                    if(alist[i].getAttribute('data-value')=='%s')
                        {alist[i].children[0].click()}
                        }
                """ % key
                #商品没有在页面上进行展示的情况,商品没有促销价
                if self.driver.find_element_by_xpath('//li[@data-value="%s"]'%key).get_attribute('class') == 'tb-out-of-stock':
                    dict_new["propertyPics"][key_demo].append({'discount_price': '','on_sale':'false'})
                    continue
                self.driver.execute_script(js)
                discount_price = self.driver.find_element_by_xpath(
                    '//div[@class="tm-promo-price"]/span[1]').text
                dict_new["propertyPics"][key_demo].append({'discount_price':discount_price,'on_sale':'true'})
                print(discount_price)
        text = json.dumps(dict_new)
        return text

    def start(self):
        #对页码进行遍历, 获取每一页的商品数量,并调用解析函数＜＜＜
        self.driver.set_page_load_timeout(8)
        for i in range(self.start_page, self.end_page+1):
            print('跳转到第', i, '页')
            input_ele = self.driver.find_element_by_xpath('//input[@aria-label="页码输入框"]')
            input_ele.clear()
            input_ele.send_keys(str(i))
            js_submit = "var q = document.getElementsByClassName('J_Submit')[0];q.click()"
            self.driver.execute_script(js_submit)
            goods_list = self.get_goods_count()
            self.get_detail_page(goods_list=goods_list)

    def run(self):
        print('run')
        self.start()

def run_spider(start_page, end_page):
    tao_spider = Taobao_spider(start_page, end_page, keywords='T恤')
    try:
        tao_spider.run()
    except selenium.common.exceptions.TimeoutException:
        print('页面加载超时')

def main():
    run_spider(5,6)

if __name__ == '__main__':
    main()
