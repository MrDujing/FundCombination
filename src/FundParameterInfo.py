# -*- coding:UTF-8 -*-

"""
负责记录基金的参数信息：
基金代码、基金名称、基金规模、成立日期、基金评级、最差3月回报、
标准差、风险系数、夏普比、阿尔法、贝塔、R平方、持仓信息
"""
import re
from time import sleep
from IOFile import crawl_html
from bs4 import BeautifulSoup


class FundInfo:
    # 初始化定义，利用基金代码、基金名称进行唯一化
    def __init__(self, code, name, namecode):
        self.fund_code = code  # 基金代码，需要初始化赋值
        self.fund_name = name  # 基金名称，需要初始化赋值
        self.fund_chenxing_code = namecode #基金编码，晨星网特有，需要建立索引表

        # 通过天天基金网获取
        self.fund_size = 0.0  # 基金规模
        self.established_date = ""  # 成立日期
        self.bond_position_propotion = dict()  # 债券仓位占比，通过updatePositionInfoByTianTian(self)获取
        self.stock_position_proportion = dict()  # 股票仓位占比，通过updatePositionInfoByTianTian(self)获取

        # 通过晨星网获取
        self.three_month_retracement = 0.0  # 三个月最大回撤
        self.bond_total_position = dict()  # 债券总仓位、前五大持仓
        self.stock_total_position = dict()  # 股票总仓位、前十大持仓
        self.risk_assessment = dict()  # 标准差 风险系数 夏普比
        self.risk_statistics = dict()  # 阿尔法 贝塔 R平方值

        # 暂时不管
        self.institution_propotion = 0.0  # 机构持仓占比， 无法获取
        self.morningstar_evaluation = ""  # 晨星评级，选择前两年， 无法获取
        self.updateDate = None  # 获取当前更新的时间

    # 抓取十大股票持仓、五大债券持仓
    def update_position_info_by_tiantian(self):
        html_dir = '../input/'
        fund_html = self.fund_name + '_' + self.fund_code + '.html'

        from os.path import exists
        if not exists(html_dir + fund_html):
            print("fund html is not exist, we create")
            crawl_html()
        import time
        import os
        time_distance = time.time() - os.stat(html_dir + fund_html).st_mtime
        if time_distance > 3600 * 12:
            print("fund html is expired, we create")
            crawl_html()

        fund_html_file = open(html_dir + fund_html, 'r', encoding='utf-8')
        fund_html_handle = fund_html_file.read()
        fund_soup = BeautifulSoup(fund_html_handle, 'lxml')
        # 获取股票持仓所在的表,填入stock_position_proportion中
        stock_table = fund_soup.findAll("table", {"class": "ui-table-hover"})[0]
        for tr_stock in stock_table.findAll("tr"):
            td_stock = tr_stock.findAll("td")
            if len(td_stock) == 4:
                stock_proportion = re.findall(r"\d+\.?\d*", td_stock[1].getText())
                stock_name = td_stock[0].getText().strip()
                self.stock_position_proportion[''.join(stock_name.split())] = float(stock_proportion.pop(0)) / 100

        # 获取债券持仓所在的表,填入bond_position_propotion
        bond_table = fund_soup.findAll("table", {"class": "ui-table-hover"})[1]
        for tr_bond in bond_table.findAll("tr"):
            td_bond = tr_bond.findAll("td")
            if len(td_bond) == 3:
                bond_proportion_ = re.findall(r"\d+\.?\d*", td_bond[1].getText())
                bond_name = td_bond[0].getText().strip()
                self.bond_position_propotion[''.join(bond_name.split())] = float(bond_proportion_.pop(0)) / 100

    # 更新基金信息，从天天网上抓取，利用html解析原理
    def update_fund_info_by_tiantian(self):
        html_dir = '../input/'
        fund_html = self.fund_name + '_' + self.fund_code + '.html'

        from os.path import exists
        if not exists(html_dir + fund_html):
            print("fund html is not exist, we create")
            crawl_html()
        import time
        import os
        time_distance = time.time() - os.stat(html_dir + fund_html).st_mtime
        if time_distance > 3600 * 12:
            print("fund html is expired, we create")
            crawl_html()

        fund_html_file = open(html_dir + fund_html, 'r', encoding='utf-8')
        fund_html_handle = fund_html_file.read()
        fund_soup = BeautifulSoup(fund_html_handle, 'lxml')
        fund_info_div = fund_soup.findAll("div", {"class": "infoOfFund"})[0]
        # 获取基金规模信息
        fund_size_text = fund_info_div.findAll("td")[1].text
        self.fund_size = re.findall(r"\d+\.?\d*", fund_size_text).pop(0)
        # 提取基金成立日期
        established_date_text = fund_info_div.findAll("td")[3].text
        self.established_date = re.findall(r'\d{4}-\d{2}-\d{2}', established_date_text).pop(0)

    # 更新基金信息，从晨星网上抓取，利用selinum原理
    def update_fund_info_by_chenxing(self):
        from selenium import webdriver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_driver = webdriver.Chrome(options=chrome_options)
        chenxing_fund_url = "http://cn.morningstar.com/quicktake/" + self.fund_chenxing_code
        """
        利用driver加载基金网页，此处应该输入用户名密码
        需要把密码输入移至最外层，只输一次密码
        """
        chenxing_cookies = ""
        if chenxing_cookies == "":
            chrome_driver.get(chenxing_fund_url)
            username = chrome_driver.find_element_by_id('emailTxt')
            password = chrome_driver.find_element_by_id('pwdValue')
            username.send_keys('*******@*****.com')
            password.send_keys('*******')
            submit = chrome_driver.find_element_by_id('loginGo')
            submit.click()
            sleep(3)
            # 获取网站cookie
            chenxing_cookies = chrome_driver.get_cookies()
        else:
            chrome_driver.get(chenxing_fund_url)
        # 获取基金三个月内的最大回撤
        sleep(3)
        self.three_month_retracement = float(chrome_driver.find_element_by_id("qt_worst").find_element_by_class_name("r3").text)
        # 获取股票总仓位、前十大持仓、债券总仓位、前五大持仓
        sleep(3)
        self.stock_total_position["stock_total_position"] = float(chrome_driver.find_element_by_class_name("stock").text) / 100  # 股票的总仓位
        sleep(3)
        self.bond_total_position["bond_total_position"] = float(chrome_driver.find_element_by_class_name("bonds").text) / 100  # 债券的总仓位
        sleep(3)
        self.stock_total_position["ten_stock_position"] = float(re.findall(r"\d+\.?\d*", chrome_driver.find_element_by_id("qt_stocktab").text).pop(0)) / 100 # 十大股票仓位
        sleep(3)
        self.bond_total_position["five_bond_position"] = float(re.findall(r"\d+\.?\d*", chrome_driver.find_element_by_id("qt_bondstab").text).pop(0)) / 100 # 五大债券仓位
        # 获取标准差
        sleep(3)
        standard_deviation = chrome_driver.find_element_by_id("qt_risk").find_elements_by_xpath('li').pop(15).text
        if standard_deviation != "-":
            standard_deviation = float(standard_deviation)
        self.risk_assessment["standard_deviation"] = standard_deviation
        # 获取风险系数
        sleep(3)
        risk_coefficient = chrome_driver.find_element_by_id("qt_risk").find_elements_by_xpath('li').pop(22).text
        if risk_coefficient != "-":
            risk_coefficient = float(risk_coefficient)
        self.risk_assessment["risk_coefficient"] = risk_coefficient
        # 获取夏普比
        sleep(3)
        sharpby = chrome_driver.find_element_by_id("qt_risk").find_elements_by_xpath('li').pop(29).text
        if sharpby != "-":
            sharpby = float(sharpby)
        self.risk_assessment["sharpby"] = sharpby
        # 获取阿尔法
        sleep(3)
        alpha = chrome_driver.find_element_by_id("qt_riskstats").find_elements_by_xpath('li').pop(4).text
        if alpha != "-":
            alpha = float(alpha)
        self.risk_statistics["alpha"] = alpha
        # 获取贝塔
        sleep(3)
        beta = chrome_driver.find_element_by_id("qt_riskstats").find_elements_by_xpath('li').pop(7).text
        if beta != "-":
            beta = float(beta)
        self.risk_statistics["beta"] = beta
        # 获取R平方
        sleep(3)
        r_square = chrome_driver.find_element_by_id("qt_riskstats").find_elements_by_xpath('li').pop(10).text
        if r_square != "-":
            r_square = float(r_square)
        self.risk_statistics["r_square"] = r_square
