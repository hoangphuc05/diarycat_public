import os
import discord
from dotenv import load_dotenv
from discord.ext import commands,tasks
from time import time
from datetime import datetime
import asyncio


from connection import Connection

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

baseEntry = os.getenv("BASEURL")

client = discord.Client()

prefix = "dl!"
supportServer = ""

db = Connection()

reminded = []

#help content
helpString = '''
`dl!add <a note> <attach a picture>` to add an entry to your diary!
`dl!addAnyway <a note> <attach a picture>` to add an entry to your diary when you don't want to wait!
`dl!addText <a note>` to add an entry with no picture.
`dl!addTextAnyway <a note>` to skip the 1-day cooldown and add a note with no picture
`dl!read` to see all of your picture!
`dl!viewAnnouncement` to see the newest announcement.

You can turn reminding function on or off using `dl!remindOn` or `dl!remindOff`

If there is no arrow to navigate through your entries, you can manually add ⬅️ and ➡️ to move through entries or check the bot permission to add emoji.
Need further help? Join the support server at: https://discord.gg/XR5nPnRbUk
'''

#announmence content
annContent = ""
announced = []
annLifeTime = 0
annStartTime = 0

#boolean for loggin on or off
isLogging = False
logChannel = None

#error notified list to not flood them with message
notifiedError = []

