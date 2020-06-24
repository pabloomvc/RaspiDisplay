import pyrebase
from tkinter import *
from bs4 import BeautifulSoup
import requests
from threading import Timer
from datetime import datetime
import webbrowser
import time
import pygame
import subprocess
from PIL import Image, ImageTk

config = {
    'apiKey': "AIzaSyDqfcRf6eyzWOHSkTiz8x6eR4IspTg4Oqg",
    'authDomain': "raspidisplay-74f02.firebaseapp.com",
    'databaseURL': "https://raspidisplay-74f02.firebaseio.com",
    'projectId': "raspidisplay-74f02",
    'storageBucket': "raspidisplay-74f02.appspot.com",
    'messagingSenderId': "347511820457",
    'appId': "1:347511820457:web:3b9c075c87b5dbcd57d9b8"
}

def clearFrame(frame):
    # destroy all widgets from frame
    for widget in frame.winfo_children():
       widget.destroy()

def clock():
    t=time.strftime('%H:%M',time.localtime())
    if t!='':
        timeLabel.config(text=t)
    window.after(100,clock)

def getWeather():
    # Set the URL you want to webscrape from
    url = """https://weather.com/en-GB/weather/today/l/a64186d9cfcc8ba1b5212834f28d189fc0699cbdd1c364c40920bbe4fbb0a7ea"""
    # Connect to the URL
    response = requests.get(url)
    # Parse HTML and save to BeautifulSoup object
    soup = BeautifulSoup(response.text, "html.parser")
    #Temperatura actual
    currentTemp = soup.find('span',{"data-testid": "TemperatureValue"}).text
    desc = soup.find('div', {"data-testid": "wxPhrase"}).text
    #print(currentTemp, desc)
    #Maxima y minima
    lista = list(soup.find('div', {"class": "_-_-components-src-organism-CurrentConditions-CurrentConditions--tempHiLoValue--3T1DG"}))
    maxTemp = lista[0].text
    minTemp = lista[2].text
    #Load corresponding image
    print(list(desc))
    weatherImages = {
        'Sunny':['Sunny', 'Fair', 'Clear'], 
        'Partly Cloudy':['Partly Cloudy'],
        'Mostly Cloudy': ['Mostly Cloudy', 'Cloudy'],
        'Rainy': ['Rainy','Showers','PM Showers', 'AM Showers', 'Rain']
        }
    for image in weatherImages.keys():
        if desc in weatherImages[image]:
            imageName = image

    img = ImageTk.PhotoImage(Image.open('/home/pi/Documents/Projects/Dashboard/RaspiDisplay/Images/{}.jpg'.format(imageName)).resize((150, 150)))
    #print("Max: {}C / Min: {}C".format(maxTemp,minTemp))
    weather_data = {"currentTemp":currentTemp, "description":desc, "maxTemp":maxTemp, "minTemp":minTemp, "image":img}
    return weather_data

def get_news():
    url = "https://news.ycombinator.com/"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = soup.find_all('a',class_='storylink')
    data = []
    for i in range(min(10,len(links))):
        pair = (links[i].get_text(),links[i].get('href'))
        data.append(pair)
    return data

def open_website(url):
    webbrowser.open(url)

def init_storage():
    firebase = pyrebase.initialize_app(config)
    storage = firebase.storage()
    return storage

def init_window():
    window = Tk()
    #window.geometry('1200x600')
    window.attributes('-fullscreen', 1)
    window.title('Welcome')
    return window

def control_tv(command):
    if command == "on":
        subprocess.Popen("echo 'on 0' | cec-client -s -d 1")
    elif command == "off":
        subprocess.Popen("echo 'standby 0' | cec-client -s -d 1")
    else:
        pass

def update_weather():
    weather_data = getWeather()
    clearFrame(frame_weather)
    Label(frame_weather, text="Weather Today", bg='#f0c000', pady=5, font=('Arial', 12, 'bold')).pack(fill='x')
    imgLabel = Label(frame_weather, image=weather_data['image'],borderwidth=0, highlightthickness = 0)#,borderwidth=0, highlightthickness = 0
    imgLabel.image = weather_data['image']
    imgLabel.place(x=10, y=40)
    temp_pos_y = 45
    Label(frame_weather, text=weather_data['currentTemp'], font=('Arial Bold', 60), bg="#186090", fg="white").place(x=dim['weather'][0]*0.4,y=temp_pos_y)
    Label(frame_weather, text=weather_data['description'], font=('Arial Bold', 20), bg="#186090", fg="white").place(x=dim['weather'][0]*0.4+5,y=dim['weather'][1]*0.58)

