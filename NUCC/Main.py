import email.message
import shutil
import requests
import smtplib
import urllib.request, bs4
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import os
import configparser

config =configparser.ConfigParser()
config.read(os.path.join(os.getcwd(),'config.ini'))
csvfolder = config['Inventory']['csvfolder']

mailto = config['MailInfo']['MailTO']
mailfrom = config['MailInfo']['MailFrom']
mailCC = config['MailInfo']['MailCC']
SMTPServer = config['MailInfo']['SMTPServer']

url = config['Inventory']['url']


def NotifyEmail(WriteMessage, Subject, MailFrom, MailTO, MailCC, SMTPServer,color):
    msg = email.message.Message()
    msg['Subject'] = Subject
    msg['From'] = MailFrom
    msg['To'] = MailTO
    msg['cc'] = MailCC
    msg.add_header('Content-Type', 'text/html')
    s = smtplib.SMTP(SMTPServer)
    msg.set_payload("<!DOCTYPE html><html><body>"
                    + "<table style='width:800px; padding:10px; border-left:2px solid "+color+"; border-right:2px solid "+color+"; border-top:10px solid "+color+"; border-bottom:20px solid "+color+"; Color:#1f497d; cellspacing='5' align='center'"
                    + "<br><br>"
                    + "Hello Team,"
                    + "<br><br>"
                    + WriteMessage
                    + "<br><br>"
                    + "Thanks, Claims Data Automation Team"
                    + "<br><br>"
                    + "</table>"
                      "</body>"
                      "</html>")
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()

def download_Csv(url,name):
    req = requests.get(url,verify = False)
    url_content = req.content
    csv_file = open(csvfolder +name+ '.csv', 'wb')
    csv_file.write(url_content)
    csv_file.close()

def UpdateFName(purl,name):
    files = os.listdir(csvfolder)
    for file in files:
        if(name == file):
            print("Both the files are same")
            return 0;# Both the files are same
        elif ('.csv' in file and float(file.split('.')[0].split('_')[2])<float(name.split('.')[0].split('_')[2])):
            print(file.split('.')[0].split('_')[2])
            print(name.split('.')[0].split('_')[2])
            shutil.move(os.path.join(csvfolder,file), os.path.join(csvfolder, "Archive"))
            # os.remove(csvfolder+file)
    download_Csv('https://www.nucc.org/'+purl,name.replace(".csv", ""))
    NotifyEmail("National Uniform Claim Committee file updated with latest version : "+name ,"NUCC Updated",mailfrom,mailto,mailCC,SMTPServer,"#319C34")

try:
    # context = ssl._create_unverified_context()
    # pages = bs4.BeautifulSoup(urllib.request.urlopen(url).read())
    pages = requests.get(url,verify = False)
    pages = pages.text
    pages = bs4.BeautifulSoup(pages)
    lists = pages('li')# your list of unordered list elements
    for ele in lists:
        # print('*************************')
        # print(ele)
        soup = BeautifulSoup(str(ele),"lxml")
        # print(soup.a.string)
        # print(soup.a['href'])
        if("Version" in str(soup.a.string)):
            name = soup.a['href'].split("/")
            UpdateFName(soup.a['href'],name[4])
            print(name[4])
            print(soup.a['href'])
            break
except Exception as e:
    NotifyEmail("National Uniform Claim Committee file update failed with message : "+str(e) ,"NUCC Failure ",mailfrom,mailto,mailCC,SMTPServer,"#BE4322")

