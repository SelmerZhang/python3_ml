#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 07:27:49 2017

@author: cloudsbing
"""
'''
Created on Oct 19, 2010

@author: Peter
'''
import math
import copy
import os
import time

#  python 的高级表达方式
# 1 条件表达式
def get_log(x):
    if x > 0:
        y = math.log(x)
    else:
        y = float('nan')
    return y


def get_log2(x):
    y = math.log(x) if x > 0 else float('nan')
    return y


# 列表推导式

def list_explore():
    list = []
    for i in range(1000):
        if i % 2 == 0:
            list.append(i)
    return list


def list_explore2():
    list = [i for i in range(1000) if i % 2 == 0]  # 输出满足条件的偶数
    return list


# 深拷贝和浅拷贝
# 1 赋值
def copy_wide():
    a = {1: [1, 2, 3]}
    b = a
    return b


# 拷贝父对象，不拷父对象的内部对象
def copy_simple():
    a = {1: [1, 2, 3]}
    b = a.copy()
    return b


# 深拷贝
def copy_deep():
    a = {1: [1, 2, 3]}
    b = copy.deepcopy(a)  # 如果文件过大，深拷贝会出现内存溢出问题
    return b


# map() 函数，用于数据清洗
# 1 获取两个列表对一个位置的最小值
def compare_list():
    list1 = [1, 3, 5, 20, 9]
    list2 = [2, 4, 6, 8, 10]
    minList = map(min, list1, list2)
    # print [item for item in minList]
    print(minList)  # or


#  匿名函数，当函数比较简单，不需要写函数名，只需要些函数体就可以，通常结合 map使用
def lambda_func():
    print("lambda 结合map")
    list1 = [1, 3, 5, 20, 9]
    list2 = [2, 4, 6, 8, 10]
    result = map(lambda x, y: x * 2 + y, list1, list2)
    print(result)
    print(list(result))


#
"""
多进程并发，进程类 Process start(启动进程), join()(等子进程结束后，再继续向下运行，通常用于进程间的同步)
Pool类，进程池，用于管理多个进程
apply() 进程间是阻塞的
apply_asynv(),进程间是非阻塞的
close() 关闭进程池，比接收新的任务
join（）主进程阻塞，等待子进程的退出，要在close()之后使用。同Porcess的join（）方法不一样
"""


def run_proc(n):
    print("第{}次循环，子进程id:{},父进程id:{}", format(n, os.getppid(), os.getpid()))
    time.sleep(1)


if __name__ == '__main__':
    # print(copy_wide())
    # print(copy_simple())
    # print(copy_deep())
    compare_list()
    # lambda_func()

    # run_proc(os.getppid())
    # print("父进程的id", os.getppid())

    # get_log(3)
    # print(get_log2(3))
    # print(list_explore())
    # print(list_explore2())

    # map 的函数名称，是一个min() 的函数名称。比较大小
