from os import remove
from os.path import exists, join, getctime
import shutil
import glob
from Info.Paths import Model_Path


def Delete_Model(UserName, txt, ClassifierName=None, ModelName=None):
	if exists(Model_Path[0:(len(Model_Path) - 1)]):  # don't consider "/"
		Path = Model_Path + "User_" + UserName
		if exists(Path):
			if ModelName == ClassifierName == None:
				shutil.rmtree(Path, ignore_errors=True)
			else:
				Path += "/" + ClassifierName
				if exists(Path):
					if ModelName is None:
						shutil.rmtree(Path, ignore_errors=True)
					else:
						Path += "/" + ModelName
						if exists(Path + ".h5"):
							remove(Path + ".h5")
						else:
							print("FROM Delete_Model: " + Path + ".h5 doesn't exist")
						if txt:
							if exists(Path + ".txt"):
								remove(Path + ".txt")
							else:
								print("FROM Delete_Model: " + Path + ".txt doesn't exist")
				else:
					print("FROM Delete_Model: This user have not models created with " + ClassifierName + " Classifier")
		else:
			print("FROM Delete_Model: User have not models")
	else:
		print("FROM Delete_Model: Model_Path not found")


# return none if something went wrong,else return file path
# return Ticket Model if specified,return last created model if Ticket is None
def getTrainedModel(UserName, ClassifierName, Ticket=None):
	Path = Model_Path + "User_" + UserName + "/" + ClassifierName + "/"
	if exists(Path):
		if Ticket is None:  # return last created Model
			list_of_files = glob.glob(join(Path, "*.h5"))
			latest_file = max(list_of_files, key=getctime)
			Path += latest_file
			if exists(Path):
				return Path
			else:
				print("FROM getTrainedModel: No Models for this User and this Classifier")
				return None
		else:
			CheckPath = Model_Path + "User_" + Ticket.split("_")[1] + "/" +Ticket.split("_")[0] + "/"
			# need to check, because in the ticket name are included user and classifier name
			if Path == CheckPath:
				Path += Ticket + ".h5"
				if exists(Path):
					return Path
				else:
					print("FROM getTrainedModel: This Model doesn't exist")
					return None
			else:
				print("FROM getTrainedModel: Username or Classifier Name different from Ticket")
				return None
	else:
		print("FROM getTrainedModel: Wrong Username or Classifier Name")
		return None


def InsertNewClassifier():  # giacomo essendo su un'altra macchina come presumo mi arrivi il file?
	print("da implementare")


#print(getTrainedModel("GiacomoGiorgi", "Classifier1","Classifier1_GiacomoGiorgi__2019-11-1418:04:54.6045082"))
# Delete_Model("Prova1",True,"Classifier1","Classifier1_GiacomoGiorgi__2019-11-1418:03:31.594630")
