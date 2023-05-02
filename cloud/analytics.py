import matplotlib
matplotlib.use('agg')

from unittest import result
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime
import matplotlib.pyplot as plt
import base64

MET = 3.5


uri = "mongodb+srv://Akhil:adspassword@cluster0.46dip.mongodb.net/test"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['ADSProjectData']
collection = db['healthData']
user_data = db['users']

def get_report(userId,period):
    heartrate_data = []
    heartrate_aggregate = 0
    systolic_bloodpressure_aggregate = 0
    diastolic_bloodpressure_aggregate = 0
    counter = 1
    today = datetime.datetime.today()
    formatted_date = today - datetime.timedelta(days=period)
    start_time = datetime.datetime.combine(formatted_date.date(), datetime.time.min).isoformat()
    end_time = datetime.datetime.combine(today.date(), datetime.time.max).isoformat()


    steps_query = {'timestamp': {'$gte': start_time, '$lt': end_time}}

    results = collection.find(steps_query)
    if collection.count_documents(steps_query) != 0:
        for result in results:
            heartrate_aggregate += result['heartbeat']
            systolic_bloodpressure_aggregate += result['bp']['systolic']
            diastolic_bloodpressure_aggregate += result['bp']['diastolic']
            counter += 1
    average_heartrate = round(heartrate_aggregate/counter)
    average_systolic = round(systolic_bloodpressure_aggregate/counter)
    average_diastolic = round(diastolic_bloodpressure_aggregate/counter)
    print(average_heartrate,average_systolic,average_diastolic)
    return {'average_heartrate':average_heartrate,
            'average_systolic':average_systolic,
            'average_diastolic':average_diastolic
            }

def get_calories_info(userId,period):
    steps = 0
    exercise_factor = {1 : 1.2,
                       2 : 1.375,
                       3 : 1.55,
                       4 : 1.725,
                       5 : 1.9}
    steps_query = {'email' : userId}
    results = list(user_data.find(steps_query))
    if user_data.count_documents(steps_query) != 0:
        weight          = results[0]['weight']
        gender          = results[0]['gender']
        height          = results[0]['height']
        age             = results[0]['age'] 
        exercise_activity = results[0]['exercise_activity']
    today = datetime.datetime.today()
    formatted_date = today - datetime.timedelta(days=period)

    start_time = datetime.datetime.combine(formatted_date.date(), datetime.time.min).isoformat()
    end_time = datetime.datetime.combine(today.date(), datetime.time.max).isoformat()

    steps_query = {'timestamp': {'$gte': start_time, '$lt': end_time}}
    results = collection.find(steps_query)
    for result in results:
        steps += result['stepcount']
    print(f'steps {steps}')
    calories_burnt = round(((MET * 3.5 * weight) / 2000) * steps)
    print(calories_burnt)

    if gender == 'M':
        BMR = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    else:
        BMR = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
    calories_to_be_burnt = BMR * exercise_factor[exercise_activity] * period
    print(calories_to_be_burnt)

    steps_required = round(((calories_to_be_burnt - calories_burnt) / ( weight * 0.69)) * 70) * period
    print(steps_required)

    if gender == 'M':
        stride = (height * 0.415)/100 
    else:
        stride = (height * 0.413)/100
    distance = round((steps * stride)/1000,2)
    print(distance)

    fig, ax = plt.subplots()
    values = [steps, steps_required-steps]
    labels = ['Steps walked', 'Steps need to be completed']
    colors = ['red', 'grey']
    # Plot
    ax.pie(values, labels=labels, colors=colors, startangle=90,wedgeprops={'width': 0.5},pctdistance=0.85,autopct='%1.1f%%')
    ax.set_title('Steps Calculator')
    # Show the plot
    # plt.show()
    fig.savefig("steps.png")

    fig, ax = plt.subplots()
    values = [calories_burnt, calories_to_be_burnt-calories_burnt]
    labels = ['Calories burnt', 'Calories to be burnt']
    colors = ['red', 'grey']
    # Plot
    ax.pie(values, labels=labels, colors=colors, startangle=90, wedgeprops={'width': 0.5},pctdistance=0.85,autopct='%1.1f%%')
    ax.set_title('Calories Calculator')

    # Show the plot
    # plt.show()
    # encode the figure as PNG and write it to a byte buffer
    # buf = io.BytesIO()
    plt.savefig("calories.png")
    # img_data=getImageEncode("calories.png")
    # 'calorie_chart':img_data
    return {'step_count':steps,'steps_required':steps_required,'distance_travlled':distance,'calories_burnt':calories_burnt,'calories_to_be_burnt':calories_to_be_burnt}

def getImageEncode(filename):
    print('generating image')
    with open(filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    print('ended')
    return encoded_string
        