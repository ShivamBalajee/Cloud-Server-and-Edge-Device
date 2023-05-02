import json

import pymongo
from bson import json_util
from flask import Flask, request, jsonify,Response
from bson.objectid import ObjectId
import analytics
import symptoms


app = Flask(__name__)


# client = pymongo.MongoClient(
        # "mongodb://ADSProject:forADSProject123@cluster0-shard-00-00.46dip.mongodb.net:27017,cluster0-shard-00-01.46dip.mongodb.net:27017,cluster0-shard-00-02.46dip.mongodb.net:27017/?ssl=true&replicaSet=atlas-2y92ub-shard-0&authSource=admin&retryWrites=true&w=majority")
# uri = "mongodb+srv://Akhil:adspassword@cluster0.46dip.mongodb.net/test"
# client = pymongo.MongoClient(uri)

client = pymongo.MongoClient('mongodb://mongo')
db = client["ADSProjectData"]
collection = db["healthData"]
userCollection=db['users']
receivedData = []

@app.route('/startCloudServer', methods=['POST'])
def startCloudServer():
    # receiving data from edge
    receivedData = request.get_json(force=True) # force=True is necessary if another developer forgot to set the MIME type to 'application/json'

    # print('receivedData: ', receivedData)

    # now send this received data to MongoDB
    collection.insert_many(receivedData)

    # reading the data from Mongo db to perform analytics
    dbData = []
    # print('data fetched from MongoDB. ')
    for i in collection.find():
        # print(i)
        dbData.append(i)
    return json.loads(json_util.dumps(dbData))

@app.route('/createUser', methods=['POST'])
def createUser():
    data = request.get_json(force=True)
    name = data['name']
    height = str(data['height'])
    weight = str(data['weight'])
    gender = data['gender']
    email=str(data['email'])
    user = {'name': name, 'height': height, 'weight': weight, 'gender': gender,'email':email}
    result = userCollection.insert_one(user) # Insert the user data to the 'users' collection
    return jsonify({'message': 'User created successfully', 'user_id': str(result.inserted_id)})

@app.route('/getUser/<userid>', methods=['GET'])
def getUsers(userid):
    user=userCollection.find_one({'email':userid },{'_id': 0})
    if user:
            # Serialize the user object to JSON
            json_user = json.dumps(user)

            # Return the JSON user object with a 'Content-Type' header of 'application/json'
            return Response(json_user, content_type='application/json')
    else:
        # Return a 404 error if the user is not found
        return 'User not found', 404

@app.route('/getAnalytics/<userId>/<numOfDays>', methods=['GET'])
def getAnalytics(userId,numOfDays):
    # monthly
    # weekly
    report=analytics.get_report(userId,int(numOfDays))
    calory_info=analytics.get_calories_info(userId,int(numOfDays))
    report.update(calory_info)
    return json.dumps(report)

@app.route('/getPrecautions', methods=['GET'])  
def getPrecautions():
    precuations=symptoms.get_precautions()
    return json.dumps(precuations)

app.run('0.0.0.0', 8081)