def update_news():
    news = get_news()
    clearFrame(frame_news)
    Label(frame_news, text="What's new today", bg='#f0c000', pady=5, font=('Arial', 12, 'bold')).pack(fill='x')
    for n in range(len(news)):
        Label(frame_news, text='{}) {}'.format(n+1,news[n][0]), anchor="w", width=72, bg="#113455", fg="white", relief="solid",font=('Arial Bold', 12)).pack(padx=10,pady=12)
        if n<9:
            window.bind('{}'.format(n+1), lambda event, url = news[n][1]: open_website(url)) 
        else:
            window.bind('0', lambda event, url = news[n][1]: open_website(url))

def update_todo():
    # Download todo from the cloud
    path_todo_cloud = 'dailyFiles/todo.txt'
    path_todo_local = "/home/pi/Documents/Projects/Dashboard/RaspiDisplay/todo.txt"
    storage.child(path_todo_cloud).download('/home/pablo/PythonScripts/RaspiDisplay/todo.txt')
    clearFrame(frame_todo)
    Label(frame_todo, text="For today", bg='#f0c000', pady=5, font=('Arial', 12, 'bold')).pack(fill='x')
    with open(path_todo_local) as file:
        for line in file:
            print(line)
            Label(frame_todo, text='● '+ line.rstrip('\n'), anchor="w", width=40, font=('Arial', 18, 'bold'), fg="white", bg="#185D8C").pack(padx=20,pady=15)

def update_routine():
    # Download morning routine from the cloud
    #path_todo_cloud = 'dailyFiles/todo.txt' #THIS IS GONNA BE CHANGED
    path_todo_local = "/home/pi/Documents/Projects/Dashboard/RaspiDisplay/todo.txt" #THIS IS GONNA BE CHANGED
    #storage.child(path_todo_cloud).download('/home/pablo/PythonScripts/RaspiDisplay/todo.txt') #THIS IS GONNA BE CHANGED
    clearFrame(frame_routine)
    Label(frame_routine, text="Morning Routine", bg='#f0c000', pady=5, font=('Arial', 12, 'bold')).pack(fill='x')
    with open(path_todo_local) as file:
        for line in file:
            print(line)
            Label(frame_routine, text='● '+ line.rstrip('\n'), anchor="w", width=40, font=('Arial', 18, 'bold'), fg="#184878", bg="#B4E4E4").pack(padx=20,pady=15)


def update_alarm():
    # Download Alarm_Time from the cloud
    print('Downloading Alarm Time from Firebase')
    path_alarm_time_cloud = 'dailyFiles/Alarm_Time.txt'
    path_alarm_time_local = "/home/pi/Documents/Projects/Dashboard/RaspiDisplay/Alarm_Time.txt"
    storage.child(path_alarm_time_cloud).download(path_alarm_time_local)
    time.sleep(20)
    with open(path_alarm_time_local) as file:
        for line in file:
            line = line.split(':')
            hour = line[0]
            minute = line[1].rstrip('\n')
    alarm_label.config(text='{}:{}'.format(hour, minute), font=('Arial Bold', 30))
    alarm_label.pack(padx=40, pady=20)
    print('Alarm is gonna be set at {}:{}'.format(hour, minute))
    return (hour, minute)
############## FUNCIONES DE LA ALARMA #####################

