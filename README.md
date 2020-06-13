# RaspiDisplay
A Tkinter based display for Raspberry Pi, aimed at helping you wake up better in the morning. Among other things, this display will serve as an alarm clock, will display the current time, will show you your to-do list for the day and will scrape news from the internet and display them on screen for you to see in the morning.

Details:
- The display uses Tkinter as a GUI framework. 
- To serve as an alarm clock, the program access and downloads a text file stored in a Firebase project (for which it uses the Pyrebase library), obtaining the time the user wants to wake up at. Calculates the time until the alarm time, and then plays a song using Pygame. The program executes the alarm functionality on a different thread, which spends most of its time sleeping, trying to minimize the use of resources. 
- The program scrapes the top 10 news from Hacker News, and displays them on screen. In addition to this, each one of the number keys in the keyboard are binded with each one of the news. This way, by pressing any number key, the corresponding new will be open in the Raspberry Pi's default browser.
- The To-do list for the day is obtained from Firebase as well. Although in the future I would like the program to access some calendar online. 

