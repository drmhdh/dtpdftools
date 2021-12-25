# !/usr/bin/python
# -*- coding: utf-8 -*-

# ABOUT DEV. & SOURCE CODE
#    nabilanavab, india, kerala
#    Telegram: @nabilanavab
#    Email: nabilanavab@gmail.com
#    copyright ©️ 2021 nabilanavab
#    Released Under Apache License


import os
import fitz
import shutil
import logging
import convertapi
from PIL import Image
from time import sleep
from configs import Config, Msgs, ADMINS
from pugins import callbacks
from pyrogram import Client, filters
from pyrogram.types import ForceReply
from PyPDF2 import PdfFileWriter, PdfFileReader
from pyrogram.types import InputMediaPhoto, InputMediaDocument
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

logger = logging.getLogger(__name__)

# LOGGING INFO
# logging.basicConfig(level=logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

BOT = {}
# PYROGRAM INSTANCE 
"""bot = Client(
    "pdf2img",
    parse_mode = "markdown",
    api_id = Config.API_ID,
    api_hash = Config.API_HASH,
    bot_token = Config.API_TOKEN
)"""

# GLOBAL VARIABLES
PDF = {}            # save images for generating pdf 
media = {}          # sending group images(pdf 2 img)
PDF2IMG = {}        # save fileId of each user(later uses)
PROCESS = []        # to check current process
mediaDoc = {}       # sending group document(pdf 2 img)
PAGENOINFO = {}     # saves no.of pages that user send last
PDF2IMGPGNO = {}    # more info about pdf file(for extraction)


# SUPPORTED FILES
suprtedFile = [
    ".jpg", ".jpeg", ".png"
]                                       # Img to pdf file support
suprtedPdfFile = [
    ".epub", ".xps", ".oxps",
    ".cbz", ".fb2"
]                                       # files to pdf (zero limits)
suprtedPdfFile2 = [
    ".csv", ".doc", ".docx", ".dot",
    ".dotx", ".log", ".mpp", ".mpt",
    ".odt", ".pot", ".potx", ".pps",
    ".ppsx", ".ppt", ".pptx", ".pub",
    ".rtf", ".txt", ".vdx", ".vsd",
    ".vsdx", ".vst", ".vstx", ".wpd",
    ".wps", ".wri", ".xls", ".xlsb",
    ".xlsx", ".xlt", ".xltx", ".xml"
]                                       # file to pdf (ConvertAPI limit)


# CREATING ConvertAPI INSTANCE
if Config.CONVERT_API is not None:
    convertapi.api_secret = os.getenv("CONVERT_API")

if Config.MAX_FILE_SIZE:
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE"))
    MAX_FILE_SIZE_IN_kiB = MAX_FILE_SIZE * 10000
    
# if message is an image
@Client.on_message(filters.private & filters.photo)
async def images(bot, message):
    
    try:
        await bot.send_chat_action(
            message.chat.id, "typing"
        )
        
        if Config.UPDATE_CHANNEL:
            check = await forceSub(message.chat.id)
            
            if check == "notSubscribed":
                return
        
        imageReply = await bot.send_message(
            message.chat.id,
            "`Downloading your Image..⏳`",
            reply_to_message_id = message.message_id
        )
        
        if not isinstance(PDF.get(message.chat.id), list):
            PDF[message.chat.id] = []
        
        await message.download(
            f"{message.chat.id}/{message.chat.id}.jpg"
        )
        
        img = Image.open(
            f"{message.chat.id}/{message.chat.id}.jpg"
        ).convert("RGB")
        
        PDF[message.chat.id].append(img)
        await imageReply.edit(
            Msgs.imageAdded.format(len(PDF[message.chat.id]))
        )
        
    except Exception:
        pass
    
    
 