class dailyClient(discord.Client):

    async def checkAnnounce(self, message):
        global annContent, announced, annLifeTime, annStartTime
        if not annContent:
            return
        
        #check if the user already received the announcement
        if str(message.author) in announced:
            return

        #check life time and delete announcement accordingly
        if annLifeTime == -1:
            pass
        elif int(time()) - annStartTime > annLifeTime:
            annContent = ""
            announced = []
            annLifeTime = 0
            annStartTime = 0
            return
        else:
        #announce the announcement
            await message.channel.send(annContent)
            announced.append(str(message.author))

    @tasks.loop(seconds=70)
    async def checkDaily(self):
        try:
            allReminded = db.getRemindedList()
            allUser = db.getAllUser()
            #check with database
            print(allReminded)
            #print(allUser)
            if allReminded == -1:
                print("All reminded error")
                return
            for user in allUser:
                
                if (not (str(user[0]),) in allReminded) and int(time()) - int(user[1]) > 86400:
                    await asyncio.sleep(3)
                    try:
                        channel = client.get_channel(int(user[2]))
                    except:
                        channel = None
                        pass
                    if channel != None:
                        
                        try:
                            await channel.send("How was your day, <@{}>?".format(user[0]))
                            db.addRemindList(str(user[0]))
                            print(f'{user[0]} was tagged!')
                            if logChannel != None:
                                await logChannel.send(f"`{user[0]} reminded.`")
                        except Exception as e:
                            pass
                        
                        
                        
        except Exception as e:
            print("Loop error:" + str(e))
        


        # #old check 
        # for user in allUser:
        #     #and int(time()) - int(user[1]) < 93600
        #     if (int(time()) - int(user[1]) > 86400 and int(time()) - int(user[1]) < 90000  and not user[0] in reminded):
        #         await asyncio.sleep(10)
        #         channel = client.get_channel(int(user[2]))
        #         if channel != None:
        #             await channel.send('How was your day, <@{}>?'.format(user[0]))
        #             #await channel.send('You can turn this off by `dl!remindOff')
        #             #await logChannel.send('Reminder sent for user {}'.format([user[0]]))
        #             reminded.append(str(user[0]))
                    
            

    @client.event
    async def on_ready(self):
        await client.change_presence(activity=discord.Game(name="dl!help"))
        pass
    async def on_message(self, message):
        try:
            global annContent, announced, annLifeTime, annStartTime, helpString, isLogging, logChannel, notifiedError

            if message.author == client.user:
                return
            #ignore the bot
            if (message.author.bot):
                return

            #strip the chat into arguments
            #chatContent = message.content.strip()
            arg = message.content.strip().split()

            if len(arg) < 1:
                return

            #admin command
            #put an announcement here

            #arg[1] is the life time the announcement will be on for
            #arg[2] is the content of the announcenent
            # print(message.content)
            # print(arg)
            # print(str(message.author))

            #logging all the command
            if isLogging and logChannel != None and message.content.startswith(prefix):
                logEmbed = discord.Embed()
                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                logEmbed.add_field(name="Command", value=arg[0])
                logEmbed.add_field(name="Attached Length", value= str(len(message.attachments)))
                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                await logChannel.send(embed = logEmbed)

            if arg[0].lower() == prefix+"announcement" and len(arg) > 2 and str(message.author.id) == "363694976665780226":
                #clear the old announce
                annContent = ""
                announced = []
                annLifeTime = 0
                annStartTime = 0
                
                annStartTime = int(time()) 
                annLifeTime = int(arg[1])
                #delete first 2 arg in list
                arg.pop(0)
                arg.pop(0)
                annContent = message.content[message.content.find(arg[0],len(prefix+"announc")+1):]

                await message.channel.send("Current announcement content set to: " + annContent)
                return

            if arg[0].lower() == (prefix+"clearannounce") and str(message.author.id) == "363694976665780226":
                annContent = ""
                announced = []
                annLifeTime = 0
                annStartTime = 0

                await message.channel.send("OK")
                return
            


            if arg[0].lower() == (prefix + "sethelp") and str(message.author.id) == "363694976665780226":
                arg.pop(0)
                helpString = message.content[message.content.find(arg[0],len(prefix+"setHep")):]

                await message.channel.send("Current help content set to: " + helpString)
                return
                
            #set whhich channel will be used for log (Discord wide)
            if arg[0].lower() == (prefix + "setlogchannel") and str(message.author.id) == "363694976665780226":
                isLogging = True
                logChannel = message.channel
                await message.channel.send("channel set as Log")
            
            if arg[0].lower() == (prefix + "logoff") and str(message.author.id) == "363694976665780226":
                isLogging = False
                await message.channel.send("log is off")

            if arg[0].lower() == (prefix + "logon") and str(message.author.id) == "363694976665780226":
                if logChannel != None:
                    isLogging = True
                    await message.channel.send("Log is on")
                else:
                    await message.channel.send("Please setLogChannel")

            if arg[0].lower() == (prefix + "servercount") and str(message.author.id) == "363694976665780226":
                await message.channel.send("Current server count: " + str(len(client.guilds)))

            if arg[0].lower() == (prefix + "adminhelp") and str(message.author.id) == "363694976665780226":
                await message.channel.send('''
`dl!announce <life time> <announce content>`
`dl!clearAnnounce`: clear current announcement
`dl!setHelp`: set help content
`setLogChannel`: set log channel for discord wide log
`logOff`
`logOn`
`serverCount`
                '''
                )

            #normal area for normal user
            if arg[0].lower() == (prefix + "viewannouncement"):
                if not annContent:
                    await message.channel.send("There is no new announcement")
                else:
                    await message.channel.send(annContent)
            

            #turn off the reminding function
            if arg[0].lower() == (prefix + "remindoff"):
                result = db.turnReminder(str(message.author.id), 0)
                if result[0] == 1:
                    await message.channel.send(f"Reminder is off! You can turn back on using `{prefix}remindOn`")
                else:
                    await message.channel.send("An error has occured, the error has been submitted, please try again later or contact support server")

            #turn on the reminding function
            if arg[0].lower() == (prefix + "remindon"):
                result = db.turnReminder(str(message.author.id), 1)
                if result[0] == 1:
                    await message.channel.send(f"Reminder is on! You can turn this off by using `{prefix}remindOff`")
                else:
                    await message.channel.send("An error has occured, the error has been submitted, please try again later or contact support server")

            if arg[0].lower() == (prefix + "add"):
                if (len(message.attachments) >= 1):
                    #get the last time, reset if higher than 48 hours/172800 seconds
                    lastTime = db.getLastTime(message.author.id)
                    if lastTime != -1:
                        #over 48 hours -> reset the streak
                        if int(time()) - int(lastTime) > 172800:


                            #add the picture
                            result = db.addDailyPic2(message.author.id, message.content[len(arg[0])+1:], message.attachments[0].url, message.author.name)
                            try:
                                db.removeRemindList(str(message.author.id))
                                #remove from reminded list
                                #reminded.remove(str(message.author.id))
                            except:
                                pass

                            #successful upload daily pics
                            if result[0] == 1:
                                #reset streak
                                db.resetStreak(message.author.id)
                                #update the time
                                db.updateLastTime(message.author.id,message.channel.id)
                                await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                            else:
                                await message.channel.send("Upload failed, please try again later or with a different picture.")
                                if isLogging:
                                    logEmbed = discord.Embed()
                                    logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                    logEmbed.add_field(name="Error", value=result[1])
                                    logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                    await logChannel.send(embed = logEmbed)

                        
                        #deny entry if under 24 hours
                        elif int(time()) - int(lastTime) < 86400:
                            waitTime = 86400 -  (int(time()) - int(lastTime))
                            await message.channel.send("Wait for another {} hours {} mins!!".format(int(waitTime/3600), int((waitTime - (int(waitTime/3600))*3600)/60) ))
                            await message.channel.send("You can skip the wait with `dl!addAnyway`")
                        else:
                            


                            #add the picture
                            result = db.addDailyPic2(message.author.id, message.content[len(arg[0])+1:], message.attachments[0].url, message.author.name)
                            try:
                                #remove from reminded list
                                #reminded.remove(str(message.author.id))
                                db.removeRemindList(str(message.author.id))
                            except:
                                pass
                            
                            #successful upload daily pics
                            if result[0] == 1:
                                #update the time
                                db.updateLastTime(message.author.id,message.channel.id)
                                await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                            else:
                                await message.channel.send("Upload failed, please try again later or with a different picture.")
                                if isLogging:
                                    logEmbed = discord.Embed()
                                    logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                    logEmbed.add_field(name="Error", value=result[1])
                                    logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                    await logChannel.send(embed = logEmbed)

                    else:

                        #add the picture
                        result = db.addDailyPic2(message.author.id, message.content[len(arg[0])+1:], message.attachments[0].url, message.author.name)
                        #successful upload daily pics
                        if result[0] == 1:
                            #update the time
                            db.updateLastTime(message.author.id,message.channel.id)
                            await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                        else:
                            await message.channel.send("Upload failed, please try again later or with a different picture.")
                            if isLogging:
                                logEmbed = discord.Embed()
                                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                logEmbed.add_field(name="Error", value=result[1])
                                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                await logChannel.send(embed = logEmbed)

                    await self.checkAnnounce(message)
                else:
                    await message.channel.send("Please attach a picture! You can use `dl!addText` to add a diary page without picture")
                    await logChannel.send("E: No picture given")


            #add with no image and just text
            if arg[0].lower() == (prefix + "addtext"):
                #check if there is text
                if len(arg) < 2:
                    await message.channel.send("Please add some text!")
                    return

                #get the last time, reset if higher than 48 hours/172800 seconds
                lastTime = db.getLastTime(message.author.id)
                if lastTime != -1:
                    #over 48 hours -> reset the streak
                    if int(time()) - int(lastTime) > 172800:
                        #add the picture
                        result = db.addDailyText(message.author.id, message.content[len(arg[0])+1:], message.author.name)
                        
                        try:
                            db.removeRemindList(str(message.author.id))
                            #remove from reminded list
                            #reminded.remove(str(message.author.id))
                        except:
                            pass

                        #successful upload daily pics
                        if result[0] == 1:
                            #reset streak
                            db.resetStreak(message.author.id)
                            #update the time
                            db.updateLastTime(message.author.id,message.channel.id)
                            await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                        else:
                            await message.channel.send("Upload failed, please try again later.")
                            if isLogging:
                                logEmbed = discord.Embed()
                                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                logEmbed.add_field(name="Error", value=result[1])
                                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                await logChannel.send(embed = logEmbed)

                    
                    #deny entry if under 24 hours
                    elif int(time()) - int(lastTime) < 86400:
                        waitTime = 86400 -  (int(time()) - int(lastTime))
                        await message.channel.send("Wait for another {} hours {} mins!!".format(int(waitTime/3600), int((waitTime - (int(waitTime/3600))*3600)/60) ))
                        #await message.channel.send("")
                    else:
                        


                        #add the picture
                        result = db.addDailyText(message.author.id, message.content[len(arg[0])+1:], message.author.name)
                        try:
                            #remove from reminded list
                            #reminded.remove(str(message.author.id))
                            db.removeRemindList(str(message.author.id))
                        except:
                            pass
                        
                        #successful upload daily pics
                        if result[0] == 1:
                            #update the time
                            db.updateLastTime(message.author.id,message.channel.id)
                            await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                        else:
                            await message.channel.send("Upload failed, please try again later.")
                            if isLogging:
                                logEmbed = discord.Embed()
                                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                logEmbed.add_field(name="Error", value=result[1])
                                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                await logChannel.send(embed = logEmbed)

                else:

                    #add the picture
                    result = db.addDailyText(message.author.id, message.content[len(arg[0])+1:], message.author.name)
                    #successful upload daily pics
                    if result[0] == 1:
                        #update the time
                        db.updateLastTime(message.author.id,message.channel.id)
                        await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                    else:
                        await message.channel.send("Upload failed, please try again later.")
                        if isLogging:
                            logEmbed = discord.Embed()
                            logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                            logEmbed.add_field(name="Error", value=result[1])
                            logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                            await logChannel.send(embed = logEmbed)

                await self.checkAnnounce(message)

            #add text anyway
            if arg[0].lower() == (prefix + "addtextanyway"):
                #check if there is text
                if len(arg) < 2:
                    await message.channel.send("Please add some text!")
                    return
                    
                #get the last time, reset if higher than 48 hours/172800 seconds
                lastTime = db.getLastTime(message.author.id)

                #if there is a last time
                if lastTime != -1:
                    #over 48 hours -> reset the streak
                    if int(time()) - int(lastTime) > 172800:
                        
                        #add the picture
                        result = db.addDailyText(message.author.id, message.content[len(arg[0]) + 1:], message.author.name)
                        if result[0] == 1:
                            db.resetStreak(message.author.id)
                            #update the time
                            db.updateLastTime(message.author.id,message.channel.id)
                            await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                        else:
                            await message.channel.send("Upload failed, please try again later or with a different picture.")
                            if isLogging:
                                logEmbed = discord.Embed()
                                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                logEmbed.add_field(name="Error", value=result[1])
                                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                await logChannel.send(embed = logEmbed)

                        try:
                            #remove from reminded list
                            #reminded.remove(str(message.author.id))
                            db.removeRemindList(str(message.author.id))
                        except:
                            pass
                    
                    #add anyway if under 24 hours
                    elif int(time()) - int(lastTime) < 86400:
                        waitTime = 86400 -  (int(time()) - int(lastTime))
                        
                        
                        #add the picture
                        result = db.addDailyText(message.author.id, message.content[len(arg[0]) + 1:], message.author.name)
                        
                        if result[0] == 1:
                            #update the time
                            db.forceUpdate(message.author.id,message.channel.id)
                            await message.channel.send("Your current streak is still " + str(db.getStreak(message.author.id)) + " days")
                        else:
                            await message.channel.send("Upload failed, please try again later or with a different picture.")
                            if isLogging:
                                logEmbed = discord.Embed()
                                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                logEmbed.add_field(name="Error", value=result[1])
                                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                await logChannel.send(embed = logEmbed)
                        
                        
                        try:
                            #remove from reminded list
                            #reminded.remove(str(message.author.id))
                            db.removeRemindList(str(message.author.id))
                        except:
                            pass

                    else:


                        #add the picture
                        result = db.addDailyText(message.author.id, message.content[len(arg[0]):], message.author.name)
                        if result[0] == 1:
                            #update the time
                            db.updateLastTime(message.author.id,message.channel.id)
                            await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                        else:
                            await message.channel.send("Upload failed, please try again later or with a different picture.")
                            
                            if isLogging:
                                logEmbed = discord.Embed()
                                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                logEmbed.add_field(name="Error", value=result[1])
                                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                await logChannel.send(embed = logEmbed)

                        try:
                            #remove from reminded list
                            #reminded.remove(str(message.author.id))
                            db.removeRemindList(str(message.author.id))
                        except:
                            pass
                #first entry ever
                else:

                    #add the picture
                    result = db.addDailyText(message.author.id, message.content[len(arg[0]):], message.author.name)
                    if result[0] == 1:
                        #update the time
                        db.updateLastTime(message.author.id,message.channel.id)
                        await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                    else:
                        await message.channel.send("Upload failed, please try again later or with a different picture.")
                        await logChannel.send("Upload failed!")
                        if isLogging:
                            logEmbed = discord.Embed()
                            logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                            logEmbed.add_field(name="Error", value=result[1])
                            logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                            await logChannel.send(embed = logEmbed)

                #check if there is any new announcement
                await self.checkAnnounce(message)
            
            #force add?
            if arg[0].lower() == (prefix + "addanyway"):
                if (len(message.attachments) >= 1):
                    
                    #get the last time, reset if higher than 48 hours/172800 seconds
                    lastTime = db.getLastTime(message.author.id)

                    #if there is a last time
                    if lastTime != -1:
                        #over 48 hours -> reset the streak
                        if int(time()) - int(lastTime) > 172800:
                            
                            #add the picture
                            result = db.addDailyPic2(message.author.id, message.content[len(arg[0]) + 1:], message.attachments[0].url, message.author.name)
                            if result[0] == 1:
                                db.resetStreak(message.author.id)
                                #update the time
                                db.updateLastTime(message.author.id,message.channel.id)
                                await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                            else:
                                await message.channel.send("Upload failed, please try again later or with a different picture.")
                                if isLogging:
                                    logEmbed = discord.Embed()
                                    logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                    logEmbed.add_field(name="Error", value=result[1])
                                    logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                    await logChannel.send(embed = logEmbed)

                            try:
                                #remove from reminded list
                                #reminded.remove(str(message.author.id))
                                db.removeRemindList(str(message.author.id))
                            except:
                                pass
                        
                        #deny entry if under 24 hours
                        elif int(time()) - int(lastTime) < 86400:
                            waitTime = 86400 -  (int(time()) - int(lastTime))
                            
                            
                            #add the picture
                            result = db.addDailyPic2(message.author.id, message.content[len(arg[0]) + 1:], message.attachments[0].url, message.author.name)
                            
                            if result[0] == 1:
                                #update the time
                                db.forceUpdate(message.author.id,message.channel.id)
                                await message.channel.send("Your current streak is still " + str(db.getStreak(message.author.id)) + " days")
                            else:
                                await message.channel.send("Upload failed, please try again later or with a different picture.")
                                if isLogging:
                                    logEmbed = discord.Embed()
                                    logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                    logEmbed.add_field(name="Error", value=result[1])
                                    logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                    await logChannel.send(embed = logEmbed)
                            
                            
                            try:
                                #remove from reminded list
                                #reminded.remove(str(message.author.id))
                                db.removeRemindList(str(message.author.id))
                            except:
                                pass

                        else:


                            #add the picture
                            result = db.addDailyPic2(message.author.id, message.content[len(arg[0]):], message.attachments[0].url, message.author.name)
                            if result[0] == 1:
                                #update the time
                                db.updateLastTime(message.author.id,message.channel.id)
                                await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                            else:
                                await message.channel.send("Upload failed, please try again later or with a different picture.")
                                
                                if isLogging:
                                    logEmbed = discord.Embed()
                                    logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                    logEmbed.add_field(name="Error", value=result[1])
                                    logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                    await logChannel.send(embed = logEmbed)

                            try:
                                #remove from reminded list
                                #reminded.remove(str(message.author.id))
                                db.removeRemindList(str(message.author.id))
                            except:
                                pass
                    #first entry ever
                    else:

                        #add the picture
                        result = db.addDailyPic2(message.author.id, message.content[len(arg[0]):], message.attachments[0].url, message.author.name)
                        if result[0] == 1:
                            #update the time
                            db.updateLastTime(message.author.id,message.channel.id)
                            await message.channel.send("Your current streak is " + str(db.getStreak(message.author.id)) + " days")
                        else:
                            await message.channel.send("Upload failed, please try again later or with a different picture.")
                            await logChannel.send("Upload failed!")
                            if isLogging:
                                logEmbed = discord.Embed()
                                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                                logEmbed.add_field(name="Error", value=result[1])
                                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                                await logChannel.send(embed = logEmbed)

                    #check if there is any new announcement
                    await self.checkAnnounce(message)
                else:
                    await message.channel.send("Please attach a picture! You can use `dl!addTextAnyway` if add a diary page without picture")
                    await logChannel.send("E: No picture given")

                        

            if arg[0].lower() == (prefix + "read"):
                await self.checkAnnounce(message)
                await asyncio.sleep(0.5)
                entries = db.viewDailyPic(message.author.id)
                #no entries found
                if len(entries) == 0:
                    await message.channel.send("No entry found, please add a new entry using `dl!add`. Use `dl!help` to get support if you already added something.")
                    return 
    

                #index = 0
                index = len(entries) -1
                #generate embed
                embedVar = discord.Embed(title = entries[index][2])\
                
                #check if it is longer than 1024
                
                parts = [entries[index][3][i:i+1023] for i in range(0, len(entries[index][3]), 1023)]
                for i in range(0,len(parts)):
                    if i == 0:
                        embedVar.add_field(name="Note", value= parts[i])
                    else:
                        embedVar.add_field(name="Part "+str(i+1), value= parts[i])
                embedVar.set_image(url = baseEntry + entries[index][4])
                embedVar.set_footer(text="Noted as "+ entries[index][5])
                
                try:
                    msg = await message.channel.send(embed = embedVar)
                    try:
                        await msg.add_reaction("⬅️")
                        await msg.add_reaction("➡️")
                    except:
                        await message.channel.send("Error: Can't add emoji, check my permission or manually add ⬅️ to go back and ➡️ to go forward.")
                except Exception as e:
                    await message.channel.send("Cannot show entries, please check my permission and allow sending embedded message")
                    await message.channel.send(f"Error code: {e}\nuse `dl!help` for more information.")

                
                def reactCheck(reaction, user):
                    return not user.bot

                while True:
                    try:
                        reaction, user = await client.wait_for('reaction_add',timeout=60, check= reactCheck)
                    except asyncio.TimeoutError:
                        
                        break
                    else:
                        await reaction.remove(user)
                        if str(reaction) == '➡️':
                            index += 1
                        if str(reaction) == "⬅️":
                            index -= 1
                        if index < 0:
                            index = len(entries) -1
                        if index > len(entries) -1:
                            index = 0
                        
                        embedVar = discord.Embed(title = entries[index][2])

                        parts = [entries[index][3][i:i+1023] for i in range(0, len(entries[index][3]), 1023)]
                        for i in range(0,len(parts)):
                            if i == 0:
                                embedVar.add_field(name="Note", value= parts[i])
                            else:
                                embedVar.add_field(name="Part "+str(i+1), value= parts[i])

                        embedVar.set_image(url = baseEntry + entries[index][4])
                        embedVar.set_footer(text="Noted as "+ entries[index][5])
                        await msg.edit(embed = embedVar)
            
            #set the reminder on or off
            # if message.content.startswith(prefix+"remind"):
            #     if arg[1] == "on":


            if arg[0].lower() == (prefix + "help"):
                # await message.channel.send("`dl!add <a note> <a picture>` to add an entry to your diary!")
                # await message.channel.send("`dl!forceAdd <a note> <a picture>` to add an entry to your diary when you don't want to wait!")
                # await message.channel.send("`dl!read` to see all of your picture!")
                # await message.channel.send("`dl!remindOff` to set reminder off")
                # await message.channel.send("`dl!remindOn` to set reminder on")
                await message.channel.send(helpString)
    
        except Exception as e:
            print(e)
            dm_channel = message.author.dm_channel
            if dm_channel == None:
                dm_channel = await message.author.create_dm()
            
            #send a message to dm_channel
            if str(message.author.id) not in notifiedError:
                await dm_channel.send("An error has occured, please try again later or try checking the bot permission to send message/embeded message or use  `dl!help` to get help\n\nThe error has been submitted to the developer.")
                notifiedError.append(str(message.author.id))
            if logChannel != None:
                await logChannel.send(f"An error happened for user {str(message.author)}! Error Description: {e}")



client = dailyClient()
client.checkDaily.start()
client.run(token)