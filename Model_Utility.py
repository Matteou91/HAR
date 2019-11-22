from os import remove
from os.path import exists, join, getctime
import shutil
import glob
import json
from keras.models import load_model
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
				model = load_model(Path)
				return model
			else:
				print("FROM getTrainedModel: No Models for this User and this Classifier")
				return None
		else:
			CheckPath = Model_Path + "User_" + Ticket.split("_")[1] + "/" +Ticket.split("_")[0] + "/"
			# need to check, because in the ticket name are included user and classifier name
			if Path == CheckPath:
				Path += Ticket + ".h5"
				if exists(Path):
					model = load_model(Path)
					return model
				else:
					print("FROM getTrainedModel: This Model doesn't exist")
					return None
			else:
				print("FROM getTrainedModel: Username or Classifier Name different from Ticket")
				return None
	else:
		print("FROM getTrainedModel: Wrong Username or Classifier Name")
		return None


def InsertNewClassifier(model, model_name, user_name, classifier_name):  # NEVER use _ or / in model_name
	# creating working space if not exist
	if not exists(Model_Path[0:(len(Model_Path) - 1)]):
		makedirs(Model_Path[0:(len(Model_Path) - 1)])
	if not exists(Model_Path + "User_" + user_name):
		makedirs(Model_Path + "User_" + user_name)
	if not exists(Model_Path + "User_" + user_name + '/' + classifier_name):
		makedirs(Model_Path + "User_" + user_name + '/' + classifier_name)

	# ticket that give back to client
	Path = Model_Path + "User_" + user_name + '/' + classifier_name + '/'
	if not exists(Path + "Model_info.Json"):
		file = open(Path + "Model_info.Json", 'w')
		file.write("{\n}\n")
		file.close()
	else:
		file = open(Path + "Model_info.Json", 'r')
		try:
			Models = json.load(file)
		except:
			file.close()
			print("From Train_Classifier: " + Path + "Model_info.Json is corrupted")
			return None
		file.close()
		Models.update({model_name: "ready"})
		file = open(Path + "Model_info.Json", 'w')
		json.dump(Models, file)
		file.close()
	if exists(Path + model_name + ".h5"):
		print("From InsertNewClassifier: " + Model_Path + model_name + " already exist, overwriting")
	model.save(Path + model_name + ".h5")
