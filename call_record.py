#  coding:UTF-8
import time
import datetime
#import udatetime

class CallRecord:
	def __init__(self, phone, opposite_phone, call_time, call_duration,call_type):
		self.phone=phone
		self.opposite_phone=opposite_phone
		self.time=call_time
		self.duration=float(call_duration)
		#'1' 呼出 '2' 呼入
		self.call_type=call_type
		#self.format_time = datetime.datetime.strptime(self.time,'%Y-%m-%d %H:%M:%S')
		s2=self.time
		arr1=s2.split(" ")
		arr2=arr1[0].split("-")
		arr3=arr1[1].split(":")
		self.format_time = datetime.datetime(*map(int, [arr2[0], arr2[1], arr2[2], arr3[0], arr3[1], arr3[2]]))
		#self.format_time = datetime.datetime(*map(int, [s2[:4], s2[5:7], s2[8:10],s2[11:13], s2[14:16], s2[17:]]))

		#最快的时间解析方式
		#s2=s2.replace(" ","T")
		#self.format_time=udatetime.from_string(s2)

		self.year=str(self.format_time.year)
		self.month_of_year=str(self.format_time.month)
		#self.week_of_year=self.format_time.strftime('%W')
		self.week_of_year=str(self.format_time.isocalendar()[1])
		self.day_of_year=str(self.format_time.day)


	def get_year(self):
		return self.year

	def get_month_of_year(self):
		self.month_of_year

	def get_week_of_year(self):
		return self.week_of_year

	def get_day_of_year(self):
		return self.day_of_year
	def get_hour(self):
		return self.format_time.hour

	def is_call_out(self):
		if self.call_type == '1' :
			return True
		return False
	def is_call_in(self):
		if self.call_type == '2' :
			return True
		return False
	def is_working_day(self):
		if self.format_time.weekday()>=0 and self.format_time.weekday()<=4 :
			return True
		return False
	def is_working_day_morning(self):
		if self.get_hour()>=6 and self.get_hour() < 12 and self.is_working_day() :
			return True
		return False
	def is_working_day_afternoon(self):
		if self.get_hour()>=12 and self.get_hour() <= 18 and self.is_working_day() :
			return True
		return False
	def is_working_day_evening(self):
		if self.get_hour()>=18 and self.get_hour() <= 24 and self.is_working_day() :
			return True
		return False
	def is_working_day_night(self):
		if self.get_hour()>=0 and self.get_hour() <= 6 and self.is_working_day() :
			return True
		return False
	def call_time_hour_in_range(self, s,e):
		if self.get_hour()>=s and self.get_hour() <= e:
			return True
		return False

class ContactIntimate:
	def __init__(self, phone, label, weight):
		self.phone=phone
		self.label=label
		self.weight=weight
	def to_string(self):
		s='{"phone":"'+self.phone
		s=s+'","label":"'+str(self.label)
		s=s+'","weight":"'+str(self.weight)
		s=s+'"}'
		return s


