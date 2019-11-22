from keras.models import load_model
from contextlib import redirect_stdout
from datetime import datetime
from threading import Thread
from numpy import mean
from numpy import std
from os import makedirs
from os.path import exists
from Info.Paths import Classifier_Path, Model_Path
from Prepare_Data import Prepare_Data
import json

#test import
from DB_func import getSensorsData


def summarize_results(scores):
    print(scores)
    m, s = mean(scores), std(scores)
    print('Accuracy: %.3f%% (+/-%.3f)' % (m, s))


# fit_network_thread to fit the network in a separated thread
def fit_network_thread(filename, classifierName, activity, axes, device, probability, sensor, user, timestart, timeend, verbose, epochs, batch_size, testperc, ag, Xvalidation, cross_val_repeat):
    # need modify to use cross validation
    # need to change this with a call to getSensorData on db server
    Json = getSensorsData(activity, axes, device, probability, sensor, user, timestart, timeend)
    array, labels, test, test_labels, Validation, Validation_labels = Prepare_Data(Json, classifierName, Xvalidation, testperc, ag)
    file_info = Model_Path + "User_" + user+'/' + classifierName + '/' + "Model_info.Json"
    if exists(file_info):
        info_file = open(file_info, 'r')
        try:
            Models = json.load(info_file)
        except:
            print("From fit_network_thread: " + file_info + " is corrupted")
            info_file.close()
            return
        info_file.close()
        info_file = open(file_info, 'w')
        if array is None or labels is None or test is None or test_labels is None or Validation is None or Validation_labels is None:
            print("From fit_network_thread: something went wrong with parameters creation, please try again")
            Models.update({filename: "error"})
            json.dump(Models, info_file)
            info_file.close()
        else:
            scores = list()
            model = load_model(Classifier_Path + classifierName + '.h5')
            with open(filename + '.txt', 'a') as file:  # putting stats inside filename.txt
                with redirect_stdout(file):
                    for r in range(cross_val_repeat):
                        model.fit(array, labels, epochs=epochs, batch_size=batch_size, verbose=verbose, validation_data=(Validation, Validation_labels))
                        _, accuracy = model.evaluate(test, test_labels, batch_size=batch_size, verbose=1)  # evaluate model
                        score = accuracy
                        score = score * 100.0
                        print('>#%d: %.3f' % (r + 1, score))
                        scores.append(score)
                    model.save(filename + '.h5')
                    summarize_results(scores)
                    file.close()
            Models.update({filename: "ready"})
            json.dump(Models, info_file)
            info_file.close()
    else:
        print("From fit_network_thread: " + file_info + " does not exist")


# Train a classifier with data from PeronalDevicesDb and return a ticket to take the created Model
# if ticket is None  Model_info.Json was corrupted
def Train_Classifier(classifierName, activity, axes, device, probability, sensor, user, timestart, timeend, verbose, epochs, batch_size, testperc, ag, Validation=False, cross_val_repeat=1):
    now = str(datetime.now())
    now = now.replace(" ", "")
    Model_Path_Check = Model_Path[0:(len(Model_Path)-1)]  # don't consider "/"
    # creating working space
    if not exists(Model_Path_Check):
        makedirs(Model_Path_Check)
    if not exists(Model_Path+"User_"+user):
        makedirs(Model_Path+"User_"+user)
    if not exists(Model_Path + "User_" + user+'/'+classifierName):
        makedirs(Model_Path + "User_" + user+'/'+classifierName)

    # ticket that give back to client
    ticket = classifierName + "_" + user + "__" + now
    filename = Model_Path + "User_" + user+'/' + classifierName + '/' + ticket

    if not exists(Model_Path + "User_" + user+'/'+classifierName+'/'+"Model_info.Json"):
        file = open(Model_Path + "User_" + user+'/'+classifierName+'/'+"Model_info.Json", 'w')
        file.write("{\n}\n")
        file.close()
    else:
        file = open(Model_Path + "User_" + user+'/'+classifierName+'/'+"Model_info.Json", 'r')
        try:
            Models = json.load(file)
        except:
            file.close()
            print("From Train_Classifier: " + Model_Path + "User_" + user + '/' + classifierName + '/' + "Model_info.Json is corrupted")
            return None
        file.close()
        Models.update({filename: "in_progress"})
        file = open(Model_Path + "User_" + user + '/' + classifierName + '/' + "Model_info.Json", 'w')
        json.dump(Models, file)
        file.close()
    # let another thread finish execute code and give back the ticket to client
    thread = Thread(target=fit_network_thread, args=(filename, classifierName, activity, axes, device, probability, sensor, user, timestart, timeend, verbose, epochs, batch_size, testperc, ag, Validation, cross_val_repeat,))
    thread.start()
    return ticket

print("ticket = ",Train_Classifier("Classifier64810" , None, None, None, None, None, "GiacomoGiorgi", None, None, 1, 2, 64 , 20 , 0, True , 1))