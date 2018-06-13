# -*- coding: utf-8 -*-

"""
    作者:     Robin
    版本:     1.0
    日期:     2018/05
    文件名:    main.py
    功能：     主程序

    实战案例2：客户消费数据分析
    任务：
        - 1. 比较各国家的客户数
        - 2. 比较各国家的成交额
        - 3. 统计各国家交易记录的趋势

    数据集来源： https://archive.ics.uci.edu/ml/datasets/Online%20Retail


"""

import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

RAW_DATA_FILE = './data/online_retail.xlsx'
CLN_DATA_FILE = './output/cln_online_retail.csv'


def inspect_data(data_df):
    """
        查看数据集信息

        参数：
            - data_df:  DataFrame数据
    """
    print('数据集基本信息')
    print(data_df.info())

    print('\n数据集统计信息')
    print(data_df.describe())

    print('\n数据集预览')
    print(data_df.head())


def clean_data(data_df):
    """
        数据清洗，包括去除空记录，去除重复记录

        参数：
            - data_df:  DataFrame数据

        返回：
            - cln_data_df:  清洗后的数据
    """
    # 去除空记录后的数据
    non_empty_data_df = data_df.dropna()
    n_empty = data_df.shape[0] - non_empty_data_df.shape[0]

    # 去重后的记录
    cln_data_df = non_empty_data_df.drop_duplicates()
    n_duplicates = data_df.shape[0] - cln_data_df.shape[0]
    print('原始数据共有{}条记录，清洗后的数据共有{}条有效记录。（其中空记录有{}条，重复记录有{}条。）'.format(
        data_df.shape[0], cln_data_df.shape[0], n_empty, n_duplicates))

    # 保存清洗结果
    cln_data_df.to_csv(CLN_DATA_FILE, index=False, encoding='utf-8')

    return cln_data_df


def show_customer_stats(data_df):
    """
        比较各国家的客户数

        参数：
            - data_df:  DataFrame数据
    """
    customer_per_country = data_df.drop_duplicates(['CustomerID'])['Country'].value_counts()
    # 由于'United Kingdom'数据过多，所以这里只考虑其他国家
    customer_per_country_df = \
        customer_per_country[customer_per_country.index != 'United Kingdom'].to_frame().T

    # 可视化结果
    sns.barplot(data=customer_per_country_df)
    plt.xticks(rotation=90)  # 横坐标旋转角度
    plt.xlabel('Country')
    plt.ylabel('#Customers')
    plt.tight_layout()
    plt.savefig('./output/customer_per_country.png')
    plt.show()


def show_total_cost_stats(data_df):
    """
        比较各国家的成交额

        参数：
            - data_df:  DataFrame数据
    """
    # 过滤掉"取消"的交易记录，以及'United Kingdom'的数据
    cond1 = ~data_df['InvoiceNo'].str.startswith('C')
    cond2 = data_df['Country'] != 'United Kingdom'
    valid_data_df = data_df[cond1 & cond2].copy()
    valid_data_df['TotalCost'] = valid_data_df['UnitPrice'] * valid_data_df['Quantity']
    cost_per_country = valid_data_df.groupby('Country')['TotalCost'].sum()

    # 可视化结果
    cost_per_country.sort_values(ascending=False).plot(kind='bar')
    plt.ylabel('Total Cost')
    plt.tight_layout()
    plt.savefig('./output/cost_per_country.png')
    plt.show()


def show_trend_by_country(data_df):
    """
        统计各国家交易记录的趋势

        参数：
            - data_df:  DataFrame数据
    """
    countries = ['Germany', 'France', 'Spain', 'Belgium', 'Switzerland']
    data_df = data_df[data_df['Country'].isin(countries)].copy()

    data_df['InvoiceDate'] = pd.to_datetime(data_df['InvoiceDate'])
    data_df['InvoiceYear'] = data_df['InvoiceDate'].dt.year.astype(str)
    data_df['InvoiceMonth'] = data_df['InvoiceDate'].dt.month.astype(str)
    data_df['InvoiceYearMonth'] = data_df['InvoiceYear'].str.cat(data_df['InvoiceMonth'], sep='-')
    month_country_count = data_df.groupby(['InvoiceYearMonth', 'Country'])['StockCode'].count()
    month_country_count_df = month_country_count.unstack()
    month_country_count_df.index = pd.to_datetime(month_country_count_df.index).to_period('M')
    month_country_count_df.sort_index(inplace=True)

    # 可视化结果
    # 堆叠柱状图
    month_country_count_df.plot(kind='bar', stacked=True, rot=45)
    plt.xlabel('Month')
    plt.ylabel('#Transaction')
    plt.tight_layout()
    plt.savefig('./output/country_trend_stacked_bar.png')
    plt.show()

    # 热图
    sns.heatmap(month_country_count_df.T)
    plt.xlabel('Month')
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig('./output/country_trend_heatmap.png')
    plt.show()


def main():
    """
        主函数
    """
    if not os.path.exists(CLN_DATA_FILE):
        # 如果不存在清洗后的数据集，进行数据清洗
        raw_data_df = pd.read_excel(RAW_DATA_FILE, dtype={'InvoiceNo': str,
                                                          'StockCode': str,
                                                          'CustomerID': str})

        # 查看数据集信息
        inspect_data(raw_data_df)

        # 数据清洗
        cln_data_df = clean_data(raw_data_df)
    else:
        print('读取已清洗的数据')
        cln_data_df = pd.read_csv(CLN_DATA_FILE)

    # 数据分析
    # 1. 比较各国家的客户数
    show_customer_stats(cln_data_df)

    # 2. 比较各国家的成交额
    # show_total_cost_stats(cln_data_df)

    # 3. 统计各国家交易记录的趋势
    # show_trend_by_country(cln_data_df)


if __name__ == '__main__':
    main()
