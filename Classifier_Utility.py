from os import remove
from os.path import exists,join
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
				print(ClassifierName+".h5 doesn't exist")
	else:
		print("Classifier_Path not found")


def InsertNewClassifier():  # giacomo essendo su un'altra macchina come presumo mi arrivi il file?


def GetClassifier():