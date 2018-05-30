#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 07:27:49 2017

@author: cloudsbing
"""
'''
    作者:     gangzhu
    版本:     1.0
    日期:     2018/05
    文件名:    main.py
    功能：     主程序

'''
import pandas as pd

# s = pd.Series(10, index=['a', 'b', 'c'])
s = pd.Series(10)
print(s)

# 多维，是 excel 中的表格。一列数据是收上门索引 。

# 字典类型，天剑一个新的额key

# 基本数据对象及操作
import pandas as pd

countries = ['中国', '美国', '澳大利亚']
countries_s = pd.Series(countries)
print(type(countries_s))
print(countries_s)

print(countries_s.values)

# 数组
numbers = [4, 5, 6]  # 里面为内容，自动加入索引
print(pd.Series(numbers))

# 字典
country_dicts = {'CH': '中国', 'US': '美国', 'AU': '澳大利亚'}
country_dict_s = pd.Series(country_dicts)  # 将数据的 key 和 value 对应的显示出来
print(country_dict_s)

# schema 信息，赋值给对象的方法变量,类似set方法
country_dict_s.index.name = 'Code'
country_dict_s.name = 'Country'

print(country_dict_s.index.name)
print(country_dict_s.name)

countries = ['中国', '美国', '澳大利亚', None]  # None
print(pd.Series(countries))

numbers = [4, 5, 6, None]  # NaN 数值
print(pd.Series(numbers))

country_dicts = {'CH': '中国',
                 'US': '美国',
                 'AU': '澳大利亚'}

country_dict_s = pd.Series(country_dicts)  # key value

country_dict_s
print('iloc:', country_dict_s.iloc[1])
print('iloc:', country_dict_s.loc['CH'])
print('自动:', country_dict_s['CH'])

print('iloc:\n', country_dict_s.iloc[[0, 2]])  # 左开右闭
print()
print('loc:\n', country_dict_s.loc[['US', 'AU']])  #

import numpy as np

s = pd.Series(np.random.randint(0, 1000, 10000))  # (最小，最大，长度)
print(u'向量化操作')
print(s.head())  # 默认显示前五行
print(len(s))

# dataframe
import pandas as pd

# json 数据
country1 = pd.Series({'Name': '中国',
                      'Language': 'Chinese',
                      'Area': '9.597M km2',
                      'Happiness Rank': 79})

country2 = pd.Series({'Name': '美国',
                      'Language': 'English (US)',
                      'Area': '9.834M km2',
                      'Happiness Rank': 14})

country3 = pd.Series({'Name': '澳大利亚',
                      'Language': 'English (AU)',
                      'Area': '7.692M km2',
                      'Happiness Rank': 9})

pd.DataFrame([country1, country2, country3], index=['CH', 'US', 'AU'])



