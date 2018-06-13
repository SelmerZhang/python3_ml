#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 07:27:49 2017

@author: cloudsbing
"""
'''
    作者:     gangzhu
    版本:     1.0
    日期:     2018/06
    文件名:    main.py
    功能：     主程序，水果识别

'''
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.model_selection import train_test_split

#
# 1 数据加载
fruits_df = pd.read_table('data/fruit_data_with_colors.txt')
print(fruits_df.head())

# 标签 创建目录标签和名称的字典(提取两个字段放入字典中)
fruit_name_dict = dict(zip(fruits_df['fruit_label'], fruits_df['fruit_name']))
print(fruit_name_dict)

# 划分数据集
""" 
x 为特征
y 为标签
字典是对标签的解释 dim 表
"""
# X 为特征，y 为标签
X = fruits_df[['mass', 'width', 'height', 'color_score']]
y = fruits_df['fruit_label']

# 划分数据方法
"""
训练集：测试集 = 4：1
"""
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1 / 4, random_state=0)
print('数据集样本数：{}，训练集样本数：{}，测试集样本数：{}'.format(len(X), len(X_train), len(X_test)))

# 2 可视化查看特征标量(3D效果显示训练数据 标签)
# 查看数据集
sns.pairplot(data=fruits_df, hue='fruit_name', vars=['mass', 'width', 'height', 'color_score'])
plt.show()

# 3D 显示
from mpl_toolkits.mplot3d import Axes3D

# 每个 label 字段的值，赋予不同的颜色
label_color_dict = {1: 'red', 2: 'green', 3: 'blue', 4: 'yellow'}
# 为训练数据的每条数据的 特征标签 lebel 赋予颜色
colors = list(map(lambda label: label_color_dict[label], y_train))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(X_train['width'], X_train['height'], X_train['color_score'], c=colors, marker='o', s=100)

# 显示坐标 解释标签

# ax.set_xlabel('width')
# ax.set_ylabel('height')
# ax.set_zlabel('color_score')
plt.show()

"""3 选择模型"""
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=5)

"""4 训练模型"""
# X_train 特征，y_train 标签(真实值)
knn.fit(X_train, y_train)

"""5 测试模型"""
y_predict = knn.predict(X_test)
print(y_predict)
print(list(y_test))  # 测试集的真实值

"""6 计算准确率"""
from sklearn.metrics import accuracy_score

hit_accuracy = accuracy_score(y_test, y_predict)
print("准确率为： {}".format(hit_accuracy))
