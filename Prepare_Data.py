import json
from Info.Paths import Classifier_Path
from keras.models import load_model
from keras.utils import  to_categorical
from Info.DataInfo import Labels,axis
from numpy import empty
import numpy


def remove_extradata(list,leng):
	for i in range(len(Labels)):
		listlen = len(list[i])
		listsurp = listlen % leng
		if listsurp > 0:
			for j in range(listsurp):
				list[i].pop(listlen - 1 - j)


def create_label_array(list,n_timesteps):
	templist=[]
	for i in range(len(list)):
		for y in range(int(len(list[i]) / n_timesteps)):
			templist.append(i)
	labelarray=numpy.array(templist).reshape(len(templist),1)
	labelarray= to_categorical(labelarray,len(Labels),numpy.int64)
	return labelarray


def Prepare_Data(Json, Classifier_name, Validation, testperc):
	json_acceptable_string = Json.replace("'", "\"")
	Json = json.loads(json_acceptable_string)
	# need to know n° of timesteps for each timeseries
	model = load_model(Classifier_Path + Classifier_name + ".h5")
	n_timesteps = model.layers[0].input_shape[1]
	# type could be train validation or test
	# using lists cause i need to order depending from labels
	ACC_list, Gyro_list = [], []  # giacomo va bene così per le liste o uso list()
	for i in range(len(Labels)):
		# adding enough assix as much as existing labels
		ACC_list.append([]) # giacomo qui va bene?
		Gyro_list.append([])
	for a in Json["_raw"]["series"][0]["values"]:  # this depend from json format (obtained from get_data on db server)
		if a[5] == "accelerometer":
			# will be appended magnitude x y z cause they are in this order in the query result
			ACC_list[Labels[a[1]]].append(a[7])
		if a[5] == "gyroscope":
			# will be appended magnitude x y z cause they are in this order in the query result
			Gyro_list[Labels[a[1]]].append(a[7])
	# removing surplus data before create numpyarray
	leng=n_timesteps*axis
	remove_extradata(ACC_list, leng)
	remove_extradata(Gyro_list, leng)

	"""list = []
	for elem in ACC_list:
		list.append(numpy.asarray(elem, dtype=numpy.float64))
	print("type list",type(list))
	print("type list[0]",type(list[0]))"""
	return ACC_list
