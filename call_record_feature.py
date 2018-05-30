#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
Created on Sat Mar 25 07:27:49 2017

@author: cloudsbing
"""
'''
Created on Oct 19, 2010

@author: Peter
'''
import numpy as np
import time
#import datetime
import math
import data_helper
from call_record import ContactIntimate
import logging
import datetime

import xgboost as xgb

FIELD_SEG="\t"
RECORD_SEG="\n"

#label
LABEL_HOME="10001"
LABEL_OTHER="00000"

def get_bursts(list_inx, list_call_record):
	#20分钟内连续通话的 连续次数
	"""
	13:00
	13:15
	13:30

	14:00
	14:18
	burst=2 每次 burst为3 2
	"""
	burst_time=60*20
	index_list=[]
	for v in range(1,len(list_inx)):
		pre=list_call_record[list_inx[v-1]]
		cur=list_call_record[list_inx[v]]
		if data_helper.diff_seconds(pre, cur)-pre.duration<burst_time:
			index_list.append(v)
	count=0
	tmp_long_count=0
	tmp_count=0
	for v in range(1,len(index_list)):
		if index_list[v]- index_list[v-1] == 1:
			count+=1
			tmp_count+=1
			tmp_long_count=max(tmp_long_count, tmp_count)
		else:
			tmp_count=0
	totalNumberOfBursts=0.0
	if len(index_list) == 1:
		totalNumberOfBursts=1.0
	else:
		totalNumberOfBursts = len(index_list) - count
	totalburstlength=len(index_list)*2 - count
	averageBurstsLength=0
	if len(index_list) == 0:
		averageBurstsLength=0.0
		longestBurstsLength=0.0
	elif len(index_list) == 1:
		averageBurstsLength=2.0
		longestBurstsLength=2.0
	else:
		averageBurstsLength=float(totalburstlength)/totalNumberOfBursts
		longestBurstsLength=tmp_long_count+2
	return totalNumberOfBursts, averageBurstsLength, longestBurstsLength

def CallsFeaturesPerWeek(tmp_call_year_week_map):
	values=tmp_call_year_week_map.values()
	values_length=len(values)
	if values_length<1:
		return [0.0,0.0,0.0,0.0,0.0]
	values.sort()
	min_value=values[0]
	max_value=values[-1]
	med_value=0.0
	if len(values)%2==0:
		med_value=float(values[values_length/2]+values[values_length/2-1])/2
	else:
		med_value=float(values[values_length/2])
	avg_value=float(sum(values))/values_length
	sum_value=0.0
	std_value=0.0
	if values_length>1:
		for v in values:
			sum_value+=math.sqrt( (float)(v-avg_value)*(v-avg_value) )
		std_value=float(sum_value)/(values_length-1)
	return [avg_value, max_value, min_value, med_value, std_value]

#  获取统计记录的特征
def get_call_feature(data_inx, list_call_record):
	#output
	list_sig_feature=[]
	list_fam_feature=[]
	opposite_phone_map={}

	total_week_of_year_map={}
	total_day_of_year_map={}
	tmp_total_call_out_count=0.0
	tmp_all_call_out_duration=0.0
	tmp_total_call_in_count=0.0
	total_call_duration=0.0
	for inx in data_inx :
		phone=list_call_record[inx].opposite_phone
		#t2=list_call_record[inx].format_time
		#key=time.strftime('%Y-%W',t2)
		key= "%s-%s" % (list_call_record[inx].get_year(),list_call_record[inx].get_week_of_year())
		total_week_of_year_map[key]=""
		#key=time.strftime('%Y-%j',t2)
		key= "%s-%s" % (list_call_record[inx].get_year(),list_call_record[inx].get_day_of_year())
		total_day_of_year_map[key]=""
		if opposite_phone_map.has_key(phone):
			opposite_phone_map[phone].append(inx)
		else:
			opposite_phone_map[phone]=[]
			opposite_phone_map[phone].append(inx)
		if list_call_record[inx].is_call_out():
			tmp_total_call_out_count+=1
			tmp_all_call_out_duration+=list_call_record[inx].duration
		else:
			tmp_total_call_in_count+=1
		total_call_duration+=list_call_record[inx].duration
	#print "data_inx",data_inx
	#单个号码
	min_date_call_record=list_call_record[data_inx[0]]
	max_date_call_record=list_call_record[data_inx[-1]]
	total_days=data_helper.diff_days(min_date_call_record, max_date_call_record)+1
	for v in opposite_phone_map:
		list_inx=opposite_phone_map[v]
		month_of_year_map={}
		week_of_year_map={}
		day_of_year_map={}
		pre=min_date_call_record
		max_gap_days=0.0
		WeekdayCallsMonrning=0.0
		WeekdayCallAfternoon=0.0
		weekdayCallEvening=0.0
		weekdayCallNight=0.0
		totalCallsWeekdays=0.0
		totalCallDuration=0.0
		totalCallDurationWeekends=0.0
		maxDurationOutgoingCalls=0.0
		maxDurationIncomingCalls=0.0
		tmp_total_call_out_duration=0.0
		tmp_90_days_call_out_duration=0.0
		call_out_count=0.0
		call_in_count=0.0
		tmp_call_hour_map={}
		tmp_call_duration=0.0
		tmp_specify_time_duration_eve=0.0
		tmp_specify_time_duration_morn=0.0
		tmp_specify_time_duration_noon=0.0
		tmp_specify_time_duration_afn=0.0
		tmp_call_out_year_week_map={}
		tmp_call_in_year_week_map={}
		tmp_call_duration_list=[]
		for inx in list_inx:
			#t2=list_call_record[inx].format_time
			#key=time.strftime('%Y-%m', t2)
			key= "%s-%s" % (list_call_record[inx].get_year(),list_call_record[inx].get_month_of_year())
			month_of_year_map[key]=""
			#key=time.strftime('%Y-%W',t2)
			key= "%s-%s" % (list_call_record[inx].get_year(),list_call_record[inx].get_week_of_year())
			week_of_year_map[key]=""
			#key=time.strftime('%Y-%j',t2)
			key= "%s-%s" % (list_call_record[inx].get_year(),list_call_record[inx].get_day_of_year())
			day_of_year_map[key]=""

			#计算2次通话最大间隔天数
			tmp=data_helper.diff_days(pre, list_call_record[inx])
			if max_gap_days<tmp:
				max_gap_days=tmp
			pre=list_call_record[inx]
			#工作日各时段通话次数
			if list_call_record[inx].is_working_day_morning():
				WeekdayCallsMonrning+=1
			if list_call_record[inx].is_working_day_afternoon():
				WeekdayCallAfternoon+=1
			if list_call_record[inx].is_working_day_evening():
				weekdayCallEvening+=1
			if list_call_record[inx].is_working_day_night():
				weekdayCallNight+=1
			if list_call_record[inx].is_working_day():
				totalCallsWeekdays+=1
			else:
				totalCallDurationWeekends+=list_call_record[inx].duration
			totalCallDuration+=list_call_record[inx].duration
			if list_call_record[inx].is_call_out():
				call_out_count+=1
				maxDurationOutgoingCalls = max(maxDurationOutgoingCalls, list_call_record[inx].duration)
				tmp_total_call_out_duration+=list_call_record[inx].duration
				#key=time.strftime('%Y-%W',t2)
				key= "%s-%s" % (list_call_record[inx].get_year(),list_call_record[inx].get_week_of_year())
				if tmp_call_out_year_week_map.has_key(key):
					tmp_call_out_year_week_map[key]+=1
				else:
					tmp_call_out_year_week_map[key]=1
			else:
				call_in_count+=1
				maxDurationIncomingCalls=max(maxDurationIncomingCalls, list_call_record[inx].duration)
				#key=time.strftime('%Y-%W',t2)
				key= "%s-%s" % (list_call_record[inx].get_year(),list_call_record[inx].get_week_of_year())
				if tmp_call_in_year_week_map.has_key(key):
					tmp_call_in_year_week_map[key]+=1
				else:
					tmp_call_in_year_week_map[key]=1

			#90天内
			if data_helper.diff_days(list_call_record[inx], max_date_call_record)<=90:
				tmp_90_days_call_out_duration+=list_call_record[inx].duration
			tmp_call_hour_map[list_call_record[inx].get_hour()/2]=""
			tmp_call_duration+=list_call_record[inx].duration
			if list_call_record[inx].call_time_hour_in_range(0,7) or list_call_record[inx].call_time_hour_in_range(18,23):
				tmp_specify_time_duration_eve+=list_call_record[inx].duration
			if list_call_record[inx].call_time_hour_in_range(9,10):
				tmp_specify_time_duration_morn+=list_call_record[inx].duration
			if list_call_record[inx].call_time_hour_in_range(11,12):
				tmp_specify_time_duration_noon+=list_call_record[inx].duration
			if list_call_record[inx].call_time_hour_in_range(14,16):
				tmp_specify_time_duration_afn+=list_call_record[inx].duration
			tmp_call_duration_list.append(list_call_record[inx].duration)

		tmp=data_helper.diff_days(pre,max_date_call_record)
		if max_gap_days<tmp:
			max_gap_days=tmp
		longestGapDays=max_gap_days
		totalGapDay=total_days-len(day_of_year_map)
		ratioGapDayToLoggedDays=float(totalGapDay)/total_days
		weeklyCallsFrequency=len(week_of_year_map)
		averageCallsPerWeek=float(len(list_inx))/len(week_of_year_map)
		ratioWeeklyRecurringCommToTotalWeeks=float(len(week_of_year_map))/len(total_week_of_year_map)
		#周末通话次数占比
		ratioBetweenWeekendCallToTotal=float(len(list_inx)-totalCallsWeekdays)/len(list_inx)
		totalCallFrequency=len(list_inx)
		#周末通话次数
		totalCallFrequencyWeekends=len(list_inx)-totalCallsWeekdays
		if totalCallDuration==0.0:
			durationOutgoingCallsToTotalCallsDuration=0.0
		else:
			durationOutgoingCallsToTotalCallsDuration=float(tmp_total_call_out_duration)/totalCallDuration
		durationCallsForPastPeriods=tmp_90_days_call_out_duration
		if totalCallDuration==0.0:
			ratioWeekendCallDurationToTotalDuration=0.0
		else:
			ratioWeekendCallDurationToTotalDuration=float(totalCallDurationWeekends)/totalCallDuration
		medianCallDurations=0.0
		tmp_call_duration_list.sort()
		if len(tmp_call_duration_list) %2 == 0:
			inx_length=len(tmp_call_duration_list)
			medianCallDurations=(tmp_call_duration_list[inx_length/2]+tmp_call_duration_list[(inx_length-1)/2])/2
		else:
			inx_length=len(tmp_call_duration_list)
			medianCallDurations=tmp_call_duration_list[inx_length/2]
		longestDurationCall=max(maxDurationOutgoingCalls, maxDurationIncomingCalls)
		#周末每次平均通话时长
		avgCallDurationWeekends=0.0
		if (len(list_inx)-totalCallsWeekdays) != 0:
			avgCallDurationWeekends=float(totalCallDurationWeekends)/(len(list_inx)-totalCallsWeekdays)

		totalNumberOfBursts, averageBurstsLength, longestBurstsLength=get_bursts(list_inx, list_call_record)
		ratioIncomingToOutgoing=1.0
		if call_in_count != 0:
			ratioIncomingToOutgoing=float(call_out_count+1)/(call_in_count+1)
		ratioOutgoingCommToTotalComms=float(call_out_count)/len(list_inx)
		commsToTotalCalls=float(len(list_inx))/len(list_call_record)
		daysHadCommToDaysLogged=float(len(day_of_year_map))/len(total_day_of_year_map)
		monthlyCallsFrequency=len(month_of_year_map)
		hourSegmentCallsFrequency=len(tmp_call_hour_map)
		if tmp_total_call_out_count==0.0:
			outgoingCommToTotalOutgoingComms=0.0
		else:
			outgoingCommToTotalOutgoingComms=float(call_out_count)/tmp_total_call_out_count
		if tmp_total_call_in_count == 0.0:
			incomingCommToTotalIncomingComms=0.0
		else:
			incomingCommToTotalIncomingComms=float(call_in_count)/tmp_total_call_in_count
		durationSingleTotalCallsToTotalCallsDuration=float(tmp_call_duration)/total_call_duration
		if tmp_all_call_out_duration==0.0:
			durationSingleOutgoingCallsToTotalOutgoingCallsDuration=0.0
		else:
			durationSingleOutgoingCallsToTotalOutgoingCallsDuration=float(tmp_total_call_out_duration)/tmp_all_call_out_duration
		ratioSpecifyCallDurationToTotalDurationEve=float(tmp_specify_time_duration_eve)/total_call_duration
		ratioSpecifyCallDurationToTotalDurationMorn=float(tmp_specify_time_duration_morn)/total_call_duration
		ratioSpecifyCallDurationToTotalDurationNoon=float(tmp_specify_time_duration_noon)/total_call_duration
		ratioSpecifyCallDurationToTotalDurationAfn=float(tmp_specify_time_duration_afn)/total_call_duration

		outgoingCallsFeaturesPerWeek=CallsFeaturesPerWeek(tmp_call_out_year_week_map)
		incomingCallsFeaturesPerWeek=CallsFeaturesPerWeek(tmp_call_in_year_week_map)
		avgOutgoingCallsFeaturesPerWeek=outgoingCallsFeaturesPerWeek[0]
		maxOutgoingCallsFeaturesPerWeek=outgoingCallsFeaturesPerWeek[1]
		minOutgoingCallsFeaturesPerWeek=outgoingCallsFeaturesPerWeek[2]
		medOutgoingCallsFeaturesPerWeek=outgoingCallsFeaturesPerWeek[3]
		stdOutgoingCallsFeaturesPerWeek=outgoingCallsFeaturesPerWeek[4]

		avgIncomingCallsFeaturesPerWeek=incomingCallsFeaturesPerWeek[0]
		maxIncomingCallsFeaturesPerWeek=incomingCallsFeaturesPerWeek[1]
		minIncomingCallsFeaturesPerWeek=incomingCallsFeaturesPerWeek[2]
		medIncomingCallsFeaturesPerWeek=incomingCallsFeaturesPerWeek[3]
		stdIncomingCallsFeaturesPerWeek=incomingCallsFeaturesPerWeek[4]

		# sig_feature 标记特征
		sig_feature=[0 for i in range(51)]
		sig_feature[0]=-1
		sig_feature[1]=totalGapDay
		sig_feature[2]=ratioGapDayToLoggedDays
		sig_feature[3]=longestGapDays
		sig_feature[4]=weeklyCallsFrequency
		sig_feature[5]=averageCallsPerWeek
		sig_feature[6]=ratioWeeklyRecurringCommToTotalWeeks
		sig_feature[7]=WeekdayCallsMonrning
		sig_feature[8]=WeekdayCallAfternoon
		sig_feature[9]=weekdayCallEvening
		sig_feature[10]=weekdayCallNight
		sig_feature[11]=totalCallsWeekdays
		sig_feature[12]=ratioBetweenWeekendCallToTotal
		sig_feature[13]=totalCallFrequency
		sig_feature[14]=totalCallFrequencyWeekends
		sig_feature[15]=avgOutgoingCallsFeaturesPerWeek
		sig_feature[16]=maxOutgoingCallsFeaturesPerWeek
		sig_feature[17]=minOutgoingCallsFeaturesPerWeek
		sig_feature[18]=medOutgoingCallsFeaturesPerWeek
		sig_feature[19]=stdOutgoingCallsFeaturesPerWeek
		sig_feature[20]=avgIncomingCallsFeaturesPerWeek
		sig_feature[21]=maxIncomingCallsFeaturesPerWeek
		sig_feature[22]=minIncomingCallsFeaturesPerWeek
		sig_feature[23]=medIncomingCallsFeaturesPerWeek
		sig_feature[24]=stdIncomingCallsFeaturesPerWeek
		sig_feature[25]=totalCallDuration
		sig_feature[26]=totalCallDurationWeekends
		sig_feature[27]=maxDurationOutgoingCalls
		sig_feature[28]=maxDurationIncomingCalls
		sig_feature[29]=durationCallsForPastPeriods
		sig_feature[30]=ratioWeekendCallDurationToTotalDuration
		sig_feature[31]=medianCallDurations
		sig_feature[32]=longestDurationCall
		sig_feature[33]=avgCallDurationWeekends
		sig_feature[34]=totalNumberOfBursts
		sig_feature[35]=averageBurstsLength
		sig_feature[36]=longestBurstsLength
		sig_feature[37]=ratioOutgoingCommToTotalComms
		sig_feature[38]=commsToTotalCalls
		sig_feature[39]=daysHadCommToDaysLogged
		sig_feature[40]=monthlyCallsFrequency
		sig_feature[41]=hourSegmentCallsFrequency
		sig_feature[42]=outgoingCommToTotalOutgoingComms
		sig_feature[43]=incomingCommToTotalIncomingComms
		sig_feature[44]=durationSingleTotalCallsToTotalCallsDuration
		sig_feature[45]=durationSingleOutgoingCallsToTotalOutgoingCallsDuration
		sig_feature[46]=ratioIncomingToOutgoing
		sig_feature[47]=durationOutgoingCallsToTotalCallsDuration
		sig_feature[48]=ratioSpecifyCallDurationToTotalDurationEve
		sig_feature[49]=ratioSpecifyCallDurationToTotalDurationMorn
		sig_feature[50]=ratioSpecifyCallDurationToTotalDurationAfn
		list_sig_feature.append(sig_feature)
		#print sig_feature
		fam_feature=[0 for i in range(48)]
		fam_feature[0]=-1
		fam_feature[1]=totalGapDay
		fam_feature[2]=ratioGapDayToLoggedDays
		fam_feature[3]=longestGapDays
		fam_feature[4]=weeklyCallsFrequency
		fam_feature[5]=averageCallsPerWeek
		fam_feature[6]=ratioWeeklyRecurringCommToTotalWeeks
		fam_feature[7]=WeekdayCallsMonrning
		fam_feature[8]=WeekdayCallAfternoon
		fam_feature[9]=weekdayCallEvening
		fam_feature[10]=weekdayCallNight
		fam_feature[11]=totalCallsWeekdays
		fam_feature[12]=ratioBetweenWeekendCallToTotal
		fam_feature[13]=totalCallFrequency
		fam_feature[14]=totalCallFrequencyWeekends
		fam_feature[15]=avgOutgoingCallsFeaturesPerWeek
		fam_feature[16]=maxOutgoingCallsFeaturesPerWeek
		fam_feature[17]=minOutgoingCallsFeaturesPerWeek
		fam_feature[18]=medOutgoingCallsFeaturesPerWeek
		fam_feature[19]=stdOutgoingCallsFeaturesPerWeek
		fam_feature[20]=avgIncomingCallsFeaturesPerWeek
		fam_feature[21]=maxIncomingCallsFeaturesPerWeek
		fam_feature[22]=minIncomingCallsFeaturesPerWeek
		fam_feature[23]=medIncomingCallsFeaturesPerWeek
		fam_feature[24]=stdIncomingCallsFeaturesPerWeek
		fam_feature[25]=totalCallDuration
		fam_feature[26]=totalCallDurationWeekends
		fam_feature[27]=maxDurationOutgoingCalls
		fam_feature[28]=maxDurationIncomingCalls
		fam_feature[29]=durationCallsForPastPeriods
		fam_feature[30]=ratioWeekendCallDurationToTotalDuration
		fam_feature[31]=medianCallDurations
		fam_feature[32]=longestDurationCall
		fam_feature[33]=avgCallDurationWeekends
		fam_feature[34]=totalNumberOfBursts
		fam_feature[35]=averageBurstsLength
		fam_feature[36]=longestBurstsLength
		fam_feature[37]=ratioOutgoingCommToTotalComms
		fam_feature[38]=commsToTotalCalls
		fam_feature[39]=daysHadCommToDaysLogged
		fam_feature[40]=monthlyCallsFrequency
		fam_feature[41]=hourSegmentCallsFrequency
		fam_feature[42]=outgoingCommToTotalOutgoingComms
		fam_feature[43]=incomingCommToTotalIncomingComms
		fam_feature[44]=durationSingleTotalCallsToTotalCallsDuration
		fam_feature[45]=durationOutgoingCallsToTotalCallsDuration
		fam_feature[46]=ratioSpecifyCallDurationToTotalDurationEve
		fam_feature[47]=ratioSpecifyCallDurationToTotalDurationMorn
		list_fam_feature.append(fam_feature)
	return opposite_phone_map.keys(), list_sig_feature, list_fam_feature

def do_filter2(np_labels_prob_inx, labels_prob, np_sig_feature):
	list_phone_inx=[]
	for v in np_labels_prob_inx:
		if (
		labels_prob[v][0]>=0.1
		and labels_prob[v][1]>=0.1
		and labels_prob[v][2]>0.01
		#13 totalCallFrequency
		and np_sig_feature[v][13]>=2
		# monthlyCallsFrequency
		and np_sig_feature[v][40]>1
		# avgOutgoingCallsFeaturesPerWeek
		and np_sig_feature[v][15]>0):
			list_phone_inx.append(v)
	return list_phone_inx

def filter_major(np_labels_prob_inx, labels_prob, np_sig_feature):
	list_phone_inx=[]
	for v in np_labels_prob_inx:
		if (
		labels_prob[v][0]>=0.1
		and labels_prob[v][1]>=0.1
		and labels_prob[v][2]>0.01
		#13 totalCallFrequency
		and np_sig_feature[v][13]>=2
		# monthlyCallsFrequency
		and np_sig_feature[v][40]>1
		# avgOutgoingCallsFeaturesPerWeek
		and np_sig_feature[v][15]>0):
			list_phone_inx.append(v)
	return list_phone_inx
def filter_secondary(np_labels_prob_inx, labels_prob, np_sig_feature):
	list_phone_inx=[]
	for v in np_labels_prob_inx:
		if (
		labels_prob[v][0]>=0.1
		and labels_prob[v][1]>=0.1
		and labels_prob[v][2]>0.2
		#13 totalCallFrequency
		and np_sig_feature[v][13]>3
		# monthlyCallsFrequency
		and np_sig_feature[v][40]>=1):
			list_phone_inx.append(v)
	return list_phone_inx

def do_classify(call_record,sig_model,fam_model):
	logger = logging.getLogger(__name__)

	#t1=datetime.datetime.now() # 获取数据参数
	data_inx, list_call_record=data_helper.load_call_record_from_json(call_record)
	if len(data_inx)<1:
		return []
	#t2=datetime.datetime.now()
	#logger.info("load json cost time: %d ms" % ((t2-t1).seconds*1000+(t2-t1).microseconds/1000) )

	# t1=datetime.datetime.now() # 获取通话记录特征
	list_phone, list_sig_feature, list_fam_feature=get_call_feature(data_inx, list_call_record)
	#t2=datetime.datetime.now()
	#logger.info("get feature cost time: %d ms" % ((t2-t1).seconds*1000+(t2-t1).microseconds/1000) )

	#t1=t2
	np_sig_feature=np.array(list_sig_feature)
	dtest = xgb.DMatrix(np_sig_feature)
	sig_preds = sig_model.predict(dtest, output_margin=True )
	#t2=datetime.datetime.now()
	#logger.info("sig_preds predict cost time: %d ms" % ((t2-t1).seconds*1000+(t2-t1).microseconds/1000) )
	#print sig_preds

	#t1=datetime.datetime.now()
	np_fam_feature=np.array(list_fam_feature)
	dtest = xgb.DMatrix(np_fam_feature)
	fam_preds=fam_model.predict(dtest, output_margin=True)
	#print fam_preds
	#t2=datetime.datetime.now()
	#logger.info("fam_preds predict cost time: %d ms" % ((t2-t1).seconds*1000+(t2-t1).microseconds/1000) )

	ret=get_labels(list_phone, sig_preds,fam_preds,np_sig_feature)
	return ret

def get_labels(list_phone, sig_preds,fam_preds, np_sig_feature):
	np_labels_prob=np.zeros((len(sig_preds),3),dtype=float)
	np_labels_prob[:,0]=sig_preds
	np_labels_prob[:,1]=fam_preds
	np_labels_prob[:,2]=np_labels_prob[:,0]*np_labels_prob[:,1]
	#排序 降序
	np_labels_prob_inx=np.argsort(-np_labels_prob[:,2],axis=0)
	#规则过滤
	list_phone_inx=[]
	#list_phone_inx=do_filter2(np_labels_prob_inx, np_labels_prob, np_sig_feature)
	list_phone_inx=filter_major(np_labels_prob_inx, np_labels_prob, np_sig_feature)
	if len(list_phone_inx)<1:
		list_phone_inx=filter_secondary(np_labels_prob_inx, np_labels_prob, np_sig_feature)

	ret=[]
	for v in list_phone_inx:
		#垃圾号码过滤
		if is_spam_number(list_phone[v]):
			continue
		ci=ContactIntimate(list_phone[v], LABEL_HOME, np_labels_prob[v,2])
		ret.append(ci)
	return ret

#init
spam_number_dict={}
def load_spam_number(file):
	global spam_number_dict
	#spam_number_dict.clear()
	examples = list(open(file, "r").readlines())
	for v in examples:
		spam_number_dict[v.strip()]=v.strip()
	return spam_number_dict
def is_spam_number(phone):
	if spam_number_dict.has_key(phone):
		return True
	return False
def get_spam_number_dict_size():
	return len(spam_number_dict)