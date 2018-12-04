#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/26 15:29
# @Author  : blvin.Don
# @File    : v1.py

import time
import re
import json
import requests
import collections
from selenium import webdriver
from bs4 import BeautifulSoup
from aip import AipNlp
from Weibo.Crawler import Function
# import WeiboSpoder.Spider.DataBase_sp
# import WeiboSpoder.Spider.Function
browser = webdriver.Firefox()

#登录微博
def Login():
    browser.get("https://passport.weibo.cn/signin/login")
    time.sleep(30)

#得到转发和评论次数
def Get_tran_and_comm(Str):
    comm = tran = 0
    try:
        if re.findall(r'评论\[\d+\]', Str)[0][3:-1]:
            comm = int(re.findall(r'评论\[\d+\]', Str)[0][3:-1])
        if re.findall(r'转发\[\d+\]', Str)[0][3:-1]:
            tran = int(re.findall(r'转发\[\d+\]', Str)[0][3:-1])
    except:
        pass
    return comm,tran

#得到时间特征
def Get_time_features(n_time):
    b = collections.Counter(n_time)
    count = set(x for x in n_time if b[x] >= 2)
    return len(count)

#Reputation值
def Get_Reputation(no_atten,no_fans):
    #拉普拉斯平滑
    return no_fans/(no_atten+no_fans+1)

#计算文本相似度
def Get_weibo_sim(weibo):
    """ 你的 APPID AK SK """
    APP_ID = '11286782'
    API_KEY = 'LGUPoiUYz8qvTISDa0gFySyl'
    SECRET_KEY = 'GVEOrDHC8Fie9IfNXL3v6Vxzwu2T7aGd'
    client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
    """ 如果有可选参数 """
    options = {}
    options["model"] = "CNN"
    """ 带参数调用短文本相似度 """
    sim = 0
    count = 0
    if len(weibo)>1:
        for i in range(0, len(weibo)):
            for j in range(i + 1, len(weibo)):
                try:
                    # print(client.simnet(str(weibo[i]), str(weibo[j]), options))
                    sim = sim + client.simnet(str(weibo[i]), str(weibo[j]), options)['score']
                    count = count + 1
                except:
                    pass
        return sim /(count+1)
    else:
        return 0
#获取所有粉丝
def Get_fans(id):
    page = 1
    fans_list = set()
    while page <= 20:
        try:
            r = requests.get(
                'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_' +
                str(id) + '&type=all&since_id=' + str(page))
            # print(json.loads(r.text))
            if json.loads(r.text)['ok'] == 1:
                temp = re.findall(r'"id":\d{10}',str(r.text))
                # print(temp)
                for i in temp:
                    fans_list.add(i[5:])
            else:
                return fans_list
        except:
            pass
        page = page + 1
    return fans_list


#粉丝列表
def Get_fans_list(id):
    page = 1
    fans_list = set()
    while page <= 10:
        try:
            r = requests.get(
                'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_' +
                str(id) + '&type=all&since_id=' + str(page))
            # print(json.loads(r.text))
            if json.loads(r.text)['ok'] == 1:
                temp = re.findall(r'"id":\d{10}',str(r.text))
                # print(temp)
                for i in temp:
                    fans_list.add(i[5:])
            else:
                return fans_list
        except:
            pass
        page = page + 1
    return fans_list


#获取关注列表
def Get_atten_list(id):
    page = 1
    atten_list = set()
    browser.get('https://weibo.cn/'+str(id)+'/follow?page='+str(page))
    time.sleep(1)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    temp = soup.find_all('div',{'class':'pa'})
    # print(temp[0].get_text())
    if len(temp)==0:
        n_page = 1
    else:
        n_page = re.findall('/\d+',str(temp[0].get_text()))[0][1:]
    # print(n_page)
    for i in re.findall(r'<a href="https://weibo.cn/u/\d{10}"',str(soup)):
        atten_list.add(i[-11:-1])
    while (page < int(n_page)) & (page <= 9):
        browser.get('https://weibo.cn/' + str(id) + '/follow?page=' + str(page+1))
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        for i in re.findall(r'<a href="https://weibo.cn/u/\d{10}"', str(soup)):
            atten_list.add(i[-11:-1])
        page = page+1
        time.sleep(1)
    return atten_list