# if message is a document/file
@Client.on_message(filters.command(["scan"])) #& filters.document  & filters.private
async def documents(bot, message):
    
    try:
        await bot.send_chat_action(
            message.chat.id, "typing"
        )
        
        if Config.UPDATE_CHANNEL:
            check = await forceSub(message.chat.id)
            
            if check == "notSubscribed":
                return
        
        isPdfOrImg = message.reply_to_message.document.file_name
        fileSize = message.reply_to_message.document.file_size
        fileNm, fileExt = os.path.splitext(isPdfOrImg)
        
        if Config.MAX_FILE_SIZE and fileSize >= int(MAX_FILE_SIZE_IN_kiB):
            
            try:
                bigFileUnSupport = await bot.send_message(
                    message.chat.id,
                    Msgs.bigFileUnSupport.format(Config.MAX_FILE_SIZE, Config.MAX_FILE_SIZE)
                )
                
                sleep(5)
                
                await bot.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = message.message_id
                )
                
                await bot.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = bigFileUnSupport.message_id
                )
                
            except Exception:
                pass
        elif fileExt.lower() in suprtedFile:
            
            try:
                imageDocReply = await bot.send_message(
                    message.chat.id,
                    "`Downloading your Image..⏳`",
                    reply_to_message_id = message.reply_to_message.message_id
                )
                
                if not isinstance(PDF.get(message.chat.id), list):
                    PDF[message.chat.id] = []
                
                await message.reply_to_message.download(
                    f"{message.chat.id}/{message.chat.id}.jpg"
                )
                
                img = Image.open(
                    f"{message.chat.id}/{message.chat.id}.jpg"
                ).convert("RGB")
                
                PDF[message.chat.id].append(img)
                await imageDocReply.edit(
                    Msgs.imageAdded.format(len(PDF[message.chat.id]))
                )
            
            except Exception as e:
                await imageDocReply.edit(
                    Msgs.errorEditMsg.format(e)
                )
                
                sleep(5)
                await bot.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = imageDocReply.message_id
                )
                
                await bot.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = message.message_id
                )
        
        elif fileExt.lower() == ".pdf":
            
            try:
                if message.chat.id in PROCESS:
                    
                    await message.reply_text(
                        '`Doing Some other Work.. 🥵`'
                    )
                    return
                
                pdfMsgId = await bot.send_message(
                    message.chat.id,
                    "`Processing.. 🚶`"
                )
                
                await message.reply_to_message.download(
                    f"{message.reply_to_message.message_id}/pdftoimage.pdf"
                )
                
                doc = fitz.open(f'{message.reply_to_message.message_id}/pdftoimage.pdf')
                noOfPages = doc.pageCount
                
                PDF2IMG[message.chat.id] = message.reply_to_message.document.file_id
                PDF2IMGPGNO[message.chat.id] = noOfPages
                
                await bot.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = pdfMsgId.message_id
                )
                
                await bot.send_chat_action(
                    message.chat.id, "typing"
                )
                
                pdfMsgId = await message.reply_to_message.reply_text(
                    Msgs.pdfReplyMsg.format(noOfPages),
                    reply_markup = ForceReply(),
                    parse_mode = "md"
                )
                
                doc.close()
                shutil.rmtree(f'{message.message_id}')
            
            except Exception as e:
                
                try:
                    PROCESS.remove(message.chat.id)
                    doc.close()
                    shutil.rmtree(f'{message.reply_to_message.message_id}')
                    
                    await pdfMsgId.edit(
                        Msgs.errorEditMsg.format(e)
                    )
                    """sleep(15)
                    await bot.delete_messages(
                        chat_id = message.chat.id,
                        message_ids = pdfMsgId.message_id
                    )"""
                    sleep(15)
                    await bot.delete_messages(
                        chat_id = message.chat.id,
                        message_ids = message.message_id
                    )
                
                except Exception:
                    pass
            
        elif fileExt.lower() in suprtedPdfFile:
            try:
                await bot.send_chat_action(
                    message.chat.id, "typing"
                )
                pdfMsgId = await message.reply_text(
                    "`Downloading your file..⏳`",
                )
                
                await message.reply_to_message.download(
                    f"{message.reply_to_message.message_id}/{isPdfOrImg}"
                )
                
                await pdfMsgId.edit(
                    "`Creating pdf..`💛"
                )
                
                Document = fitz.open(
                    f"{message.reply_to_message.message_id}/{isPdfOrImg}"
                )
                
                b = Document.convert_to_pdf()
                
                pdf = fitz.open("pdf", b)
                pdf.save(
                    f"{message.reply_to_message.message_id}/{fileNm}.pdf",
                    garbage = 4,
                    deflate = True,
                )
                pdf.close()
                
                await pdfMsgId.edit(
                    "`Started Uploading..`🏋️"
                )
                
                sendfile = open(
                    f"{message.reply_to_message.message_id}/{fileNm}.pdf", "rb"
                )
                
                await bot.send_document(
                    chat_id = message.chat.id,
                    document = sendfile,
                    thumb = Config.PDF_THUMBNAIL,
                    caption = f"`Converted: {fileExt} to pdf`"
                )
                await pdfMsgId.edit(
                    "`Uploading Completed..❤️`"
                )
                
                shutil.rmtree(f"{message.reply_to_message.message_id}")
                
                sleep(5)
                await bot.send_chat_action(
                    message.chat.id, "typing"
                )
                await bot.send_message(
                    message.chat.id, Msgs.feedbackMsg,
                    disable_web_page_preview = True
                )
            
            except Exception as e:
                
                try:
                    shutil.rmtree(f"{message.reply_to_message.message_id}")
                    await pdfMsgId.edit(
                        Msgs.errorEditMsg.format(e)
                    )
                    sleep(15)
                    await bot.delete_messages(
                        chat_id = message.chat.id,
                        message_ids = pdfMsgId.message_id
                    )
                    await bot.delete_messages(
                        chat_id = message.chat.id,
                        message_ids = message.message_id
                    )
                    
                except Exception:
                    pass
        
        elif fileExt.lower() in suprtedPdfFile2:
            
            if os.getenv("CONVERT_API") is None:
                
                pdfMsgId = await message.reply_text(
                    "`Owner Forgot to add ConvertAPI.. contact Owner 😒`",
                )
                sleep(15)
                await bot.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = pdfMsgId.message_id
                )
            
            else:
                try:
                    await bot.send_chat_action(
                        message.chat.id, "typing"
                    )
                    pdfMsgId = await message.reply_to_message.reply_text(
                        "`Downloading your file..⏳`",
                    )
                    
                    await message.reply_to_message.download(
                        f"{message.reply_to_message.message_id}/{isPdfOrImg}"
                    )
                    
                    await pdfMsgId.edit(
                        "`Creating pdf..`💛"
                    )
                    
                    try:
                        await convertapi.convert(
                            "pdf",
                            {
                                "File": f"{message.reply_to_message.message_id}/{isPdfOrImg}"
                            },
                            from_format = fileExt[1:],
                        ).save_files(
                            f"{message.reply_to_message.message_id}/{fileNm}.pdf"
                        )
                        
                    except Exception:
                        
                        try:
                            shutil.rmtree(f"{message.reply_to_message.message_id}")
                            await pdfMsgId.edit(
                                "ConvertAPI limit reaches.. contact Owner"
                            )
                            
                        except Exception:
                            pass
                    
                    sendfile = open(
                        f"{message.reply_to_message.message_id}/{fileNm}.pdf", "rb"
                    )
                    await bot.send_document(
                        chat_id = message.chat.id,
                        Document = sendfile,
                        thumb = Config.PDF_THUMBNAIL,
                        caption = f"`Converted: {fileExt} to pdf`",
                    )
                    
                    await pdfMsgId.edit(
                        "`Uploading Completed..`🏌️"
                    )
                    
                    shutil.rmtree(f"{message.reply_to_message.message_id}")
                    
                    sleep(5)
                    await bot.send_chat_action(
                        message.chat.id, "typing"
                    )
                    await bot.send_message(
                        message.chat.id, Msgs.feedbackMsg,
                        disable_web_page_preview = True
                    )
                
                except Exception:
                    pass
        
        else:
            
            try:
                await bot.send_chat_action(
                    message.chat.id, "typing"
                )
                unSuprtd = await bot.send_message(
                    message.chat.id, "`unsupported file..🙄`"
                )
                sleep(15)
                await bot.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = message.message_id
                )
                await bot.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = unSuprtd.message_id
                )
                
            except Exception:
                pass
            
    except Exception:
        pass







