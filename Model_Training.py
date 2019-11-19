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
#test import
from DB_func import getSensorsData


def summarize_results(scores):
    print(scores)
    m, s = mean(scores), std(scores)
    print('Accuracy: %.3f%% (+/-%.3f)' % (m, s))


def fit_network_thread(filename, classifileName, activity, axes, device, probability, sensor, user, timestart, timeend, verbose, epochs, batch_size, testperc,Validation,repeats):
    #need to change this with a call to getSensorData on db server
    Json = getSensorsData(activity, axes, device, probability, sensor, user, timestart, timeend)
    trainX, trainY, testX, testY, validationX, validationY, Gyro_array, Gyro_labels, Gyro_test, Gyro_test_labels, Gyro_Validation, Gyro_Validation_labels= Prepare_Data(Json, classifileName, Validation, testperc)
    scores = list()
    model = load_model(Classifier_Path + classifileName + '.h5')
    # giacomo devo effettuare repeats volte l'esperimento? se NO => eliminare +str(r)+ al prossimo giacomo
    with open(filename + '.txt', 'a') as file:  # putting stats inside filename.txt
        with redirect_stdout(file):
            for r in range(repeats):
                model.fit(trainX, trainY, epochs=epochs, batch_size=batch_size, verbose=verbose, validation_data=(validationX, validationY))
                _, accuracy = model.evaluate(testX, testY, batch_size=batch_size, verbose=1)  # evaluate model
                score = accuracy
                score = score * 100.0
                print('>#%d: %.3f' % (r + 1, score))
                scores.append(score)
            model.save(filename + str(r) + '.h5')# giacomo salvo 1 modello ogni repeat
            summarize_results(scores)
            file.close()


def Train_Classifier(classifierName, activity, axes, device, probability, sensor, user, timestart, timeend, verbose, epochs, batch_size, testperc, Validation=False, repeats=1):
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
    filename = Model_Path + "User_" + user+'/'+classifierName+'/'+ ticket
    # let another thread finish execute code and give back the ticket to client
    thread = Thread(target=fit_network_thread, args=(filename, classifierName, activity, axes, device, probability, sensor, user, timestart, timeend, verbose, epochs, batch_size, testperc,Validation,repeats,))
    thread.start()
    return ticket

print("ticket = ",Train_Classifier("Classifier2" , None, None, None, None, None, "GiacomoGiorgi", None, None, 1, 2, 64 , 20 , True , 1))