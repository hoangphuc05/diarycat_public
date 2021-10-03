#!/bin/bash

/usr/bin/curl -X POST -H "Content-Type: multipart/form-data" -F 'content=Backup script started' https://discord.com/api/webhooks/<webhook_url>
/usr/bin/curl -X POST -H "Content-Type: multipart/form-data" -F 'content=Backing up main database' https://discord.com/api/webhooks/<webhook_url>
/usr/bin/sqlite3 /home/hphucs/dailyBot/database/data.db ".backup '/home/hphucs/dailyBot/database/backup/backup_database.db'"
result=$(/usr/local/bin/aws s3 sync "/home/hphucs/dailyBot/database/backup" s3://dailybotbackup/backup)
/usr/bin/curl -X POST -H "Content-Type: multipart/form-data" -F $"content=Backup database output \`\`\`$result\`\`\`" https://discord.com/api/webhooks/<webhook_url>
#synce all the picture
/usr/bin/curl -X POST -H "Content-Type: multipart/form-data" -F 'content=Sync upload picture starting' https://discord.com/api/webhooks/<webhook_url>
results=$(/usr/local/bin/aws s3 sync /var/www/html/dailyPics/uploads s3://dailybotbackup/uploads)
/usr/bin/curl -X POST -H "Content-Type: multipart/form-data" -F $"content=Sync output \`\`\`$results\`\`\`" https://discord.com/api/webhooks/<webhook_url>