# REPLY TO /start COMMAND
@Client.on_message(filters.command(["start"]))
async def start(bot, message):
    
    try:
        await bot.send_chat_action(
            message.chat.id, "typing"
        )
        
        if Config.UPDATE_CHANNEL:
        
            try:
                await bot.get_chat_member(
                    str(Config.UPDATE_CHANNEL), message.chat.id
                )
            
            except Exception:
                invite_link = await bot.create_chat_invite_link(
                    int(Config.UPDATE_CHANNEL)
                )
                
                await bot.send_message(
                    message.chat.id,
                    Msgs.forceSubMsg.format(
                        message.from_user.first_name, message.chat.id
                    ),
                    reply_markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🌟 JOIN CHANNEL 🌟",
                                    url = invite_link.invite_link
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "Refresh ♻️",
                                    callback_data = "refresh"
                                )
                            ]
                        ]
                    )
                )
                
                await bot.delete_messages(
                    chat_id = message.chat.id,
                    message_ids = message.message_id
                )
                return
        
        await bot.send_message(
            message.chat.id,
            Msgs.welcomeMsg.format(
                message.from_user.first_name, message.chat.id
            ),
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "About",
                            callback_data = "strtDevEdt"
                        ),
                        InlineKeyboardButton(
                            "Help 🎊",
                            callback_data = "imgsToPdfEdit"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Close",
                            callback_data = "close"
                        )
                    ]
                ]
            )
        )
        await bot.delete_messages(
            chat_id = message.chat.id,
            message_ids = message.message_id
        )
        
    except Exception:
        pass
    
    
    
