import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pyquery import PyQuery as pq
import pymongo
from config import *


# 配置MONGODB信息
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]
# 配置selenium模拟浏览器, 设置为开发者模式,防止被各大网站识别出来使用了selenium
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-automation'])
browser = webdriver.Chrome(chromedriver_location, options=options)
# 设置explicit wait time为20s, 因为微博账号登录淘宝网速度有些久
wait = WebDriverWait(browser, 20)


# 用来登录淘宝账号
def login_taobao():
    login_url = 'https://login.taobao.com/member/login.jhtml'
    # 模拟打开网页
    browser.get(login_url)
    try:
        # find weibo login button and press click
        weibo_login_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#login-form > div.login-blocks.sns-login-links > a.weibo-login'))
        )
        weibo_login_button.click()

        # input username and password
        username_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(2) > div > input'))
        )
        password_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(3) > div > input'))
        )
        login_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#pl_login_logged > div > div:nth-child(7) > div:nth-child(1) > a > span'))
        )
        username_input.send_keys(weibo_username)
        password_input.send_keys(weibo_pwd)
        login_button.click()
        print('log in taobao with weibo account...')

        # check whether the page jumps to taobao.com
        wait.until(
            EC.title_contains('淘宝网')
        )
        print('successful log in taobao')
    except TimeoutException:
        print('log in taobao timeout')
        # retry to log in
        login_taobao()


# 搜索需要的商品
def search():
    try:
        # find search box and click button
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button"))
        )
        input.send_keys(KEYWORD)
        submit.click()
        print('successful input ' + KEYWORD + ' and search...')
        # 得到总页数
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total'))
        )
        total_page_number = int(re.findall('\d+', total.text)[0])
        print('total page number is ' + str(total_page_number))
        get_products()
        return total_page_number
    except TimeoutException:
        print('can not load taobao page...')
        browser.get('https://www.taobao.com')
        search()


# 实现翻页操作
def next_page(page_number):
    # find next page input box and jump to button
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit"))
        )
        input.clear()
        input.send_keys(page_number)
        submit.click()
        print('successful jump to page No.' + str(page_number))
        # 设置等待10s使页面完全加载, 同时估计淘宝的反爬机制, 如果不设置等待时间运行到一半会中断
        time.sleep(10)
        get_products()
    except TimeoutException:
        print('next page time out')
        next_page(page_number)


# 得到商品具体信息
def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    # 初始化字符串生成PyQuery对象
    doc = pq(browser.page_source)
    # items()生成iterator迭代器
    items = doc('#mainsrp-itemlist .items .item').items()
    # 查询想要的一些信息并生成字典
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.ctx-box .row .price').text(),
            'title': item.find('.title').text(),
            'location': item.find('.location').text()
        }
        print(product)
        save_to_mongo(product)


# 存储至MongoDB数据库
def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert_one(result):
            print('save to mongodb success', result)
    except Exception:
        print('save to mongodb fail', result)


if __name__ == '__main__':
    try:
        login_taobao()
        total_page_number = search()
        for i in range(2, total_page_number+1):
            next_page(i)
        print('爬取完成')
    except Exception:
        print('爬取失败')
    finally:
        browser.close()


