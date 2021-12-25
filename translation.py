class Translation(object):
    START_TEXT = """Hello <i><b>{}</b></i>,
I Can rename ✍ with custom thumbnail and upload as video/file
Type /help for more details."""
    DOWNLOAD_START_VIDEO = "Downloading Video to my server.....📥"
    DOWNLOAD_START = "Downloading File to my server.....📥"
    UPLOAD_START_VIDEO = "Uploading as video.....📤"
    UPLOAD_START = "Uploading as File.....📤"
    RCHD_TG_API_LIMIT = "Downloaded in {} seconds.\nDetected File Size: {}\nSorry.\nBut, I cannot upload files greater than 1.95GB due to Telegram API limitations.I can't do anything for that 🤷‍♂️."
    AFTER_SUCCESSFUL_UPLOAD_MSG = "📄 Done"
    AFTER_SUCCESSFUL_UPLOAD_MSG_VIDEO = "🎞 Done"
    AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = "📥 {} seconds.\n📤 {} seconds."
    SAVED_CUSTOM_THUMB_NAIL = "Custom File thumbnail saved ✅️ .\nThis image will be deleted with in 24hr🗑"
    DEL_ETED_CUSTOM_THUMB_NAIL = "✅ Custom thumbnail cleared succesfully."
    FF_MPEG_DEL_ETED_CUSTOM_MEDIA = "✅ Media cleared succesfully."
    SAVED_RECVD_DOC_FILE = "Document Downloaded Successfully. ✅"
    SAVED_RECVD_DOC_FILE_VIDEO = "Video Downloaded Successfully. ✅"
    CUSTOM_CAPTION_UL_FILE = ""
    NO_CUSTOM_THUMB_NAIL_FOUND = "❓ No Custom ThumbNail found."
    USER_ADDED_TO_DB = "User <a href='tg://user?id={}'>{}</a> added to {} till {}."
    HELP_USER = """Hai <b><i>{}</i></b>, 
1. Send Me A Thumbnail.
2. Send me the file to be Renamed.
3. Reply to that message with <code>/rename new name.extension</code>. with custom thumbnail support.\n(upload as file)
4. Reply to that message with <code>/rename_video new name.extension</code>. with custom thumbnail support.\n(uploading as Video)
5. Send <code>/deletethumbnail</code> for deleting saved thumbnail
"""
    REPLY_TO_DOC_FOR_RENAME_FILE = "🤦‍♂️ Reply to a Telegram media to `/rename New Name.extension` with custom thumbnail support.\n\n(For uploading as file).\n\nSee /help for more information. "
    REPLY_TO_DOC_FOR_RENAME_VIDEO = "🤦‍♂ Reply to a Telegram media to `/rename_video New Name.extension` with custom thumbnail support.\n\n(For uploading as video).\n\nSee /help for more information."
    IFLONG_FILE_NAME = """File Name limit allowed by Telegram is {alimit} characters.
The given file name has {num} characters.
<b>Essays Not allowed in Telegram file name!</b>
Please short your file name and try again!"""

    
class Localisation(object):    
    START_TEXT = "Send me any file to begin."

    FORCE_SUB_TEXT = "In order to use this bot, you've to join my parent channel."

    CHANNEL_LINK = "https://t.me/dental_case _study"

    SUPPORT_LINK = "https://t.me/dent_tech_for_books"

    info_text = "This bot is developed by @dent_tech_for_books\n\nWritten in python library TELETHON.\n\nBot by : @dent_tech_for_books\nSupport : @dental_case_study\n\nV1.1"   

    help_text = "Send me any video file to start compressing it or any kind of file to rename it.\n\n/compress - negligible loss compression\n/convert - change formats or extract audio of any video\n/rename - rename any file, extension not required\n/trim - cut your videos" 

    source_text = "Deploy your own bot.\n\nMain branch - Personal use\nPublic branch - For your channel"

    DEV = "https://t.me/dent_tech_for_books"

    spam_notice = "This bot is hosted on heroku, and hence can run just run one process at a time.Spamming the bot or encoding adult videos will lead you to a ban."

    JPG = "LOCAL/video_convertor.jpg"

    JPG2 = "LOCAL/20211215_165751.jpg"

    JPG3 = "LOCAL/PicsArt_12-16-08.57.15.jpg"
