#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 导入Python自带的HTMLParser解析器模块,可以解析html网页内容
from html.parser import HTMLParser
# 导入request模块
from urllib import request
from urllib import error
import sys
import re


# import weather3

# 自定义类,继承HTMLParser
class MyHTMLParser1(HTMLParser):
    def __init__(self):
        self.flag = 0  # 类变量作为指针定位要获取内容的位置
        self.bflag = 0  # 类变量作为指针定位要获取内容的位置
        self.is_get_data = 0  # 类变量用来计数共有基础标签内容
        self.res = []
        super().__init__()

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for attr in attrs:
                if attr[1] == 'left':
                    if self.flag == 0:
                        self.flag = 1

        if tag == 'h2' and self.flag == 1:
            self.is_get_data += 1
        if tag == 'h5' and self.flag == 1:
            self.is_get_data += 1
        if tag == 'h6' and self.flag == 1:
            self.is_get_data += 1

        if tag == 'dd' and self.flag == 1:
            for attr in attrs:
                if attr[1] == 'week':
                    self.is_get_data += 1
                elif attr[1] == 'shidu':
                    self.bflag += 1
        if tag == 'span' and self.flag == 1:
            self.bflag = 1
            self.is_get_data += 1

        if (tag == 'b' or tag == 'br') and self.bflag == 1 and self.flag == 1:
            self.is_get_data += 1

    def handle_endtag(self, tag):
        if tag == 'div' and self.flag == 1:
            self.flag = -1
            self.is_get_data = 0

        if (tag == 'span' or tag == 'dd') and self.flag == 1:
            self.bflag = 0

    def handle_data(self, data):
        if self.is_get_data > 0 and self.flag == 1:
            self.is_get_data -= 1
            self.res.append(data)


def weather_info(addr):
    weather_url = 'http://www.tianqi.com/{}/'.format(addr)
    try:
        with request.urlopen(weather_url) as f:
            data = f.read().decode()
        parser1 = MyHTMLParser1()
        parser1.feed(data)
        msg = ''
        for line in parser1.res:
            if (line == '南京' and addr != 'nanjing') \
                    or (line == '宿迁' and addr != 'suqian'):
                return '请输入正确的中国城市名拼音!'
                # break
            msg += '{}\n'.format(line)
        return msg

    except request.URLError:
        # print('网络异常或页面未找到')
        return '网络异常或页面未找到'
    except error.HTTPError:
        return '网络异常或页面未找到'

# if __name__ == '__main__':
#     main()