#计算特征
def Get_feature(User_ID):
    print("用户"+str(User_ID)+"的特征:")
    browser.get("https://weibo.cn/u/"+str(User_ID))
    weibo = []
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    #获取关注数
    n_Attent = re.findall(r'关注\[\d+\]',str(soup))[0][3:-1]
    #获取粉丝数
    n_fans = re.findall(r'粉丝\[\d+\]',str(soup))[0][3:-1]

    #获取第一页的信息
    n_digit = n_symbol = 0
    # 链接数
    n_link = str(soup).count("http://")
    n_ment = str(soup).count("@")
    n_PC = str(soup).count("来自微博 weibo.com")
    #转发的微博数
    n_tran = int(len(soup.find_all('span',attrs={'class':'cmt'}))/3)
    #微博ID和时间统计信息
    n_time = []
    #转发量和转发量
    Comm = Tran = 0
    for s in soup.find_all('div',{'class':'c'}):
        Comm = Comm+Get_tran_and_comm(str(s))[0]
        Tran = Tran+Get_tran_and_comm(str(s))[1]
    for i in soup.find_all('span',attrs={'class':'ctt'})[1:]:
        #数字个数
        n_digit = n_digit+len(re.sub("\D", "", i.get_text()))
        cont = re.compile(u"[\u4e00-\u9fa5]").findall(i.get_text())
        if cont:
            weibo.append(''.join(cont))
        n_symbol = len(i.get_text())-n_digit-len(''.join(cont))
    #统计时间信息
    for c in soup.find_all('span',attrs={'class':'ct'}):
        s = re.findall(r'20\d{2}-\d{2}-\d{2} \d{2}:\d{2}', str(c))
        if s:
            n_time.append(s[0])
    # print("关注数：", n_Attent, "粉丝数：", n_fans,"链接数:",n_link,"@次数：",n_ment,n_PC ,n_tran,Comm,Tran,n_time,n_symbol)
    #当前第1页面
    current_page = 1
    # #获取总的微博页数
    try:
        n_page = int(soup.find_all(id="pagelist")[0].get_text().split('/')[1][:-1])
    except:
        n_page = 0

    # 当i<总页数并且i<20时，翻页
    if Function.is_number(n_page):
        n_page = n_page
    else:
        n_page = 1
    # print("微博页数：", n_page)
    while (current_page > 0)&(current_page < int(n_page))&(current_page < 10):
        browser.get("https://weibo.cn/u/"+str(User_ID)+"?page="+str(current_page+1))
        soup_new = BeautifulSoup(browser.page_source, 'html.parser')
        n_link = n_link + str(soup_new).count("http://")
        n_ment = n_ment+str(soup_new).count("@")
        n_PC = n_PC + str(soup_new).count("来自微博 weibo.com")
        n_tran = n_tran+int(len(soup_new.find_all('span', attrs={'class': 'cmt'})) / 3)
        for s in soup_new.find_all('div', {'class': 'c'}):
            Comm = Comm + Get_tran_and_comm(str(s))[0]
            Tran = Tran + Get_tran_and_comm(str(s))[1]
        for i in soup_new.find_all('span', attrs={'class': 'ctt'})[1:]:
            n_digit = n_digit + len(re.sub("\D", "", i.get_text()))
            cont = re.compile(u"[\u4e00-\u9fa5]").findall(i.get_text())
            if cont:
                weibo.append(''.join(cont))
            n_symbol = n_symbol+len(i.get_text())-len(re.sub("\D", "", i.get_text()))-len(''.join(cont))
        for m in soup_new.find_all('span', attrs={'class': 'ct'}):
            s = re.findall(r'20\d{2}-\d{2}-\d{2} \d{2}:\d{2}', str(m))
            if s:
                n_time.append(s[0])
        current_page = current_page + 1
        time.sleep(0.1)

    #     current_page = int(re.sub("\D", "", soup.find_all(id="pagelist")[0].get_text().split('/')[0]))
    ave_URl = round(n_link/(len(weibo)+1),2)
    # print("平均链接数：",ave_URl)
    tran_rate = round(n_tran/(len(weibo)+1),2)
    # print("转发的微博占比：",tran_rate)
    # print("微博内容：",weibo)
    ave_comm = round(Comm/(len(weibo)+1),2)
    # print("平均评论量：",ave_comm)
    ave_tran = round(Tran/(len(weibo)+1),2)
    # print("平均被转发次数：",ave_tran)
    ave_digit = round(n_digit/(len(weibo)+1),2)
    # print("平均数字个数：", ave_digit)
    ave_ment = round(n_ment/(len(weibo)+1),2)
    # print("平均@次数：",ave_ment)
    ave_symbol = round(n_symbol/(len(weibo)+1),2)
    # print("平均符号个数：",ave_symbol)
    PC_rate = round(n_PC/(len(weibo)+1),2)
    # print("PC端发博占比:",PC_rate)
    minute2 = Get_time_features(n_time)
    # print("每分钟发微博超过2次的次数:",minute2)
    reputation = round(Get_Reputation(int(n_Attent),int(n_fans)),2)
    # print("Reputation值:",reputation)
    sim = round(Get_weibo_sim(weibo[:int(len(weibo)%10)]),2)
    # print("文本相似度：",sim)
    fans = Get_fans_list(User_ID)
    # print("粉丝列表：",fans)
    atten = Get_atten_list(User_ID)
    # print("关注列表：",atten)
    no_fans = len(fans)
    no_atten = len(atten)
    no_mutual = len(fans.intersection(atten))
    mutual_rate = round(no_mutual/(no_fans+no_atten-no_mutual),2)
    # print("互粉率：",mutual_rate)
    # print(weibo)
    print(sim,ave_URl,ave_tran,ave_comm,ave_digit,ave_symbol,reputation,mutual_rate,tran_rate,ave_ment,PC_rate,minute2)
    return sim,ave_URl,ave_tran,ave_comm,ave_digit,ave_symbol,reputation,mutual_rate,tran_rate,ave_ment,PC_rate,minute2

#获取恶意用户列表
def Get_id(keyword):
    browser.get('https://weibo.cn/search/')
    browser.find_element_by_xpath('/html/body/div[4]/form/div/input[1]').send_keys(keyword)
    time.sleep(2)
    browser.find_element_by_xpath('/html/body/div[4]/form/div/input[3]').click()
    time.sleep(2)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    temp = re.findall('<input name="uidList" type="hidden" value=(.*?)>',str(soup))
    uid_list = eval(temp[0]).split(',')
    # print("关键词为：",keyword,"的恶意用户为：",uid_list)
    return uid_list


if __name__ == '__main__':
    #登录微博
    # 18297995545
    # xiuqin999
    Login()
    ID = Get_fans_list(3938430772)
    print(3938430772,"的粉丝为：",ID)
    for id in ID:
        Get_feature(int(id))