# /deletes : Deletes current Images to pdf Queue
@Client.on_message(filters.command(["deletepdf"]))
async def cancelI2P(bot, message):
    
    try:
        await bot.send_chat_action(
            message.chat.id, "typing"
        )
        del PDF[message.chat.id]
        await bot.send_message(
            message.chat.id, "`Queue deleted Successfully..`🤧",
            reply_to_message_id = message.message_id
        )
        shutil.rmtree(f"{message.chat.id}")
        
    except Exception:
        await bot.send_message(
            message.chat.id, "`No Queue founded..`😲",
            reply_to_message_id = message.message_id
        )


# cancel current pdf to image Queue
@Client.on_message(filters.command(["cancelpdf"]))
async def cancelP2I(bot, message):
    
    try:
        PROCESS.remove(message.chat.id)
        await bot.send_chat_action(
            message.chat.id, "typing"
        )
        await bot.send_message(
            message.chat.id, '`Canceled current work..`🤧'
        )
    
    except Exception:
        await bot.send_message(
            message.chat.id, '`Nothing to cancel..`🏃'
        )

       
# if message is a /feedback
@Client.on_message(filters.command(["feedback"]))
async def feedback(bot, message):
    
    try:
        await bot.send_chat_action(
            message.chat.id, "typing"
        )
        await bot.send_message(
            message.chat.id, Msgs.feedbackMsg,
            disable_web_page_preview = True
        )
        
    except Exception:
        pass


