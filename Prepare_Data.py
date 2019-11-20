import json
from Info.Paths import Classifier_Path
from keras.models import load_model
from keras.utils import to_categorical
from Info.DataInfo import Labels
from numpy import empty
import numpy


def dim(list):  # return total elements of a 2 axis list
	count = 0
	for i in list:
		count += len(i)
	return count


def enough_elements(list, leng, testperc, validation):  # return True only if got enough elements to procede
	elements = int(dim(list) / leng)
	if elements < 1:
		return False
	if int(elements / 100 * testperc) < 1:
		return False
	if validation:
		if int(elements / 100 * (testperc + 20)) < 1:
			return False
	return True


def create_label_array(list, leng):
	templist = []
	for i in range(len(list)):
		if list[i]:  # skip if empty
			for y in range(int(len(list[i]) / leng)):
				templist.append(i)
	labelarray = numpy.array(templist).reshape(len(templist), 1)
	labelarray = to_categorical(labelarray, len(Labels), numpy.int64)
	return labelarray


def get_numpy_array(list, n_timesteps, axis):  # create monodimentional list
	list2 = []
	for i in range(len(list)):
		for j in range(len(list[i])):
			list2.append(list[i][j])
	# remove empty activities
	try:
		list2.remove([])
	except ValueError:
		pass
	arr = numpy.array(list2, numpy.int64).reshape(int(len(list2) / (n_timesteps * axis)), n_timesteps, axis)
	return arr


def get_datas_n_labels(list, n_timesteps, axis):  # return array and labelsarray
	leng = n_timesteps * axis
	labelarray = create_label_array(list, leng)
	arr = get_numpy_array(list, n_timesteps, axis)
	return arr, labelarray


def remove_extradata(list, leng):
	for i in range(len(Labels)):
		listlen = len(list[i])
		listsurp = listlen % leng
		if listsurp > 0:
			for j in range(listsurp):
				list[i].pop(listlen - 1 - j)


def extract_data(list, perc, leng):  # return none if something was wrong with %
	if perc <= 0 or perc >= 100:
		print("FROM extract_data:", "specified % must be <100 AND >0 ", perc, " is not in this range")
		return None
	else:
		extracting = []
		for i in range(len(Labels)):
			# adding enough assix as much as existing labels
			extracting.append([])
		for i in range(len(Labels)):
			perclen = int(len(list[i]) / leng)
			perclen = int(perclen / 100 * perc)
			for j in range(perclen * leng):
				listlen = len(list[i])
				extracting[i].append(list[i][listlen - 1])
				list[i].pop(listlen - 1)
		return extracting


def Prepare_Data(Json, Classifier_name, Xvalidation, testperc, ag = 0):
	# ag is used to choise if prepare only accelerometer data (ag=1) or only gyroscope data(ag=2) or both(=ag0)
	# need modify to use cross validation
	json_acceptable_string = Json.replace("'", "\"")
	Json = json.loads(json_acceptable_string)
	# need to know n° of timesteps for each timeseries
	model = load_model(Classifier_Path + Classifier_name + ".h5")
	n_timesteps = model.layers[0].input_shape[1]
	# type could be train validation or test
	# using lists cause i need to order depending from labels

	list = []
	for i in range(len(Labels)):
		# adding enough assix as much as existing labels
		list.append([])

	for a in Json["_raw"]["series"][0]["values"]:  # this depend from json format (obtained from get_data on db server)
		if a[5] == "accelerometer" and ag == 1:
			# will be appended magnitude x y z cause they are in this order in the query result
			list[Labels[a[1]]].append(a[7])
		if a[5] == "gyroscope" and ag == 2:
			# will be appended magnitude x y z cause they are in this order in the query result
			list[Labels[a[1]]].append(a[7])
		if ag == 0:
			# will be appended magnitude x y z cause they are in this order in the query result
			list[Labels[a[1]]].append(a[7])
	axis = 4
	leng = n_timesteps * axis
	if ag == 0:
		leng = leng * 2
		axis = axis * 2
	# removing surplus data before create numpyarrays
	remove_extradata(list, leng)  # double axis
	list_enough_elements = enough_elements(list, leng , testperc, Xvalidation)
	if list_enough_elements:
		array = labels = test = test_labels = Validation = Validation_labels = None
		# create test set
		test_list = extract_data(list, testperc, leng )
		test, test_labels = get_datas_n_labels(test_list, n_timesteps, axis)

		# create Validation set
		if Xvalidation is True:
			Validation_list = extract_data(list, 20, leng)
			Validation, Validation_labels = get_datas_n_labels(Validation_list, n_timesteps, axis)
		else:
			Validation = test
			Validation_labels = test_labels
		array, labels = get_datas_n_labels(list, n_timesteps, axis)
		return array, labels, test, test_labels, Validation, Validation_labels
	else:
		print("FROM Prepare_Data: not enough data for Accelerometer sensor")
		return None, None, None, None, None, None