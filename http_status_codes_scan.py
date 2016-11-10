#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
@Author：ysera
@博客：ysera.cc
'''

import requests
import sys
import csv
import time
import re

global start_time
global match_title
global match_url
global end_time

start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

match_url = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)  # 匹配URL

match_title = re.compile(r'<title>(.*?)</title>', re.I|re.S) # 匹配title

# 输出
def print_info(flag):
    print '------------------------------------------------------------------'
    if flag == 'banner':
        print '[+]    ' + u'HTTP-状态码-批量-扫描工具'
        print '[+]    ' + u'简单、灵活、便捷、快速、易用！'
        print '[+]    ' + u'输入文件：url_list.txt'
        print '[+]    ' + u'输出文件：http_status_codes.csv'
        print '[+]    ' + u'注：url_list.txt的每一行必须为完整的URL格式。'
        print '[+]    ' + u'如：http://ysera.cc'
        print '[+]    ' + u'@Author：ysera'
        print '[+]    ' + u'@博客：ysera.cc'
    if flag == 'result':
        print '[+]    ' + u'本次扫描网站数： ' + str(url_num) + ' 个'
        print '[+]    ' + u'开始时间： ' + start_time
        print '[+]    ' + u'结束时间： ' + end_time
        print '[+]    ' + u'注： 返回新http状态码的网站需要手工验证。'
        print '[+]    ' + u'参考：http://blog.csdn.net/tan6600/article/details/51584087'
        print '[+]    ' + u'详细信息请查看 http_status_codes.csv'
    print '------------------------------------------------------------------'

def get(url, csv_writer):
    response = requests.get(url.strip(), headers=headers, verify=False, allow_redirects=True, timeout=10)
    # 设置timeout为10，避免对某些打开缓慢的网站造成误报。可根据实际情况适当调整，该值直接决定扫描速度。

    response.encoding = 'utf-8'  # 设置response的编码为'utf-8',默认的'ISO-8859-1'解析中文title会乱码。
    title = match_title.findall(response.text)  # 正则匹配title,response.text会按指定编码自动解码
    # 少部门中文网站采用'gbk'编码，利用print解码时产生异常，改变编码方式，避免乱码。
    if title:
        try:
            print title[0]
        except UnicodeEncodeError, e:
            response.encoding = 'gbk'
            title = match_title.findall(response.text)
            if title:
                print title[0]

    if response.history:  # 处理301或302的网站
        redirect_order = ''
        # 跟踪网页的跳转情况
        for res in response.history:
            redirect_order += str(res.status_code) + ' -> '
        redirect_order += str(response.status_code)
        # 分开处理无title的网站
        if title:
            csv_writer.writerow([url.strip(), redirect_order, response.url, title[0]])
        else:
            csv_writer.writerow([url.strip(), redirect_order, response.url])
    else:  # 处理其他状态码
        # 分开处理无title的网站
        if title:
            csv_writer.writerow([url.strip(), str(response.status_code), '', title[0]])
        else:
            csv_writer.writerow([url.strip(), str(response.status_code), '', ''])

def scan(url):
    codes = file('http_status_codes.csv', 'wb')
    codes.write('\xEF\xBB\xBF')  # 确保写入csv中文不乱码
    csv_writer =csv.writer(codes)
    csv_writer.writerow([u'网址', u'状态码', u'最终着陆页', u'标题'])  # 写入excel的标题

    global url_num
    url_num = len(url)
    for i in range(0,url_num):
        print u'进度：' + str(i + 1)  + '/' + str(url_num)  # 实时输出进度

        if match_url.match(url[i]) == None:  # 先检查URL格式
            csv_writer.writerow([url[i].strip(), u'网址格式错误'])
        else:
            try:
                get(url[i], csv_writer)
            # 捕获requests.get()可能产生的多种异常
            except requests.exceptions.ConnectionError as e:
                csv_writer.writerow([url[i].strip(), u'DNS查询失败或拒绝连接'])
            except requests.exceptions.Timeout as e:
                csv_writer.writerow([url[i].strip(), u'请求超时'])
            except requests.exceptions.TooManyRedirects as e:
                csv_writer.writerow([url[i].strip(), u'请求超过最大重定向次数'])
            except requests.RequestException as e:
                csv_writer.writerow([url[i].strip(), u'未知错误'])
    codes.close()

if __name__ == '__main__':
    print_info('banner')
    time.sleep(5)
    f = open('url_list.txt', 'r')
    url = f.readlines()  # 读入待扫描的网站列表
    # 设置请求的user-agent，模拟真实访问
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0'}

    scan(url)

    end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    f.close()

    print_info('result')
