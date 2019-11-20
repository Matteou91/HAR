import json
from Info.Paths import Classifier_Path
from keras.models import load_model
from keras.utils import  to_categorical
from Info.DataInfo import Labels,axis
from numpy import empty
import numpy


def dim(list):  # return total elements of a 2 axis list
	count = 0
	for i in list:
		count += len(i)
	return count


def enough_elements(list, leng, testperc, validation):  # return True only if got enough elements to procede
	elements = int(dim(list)/leng)
	if elements < 1:
		return False
	if int(elements/100*testperc) < 1:
		return False
	if validation:
		if int(elements/100*20) < 1:
			return False
	return True

def create_label_array(list,leng):
	templist=[]
	for i in range(len(list)):
		if list[i]: #  skip if empty
			for y in range(int(len(list[i]) / leng)):
				templist.append(i)
	labelarray=numpy.array(templist).reshape(len(templist),1)
	labelarray= to_categorical(labelarray,len(Labels),numpy.int64)
	return labelarray


def get_numpy_array(list,n_timesteps,axis):  # create monodimentional list
	list2 = []
	for i in range(len(list)):
		for j in range(len(list[i])):
			list2.append(list[i][j])
	# remove empty activities
	try:
		list2.remove([])
	except ValueError:
		pass
	arr = numpy.array(list2, numpy.int64).reshape(int(len(list2)/(n_timesteps*axis)), n_timesteps, axis)
	return arr


def get_datas_n_labels(list,n_timesteps,axis):  #return array and labelsarray
	leng=n_timesteps*axis
	labelarray = create_label_array(list, leng)
	arr = get_numpy_array(list,n_timesteps,axis)
	return arr, labelarray

def remove_extradata(list,leng):
	for i in range(len(Labels)):
		listlen = len(list[i])
		listsurp = listlen % leng
		if listsurp > 0:
			for j in range(listsurp):
				list[i].pop(listlen - 1 - j)


def extract_data(list,perc,leng):  # return none if something was wrong with %
	if perc<=0 or perc >=100:
		print("FROM extract_data:","specified % must be <100 AND >0 ",perc," is not in this range")
		return None
	else:
		extracting = []  # giacomo va bene così per le liste o uso list()
		for i in range(len(Labels)):
			# adding enough assix as much as existing labels
			extracting.append([])  # giacomo qui va bene?
		for i in range(len(Labels)):
			perclen = int(len(list[i]) / leng)
			perclen = int(perclen / 100 * perc)
			for j in range(perclen * leng):
				listlen=len(list[i])
				extracting[i].append(list[i][listlen - 1])
				list[i].pop(listlen - 1)
		return extracting

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
	# removing surplus data before create numpyarrays
	leng = n_timesteps*axis
	remove_extradata(ACC_list, leng)
	remove_extradata(Gyro_list, leng)

	enough_ACC_elements = enough_elements(ACC_list, leng, testperc, Validation)
	enough_Gyro_elements = enough_elements(Gyro_list, leng, testperc, Validation)

	ACC_array = ACC_labels = ACC_test = ACC_test_labels = ACC_Validation = ACC_Validation_labels = Gyro_array = \
		Gyro_labels = Gyro_test = Gyro_test_labels = Gyro_Validation = Gyro_Validation_labels = None

	if enough_ACC_elements:
		# create ACC_test set
		ACC_test_list = extract_data(ACC_list, testperc, leng)
		ACC_test, ACC_test_labels = get_datas_n_labels(ACC_test_list, n_timesteps, axis)

		# create ACC_Validation set
		if Validation is True:
			ACC_Validation_list = extract_data(ACC_list, 20, leng)  # giacomo così faccio il 20% del rimanente, o dovevo farlo del totale?
			ACC_Validation, ACC_Validation_labels = get_datas_n_labels(ACC_Validation_list, n_timesteps, axis)
		else:
			ACC_Validation = ACC_test
			ACC_Validation_labels = ACC_test_labels
		ACC_array, ACC_labels = get_datas_n_labels(ACC_list, n_timesteps, axis)
	else:
		print("FROM Prepare_Data: not enough data for Accelerometer sensor")

	if enough_Gyro_elements:
		# create Gyro_test set
		Gyro_test_list = extract_data(Gyro_list, testperc, leng)
		Gyro_test, Gyro_test_labels = get_datas_n_labels(Gyro_test_list, n_timesteps, axis)
		# create Gyro_Validation set
		if Validation is True:
			Gyro_Validation_list = extract_data(Gyro_list, 20, leng)  # giacomo così faccio il 20% del rimanente, o dovevo farlo del totale?
			Gyro_Validation, Gyro_Validation_labels = get_datas_n_labels(Gyro_Validation_list, n_timesteps, axis)
		else:
			Gyro_Validation = Gyro_test
			Gyro_Validation_labels = Gyro_test_labels
		Gyro_array, Gyro_labels = get_datas_n_labels(Gyro_list, n_timesteps, axis)
	else:
		print("FROM Prepare_Data: not enough data for Gyroscope sensor")
	return ACC_array, ACC_labels, ACC_test, ACC_test_labels, ACC_Validation, ACC_Validation_labels, Gyro_array, Gyro_labels, Gyro_test, Gyro_test_labels, Gyro_Validation, Gyro_Validation_labels
