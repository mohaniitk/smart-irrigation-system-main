#subscriber file
import paho.mqtt.client as mqtt
import time
import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

i = 0

def pred_on_testData(data):
    ml_model = tf.keras.models.load_model("iot_pred.model")
    prediction = abs(ml_model.predict(data[:,:-1]))
    return prediction

def on_connect(client,userdata,flags,rc):
    print(f"connected with status code {rc}")	
    client.subscribe("bachelors/sensor_values")
    client.subscribe("bachelors/prediction")


def on_message(client,userdata, msg):
    global i
    if msg.topic == "bachelors/sensor_values":
        
        txt1 = str(msg.payload).split("'")
        if txt1[1] != 'null':
            txt = txt1[1].split("_")
            humidity = float(txt[1])
            temperature = float(txt[2])

            print("Humidity = " + str(humidity) + "%")
            print("Temperature = " + str(temperature) + " C")

        else:
            print("Null")

        h = hum_temp[i][0]
        t = hum_temp[i][1]
        p = predictions[i][0]

        pl = str(h) + "_" + str(t) + "_" + str(p)
        client.publish("bachelors/prediction", payload=pl, qos=0, retain=False)

        if i < testDataSize-1:
            i = i+1

        else:
            i = 0


        time.sleep(10)
        # client.publish("bachelors/prediction", payload=pl, qos=0, retain=False)
    # time.sleep(1)

testData = np.loadtxt('test_data.txt')
origData = pd.read_csv("sensor_data.csv")
predictions = pred_on_testData(testData)
testDataSize = predictions.size

lx_tst = testData[:, :-1]
orig_x = np.array(origData.iloc[:,:-1])

scaler = MinMaxScaler()
scaler.fit(orig_x)
hum_temp = scaler.inverse_transform(lx_tst) 

client = mqtt.Client()
client.connect("169.254.90.86",1883,60) #add ip address of the server, localhost gives the self ip address
# client.connect("192.168.214.75",1883,60) #add ip address of the server, localhost gives the self ip address
client.on_connect = on_connect
client.on_message = on_message


client.loop_forever()