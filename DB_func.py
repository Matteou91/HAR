from influxdb import InfluxDBClient

import json
import jsonpickle
from Info.DB_Info import ServAddr,ServPort,DbName

class JsonTransformer(object):
    def transform(self, myObject):
        return jsonpickle.encode(myObject, unpicklable=False)

def getSensorsData(activity, axes, device, probability, sensor, user, timestart, timeend): #Get data from DB,some field could be set to None
    # timestart and timeend must be in correct timestamp format
    client = InfluxDBClient(host=ServAddr, port=ServPort, database=DbName)#connection to database #connection to database
    query='SELECT *  FROM "activities" WHERE '#query must accept "none" fields
    if(activity==axes==device==probability==sensor==user==timestart==timeend==None):#check if all fields are empty in this case remove WHERE
        query=query.replace(" WHERE ", '')
    #set control to 0 to future check, if need to add AND in the query
    control=0
    if(activity!=None):
        query+="\"activity\" = '"+activity+"'"
        control+=1
    if(axes!=None):
        if(control>=1):
            query+=" AND "
        query+="\"axes\" = '"+axes+"'"
        control+=1
    if(device!=None):
        if(control>=1):
            query+=" AND "
        query+="\"device\" = '"+device+"'"
        control+=1
    if(probability!=None):
        if(control>=1):
            query+=" AND "
        query+="\"probability\" = '"+probability+"'"
        control+=1
    if(sensor!=None):
        if(control>=1):
            query+=" AND "
        query+="\"sensor\" = '"+sensor+"'"
        control+=1
    if(user!=None):
        if(control>=1):
            query+=" AND "
        query+="\"user\" = '"+user+"'"
        control+=1
    if(timestart!=None):
        if(control>=1):
            query+=" AND "
        query+="time >=  "+"'"+timestart+"'"
        control+=1
    if(timeend!=None):
        if(control>=1):
            query+=" AND "
        query+="time <= "+"'"+timeend+"'"
    print("print query: "+query)#could be usefull to activate to see what are u querying
    result=client.query(query)
    transformToJson = JsonTransformer()
    jsonResult = transformToJson.transform(result)
    jsonResult=json.loads(jsonResult)
    return json.dumps(jsonResult, indent=4, sort_keys=True)