# If message is /generate
@Client.on_message(filters.command(["generate"]) & filters.private)
async def generate(bot, message):
    
    try:
        newName = str(message.text.replace("/generate", ""))
        images = PDF.get(message.chat.id)
        
        if isinstance(images, list):
            pgnmbr = len(PDF[message.chat.id])
            del PDF[message.chat.id]
        
        if not images:
            await bot.send_chat_action(
                message.chat.id, "typing"
            )
            imagesNotFounded = await message.reply_text(
                "`No image founded.!!`😒"
            )
            sleep(5)
            await message.delete()
            await bot.delete_messages(
                chat_id = message.chat.id,
                message_ids = imagesNotFounded.message_id
            )
            return
        
        gnrtMsgId = await bot.send_message(
            message.chat.id, f"`Generating pdf..`💚"
        )
        
        if newName == " name":
            fileName = f"{message.from_user.first_name}" + ".pdf"
        
        elif len(newName) > 1 and len(newName) <= 15:
            fileName = f"{newName}" + ".pdf"
        
        elif len(newName) > 15:
            fileName = f"{message.from_user.first_name}" + ".pdf"
        
        else:
            fileName = f"{message.chat.id}" + ".pdf"
        
        images[0].save(fileName, save_all = True, append_images = images[1:])
        
        await gnrtMsgId.edit(
            "`Uploading pdf.. `🏋️",
        )
        await bot.send_chat_action(
            message.chat.id, "upload_document"
        )
        
        with open(fileName, "rb") as sendfile:
            
            await bot.send_document(
                chat_id = message.chat.id,
                document = sendfile,
                thumb = Config.PDF_THUMBNAIL,
                caption = f"file Name: `{fileName}`\n\n`Total pg's: {pgnmbr}`",
            )
        
        await gnrtMsgId.edit(
            "`Successfully Uploaded.. `🤫",
        )
        
        os.remove(fileName)
        shutil.rmtree(f"{message.chat.id}")
        
        sleep(5)
        await bot.send_chat_action(
            message.chat.id, "typing"
        )
        await bot.send_message(
            message.chat.id, Msgs.feedbackMsg,
            disable_web_page_preview = True
        )
        
    except Exception as e:
        os.remove(fileName)
        shutil.rmtree(f"{message.chat.id}")
        print(e)
   
    
    
