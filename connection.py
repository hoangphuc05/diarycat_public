import sqlite3
from sqlite3 import Error
import time
from discord import user
import requests
from datetime import datetime
import os

class Connection:
    '''
    A class represent a connection to a database
    This database will contain 3 tables, one for the last day a user upload image
        the other is for all the picture and text that user uploaded
        one is for if a user is reminded or not
    '''

    def __init__(self, dir = "/home/hphucs/dailyBot/database/data.db"):
        super().__init__()
        self.dir = dir
        self.conn = None
        self.cursor = None
        try:
            self.conn = sqlite3.connect(self.dir)
            self.cursor = self.conn.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS `LastTime` (`id` VARCHAR(25) NOT NULL,`time` VARCHAR(25),`streak` INT,`channel` VARCHAR(25) ,PRIMARY KEY (`id`));")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS `dailyEntries` (`id` INTEGER PRIMARY KEY,`author` VARCHAR(25) NOT NULL,`date` VARCHAR(25) NOT NULL,`message` TEXT,`url` TEXT, `name` VARCHAR(25) NOT NULL);")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS `LastRemind` (`id` VARCHAR(25) NOT NULL,`reminded` INT,`remindSwitch` INT ,PRIMARY KEY (`id`));")

        except Error as e:
            print(e)

    def getAllUser(self):
        rows = None
        try:
            self.cursor.execute("SELECT id, time, channel FROM LastTime")
            rows = self.cursor.fetchall()
            if len(rows) < 1:
                return -1
            return rows
        except Error as e:
            print(e)
            return -2

    def getRemindedList(self):
        rows = None
        try:
            self.cursor.execute("SELECT id FROM LastRemind WHERE (reminded=1 and remindSwitch=1) or remindSwitch = 0")
            rows = self.cursor.fetchall()
            if len(rows) < 1:
                return []
            return rows
        except Error as e:
            print(e)
            return -1
            

    def updateLastTime(self, id, channel):
        try:
            streak = 0
            #check if row exist
            self.cursor.execute("SELECT streak FROM LastTime WHERE id=?", (id,))
            rows = self.cursor.fetchall()
            if len(rows) == 1:
                streak = int(rows[0][0])
            streak += 1
            
            #update the time and user
            t = (str(id), str(int(time.time())),streak,str(channel))
            self.cursor.execute("INSERT or REPLACE into `LastTime` (`id`,`time`,`streak`,`channel`) VALUES (?,?,?,?)", t)
            self.conn.commit()
            return (1,"")
        except Error as e:
            print(e)
            return (-1,e)

    def addRemindList(self, id):
        try:
            remindSwitch = 1
            #check if row exist
            self.cursor.execute("SELECT remindSwitch FROM LastRemind WHERE id=?", (id,))
            rows = self.cursor.fetchall()
            if len(rows) > 0:
                remindSwitch = int(rows[0][0])
            
            
            #update the reminded to 1
            t = (str(id), 1, remindSwitch)
            self.cursor.execute("INSERT or REPLACE into `LastRemind` (`id`, `reminded`, `remindSwitch`) VALUES (?,?,?)", t)
            self.conn.commit()
            return (1, "")
        except Error as e:
            print(e)
            return(-1, e)



    def removeRemindList(self, id):
        try:
            remindSwitch = 1
            #check if row exist
            self.cursor.execute("SELECT remindSwitch FROM LastRemind WHERE id=?", (id,))
            rows = self.cursor.fetchall()
            if len(rows) > 0:
                remindSwitch = int(rows[0][0])
            
            
            #update the reminded to 0
            t = (str(id), 0, remindSwitch)
            self.cursor.execute("INSERT or REPLACE into `LastRemind` (`id`, `reminded`, `remindSwitch`) VALUES (?,?,?)", t)
            self.conn.commit()
            return (1, "")
        except Error as e:
            print(e)
            return(-1, e)

    #turn the reminder, 1 is on and 0 is off
    def turnReminder(self, id, switch: int):
        try:
            reminded = 0
            #check if row exist
            self.cursor.execute("SELECT `reminded` FROM LastRemind WHERE id=?", (id,))
            rows = self.cursor.fetchall()
            if len(rows) > 0:
                reminded = int(rows[0][0])
            
            #turn the feature on or off
            t = (str(id), reminded, int(switch))
            self.cursor.execute("INSERT or REPLACE into `LastRemind` (`id`, `reminded`, `remindSwitch`) VALUES (?,?,?)", t)
            self.conn.commit()
            return (1,"")
        except Error as e:
            print(e)
            return (-1, e)

    def forceUpdate(self, id, channel):
        try:
            streak = 0
            #check if row exist
            self.cursor.execute("SELECT streak FROM LastTime WHERE id=?", (id,))
            rows = self.cursor.fetchall()
            if len(rows) == 1:
                streak = int(rows[0][0])
            
            #don't care about the streak.
            streak = streak
            
            #update the time and user
            t = (str(id), str(int(time.time())),streak,str(channel))
            self.cursor.execute("INSERT or REPLACE into `LastTime` (`id`,`time`,`streak`,`channel`) VALUES (?,?,?,?)", t)
            self.conn.commit()
            return (1,"")
        except Error as e:
            print(e)
            return (-1,e)

    #get the last time of the user is reminded, if the user has never been reminded, return -1
    def getLastTime(self, id):
        rows = None
        try:
            self.cursor.execute("SELECT time FROM LastTime WHERE id=?", (id,))
            rows = self.cursor.fetchall()
            if len(rows) < 1:
                return -1
            return rows[0][0]
        except Error as e:
            print(e)
            return -1
        
        #result as int
    
    def getLastRemind(self, id):
        rows = None
        try:
            self.cursor.execute("SELECT lastTime FROM LastRemind WHERE id=?", (id,))
            rows = self.cursor.fetchall()
            print("a")
            if len(rows) < 1:
                return -1
            return rows[0][0]
        except Error as e:
            print(e)
            return -1

    def getChannel(self,id):
        rows = None
        try:
            self.cursor.execute("SELECT channel FROM LastTime WHERE id=?", (id,))
            rows = self.cursor.fetchall()
            if len(rows) < 1:
                return -1
            return rows[0][0]
        except Error as e:
            print(e)
            return -1
        
        #result as int

    def resetStreak(self,id):
        try:
            self.cursor.execute("UPDATE LastTime SET streak = 0 WHERE id = ?", (id,))
            self.conn.commit()
            return 1
        except Error as e:
            print(e)
            return -1

    def getStreak(self, id):
        rows = None
        try:
            self.cursor.execute("SELECT streak FROM LastTime WHERE id=?", (id,))
            rows = self.cursor.fetchall()
            return rows[0][0]
        except Error as e:
            print(e)
            return -1

    
    def delete_entries(self, user_id, entries_id):
        '''
            delete an entries matching user_id and entries_id
        '''
        #try to see if can find such entries
        try:
            self.cursor.execute("SELECT * FROM dailyEntries WHERE id=? AND author=?", (entries_id,user_id,))
            rows = self.cursor.fetchall()
            # if there's no entries, return -1 and exit the function
            if len(rows) == 0:
                return -1
            
            # Continue: deleting the entries
            self.cursor.execute("DELETE FROM dailyEntries WHERE id=? AND author=?", (entries_id,user_id,))
            self.conn.commit()
            return 1

        except Error as e:
            print(e)
            return -2

    def addDailyPic2(self, id, message, discordUrl, name):
        day = datetime.today().strftime('%d-%m-%Y')
        baseUrl="https://hphucs.me/dailyBotAPI.php"
        data = {'key':'<api key here>',
                'id' : id,
                'url': discordUrl}
        try:
            #add a new daily entry
            result = requests.post(baseUrl, data = data)
            if result.text != '-1':
                r = (str(id), str(day), str(message), str(result.text), str(name),)
                self.cursor.execute("INSERT into `dailyEntries` (`author`,`date`,`message`,`url`, `name`) VALUES (?,?,?,?,?)", r)
                self.conn.commit()
                return(1,"")
            else:
                return(-1,"Upload failed")

        except Error as e:
            print(e)
            return (-1,e)

    def addDailyText(self, id, message, name):
        day = datetime.today().strftime('%d-%m-%Y')

        try:

            r = (str(id), str(day), str(message), "none", str(name),)
            self.cursor.execute("INSERT into `dailyEntries` (`author`,`date`,`message`,`url`, `name`) VALUES (?,?,?,?,?)", r)
            self.conn.commit()
            return(1,"")

        except Error as e:
            print(e)
            return (-1,e)

    def viewDailyPic(self, id):
        rows = None
        self.cursor.execute("SELECT * FROM `dailyEntries` WHERE author=?",(id,))
        rows = self.cursor.fetchall()
        return rows
    
    def view_single_pic(self, user_id, entry_id):
        rows = None 
        self.cursor.execute("SELECT * FROM dailyEntries WHERE id=? AND author=?",(entry_id,user_id,))
        rows = self.cursor.fetchall()
        print(rows)
        return rows


'''
Test = Connection()

Test.updateLastTime("123")
print(Test.getStreak("123"))
'''