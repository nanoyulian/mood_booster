# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 04:36:35 2017

@author: nano
CPSS : Cyber Physical Social System
Mood Booster with music and light censor feedback
 
Requirements : 
1. python 2.7
2. mpg123 (install music player) pkill mpg123
3. Twitter API APP + Consumer Key + Access Token (untuk get tweet baru)
4. nltk API (model sentiment analysis komunitas twitter)
5. Twython library
6. raspberypi 3 B+ 
7. sensor cahaya modul/LDR

8. TODO : bluetooth On (Distance Sensor) 
    https://www.raspberrypi.org/forums/viewtopic.php?t=47466
    http://stackoverflow.com/questions/1996518/retrieving-the-output-of-subprocess-call    
    sudo apt-get install --no-install-recommends bluetooth
    hcitool scan 
        bluetooth smartphone 48:13:7E:4A:A8:A6 (Nano Yulian (SM-J110G))
9. TODO : Wireless On (Disance Sensor)
4c:66:41:5e:0b:00 

https://www.realvnc.com/docs/raspberry-pi.html remote
1. "scan sudo netdiscover -r 192.168.1.0/24 -i wls1"
2. ssh connect via putty ke ip raspberrypi
3. jalankan "vncserver" dan lihat ip:port 
4. pada laptop buka vncviewer dan masukkan ip:port dan connect
5. selesai. 

"""
import sys
import re
import urllib2
import json
import subprocess
from twython import Twython # pip install twython
import time # standard lib
from mood_setting import MoodSetting as ms
#import RPi.GPIO as GPIO #on raspi 3
from os import listdir
from os.path import isfile, join
from random import randint

# return None atau 1 (konek)
def checkBTLocation():  
    BTStatus = False
    
    cmd = 'rfcomm connect 0 ' + ms.BTDEVICE + ' 1 10> /dev/null >/dev/null &'
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)  
    
    cmd = 'hcitool rssi ' + ms.BTDEVICE
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    
    while True:
      line = p.stdout.readline()
      if not line:
         break
      #print line
      if line != None :
          BTStatus = True

    return BTStatus
      
#print checkBTLocation("48:13:7E:4A:A8:A6")
#    
#if checkBTLocation("48:13:7E:4A:A8:A6") == None:
#    print "Kambing"
#
def getLatestTweet(): 
    ''' Go to https://apps.twitter.com/ to register your app to get your api keys '''
    
    twitter = Twython(ms.CONSUMER_KEY,ms.CONSUMER_SECRET,ms.ACCESS_KEY,ms.ACCESS_SECRET)
    user_timeline = twitter.get_user_timeline(screen_name=ms.IDTWITTER,count=1)
    #print user_timeline[0]['text']    
    return user_timeline[0]['text']
    

#preprocessing tweet
def processTweet(tweet):
    # process the tweets
    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet

#
#def lightCensor():
#	#isi syntax sensor cahaya matiin n nyalain lampu disini
#	GPIO.setmode(GPIO.BCM)
#	GPIO.setwarnings(False)
#	GPIO.setup(4,GPIO.IN)
#	GPIO.setup(18,GPIO.OUT)
#
#	if GPIO.input(4) == 1 :
#         #print "LED on"
#         GPIO.output(18,GPIO.HIGH)
#         return "DARK"
#	else :
#         #print "LED off"
#         GPIO.output(18,GPIO.LOW)
#         return "LIGHT"


def isConditionChanged(tweet,mood) :
	#print tweet, processTweet(getLatestTweet())
	if (tweet != processTweet(getLatestTweet())) :
		return True
	else :
		return False
   
#START HERE
#inisialisasi awal
current_tweet = ''
current_mood = ''

def playSongBasedOnTweet(tweet) :
	subprocess.Popen("pkill mpg123", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
	url = 'http://text-processing.com/api/sentiment/'
	req = urllib2.Request(url, tweet, {'Content-Type': 'application/json'})
	f = urllib2.urlopen(req)	
	#print "AWAL MAENIN LAGU DARI TWEET " + tweet
	for x in f:
         jsonResponse=json.loads(x)
         print jsonResponse["probability"]
         print jsonResponse["label"]     
      
         if (jsonResponse["label"] == "neutral" or jsonResponse["label"] == "pos") :       
             print "You are in a POSITIVE MOOD :)"
             print "System is playing a POSITVE song for you..." 
             current_mood = 'pos'
             p = subprocess.Popen("mpg123 -z pos_musics/"+ posMusics[randint(0,numOfPosMusics)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
             subprocess.Popen("pkill mpg123", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
             p = subprocess.Popen("mpg123 -z pos_musics/"+ posMusics[randint(0,numOfPosMusics)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
             
             #print p.stdout.read()
         else:
             print "You are in a NEGATIVE MOOD :("  
             print "System is playing a NEGATIVE song for you..."             
             current_mood = 'neg'
             p = subprocess.Popen("mpg123 -z neg_musics/" + negMusics[randint(0,numOfNegMusics)] , stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
             subprocess.Popen("pkill mpg123", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
             p = subprocess.Popen("mpg123 -z neg_musics/"+ negMusics[randint(0,numOfNegMusics)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
             
             #print p.stdout.read() 
	f.close()

#Load list from pos and neg folder 
posMusics = [f for f in listdir("pos_musics") if isfile(join("pos_musics", f))]
negMusics = [f for f in listdir("neg_musics") if isfile(join("neg_musics", f))]
numOfPosMusics = len(posMusics)-1
numOfNegMusics = len(negMusics)-1

#hanya dijalankan sekali saat pertama kali sistem dijalankan
while True :
     if(checkBTLocation()):
         print "====....Starting Mood Booster System....===="
         print "Date   : " + (time.strftime("%d/%m/%Y"))
         print "Time   : " + (time.strftime("%H:%M:%S"))
         print "User Detected....(BT-MAC ADDR :" + ms.BTDEVICE + ")"
         print "Twitter ID : @" + ms.IDTWITTER
         print "Collecting Data...."
#	lightCensor()
         current_tweet = processTweet(getLatestTweet()) # bandingin dengan var data
         playSongBasedOnTweet("text="+current_tweet)
         break 
	
#lagu habis kondisi tidak berubah ? maenin lagu dgn genre sama
#lagu belum habis kondisi berubah? ok
#lagu habis kondisi berubah ? ok
#lagu belum habis kondisi tidak berubah? ok

while True:    
    if(checkBTLocation()):
        #lightCensor()
        time.sleep(10) #twitter hanya membatasi 15-180 call/15 mnt
        #lightCensor()
        if isConditionChanged(current_tweet,current_mood) :
            print "====....Starting Mood Booster System....===="
            print "Date   : " + (time.strftime("%d/%m/%Y"))
            print "Time   : " + (time.strftime("%H:%M:%S"))
            print "User Detected....(BT-MAC ADDR :" + ms.BTDEVICE + ")"
            print "Twitter ID : @" + ms.IDTWITTER
            print "Collecting Data...."
            #print "Room Lighting : " + lightCensor()
            data = processTweet(getLatestTweet())
            current_tweet = data
            data = "text="+data
            print "Your Latest Tweet : " + "'"+data+"'"
            playSongBasedOnTweet(data)
                               
#            if (subprocess.Popen("mpg123.)) :
#                maenkan lagu acak lagi
#        
              
				
			#sambil maen lagu cek status kondisi juga 
			#time.sleep(30)  # Delay fdlm detik(seconds) REALNYA  buat 5 menit cek ulang status         
			#player = subprocess.Popen("pkill mpg123", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)			
          
               
              
##loop while 

