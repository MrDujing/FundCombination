# -*- coding:UTF-8 -*-
"""
轮询组合内的所有基金，
通过天天网、晨星网获取基金信息
并保存为csv文件，供分析使用
"""
from IOFile import read_group_fund_json, read_chenxingcode_json, read_stock_info_json
from FundParameterInfo import FundInfo


def manage_group_fund():
    group_position = dict()
    group_fund_info = read_group_fund_json()  # 获取组合基金信息
    chenxing_code = read_chenxingcode_json()  # 获取晨星编码
    for index in range(len(group_fund_info)):
        each_fund = FundInfo(group_fund_info[index]["ID"], group_fund_info[index]["name"],
                             chenxing_code[group_fund_info[index]["ID"]])
        each_fund.update_position_info_by_tiantian()
        # 将债券持仓 股票持仓 组成一个字典，方便遍历
        mixed_position = each_fund.stock_position_proportion.copy()
        mixed_position.update(each_fund.bond_position_propotion)
        # 获取当前持仓基金在组合内的比例
        group_proportion = group_fund_info[index]["proportion"]
        # 计算基金持仓占组合的比例
        for key in mixed_position.keys():
            if key not in group_position.keys():
                group_position[key] = group_proportion * mixed_position[key]
            else:
                group_position[key] += group_proportion * mixed_position[key]
    return group_position


if __name__ == '__main__':
    group_fund_position = manage_group_fund()
    stock_info = read_stock_info_json()
    result_dir = '../output/'
    output_head = '一级行业' + ',' + '二级行业' + ',' + '股票名称' + ',' + '持仓比例' + '\n'
    with open(result_dir + 'group_position.csv', 'w') as csv_file:
        csv_file.write(output_head)
        for stock_bond in group_fund_position.keys():
            if stock_bond in stock_info.keys():
                output_line = stock_info[stock_bond][0] + ',' + stock_info[stock_bond][1]
            else:
                output_line = 'default' + ',' + 'default'
            output_line = output_line + ',' + stock_bond + ',' + str(group_fund_position[stock_bond]) + '\n'
            csv_file.write(output_line)

