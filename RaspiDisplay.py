import pyrebase
from tkinter import *
from bs4 import BeautifulSoup
import requests
from threading import Timer
from datetime import datetime
import webbrowser
import time
import pygame

config = {
    'apiKey': "AIzaSyDqfcRf6eyzWOHSkTiz8x6eR4IspTg4Oqg",
    'authDomain': "raspidisplay-74f02.firebaseapp.com",
    'databaseURL': "https://raspidisplay-74f02.firebaseio.com",
    'projectId': "raspidisplay-74f02",
    'storageBucket': "raspidisplay-74f02.appspot.com",
    'messagingSenderId': "347511820457",
    'appId': "1:347511820457:web:3b9c075c87b5dbcd57d9b8"

}

def clock():
    t=time.strftime('%H:%M:%S',time.localtime())
    if t!='':
        timeLabel.config(text=t,font='Arial 35')
    window.after(100,clock)

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
    window.geometry('700x400')
    #window.attributes('-fullscreen', 1)
    window.title('Welcome')
    return window

############## FUNCIONES DE LA ALARMA #####################
def wake_up():
    pygame.mixer.init()
    pygame.mixer.music.load("/home/pablo/PythonScripts/RaspiDisplay/finale.mp3")
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

def set_alarm(container):
    
    #dt_to_check_fb = calculo_dt(3,0)
    print('Checking Firebase in 10 seconds')
    t1 = Timer(10, download_alarm_time, args=[container])
    t1.start()


def download_alarm_time(container):
    # Download Alarm_Time from the cloud
    print('Downloading Alarm Time from Firebase')
    path_alarm_time_cloud = 'dailyFiles/Alarm_Time.txt'
    path_alarm_time_local = "/home/pablo/PythonScripts/RaspiDisplay/Alarm_Time.txt"
    storage.child(path_alarm_time_cloud).download('/home/pablo/PythonScripts/RaspiDisplay/Alarm_Time.txt')

    time.sleep(20)

    with open(path_alarm_time_local) as file:
        for line in file:
            line = line.split(':')
            hour = line[0]
            minute = line[1].rstrip('\n')
    
    container['hour'] = hour
    container['minute'] = minute
    alarm_label.config(text='{}:{}'.format(hour, minute))
    
    print('Alarm is gonna be set at {}:{}'.format(hour, minute))
    print('Calculating time until waking up, and setting the alarm')
    dt = calculo_dt(int(hour),int(minute))
    time.sleep(dt)

    print('Ring!!!')
    wake_up()
    dt_to_check_fb = calculo_dt(3,0)
    time.sleep(dt_to_check_fb)
    download_alarm_time(container)
######################################################################



#Initializing window. Window and timeLabel need to be global to be accessed by the clock function
window = init_window()
timeLabel=Label(window,justify='center',padx=30, pady=10, bg='lightblue')
timeLabel.grid(row=1, column=0)
clock()

# Initializing storage reference
storage = init_storage()

container = {'hour':'07', 'minute':'45'}
alarm_label = Label(window, text='{}:{}'.format(container['hour'],container['minute']), font=("Arial Bold", 40))


def main():

    set_alarm(container)
    window.bind()
    # Download todo from the cloud
    path_todo_cloud = 'dailyFiles/todo.txt'
    path_todo_local = "/home/pablo/PythonScripts/RaspiDisplay/todo.txt"
    storage.child(path_todo_cloud).download('/home/pablo/PythonScripts/RaspiDisplay/todo.txt')

    # Display greeting
    lbl = Label(window, text="Hello",font=("Arial Bold", 40))
    lbl.grid(column=0, row=0)

    # i controls the position of the elements within the first column. Starts at 2 cause 
    # 0 and 1 are taken by the initial greeting and the current time
    i=2 

    #Display alarm time label
    alarm_label.grid(row=i,column=0)
    i = i+1

    # Loading todo's and displaying them to screen
    Label(window, text='Morning Routine!',width=80, anchor="w", bg='orange', pady=5).grid(row=i,column=0)
    i = i+1
    with open(path_todo_local) as file:
        for line in file:
            print(line)
            Label(window, text=line.rstrip('\n'), anchor="w", width=80).grid(row=i, column=0)
            i = i+1

    #Load news data and displaying on screen
    Label(window, text="What's new today",width=80, anchor="w", bg='orange', pady=5).grid(row=i,column=0)
    i = i+1
    
    news = get_news()
    for n in range(len(news)):
        Label(window, text='{}) {}'.format(n+1,news[n][0]), anchor="w", width=80).grid(row=n+i, column=0)
        # Binding each new to a number key
        if n<9:
            window.bind('{}'.format(n+1), lambda event, url = news[n][1]: open_website(url)) 
        else:
            window.bind('0', lambda event, url = news[n][1]: open_website(url))


    window.mainloop()

main()
