# Diary Cat
A Discord bot that acts as a **digital diary**, let you write and upload picture everyday!

[![Discord Bots](https://top.gg/api/widget/739410070533570582.svg)](https://top.gg/bot/739410070533570582)

## In this readme
* [Features](#Features)
* [Invite link](#Bot-page-and-invite-link)
* [Selfhost](#Self--hostsetting-upmodification)
* [Technical note](#Technical-note)

## Features
- Add a diary page with text and image using `dl!add`
- Get reminded every day about writing diary with `dl!remindOn`
- Read your diary with `dl!read`
- Manage and delete your diary page with `dl!delete`
- Keep a record of how frequently you write diary

## Bot page and invite link
- Top.gg: https://top.gg/bot/739410070533570582

## Self-host/setting up/modification
- A token can be specified by adding a file `.env` and add `DISCORD_TOKEN=[your_token]`
- Reponse and help message can be edit in [response.yaml](response.yaml)
- This bot need a backend to receive and save pictures uploaded by user. API interaction can be seen at [connection.py](connection.py#L239)


## Technical note
### Github
This GitHub page is a mirror of the main (private) Diary Cat github with some modification to hide certain information (security through ofuscation, amirite?)

List of modified/deleted file:
- Database and backend connection: `connection.py`
- Previous code base: `oldVersion/`
- (old)Database: `database/`
- Backup script: `/backup.sh`
- Log file

### Backup
Backup is made every 6 hours and stored on Amazon Web Service S3