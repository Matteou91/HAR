from os import remove
from os.path import exists, join
import glob
from Info.Paths import Classifier_Path


def Delete_Classifier(ClassifierName=None):  # name without extension, default delete all
	Path = Classifier_Path[0:(len(Classifier_Path)-1)]  # don't consider "/"
	if exists(Path):
		if ClassifierName==None:
			filelist = glob.glob(join(Path, "*.h5"))
			for f in filelist:
				remove(f)
		else:
			if exists(Classifier_Path+ClassifierName+".h5"):
				remove(Classifier_Path+ClassifierName+".h5")
			else:
				print("FROM Delete_Classifier: "+ClassifierName+".h5 doesn't exist")
	else:
		print("FROM Delete_Classifier: Classifier_Path not found")


def InsertNewClassifier(classifier, classifierName):
	if exists(Classifier_Path + classifierName + ".h5"):
		print("From InsertNewClassifier: " + Classifier_Path + classifierName + " already exist, overwriting")
	file = open(Classifier_Path + classifierName + ".h5", "w")
	file.write(classifier)
	file.close()


def GetClassifier(classifierName):
	if not exists(Classifier_Path + classifierName + ".h5"):
		print("From GetClassifier: " + Classifier_Path + classifierName + " doesn't exist")
		return None
	else:
		file = open(Classifier_Path + classifierName + ".h5")
		temp_file = file
		file.close()
		return temp_file


def get_Classifiers_Name():  # return all the Classifier name in the classifier folder
	if exists(Classifier_Path[0:(len(Classifier_Path)-1)]):
		for file in glob.glob(Classifier_Path+"*.h5"):
			name = str(file)
			name = name.split(".")[0]
			name = name.split("/")
			name = name[len(name)-1]
			print(name)