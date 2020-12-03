# -*- coding:UTF-8 -*-
"""
轮询组合内的基金，获取基金的消息
以行为单位，存储基金内容
"""
from IOFile import read_group_fund_json, read_chenxingcode_json
from FundParameterInfo import FundInfo

if __name__ == '__main__':
    fund_list = []
    group_fund_info = read_group_fund_json()  # 获取组合基金信息
    chenxing_code = read_chenxingcode_json()  # 获取晨星编码
    for index in range(len(group_fund_info)):
        each_fund = FundInfo(group_fund_info[index]["ID"], group_fund_info[index]["name"],
                             chenxing_code[group_fund_info[index]["ID"]])
        # 从天天基金网上更新信息
        each_fund.update_fund_info_by_tiantian()
        # 从晨星网上更新信息
        each_fund.update_fund_info_by_chenxing()
        fund_list.append(each_fund)
    #  将信息写入文件
    result_dir = '../output/'
    output_head = '代码' + ',' + '规模' + ',' + '基龄' + ',' + '3月回撤' + ',' + '标准差' + ',' + '风险系数' + ',' + '夏普比' + ',' + \
                  '阿尔法' + ',' + '贝塔' + ',' + 'R平方' + ',' + '股仓' + ',' + '债仓' + ',' + '十股' + ',' + '五债' + '\n'
    with open(result_dir + 'fund_info.csv', 'w') as csv_file:
        csv_file.write(output_head)
        for fund_index in fund_list:
            output_line = fund_index.fund_code + fund_index.fund_name + ',' + \
                          str(fund_index.fund_size) + ',' + \
                          fund_index.established_date + ',' + \
                          str(fund_index.three_month_retracement) + ',' + \
                          str(fund_index.risk_assessment["standard_deviation"]) + ',' + \
                          str(fund_index.risk_assessment["risk_coefficient"]) + ',' + \
                          str(fund_index.risk_assessment["sharpby"]) + ',' + \
                          str(fund_index.risk_statistics["alpha"]) + ',' +\
                          str(fund_index.risk_statistics["beta"]) + ',' + \
                          str(fund_index.risk_statistics["r_square"]) + ',' + \
                          str(fund_index.stock_total_position["stock_total_position"]) + ',' + \
                          str(fund_index.bond_total_position["bond_total_position"]) + ',' + \
                          str(fund_index.stock_total_position["ten_stock_position"]) + ',' + \
                          str(fund_index.bond_total_position["five_bond_position"]) + '\n'
            csv_file.write(output_line)
