from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense
from keras.layers import Dropout
from Info.Paths import Classifier_Path
from os import makedirs
from os.path import exists


#from Data_Management import load_dataset # delete is a test import

def Fake_model(trainX,trainY,name): #create fake model,in real API DEV will give me a real one,store them in Model/name
	n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainY.shape[1]

	#da qui a QUI1 funzione per creare il modello di un classificatore+ aggiungere parte per metterlo in un file,serve per creare ciò che mi serve per simulare
	#un modello per il classificatore che invece in futuro passerà il DEV già pronti
	model = Sequential()
	model.add(LSTM(100, input_shape=(n_timesteps,n_features)))
	model.add(Dropout(0.5))
	model.add(Dense(100, activation='relu'))
	model.add(Dense(n_outputs, activation='softmax'))
	model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
	if not exists(Classifier_Path):
		makedirs(Classifier_Path)
	model.save(Classifier_Path+name+'.h5')


#trainX, trainY, testX, testY, validationX, validationY = load_dataset("UCI ",True)  #delete
#Fake_model(trainX,trainY,"Classifier1")  #delete