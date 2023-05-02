import time
from datetime import datetime
import datetime
import random
import numpy as np
from sklearn.covariance import EllipticEnvelope
import requests
import urllib.parse




def generateData():
    heartConditionNormal = True
    o2ConditionNormal = True
    bpConditionNormal = True

    # randomly decide if the measurements are going to be 'normal' or 'abnormal'
    isNormal = random.random() <= 0.85

    if not isNormal:
        heartConditionNormal = False
        o2ConditionNormal = False
        bpConditionNormal = False

    # IN NORMAL HEART CONDITIONS
    if heartConditionNormal:
        # resting heartbeat reading
        hb = random.randint(60, 100)
    else:  # for abnormal heartbeats, we fix a set of low and high values out of which any one will be picked randomly
        abnormalHB = [20, 24, 26, 30, 32, 110, 113, 123, 130, 135]
        hb = random.choice(abnormalHB)

    # blood oxygen reading
    if o2ConditionNormal:
        spO2 = random.randint(95, 100)
    else:
        abnormalO2 = [90, 91, 92, 93, 94, 89, 88, 87, 86, 85]
        spO2 = random.choice(abnormalO2)

    # blood pressure reading
    if bpConditionNormal:
        sys = random.randint(110, 119)
        dia = random.randint(76, 79)
    else:  # we maintain corresponding indices of both arrays with low or high values and then choose a random index from each
        abnormalSys = [100, 103, 108, 112, 115, 126, 130, 145, 157, 168, 174]
        abnormalDia = [55, 58, 61, 67, 75, 86, 89, 98, 102, 115]
        randIndex = random.randint(0, 9)
        sys = abnormalSys[randIndex]
        dia = abnormalDia[randIndex]
    
    # generate step count
    step_count = 0
    for i in range(3):  # generate 3 random numbers between 0 and 4 and add to step count
        step_count += random.randint(0, 4)


    # timestamp
    timestamp = datetime.datetime.now().isoformat()

    # print({
    #         "timestamp": timestamp,  # convert timestamp to string
    #         "hb": hb,
    #         "spO2": spO2,
    #         "bp":{
    #             "sys": sys,
    #             "dia": dia
    #         }
    #     })

    return str(timestamp), hb, spO2, sys, dia,step_count

def filterData(data):
    # Use an outlier detection method to identify and remove noise from the data
    X = np.array([d[2:] for d in data])  # Extract the measurements (excluding the timestamp)
    clf = EllipticEnvelope(contamination=0.10)
    clf.fit(X)
    y_pred = clf.predict(X)

    # Filter the data by only keeping the points that are not identified as outliers
    filteredData = []
    for i, datum in enumerate(data):
        if y_pred[i] == 1:  # If the point is not an outlier, keep it
            filteredData.append(datum)

    return filteredData

def sendDataToServer(data):
    json_data = []
    for d in data:
        user=d[0]
        timestamp = d[1]
        hb = d[2]
        spo2 = d[3]
        sys = d[4]
        dia = d[5]
        stepcount=d[6]
        json_data.append({"user":user,"timestamp": timestamp, "heartbeat": hb, "spO2": spo2, "bp": {"systolic": sys, "diastolic": dia},'stepcount':stepcount})
    # uncomment
    res = requests.post("http://cloud-service:8081/startCloudServer", json=json_data)
    # res = requests.post("http://10.0.0.217:8081/startCloudServer", json=json_data)
    
    print('res status code: ', res.status_code)
    # print('response text: ', res.text)

# @app.route('/generateData', methods=['POST'])

def main(userEmail):
    records=[]
    dataToFilter = []
    while True:
        # Generate new data every 5 seconds
        #uncomment
        time.sleep(3)
        timestamp, hb, spO2, sys, dia,stepcount = generateData()
        print('heart-beat',hb)
        # timestamp=add3sec(ts)
        # ts=timestamp


        records.append({
            'user':userEmail,
            "timestamp": timestamp,  # convert timestamp to string
            "hb": hb,
            "spO2": spO2,
            "bp":{
                "sys": sys,
                "dia": dia
            },
            'stepcount':stepcount
        })
        # also create a list of generated values to filter outliers later
        dataToFilter.append([userEmail,timestamp, hb, spO2, sys, dia,stepcount])
        # print(records)

        if len(records) == 15:
            filtered_data = filterData(dataToFilter)

            # send this batch of filtered data to cloud database
            sendDataToServer(filtered_data)

            # return
            # now clear 'records' and 'dataToFilter' to restart count from 0
            records.clear()
            dataToFilter.clear()


def getUser(userId):
    # uncomment
    try:
        res = requests.get(f"http://cloud-service:8081/getUser/{userId}")
        # res = requests.get(f"http://127.0.0.1:8081/getUser/{userId}")
        if not res:
            print('user email not found')
            return None
    except Exception as e:
        print(e)
        return
    print(res.json())
    return res.json()

def createDefaultUser():
    try:
        data = {
            "name": "Joe",
            "height": 170,
            "weight": 55,
            "gender": "M",
            "email": "test@gmail.com",
            "age": 24,
            "exercise_activity": 3
        }
        res = requests.post("http://cloud-service:8081/createUser",json=data)
        # res = requests.post(f"http://127.0.0.1:8081/createUser", json=data)
        print('user created successfully',res.status_code)
    except Exception as e:
        print(e)
        return

# app.run('0.0.0.0', 8082)
if __name__ == '__main__':
    # collect user info
    # userId=input('Enter your email :')
    encoded_email = urllib.parse.quote('test@gmail.com')
    userObj = getUser(encoded_email)
    if not userObj:
        createDefaultUser()
        encoded_email = urllib.parse.quote('test@gmail.com')
        userObj = getUser(encoded_email)

    main(userObj['email'])
