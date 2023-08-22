import Adafruit_DHT
import paho.mqtt.client as mqtt
import board
import time
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd

lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d7 = digitalio.DigitalInOut(board.D11)
lcd_d6 = digitalio.DigitalInOut(board.D5)
lcd_d5 = digitalio.DigitalInOut(board.D6)
lcd_d4 = digitalio.DigitalInOut(board.D13)

lcd_columns = 20
lcd_rows = 4

lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 25

def on_connect(client,userdata, flags, rc):
    if rc==0:
        client.connected_flag=True
        print("connected with code : "+str(rc))
        client.subscribe("bachelors/sensor_values")
        client.subscribe("bachelors/prediction")
    else:
        print("Bad connection Returned code = ",rc)

def on_message(client,userdata,msg):
	if msg.topic == "bachelors/prediction":
		lcd.clear()
		#print(str(msg.payload))
		hum = str(msg.payload).split("'")[1].split('_')[0]
		temp = str(msg.payload).split("'")[1].split('_')[1]
		pred = str(msg.payload).split("'")[1].split('_')[2]
		hum = float(hum)
		hum = "{:.2f}".format(hum)
		temp = float(temp)
		temp = "{:.2f}".format(temp)
		pred = float(pred)
		pred = "{:.2f}".format(pred)
		#print("Humidity = " + str(hum)) 
		#print("Temperature = " + str(temp))
		#print("Water Flow Prediction = " + str(pred))
		dis_msg = "IOT Assignment\nHumidity = " + str(hum) + "%\nTemp = " + str(temp) + "F\nPrediction = " + str(pred) + "%"
		lcd.message = dis_msg

	time.sleep(3)



mqtt.Client.connected_flag = False
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(host = "localhost", port=1883, keepalive=60)
client.loop_start() # non-blocking loop, Loop_start starts a loop in another thread and lets the main thread continue

while not client.connected_flag:
    print("in waiting loop")
    time.sleep(1)

while(True):
	
	humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
	pl = "iot_" + str(humidity) + "_" + str(temperature)
	if humidity is not None and temperature is not None:
		client.publish("bachelors/sensor_values", payload=pl, qos=0, retain=False)
	else:
		client.publish("bachelors/sensor_values", payload="null", qos=0, retain=False)
	
    #client.publish("raspberry/topic", payload=i, qos=0, retain=False)
    #print(f"send {i} to raspberry/topic")
    
	time.sleep(3)

client.loop_stop()
client.disconnect()