def wake_up():
    pygame.mixer.init()
    pygame.mixer.music.load("/home/pi/Documents/Projects/Dashboard/RaspiDisplay/finale.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

def calculo_dt(alarm_h, alarm_m):
    #returns the number of seconds until the alarm is supposed to ring
    date = time.localtime()
    hour, minute, second = date.tm_hour*3600, date.tm_min*60, date.tm_sec
    print('Current time {}:{}:{}'.format(date.tm_hour, date.tm_min, date.tm_sec))
    converted_time = hour+minute+second
    converted_alarm = (int(alarm_h)*3600)+(int(alarm_m)*60)    
    delta = converted_alarm - converted_time

    if delta < 0:
        dif = (24*3600) - converted_time
        dt = converted_alarm + dif
    else:
        dt = delta
    return dt

def set_alarm():
    #dt_to_check_fb = calculo_dt(3,0)
    print('Checking Firebase in (1) second(s)')
    t1 = Timer(1, update_All)
    t1.start()


# If things are working properly consider changing the name of this function to 'update_all',
# and create a function 'update_alarm' where i'll put all the setting the alarm process
def update_All():
    update_weather()
    update_news()
    update_todo()
    update_routine()
    hour, minute = update_alarm()

    print('Calculating time until waking up, and setting the alarm')
    dt = calculo_dt(int(hour),int(minute))
    time.sleep(dt-60)
    control_tv("on")
    time.sleep(60)
    print('Ring!!!')
    wake_up()
    dt_to_check_fb = calculo_dt(3,0)
    time.sleep(dt_to_check_fb)
    update_All()
######################################################################


#Initializing window. Window and timeLabel need to be global to be accessed by the clock function
window = init_window()


#################################### SET FRAMES ########################################
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
dim = {
    # (width, height)
    'current time' : (round(screen_width * 0.31), round(screen_height * 0.26)),
    'alarm time' : (round(screen_width * 0.31), round(screen_height * 0.14)),
    'weather' : (round(screen_width * 0.31), round(screen_height * 0.3)),
    'news' : (round(screen_width * 0.44), round(screen_height * 0.7)),
    'todo' : (round(screen_width * 0.25), round(screen_height * 0.4)),
    'routine' : (round(screen_width *0.25), round(screen_height * 0.6)),
    'motivation' : (round(screen_width * 0.75), round(screen_height * 0.3))
}

frame_current_time = Frame(window, bg="#186090", width= dim['current time'][0], height=dim['current time'][1])
frame_current_time.pack_propagate(False)
frame_current_time.place(x = 0,y = 0)
Label(frame_current_time, text="Current time", bg='#f0c000', pady=5,font=('Arial', 12, 'bold')).pack(fill='x')

frame_alarm_time = Frame(window, bg="#3090a8", width=dim['alarm time'][0], height=dim['alarm time'][1])
frame_alarm_time.pack_propagate(False)
frame_alarm_time.place(x = 0,y = dim['current time'][1])
Label(frame_alarm_time, text="Alarm set at", bg='#f0c000', pady=5 ,font=('Arial', 12, 'bold')).pack(fill='x')

frame_weather = Frame(window, bg="#186090", width=dim['weather'][0], height=dim['weather'][1])
frame_weather.pack_propagate(False)
frame_weather.place(x = 0,y =dim['current time'][1] + dim['alarm time'][1])
Label(frame_weather, text="Weather today", bg='#f0c000', pady=5, font=('Arial', 12, 'bold')).pack(fill='x')

frame_news = Frame(window, bg="#184878", width=dim['news'][0], height=dim['news'][1])
frame_news.pack_propagate(False)
frame_news.place(x = dim['current time'][0],y = 0)
Label(frame_news, text="What's new today", bg='#f0c000', pady=5,font=('Arial', 12, 'bold')).pack(fill='x')

frame_routine = Frame(window, bg="#90d8d8", width=dim['todo'][0], height=dim['todo'][1])
frame_routine.pack_propagate(False)
frame_routine.place(x = dim['current time'][0] + dim['news'][0],y = 0)
Label(frame_routine, text='Morning Routine!', bg='#f0c000', pady=5, font=('Arial', 12, 'bold')).pack(fill='x')

frame_todo = Frame(window, bg="#186090", width=dim['routine'][0], height=dim['routine'][1])
frame_todo.pack_propagate(False)
frame_todo.place(x = dim['current time'][0] + dim['news'][0],y = dim['todo'][1])
Label(frame_todo, text="For today", bg='#f0c000', pady=5, font=('Arial', 12, 'bold')).pack(fill='x')

frame_motivation = Frame(window, bg="#001830", width=dim['motivation'][0], height=dim['motivation'][1])
frame_motivation.pack_propagate(False)
frame_motivation.place(x = 0,y = dim['current time'][1] + dim['alarm time'][1] + dim['weather'][1])
Label(frame_motivation, text="You got this!", bg='#f0c000', pady=5, font=('Arial', 12, 'bold')).pack(fill='x')


# Current time label
timeLabel=Label(frame_current_time,justify='center',padx=30, pady=10, bg="#186090", fg="white",font=("Arial Bold", 70))
timeLabel.place(x=40,y=60)
clock()

# Initializing storage reference
storage = init_storage()

# Alarm time container and label
alarm_label = Label(frame_alarm_time, text='Getting time from Firebase', bg="#3090a8",fg="white",font=("Arial Bold", 18))
alarm_label.pack(fill='x')


def main():

    set_alarm()
    window.bind()
    window.mainloop()

main()
