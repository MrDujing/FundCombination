# -*- coding:UTF-8 -*-
import json

"""
负责软件模块与本地文件的输入输出
"""


# 读取group_fund.json文件，并提取里面的信息
def read_group_fund_json(filedir='../input/', filename='group_fund.json'):
    with open(filedir+filename, 'r', encoding='utf-8') as group_fund_file:
        group_fund_info = json.load(group_fund_file)
    # 对百分比进行核验，若百分比相加不等于1，需要重新输入
    percent_sum = 0.0
    for i in range(len(group_fund_info)):
        percent_sum += group_fund_info[i]["proportion"]
    if abs(1 - percent_sum) > 0.01:
        print("fund propotion sum is not 100% and sum is :", percent_sum)
        import sys
        sys.exit()
    return group_fund_info


# 读取chenxingcode.json文件，获取代码-编码之间的索引对
def read_chenxingcode_json(filedir='../input/', filename='chenxingcode.json'):
    with open(filedir+filename, 'r', encoding='utf-8') as chenxingcode_file:
        chenxing_code_info = json.load(chenxingcode_file)
    return chenxing_code_info


# 读取stock_info.json文件，获取股票债券与行业信息的索引
def read_stock_info_json(filedir='../input/', filename='stock_info.json'):
    with open(filedir+filename, 'r', encoding='utf-8') as stock_info_file:
        stock_info = json.load(stock_info_file)
    return stock_info


# 爬取天天基金网上的网页，然后存入input中，供后期爬取上面的信息
def crawl_html():
    group_fund_info = read_group_fund_json()
    for index in range(len(group_fund_info)):
        html_dir = '../input/'
        fund_html_name = group_fund_info[index].get('name') + '_' + group_fund_info[index].get('ID') + '.html'
        # 如果存在该html文件，并且创建时间距离当前小于12小时，则不用重新创建
        from os.path import exists
        if exists(html_dir + fund_html_name):
            import time
            import os
            time_distance = time.time() - os.stat(html_dir + fund_html_name).st_ctime
            if time_distance < 3600 * 12:
                continue
        fund_url = 'http://fund.eastmoney.com/' + group_fund_info[index].get('ID') + '.html'
        from urllib.request import urlopen
        fund_html = urlopen(fund_url).read()
        with open(html_dir + fund_html_name.replace('/', '_'), "wb") as f:
            f.write(fund_html)