@Client.on_message(filters.command(["extract"])) #& filters.user(ADMINS)
async def extract(bot, message):        
    try:
        if message.chat.id in PROCESS:
            
            await bot.send_chat_action(
                message.chat.id, "typing"
            )
            await message.reply_text("`Doing Some Work..🥵`", quote=True)
            return
        
        needPages = message.text.replace('/extract ', '')
        
        if message.chat.id not in PDF2IMG:
            try:
                await bot.send_chat_action(
                    message.chat.id, "typing"
                )
            
                isPdfOrImg = message.reply_to_message.document.file_name
                fileSize = message.reply_to_message.document.file_size
                fileNm, fileExt = os.path.splitext(isPdfOrImg)
        
                if Config.MAX_FILE_SIZE and fileSize >= int(MAX_FILE_SIZE_IN_kiB):
            
                    try:
                        bigFileUnSupport = await bot.send_message(
                            message.chat.id,
                            Msgs.bigFileUnSupport.format(Config.MAX_FILE_SIZE, Config.MAX_FILE_SIZE)
                        )
                
                        sleep(5)
                
                        await bot.delete_messages(
                            chat_id = message.chat.id,
                            message_ids = message.message_id
                        )
                
                        await bot.delete_messages(
                            chat_id = message.chat.id,
                            message_ids = bigFileUnSupport.message_id
                        )
                
                    except Exception:
                        pass
        
                elif fileExt.lower() in suprtedFile:
            
                    try:
                        imageDocReply = await bot.send_message(
                            message.chat.id,
                            "`Downloading your Image..⏳`",
                            reply_to_message_id = message.message_id
                        )
                
                        if not isinstance(PDF.get(message.chat.id), list):
                            PDF[message.chat.id] = []
                
                        await message.download(
                            f"{message.chat.id}/{message.chat.id}.jpg"
                        )
                
                        img = Image.open(
                            f"{message.chat.id}/{message.chat.id}.jpg"
                        ).convert("RGB")
                
                        PDF[message.chat.id].append(img)
                        await imageDocReply.edit(
                            Msgs.imageAdded.format(len(PDF[message.chat.id]))
                        )
            
                    except Exception as e:
                
                        await imageDocReply.edit(
                            Msgs.errorEditMsg.format(e)
                        )
                
                        sleep(5)
                        await bot.delete_messages(
                            chat_id = message.chat.id,
                            message_ids = imageDocReply.message_id
                        )
                
                        await bot.delete_messages(
                            chat_id = message.chat.id,
                            message_ids = message.message_id
                        )
        
                elif fileExt.lower() == ".pdf":
            
                    try:
                        if message.chat.id in PROCESS:
                    
                            await message.reply_text(
                                '`Doing Some other Work.. 🥵`'
                            )
                            return
                
                        pdfMsgId = await bot.send_message(
                            message.chat.id,
                            "`Processing.. 🚶`"
                        )
                
                        await message.reply_to_message.download(
                            f"{message.reply_to_message.message_id}/pdftoimage.pdf"
                        )
                
                        doc = fitz.open(f'{message.reply_to_message.message_id}/pdftoimage.pdf')
                        noOfPages = doc.pageCount
                
                        PDF2IMG[message.chat.id] = message.reply_to_message.document.file_id
                        PDF2IMGPGNO[message.chat.id] = noOfPages
                
                        await bot.delete_messages(
                            chat_id = message.reply_to_message.chat.id,
                            message_ids = pdfMsgId.message_id
                        )
                
                        await bot.send_chat_action(
                            message.chat.id, "typing"
                        )
                
                        pdfMsgId = await message.reply_to_message.reply_text(
                            Msgs.pdfReplyMsg.format(noOfPages) , 
                            #text = f"Extract images from `{PAGENOINFO[message.chat.id][1]}` to `{PAGENOINFO[message.chat.id][2]}`:",
                            #reply_markup = ForceReply(),
                            #parse_mode = "md" 
                        )
                   
                        doc.close()
                        shutil.rmtree(f'{message.reply_to_message.message_id}')
             
                    except Exception as e:
                
                        try:
                            PROCESS.remove(message.reply_to_message.chat.id)
                            doc.close()
                            shutil.rmtree(f'{message.reply_to_message.message_id}')
                    
                            await pdfMsgId.edit(
                                Msgs.errorEditMsg.format(e)
                            )
                            sleep(15)
                            await bot.delete_messages(
                                chat_id = message.chat.id,
                                message_ids = pdfMsgId.message_id
                            )
                            await bot.delete_messages(
                                chat_id = message.chat.id,
                                message_ids = message.message_id
                            )
                
                        except Exception:
                            pass
        
                elif fileExt.lower() in suprtedPdfFile:
            
                    try:
                        await bot.send_chat_action(
                            message.chat.id, "typing"
                        )
                        pdfMsgId = await message.reply_to_message.reply_text(
                            "`Downloading your file..⏳`",
                        )
                
                        await message.download(
                            f"{message.reply_to_message.message_id}/{isPdfOrImg}"
                        )
                
                        await pdfMsgId.edit(
                            "`Creating pdf..`💛"
                        )
                
                        Document = fitz.open(
                            f"{message.reply_to_message.message_id}/{isPdfOrImg}"
                        )
                
                        b = Document.convert_to_pdf()
                
                        pdf = fitz.open("pdf", b)
                        pdf.save(
                            f"{message.reply_to_message.message_id}/{fileNm}.pdf",
                            garbage = 4,
                            deflate = True,
                        )
                        pdf.close()
                
                        await pdfMsgId.edit(
                            "`Started Uploading..`🏋️"
                        )
                
                        sendfile = open(
                            f"{message.reply_to_message.message_id}/{fileNm}.pdf", "rb"
                        )
                
                        await bot.send_document(
                            chat_id = message.chat.id,
                            document = sendfile,
                            thumb = Config.PDF_THUMBNAIL,
                            caption = f"`Converted: {fileExt} to pdf`"
                        )
                        await pdfMsgId.edit(
                            "`Uploading Completed..❤️`"
                        )
                
                        shutil.rmtree(f"{message.reply_to_message.message_id}")
                
                        sleep(5)
                        await bot.send_chat_action(
                            message.chat.id, "typing"
                        )
                        await bot.send_message(
                            message.chat.id, Msgs.feedbackMsg,
                            disable_web_page_preview = True
                        )
            
                    except Exception as e:
                
                        try:
                            shutil.rmtree(f"{message.reply_to_message.message_id}")
                            await pdfMsgId.edit(
                                Msgs.errorEditMsg.format(e)
                            )
                            sleep(15)
                            await bot.delete_messages(
                                chat_id = message.chat.id,
                                message_ids = pdfMsgId.message_id
                            )
                            await bot.delete_messages(
                                chat_id = message.chat.id,
                                message_ids = message.message_id
                            )
                    
                        except Exception:
                            pass
        
                elif fileExt.lower() in suprtedPdfFile2:
            
                    if os.getenv("CONVERT_API") is None:
                
                        pdfMsgId = await message.reply_text(
                            "`Owner Forgot to add ConvertAPI.. contact Owner 😒`",
                        )
                        sleep(15)
                        await bot.delete_messages(
                            chat_id = message.chat.id,
                            message_ids = pdfMsgId.message_id
                        )
            
                    else:
                
                        try:
                            await bot.send_chat_action(
                                message.chat.id, "typing"
                            )
                            pdfMsgId = await message.reply_text(
                                "`Downloading your file..⏳`",
                            )
                    
                            await message.download(
                                f"{message.message_id}/{isPdfOrImg}"
                            )
                    
                            await pdfMsgId.edit(
                                "`Creating pdf..`💛"
                            )
                    
                            try:
                                await convertapi.convert(
                                    "pdf",
                                    {
                                        "File": f"{message.message_id}/{isPdfOrImg}"
                                    },
                                    from_format = fileExt[1:],
                                ).save_files(
                                    f"{message.message_id}/{fileNm}.pdf"
                                )
                        
                            except Exception:
                        
                                try:
                                    shutil.rmtree(f"{message.message_id}")
                                    await pdfMsgId.edit(
                                        "ConvertAPI limit reaches.. contact Owner"
                                    )
                            
                                except Exception:
                                    pass
                    
                            sendfile = open(
                                f"{message.message_id}/{fileNm}.pdf", "rb"
                            )
                            await bot.send_document(
                                chat_id = message.chat.id,
                                Document = sendfile,
                                thumb = Config.PDF_THUMBNAIL,
                               caption = f"`Converted: {fileExt} to pdf`",
                            )
                            sleep(5)
                            await pdfMsgId.edit(
                                "`Uploading Completed..`🏌️"
                            )
                    
                            shutil.rmtree(f"{message.reply_to_message.message_id}")
                    
                            sleep(5)
                            await bot.send_chat_action(
                                message.reply_to_message.chat.id, "typing"
                            )
                            sleep(5)
                            await bot.send_message(
                                message.reply_to_message.chat.id, Msgs.feedbackMsg,
                                disable_web_page_preview = True
                            )
                
                        except Exception:
                            pass
          
                else:
            
                    try:
                        await bot.send_chat_action(
                            message.chat.id, "typing"
                        )
                        unSuprtd = await bot.send_message(
                            message.chat.id, "`unsupported file..🙄`"
                        )
                        sleep(15)
                        await bot.delete_messages(
                            chat_id = message.chat.id,
                            message_ids = message.message_id
                        )
                        await bot.delete_messages(
                            chat_id = message.chat.id,
                            message_ids = unSuprtd.message_id
                        )
                
                    except Exception:
                        pass
         
            except:
                pass
        
        
        pageStartAndEnd = list(needPages.replace('-',':').split(':'))
            
        if len(pageStartAndEnd) > 2:
                
            await bot.send_message(
                message.chat.id,
                "`I just asked you starting & ending 😅`"
            )
            return
            
        elif len(pageStartAndEnd) == 2:
            try:
                    
                if (1 <= int(pageStartAndEnd[0]) <= PDF2IMGPGNO[message.chat.id]):
                        
                    if (int(pageStartAndEnd[0]) < int(pageStartAndEnd[1]) <= PDF2IMGPGNO[message.chat.id]):
                        PAGENOINFO[message.chat.id] = [False, int(pageStartAndEnd[0]), int(pageStartAndEnd[1]), None]    #elmnts in list (is singlePage, start, end, if single pg number)
                            
                    else:
                        await bot.send_message(
                            message.chat.id,
                            "`Syntax Error: errorInEndingPageNumber 😅`"
                        )
                        return
                        #pass
                        
                else:
                    await bot.send_message(
                        message.chat.id,
                        "`Syntax Error: errorInStartingPageNumber 😅`"
                    )
                    return
                    #pass
                    
            except:
                    
                await bot.send_message(
                    message.chat.id,
                    "`Syntax Error: noSuchPageNumbers 🤭`"
                )
                return
                #pass
            
        elif len(pageStartAndEnd) == 1:
                
            if pageStartAndEnd[0] == "/extract":
                    
                if (PDF2IMGPGNO[message.chat.id]) == 1:
                    PAGENOINFO[message.chat.id] = [True, None, None, 1]
                    #elmnts in list (is singlePage, start, end, if single pg number)
                    
                else:
                    PAGENOINFO[message.chat.id] = [False, 1, PDF2IMGPGNO[message.chat.id], None]
                    #elmnts in list (is singlePage, start, end, if single pg number)
                    
            elif 0 < int(pageStartAndEnd[0]) <= PDF2IMGPGNO[message.chat.id]:
                PAGENOINFO[message.chat.id] = [True, None, None, pageStartAndEnd[0]]
                
            else:
                await bot.send_message(
                    message.chat.id,
                    '`Syntax Error: noSuchPageNumber 🥴`'
                )
                return
            
        else:
            await bot.send_message(
                message.chat.id,
                "`Syntax Error: pageNumberMustBeAnIntiger 🧠`"
            )
            return
            
        if PAGENOINFO[message.chat.id][0] == False:
                
            if pageStartAndEnd[0] == "/extract":
                await bot.send_message(
                    message.chat.id,
                    text = f"Extract images from `{PAGENOINFO[message.chat.id][1]}` to `{PAGENOINFO[message.chat.id][2]}` As:",
                    disable_web_page_preview = True,
                    reply_markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                     "Images 🖼️️",
                                    callback_data = "multipleImgAsImages"
                                ),
                                InlineKeyboardButton(
                                    "Document 📁 ",
                                    callback_data = "multipleImgAsDocument"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "PDF 🎭",
                                    callback_data = "multipleImgAsPdfError"
                                )
                            ]
                        ]
                    )
                )
                
            else:
                await bot.send_message(
                    message.chat.id,
                    text = f"Extract images from `{PAGENOINFO[message.chat.id][1]}` to `{PAGENOINFO[message.chat.id][2]}` As:",
                    disable_web_page_preview = True,
                    reply_markup = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Images 🖼️️",
                                    callback_data = "multipleImgAsImages"
                                ),
                                InlineKeyboardButton(
                                    "Document 📁 ",
                                    callback_data = "multipleImgAsDocument"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    "PDF 🎭",
                                    callback_data = "multipleImgAsPdf"
                                )
                            ]
                        ]
                    )
                )
                
        if PAGENOINFO[message.chat.id][0] == True:
                
            await bot.send_message(
                message.chat.id,
                text = f"Extract page number: `{PAGENOINFO[message.chat.id][3]}` As:",
                disable_web_page_preview = True,
                reply_markup = InlineKeyboardMarkup(
                    [
                         [
                            InlineKeyboardButton(
                                "Images 🖼️️",
                                callback_data = "asImages"
                            ),
                             InlineKeyboardButton(
                                "Document 📁 ",
                                callback_data = "asDocument"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "PDF 🎭",
                                callback_data = "asPdf"
                            )
                        ]
                    ]
                )
            )
        
    except Exception:
        
        try:
            del PAGENOINFO[message.chat.id]
            PROCESS.remove(message.chat.id)
            
        except Exception:
            pass
            

