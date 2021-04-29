"""
These object are fake version of discord py object for reusability, I am lazy so these objects exists
"""

class Manual_message:
    "This is a class for message representation"
    def __init__(self, author, channel, content) -> None:
        self.author = author
        self.channel = channel
        self.content = content
        self.attachments = []