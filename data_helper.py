#  coding:UTF-8
import numpy as np
import time
from call_record import CallRecord

FIELD_SEG = "\t"
RECORD_SEG = "\n"


def diff_days(call_record1, call_record2):
    """
    t1=call_record1.time.split(" ")[0]
    t2=call_record2.time.split(" ")[0]
    strformat='%Y-%m-%d'
    return (datetime.datetime.strptime(t2, strformat) - datetime.datetime.strptime(t1,strformat)).days
    """
    return (call_record2.format_time - call_record1.format_time).days


def diff_seconds(call_record1, call_record2):
    """
    strformat='%Y-%m-%d %H:%M:%S'
    return (datetime.datetime.strptime(call_record2.time, strformat) - datetime.datetime.strptime(call_record1.time,strformat)).seconds
    """
    return (call_record2.format_time - call_record1.format_time).seconds


def load_data_file(data_file):
    """
    Load data from files
    """
    # examples = list(open(data_file, "r").readlines())
    # examples = [s.strip().split("\001") for s in examples]
    examples = []
    for v in open(data_file, "r"):
        t = v.strip().split("\001")
        if len(t) < 6:
            continue
        examples.append(t)
    return examples


def load_call_record_from_file(file):
    data = load_data_file(file)
    list_call_record = []
    for v in data:
        if len(v) < 6:
            continue
        cr = CallRecord(v[1], v[2], v[3], v[4], v[5])
        list_call_record.append(cr)
    # 按照时间排序
    data_mat = np.array(data)
    data_inx = np.argsort(data_mat[:, 3], axis=0)
    return data_inx, list_call_record


"""
def load_call_record_from_url(text):
	arr=text.split(RECORD_SEG)
	list_call_record=[]
	data=[]
	for v in arr:
		tmp_arr=v.split(FIELD_SEG)
		if len(tmp_arr)<6:
			continue
		cr=CallRecord(tmp_arr[1],tmp_arr[2],tmp_arr[3],tmp_arr[4],tmp_arr[5])
		list_call_record.append(cr)
		data.append(tmp_arr)
	#按照时间排序
	if len(data)<1:
		return [],[]
	data_mat=np.array(data)
	data_inx=np.argsort(data_mat[:,3],axis=0)
	return data_inx, list_call_record
"""


def load_call_record_from_json(list_dict):
    if type(list_dict) != list:
        print("data format error.")
        return [], []
    data = []
    list_call_record = []
    for v in list_dict:
        phone = v.get("phone", "")
        opposite_phone = v.get("opposite_phone", "")
        call_time = v.get("call_time", "")
        duration = v.get("duration", "")
        call_type = v.get("call_type", "")
        if (phone == "" or opposite_phone == ""
                or call_time == "" or duration == ""
                or call_type == ""):
            continue
        cr = CallRecord(phone, opposite_phone, call_time, duration, call_type)
        list_call_record.append(cr)
        data.append(call_time)
    # 按照时间排序
    if len(data) < 1:
        return [], []
    data_mat = np.array(data)
    data_inx = np.argsort(data_mat, axis=0)
    return data_inx, list_call_record


def print_log(msg):
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), msg)
