
import discord
from discord import embeds
from discord import channel
from discord.raw_models import RawReactionActionEvent
import yaml
from datetime import datetime
from time import time 
import os
from dotenv import load_dotenv
import asyncio
import random

#connection to the database
from connection import Connection


db = Connection(dir="./database/data.db")

responses = yaml.full_load(open('./response.yaml'))
prefix = responses["default-prefix"]

load_dotenv()
baseEntry = os.getenv("BASEURL")

class DailyBot:
    def __init__(self, client: discord.client.Client) -> None:
        self.announced = []
        self.annContent = ""
        self.announced = []
        self.annLifeTime = 0
        self.annStartTime = 0

        self.annStartTime = 0
        self.annLifeTime = 0

        self.isLogging = False
        self.logChannel = None
        self.client = client


        pass
    
    async def loopUpdate(self) -> None:
        channel = None
        try:
            allReminded = db.getRemindedList()
            allUser = db.getAllUser()
            if allReminded == -1:
                print("All reminded Error")
                return 

            # get the list of questions:
            questions_list = responses["methods"]["remind"]["message"]
            
            for user in allUser:
                # generate a random question
                question = random.choice(questions_list)

                if (not (str(user[0]),) in allReminded) and int(time()) - int(user[1]) > 86400:
                    await asyncio.sleep(3)
                    try:
                        channel = self.client.get_channel(int(user[2]))
                    except:
                        channel = None
                        pass
                    if channel != None:
                        try:
                            await channel.send(question.format(user_id=user[0]))
                            db.addRemindList(str(user[0]))
                            print(f'{user[0]} was tagged!')
                            if self.logChannel != None:
                                await self.logChannel.send(f"`{user[0]} reminded.`")
                        
                        except Exception as e:
                            pass
        except Exception as e:
            print(f"Loop error: {e}")
        

    async def messageHandler(self, message: discord.message.Message):
        #print(message)
        global prefix, db
        self.prefix = prefix
        self.db = db
        args = message.content.lower().strip().split()
 
        #if there is no content in the call
        if len(args) < 1 or message.author.bot or (not args[0].lower().startswith(prefix)) or (not hasattr(self, args[0][len(prefix):])):
            return
        
        #search yaml file to find the respnse for each methods
        # try:
        #     command = args[0][len(prefix):]
        #     command_response = responses["methods"][command]
        #     command_response = responses["methods"][args[0][len(prefix):]]
        # except:
        #     pass

        #log the command to spy on people
        await self._Log(message, args)
        
        #call the check announcement function
        await self._checkAnnouncement(message, args)

        #call the function handle the command
        await getattr(self, args[0][len(prefix):])(message, args)
        return

    async def _LogRaw(self, error_info: str):
        if self.isLogging and self.logChannel != None:
            logEmbed = discord.Embed()
            logEmbed.add_field(name="Error", value=error_info)
            logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            await self.logChannel.send(error_info)
            #await self.logChannel.send(embed = logEmbed)

    async def _Log(self, message: discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        if self.isLogging and self.logChannel != None:
            logEmbed = discord.Embed()
            logEmbed.set_author(name = str(message.author.id), icon_url=message.author.avatar_url)
            logEmbed.add_field(name="Command", value=args[0])
            logEmbed.add_field(name="Attached Length", value= str(len(message.attachments)))
            logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            await self.logChannel.send(embed = logEmbed)

    #function not to be called directly?
    async def _addPicture(self, message: discord.message.Message, reset_streak:bool, args, addAnyway:bool = False):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        #check for the error again??
        if len(message.attachments) < 1:
            return

        #add the picture?
        result = self.db.addDailyPic2(message.author.id, message.content[len(args[0])+1:], message.attachments[0].url, message.author.name)
        try:
            db.removeRemindList(str(message.author.id))
            #remove from reminded list
            #reminded.remove(str(message.author.id))
        except:
            pass

        if result[0] == 1:
            
            #reset streak if needed
            if reset_streak:
                self.db.resetStreak(message.author.id)

            #update the last time
            if addAnyway == True:
                self.db.forceUpdate(message.author.id, message.channel.id)
            else:
                self.db.updateLastTime(message.author.id,message.channel.id)
            
            #notify the streak
            await message.channel.send(command_response["response-success"].format(streak_length = str(db.getStreak(message.author.id))))
        else:
            await message.channel.send(command_response["response-fail"]["upload-fail"])
            
            #send a error log
            if self.isLogging:
                logEmbed = discord.Embed()
                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                logEmbed.add_field(name="Error", value=result[1])
                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                await self.logChannel.send(embed = logEmbed)

    async def _addTextMethod(self, message: discord.message.Message, reset_streak:bool, args, addAnyway:bool = False):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        #add the picture?
        result = self.db.addDailyText(message.author.id, message.content[len(args[0])+1:], message.author.name)
        
        
        #if add successfully
        if result[0] == 1:
            
            #remove from reminded list
            try:
                db.removeRemindList(str(message.author.id))
                #remove from reminded list
                #reminded.remove(str(message.author.id))
            except:
                pass
            
            #reset streak if needed
            if reset_streak:
                self.db.resetStreak(message.author.id)

            #update the last time
            if addAnyway == True:
                self.db.forceUpdate(message.author.id, message.channel.id)
            else:
                self.db.updateLastTime(message.author.id,message.channel.id)
            
            #notify the streak
            await message.channel.send(command_response["response-success"].format(streak_length = str(db.getStreak(message.author.id))))
        else:
            await message.channel.send(command_response["response-fail"]["upload-fail"])
            
            #send a error log
            if self.isLogging:
                logEmbed = discord.Embed()
                logEmbed.set_author(name = str(message.author.name), icon_url=message.author.avatar_url)
                logEmbed.add_field(name="Error on addtext", value=result[1])
                logEmbed.set_footer(text=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                await self.logChannel.send(embed = logEmbed)

    async def _checkAnnouncement(self, message: discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        if not self.annContent:
            return 
        
        #check if user already received the announcement
        if str(message.author) in self.announced:
            return
        
        #check life time
        if self.annLifeTime == -1:
            pass 
        elif int(time()) - self.annStartTime > self.annLifeTime:
            self.annContent = ""
            self.announced = [] 
            self.annLifeTime = 0
            self.annStartTime = 0
            return 
        else:
            await message.channel.send(self.annContent)
            self.announced.append(str(message.author))




    async def help(self, message: discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        #print("a")
        helpCommand = None
        if len(args) > 1:
            helpCommand = args[1]
        if helpCommand == None:
            embedVar = discord.Embed(color = 0xd4cab8, title = "**Diary Cat Command List**", description = """
Welcome to Diary Cat!\n You can get start by using `{prefix}add [you diary entry]` and then `{prefix}read` to read your diary.\n
**You can now direct message the bot with these commands for privacy**\n  
Use `{prefix}help [command]` to learn more about a specific command.
You need further support? Join our [support server](https://discord.gg/shuJ8A3Ced)
        """.format(prefix = prefix))
            #embedVar.add_field(name = "\u200b",value="Use `{prefix}help [command]` to learn more about that specific command.\nYou need further support? Join our [support server](https://discord.gg/fumxgEFHkR)".format(prefix = prefix), inline=False)
            embedVar.add_field(inline = False,name="\n📝 **Add diary entry everyday**", value='''
You can only use these commands once every 18 hours
`{prefix}add [a note] [attach a picture]` : add an entry to your diary!
`{prefix}addText [a note]` : add an entry with no picture.
            '''.format(prefix = prefix))
            embedVar.add_field(inline=False, name="⏲️ **Manipulate time, skip the waiting!**", value=f'''
`{prefix}addAnyway [a note] [attach a picture]` : add an entry to your diary when you don't want to wait!
`{prefix}addTextAnyway [a note]` : skip the 1-day cooldown and add a note with no picture.
            ''')
            embedVar.add_field(inline = False, name = "\n📖 **Read your diary**", value = f'''
`{prefix}read` : see all of your diary entries!
`{prefix}delete` : show instruction to delete an entry.        
            ''')
            embedVar.add_field(inline= False, name="⚙️ **Setting and misc**", value=f'''
`{prefix}feedback` : send an anonymous feedback to the owner.
`{prefix}remindOn` - `{prefix}remindOff` : turn on or off the reminder, default is on.
`{prefix}invite` : get the link to invite this bot to different server.
`{prefix}help [name of the command]` : get specific help about that command.
`{prefix}viewAnnouncement` : see the newest announcement.        
            ''')
            try:
                await message.channel.send(embed = embedVar)
            except:
                await message.channel.send("An error happened! Please make sure the bot have permission to send embed link!")
        else:
            #check if the method is in yaml
            if helpCommand in responses['methods']:
                embedHelp = discord.Embed(color = 0xd4cab8, title = f"Command: {helpCommand}")
                embedHelp.add_field(inline=False, name = "Desciption", value = responses['methods'][helpCommand]['description'])
                embedHelp.add_field(inline=False, name = "Usage", value = f"`{prefix}{helpCommand} {responses['methods'][helpCommand]['structure']}`")

                await message.channel.send(embed = embedHelp)

    #remindOff: turn reminder off
    async def remindoff(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        result = self.db.turnReminder(str(message.author.id), 0)
        if result[0] == 1:
            #success
            await message.channel.send(command_response["response-success"].format(prefix = self.prefix))
        else:
            await message.channel.send(command_response["response-fail"].format(prefix = self.prefix))
        
    #remidOn: turn reminder on
    async def remindon(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        result = self.db.turnReminder(str(message.author.id), 1)
        if result[0] == 1:
            #success
            await message.channel.send(command_response["response-success"].format(prefix = self.prefix))
        else:
            await message.channel.send(command_response["response-fail"].format(prefix = self.prefix))

    async def private(self, message: discord.message.Message):
        '''
        This function call another function to handle the action, then delete the root message contains the command.
        Require permission: Manage_message
        '''
        return
        message.content = "12345"
        await message.channel.send(message.content)

    async def __pop_up_confirm(self, message:discord.message.Message, args, title = "confirm", content = "Are you sure about this?", footer="React ✅ to confirm, ❌ to cancel"):
        def reactCheck(reaction: discord.Reaction, user):
            '''
            Check if reaction of a message on a normal channel is belong to that specific message.
            This does not triggered on DM channel?? What?? 
            Update: only return true if from the original user
            '''
            # get the 
            if not user.bot and reaction.message.id == confirm_mess.id and user.id == message.author.id:
                return True
            else:
                return False

        #create an embeded to ask if want no picture
        embedVar = discord.Embed(color = 0xd4cab8, title = title,
            description = content)
        embedVar.set_footer(text = footer)
        confirm_mess = None
        try:
            confirm_mess = await message.channel.send(embed = embedVar)
        except:
            confirm_mess = await message.channel.send("Can't send embed. please check my permission! Are you sure about your action?")

        #try to add reaction
        try:
            await confirm_mess.add_reaction("✅")
            await confirm_mess.add_reaction("❌")
        except:
            await message.channel.send("Cannot add emoji, add ✅ to confirm and ❌ to stop.")

        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add',timeout=60, check= reactCheck)
            except asyncio.TimeoutError:
                return False
            
            try:
                await confirm_mess.delete(delay = 0.7)
            except:
                pass
            if str(reaction) == "✅":
                return True
            elif str(reaction) == "❌":
                return False

    async def __no_img_confirm(self, message:discord.message.Message, args):
        return await self.__pop_up_confirm(message, args, title = "No picture is attached!", content = "Do you want to add a page with only text?", footer= "You can skip this confirmation step using dl!addtext next time")


    async def __delete_img_confirm(self, message:discord.message.Message, args):
        def reactCheck(reaction: discord.Reaction, user):
            '''
            Check if reaction of a message on a normal channel is belong to that specific message.
            This does not triggered on DM channel
            '''
            if not user.bot and reaction.message.id == confirm_mess.id:
                return True
            else:
                return False

        # get the image information
        entry = self.db.view_single_pic(message.author.id, str(args[1]))
        if len(entry) ==0:
            await message.channel.send("No entry found, please check your id!")
            return False


        #create an embeded to ask for delete confirmation
        embedVar = discord.Embed(color = 0xd4cab8, title = "Image delete confirm",
            description = "Please confirm you want to delete this entries")
        embedVar.add_field(name = "Date added", value= f"{entry[0][2]}", inline=False)
        embedVar.add_field(name = "Note", value= f"{entry[0][3]}", inline=False)
        embedVar.set_image(url = baseEntry + entry[0][4])
        embedVar.set_footer(text = "React ✅ to delete, ❌ to keep.")
        confirm_mess = None
        try:
            confirm_mess = await message.channel.send(embed = embedVar)
        except:
            confirm_mess = await message.channel.send("Send message error, please check if the bot has embed message permission")
            return False

        try:
            await confirm_mess.add_reaction("✅")
            await confirm_mess.add_reaction("❌")
        except:
            pass
        
        while True:
            try:
                reaction, user = await self.client.wait_for('reaction_add',timeout=60, check= reactCheck)
            except asyncio.TimeoutError:
                return False
            
            try:
                await confirm_mess.delete(delay = 0.7)
            except:
                pass
            if str(reaction) == "✅":
                return True
            elif str(reaction) == "❌":
                return False
        
    async def __same_day_confirm(self,  message:discord.message.Message, args):
        return await self.__pop_up_confirm(message, args, title = "You already write an entry today!", content = "Are you sure you want to add another page of diary entry?", footer="You can skip this confirmation by using dl!addAnyway/addTextAnyway next time")

    async def delete(self, message:discord.message.Message, args):
        '''
        This function will show help if no parameters is provided,
        or delete entry of that user with the id
        dl!delete [id]
        '''
        if len(args) == 2:
            confirm = await self._delete_img_confirm(message, args)
            if confirm == False:
                await message.channel.send("Delete cancelled")
                return
            result = self.db.delete_entries(message.author.id, args[1])
            if result == 1:
                await message.channel.send("Entries delete successfully!\nuse `dl!read` to view your updated diary.")
            elif result == -1:
                await message.channel.send("No entries found, please check your post entry id again")
            elif result == -2:
                await message.channel.send("An error happened, please try again later.")    
                await self._LogRaw("Delete fail, please check log!")
        else:
            await message.channel.send(
                f"""
```
To delete an entry, navigate to that entries using `{self.prefix}read` and react the entry with ❌, then follow the instruction.
```
                """
            )

    #add?: add an entry...
    async def add(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass

        #check if there is any picture attached
        # if not then ask for confirmation?
        if (len(message.attachments) < 1):
            confirm = await self.__no_img_confirm(message, args)
            if confirm == False:
                await message.channel.send("No entry is added")
             
            elif confirm == True:
                #call the addtext method as if the user is calling it?
                await self.addtext(message, args)
                

            
            return
        else:
            pass 

        #get lasttime
        lastTime = self.db.getLastTime(message.author.id)
        if lastTime == -1:
            await self._addPicture(message, False, args)
            return
        
        #if not -1:
        #if over 48 hours -> reset the streak
        if int(time()) - int(lastTime) > 172800:
            await self._addPicture(message, True, args)
        
        # ask for confirm to add entry if under 18 hours
        elif int(time()) - int(lastTime) < 64800:
            # ask for confirmation if they want to add another entry in a same day
            confirm = await self.__same_day_confirm(message, args)
            if confirm == False:
                await message.channel.send("No entry is added")
            elif confirm == True:
                # call the addtext method as if the user is calling it?
                await self.addanyway(message, args)

        # else except entry
        else:
            await self._addPicture(message, False, args)
        return
        
    async def addanyway(self,  message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
    
        #check if there is any picture attached
        if (len(message.attachments) < 1):
            confirm = await self.__no_img_confirm(message, args)
            if confirm == False:
                await message.channel.send("No entry is added")
                 
            elif confirm == True:
                #call the addtext method as if the user is calling it?
                await self.addtextanyway(message, args)
                
            return
        else:
            pass 

        #get lasttime
        lastTime = self.db.getLastTime(message.author.id)
        if lastTime == -1:
            await self._addPicture(message, False, args)
            return
        
        #if not -1:
        #if over 48 hours -> reset the streak
        if int(time()) - int(lastTime) > 172800:
            await self._addPicture(message, True, args)
        
        #deny entry if under 24 hour
        elif int(time()) - int(lastTime) < 64800:
            
            await self._addPicture(message, reset_streak= False, args=args, addAnyway=True)

        #else except entry
        else:
            await self._addPicture(message, False, args)
        return

    async def addtext(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass

        # check if there's an attachment come with the message
        if (len(message.attachments) > 0):
            await message.channel.send(command_response["response-fail"]["image-fail"].format(prefix = prefix))
            await self.add(message, args)
            return
    
        # check if there is text
        if len(args) < 2:
            await message.channel.send(command_response["response-fail"]["no-text"])
            return        

        #get lasttime
        lastTime = self.db.getLastTime(message.author.id)    
        if lastTime == -1:
            await self._addTextMethod(message, False, args= args)
            return
        
        #over 48 hours -> reset the streak
        if int(time()) - int(lastTime) > 172800:
            await self._addTextMethod(message, True, args)
            return

        # if time under 18 hours, ask confirm to add entry
        elif int(time()) - int(lastTime) < 64800:
            # waitTime = 64800 -  (int(time()) - int(lastTime))
            # await message.channel.send(command_response["response-fail"]["time-fail"].format(hour= int(waitTime/3600), min = int((waitTime - (int(waitTime/3600))*3600)/60), prefix = self.prefix ))
            # ask for confirmation if they want to add another entry in a same day
            confirm = await self.__same_day_confirm(message, args)
            if confirm == False:
                await message.channel.send("No entry is added")
            elif confirm == True:
                # call the addtext method as if the user is calling it?
                await self.addtextanyway(message, args)

        else:
           await self._addTextMethod(message, False, args)

    async def addtextanyway(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass

        # check if there's an attachment, if does call another function
        if (len(message.attachments) > 0):
            await message.channel.send(command_response["response-fail"]["image-fail"].format(prefix = prefix))
            await self.addanyway(message, args)
            return

        #check if there is text
        if len(args) < 2:
            await message.channel.send(command_response["response-fail"]["no-text"])
            return        

        #get lasttime
        lastTime = self.db.getLastTime(message.author.id)    
        if lastTime == -1:
            await self._addTextMethod(message, False, args)
            return
        
        #over 48 hours -> reset the streak
        if int(time()) - int(lastTime) > 172800:
            await self._addTextMethod(message, True, args)
            return
        elif int(time()) - int(lastTime) < 64800:
            await self._addTextMethod(message, False,args, True)
        else:
            await self._addTextMethod(message, False, args)

    async def read(self, message:discord.message.Message, args):
        
        global baseEntry
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        entries = self.db.viewDailyPic(message.author.id)
        dmChannel = False
        if len(entries) == 0:
            await message.channel.send(command_response['response-fail']['no-entry'])
            return 
        
        index = len(entries) - 1
        embedVar = discord.Embed(title = entries[index][2])

        #check if it is longer than 1024
        parts = [entries[index][3][i:i+1023] for i in range(0, len(entries[index][3]), 1023)]
        for i in range(0,len(parts)):
            if i == 0:
                embedVar.add_field(name="Note", value= parts[i])
            else:
                embedVar.add_field(name="Part "+str(i+1), value= parts[i])
        embedVar.set_image(url = baseEntry + entries[index][4])
        embedVar.set_footer(text="Noted as "+ entries[index][5])

        #check if channel is DM channel
        if isinstance(message.channel, discord.channel.DMChannel):
            dmChannel = True
        else:
            dmChannel = False
        
        try:
            msg = await message.channel.send(embed = embedVar)
            try:
                await msg.add_reaction("⬅️")
                await msg.add_reaction("➡️")
            except:
                await message.channel.send("Error: Can't add emoji, check my permission or manually add ⬅️ to go back and ➡️ to go forward.")
        except Exception as e:
            await message.channel.send("Cannot show entries, please check the bot permission and allow sending embedded message")
            await message.channel.send(f"Error code: {e}\nuse `dl!help` for more information.")
            return



        def reactCheck(reaction: discord.Reaction, user):
            '''
            Check if reaction of a message on a normal channel is belong to that specific message.
            This does not triggered on DM channel
            '''
            if not user.bot and reaction.message.id == msg.id and user.id == message.author.id:
                return True
            else:
                return False

        def dmReactCheck(rawReact: discord.raw_models.RawReactionActionEvent):
            '''
            Check reaction to a message in DM channel, can be use in normal channel as well?
            '''
            if not rawReact.user_id == self.client.user.id and rawReact.message_id == msg.id:
                return True
            else:
                return False

        while True:
            try:
                if dmChannel:
                    rawReact = await self.client.wait_for('raw_reaction_add', timeout=60, check= dmReactCheck)
                    reaction = rawReact.emoji
                    user = None
                    pass
                else:
                    reaction, user = await self.client.wait_for('reaction_add',timeout=60, check= reactCheck)
            except asyncio.TimeoutError:
                break
            else:
                try:
                    if not dmChannel:
                        await reaction.remove(user)
                except:
                    pass
                if str(reaction) == '➡️':
                    index += 1
                if str(reaction) == "⬅️":
                    index -= 1
                if str(reaction) == "❌":
                    await message.channel.send(f"To delete this entry, use command:\n```cpp\n{prefix}delete {entries[index][0]}```\nIf you don't want to delete this entry, just ignore this message!\n**Warning: This action is irreversible**")

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

    async def viewannouncement(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        if not self.annContent:
            await message.channel.send(command_response["response-fail"])
        else:
            await message.channel.send(self.annContent)
    
    async def invite(self, message:discord.message.Message, args):
        """
        output invite link for the bot
        """
        await message.channel.send("You can invite this bot to your server using this link: https://discord.com/oauth2/authorize?client_id=739410070533570582&scope=bot&permissions=388160")

    async def feedback(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        '''
        Almost anonymous feedback
        '''
        if self.logChannel != None:
            await self.logChannel.send(message.content)
        embedVar = discord.Embed(color = 0xd4cab8, title = "Feedback received", description = f"Thank you for your feedback! If you want to receive further support, feel free to join the [support server](https://discord.gg/shuJ8A3Ced).")
        await message.channel.send(embed = embedVar)

    #-----------------------------------------------
    #This section is limited to admin user...
    async def sethelp(self, message:discord.message.Message , args):
        pass 

    async def announce(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        if len(args) < 3 or str(message.author.id) != "363694976665780226":
            return 

        self.annContent = ""
        self.announced = []
        self.annLifeTime = 0
        self.annStartTime = 0

        self.annStartTime = int(time()) 
        self.annLifeTime = int(args[1])
        #delete first 2 args in list
        args.pop(0)
        args.pop(0)
        self.annContent = message.content[message.content.lower().find(args[0],len(prefix+"announc")+1):]
        await message.channel.send("Current announcement content set to: " + self.annContent)
        return

    async def clearannounce(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        if str(message.author.id) != "363694976665780226":
            return
        self.annContent = ""
        self.announced = []
        self.annLifeTime = 0
        self.annStartTime = 0

        await message.channel.send("Done")
        return

    async def servercount(self, message:discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        if str(message.author.id) != "363694976665780226":
            return 
        await message.channel.send("Current server count: " + str(len(self.client.guilds)))

    async def setlogchannel(self, message: discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        if str(message.author.id) != "363694976665780226":
            return
        self.isLogging = True 
        self.logChannel = message.channel
        await message.channel.send("channel set as Log")

    async def logoff(self, message: discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        self.isLogging = False
        await message.channel.send("log is off")

    async def logon(self, message: discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        if self.logChannel != None:
            self.isLogging = True
            await message.channel.send("Log is on")
        else:
            await message.channel.send("Please setLogChannel")

    async def adminhelp(self, message: discord.message.Message, args):
        try:
            command_response = responses["methods"][args[0][len(prefix):]]
        except:
            command_response = ""
            pass
        if str(message.author.id) != "363694976665780226":
            return
        await message.channel.send(command_response["content"])


