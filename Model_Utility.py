from os import remove
from os.path import exists, join, getctime
import shutil
import glob
import json
from keras.models import load_model
from Info.Paths import Model_Path


def Delete_Model(UserName, txt, ClassifierName=None, ModelName=None):
	# only UserName remove all User space
	# UserName + ClassifierName remove all models in User_UserName/ClassifierName/
	# UserName + ClassifierName + ModelName only User_UserName/ClassifierName/ModelName.h5

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
						info_path = Path + "/Model_info.Json"
						Path += "/" + ModelName
						if exists(Path + ".h5"):
							if exists(info_path):
								info_file = open(info_path)
								try:
									Models = json.load(info_file)
									info_file.close()
									result = Models.pop(ModelName, None)
									if result is None:
										remove(Path + ".h5")
										print("From Delete_Model: Removed " + Path + ".h5 , NOT FOUND in Model_info.Json")
										if txt:
											if exists(Path + ".txt"):
												remove(Path + ".txt")
											else:
												print("FROM Delete_Model: " + Path + ".txt doesn't exist")
									else:
										if result == "ready":
											print("result is ready")
											info_file = open(info_path,"w")
											json.dump(Models, info_file)
											info_file.close()
											remove(Path + ".h5")
											print("From Delete_Model: Removed "+ Path + ".h5")
											if txt:
												if exists(Path + ".txt"):
													remove(Path + ".txt")
												else:
													print("FROM Delete_Model: " + Path + ".txt doesn't exist")
										else:
											print("From Delete_Model: Can't remove "+ Path + ".h5 , Status = " + result)
								except:
									print("From Delete_Model: " + info_path + " is corrupted, model not removed")
									info_file.close()
							else:
								remove(Path + ".h5")
								if txt:
									if exists(Path + ".txt"):
										remove(Path + ".txt")
									else:
										print("FROM Delete_Model: " + Path + ".txt doesn't exist")
						else:
							print("FROM Delete_Model: " + Path + ".h5 doesn't exist")
				else:
					print("FROM Delete_Model: This user have not models created with " + ClassifierName + " Classifier")
		else:
			print("FROM Delete_Model: User have not models")
	else:
		print("FROM Delete_Model: Model_Path not found")


# return none if something went wrong,else return model
# return Ticket Model if specified,return last created model if Ticket is None
def getTrainedModel(UserName, ClassifierName, Ticket=None):
	Path = Model_Path + "User_" + UserName + "/" + ClassifierName + "/"
	if exists(Path):
		if Ticket is None:  # return last created Model
			list_of_files = glob.glob(join(Path, "*.h5"))
			latest_file = max(list_of_files, key=getctime)
			Path += latest_file
			if exists(Path):
				try:
					model = load_model(Path)
					return model
				except:
					print("FROM getTrainedModel: got problem while loading " + Path + " returning None")
					return None
			else:
				print("FROM getTrainedModel: No Models for this User and this Classifier")
				return None
		else:
			CheckPath = Model_Path + "User_" + Ticket.split("_")[1] + "/" +Ticket.split("_")[0] + "/"
			# need to check, because in the ticket name are included user and classifier name
			if Path == CheckPath:
				Path += Ticket + ".h5"
				if exists(Path):
					try:
						model = load_model(Path)
						return model
					except:
						print("FROM getTrainedModel: got problem while loading " + Path + " returning None")
						return None
				else:
					print("FROM getTrainedModel: This Model doesn't exist")
					return None
			else:
				print("FROM getTrainedModel: Username or Classifier Name different from Ticket")
				return None
	else:
		print("FROM getTrainedModel: Wrong Username or Classifier Name")
		return None


def InsertNewModel(model, model_name, user_name, classifier_name):  # NEVER use _ or / in model_name
	# insert model as User_user_name/classifier_name/model_name.h5

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
	file = open(Path + "Model_info.Json", 'r')
	try:
		Models = json.load(file)
	except:
		file.close()
		print("From Train_Classifier: " + Path + "Model_info.Json is corrupted")
		return None
	file.close()
	try:
		model.save(Path + model_name + ".h5")
		if exists(Path + model_name + ".h5"):
			print("From InsertNewClassifier: " + Model_Path + model_name + " already exist, overwriting")
		Models.update({model_name: "ready"})
		file = open(Path + "Model_info.Json", 'w')
		json.dump(Models, file)
		file.close()
	except:
		print("From InsertNewClassifier: invalid model")


def get_Models_Name():  # return all the Classifier name in the classifier folder
	if exists(Model_Path[0:(len(Model_Path)-1)]):
		for file in glob.glob(Model_Path + "*/*/" + "*.h5"):
			name = str(file)
			path = name.split("/")
			path = path[0] + "/" + path[1] + "/" + path[2]
			name = name.split(".")[0] + "." + name.split(".")[1]
			name = name.split("/")
			name = name[len(name)-1]
			if exists(path + "/Model_info.Json"):
				info_file = open(path + "/Model_info.Json", 'r')
				try:
					Models = json.load(info_file)
					print(name + "   Status = " + Models[name])
				except:
					print(name)
			else:
				print(name)

#Delete_Model("GiacomoGiorgi", 1, "Classifier64810", "Classifier64810_GiacomoGiorgi__2019-11-2211:19:18.237318 (copia)")
InsertNewClassifier(getTrainedModel("GiacomoGiorgi", "Classifier64810", "Classifier64810_GiacomoGiorgi__2019-11-2213:35:47.35011"), "Classifier64810_GiacomoGiorgi__2019-11-2213:35:47.350115NEW", "GiacomoGiorgi", "Classifier64810")