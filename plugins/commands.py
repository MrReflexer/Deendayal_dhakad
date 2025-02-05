import os
import re, sys
import json
import base64
import logging
import random
import asyncio
import time
import pytz
from database.verify_db import vr_db
from .pmfilter import auto_filter 
from Script import script
from datetime import datetime
from database.refer import referdb
from database.config_db import mdb
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.types import *
from database.ia_filterdb import Media, Media2, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db, delete_all_msg
from info import CHANNELS, FSUB_PICS, ADMINS,  LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, CHNL_LNK, REQST_CHANNEL, GRP_LNK, SUPPORT_CHAT_ID, MAX_B_TN, VERIFY, REACTIONS, HOW_TO_VERIFY, PICS, DEENDAYAL_VERIFIED_LOG, SUBSCRIPTION, DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK, STREAM_MODE, EMOJI_MODE, OWNER_LNK, OWNER_UPI_ID, QR_CODE
from utils import get_settings, get_size, is_subscribed,  save_group_settings, temp, verify_user, check_token, check_verification, get_token, get_shortlink, get_tutorial
from database.connections_mdb import active_connection



# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


TIMEZONE = "Asia/Kolkata"
BATCH_FILES = {}


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):

    if EMOJI_MODE:    
        await message.react(emoji=random.choice(REACTIONS), big=True) 

    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [[
                    InlineKeyboardButton('тЭдя╕П с┤Ас┤Ес┤Е с┤Нс┤З с┤Ыс┤П ╩Пс┤Пс┤Ь╩А ╔в╩Ас┤Пс┤Ьс┤Ш тЭдя╕П', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('ЁЯНБ с┤Нс┤А╔к╔┤ с┤Д╩Ьс┤А╔┤╔┤с┤З╩ЯЁЯНБ', url=CHNL_LNK)
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.GSTART_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
        await asyncio.sleep(2) # ЁЯШв ЁЯШм wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
                    InlineKeyboardButton('ЁЯФ░ с┤Ас┤Ес┤Е с┤Нс┤З с┤Ыс┤П ╩Пс┤Пс┤Ь╩А ╔в╩Ас┤Пс┤Ьс┤Ш ЁЯФ░', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('ЁЯХ╡я╕ПтАНтЩВя╕П Tс┤Пс┤Ш Sс┤Зс┤А╩Ас┤Д╩Ь╔к╔┤╔в', callback_data="topsearch"),
                    InlineKeyboardButton(' sс┤Ьс┤Шс┤Шс┤П╩Ас┤Ы ЁЯФД', callback_data='channels')
                ],[
                    InlineKeyboardButton(' ╩Ьс┤З╩Яс┤Ш ЁЯЪи', callback_data='help'),
                    InlineKeyboardButton(' с┤А╩Щс┤Пс┤Ьс┤Ы тЭУ ', callback_data='about')
                ],[
                    InlineKeyboardButton('Dс┤П╔┤с┤Ас┤Ы╔кс┤П╔┤ ЁЯТ░', callback_data='donation'),
                    InlineKeyboardButton('Eс┤А╩А╔┤ с┤Нс┤П╔┤с┤З╩ПЁЯТ▓', callback_data="shortlink_info")
                ],[
                    InlineKeyboardButton('тЬи ╩Щс┤Ь╩П ъЬ▒с┤Ь╩ЩъЬ▒с┤Д╩А╔кс┤Шс┤Ы╔кс┤П╔┤ : ╩Ас┤Зс┤Нс┤Пс┤ас┤З с┤Ас┤ЕъЬ▒ тЬи', callback_data="premium_info")
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        curr_time = current_time.hour        
        if curr_time < 12:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Нс┤П╩А╔┤╔к╔┤╔в ЁЯСЛ" 
        elif curr_time < 17:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤А╥Ус┤Ыс┤З╩А╔┤с┤Пс┤П╔┤ ЁЯСЛ" 
        elif curr_time < 21:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Зс┤ас┤З╔┤╔к╔┤╔в ЁЯСЛ"
        else:
            gtxt = "╔вс┤Пс┤Пс┤Е ╔┤╔к╔в╩Ьс┤Ы ЁЯСЛ"
        m=await message.reply_text("тП│")
        await asyncio.sleep(0.4)
        await m.delete()        
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    if not await db.has_premium_access(message.from_user.id):
        channels = (await get_settings(int(message.from_user.id))).get('fsub')
        if channels:  
            btn = await is_subscribed(client, message, channels)
            if btn:
                kk, file_id = message.command[1].split("_", 1)
                btn.append([InlineKeyboardButton("тЩ╗я╕П с┤Ы╩А╩П с┤А╔вс┤А╔к╔┤ тЩ╗я╕П", callback_data=f"checksub#{kk}#{file_id}")])
                reply_markup = InlineKeyboardMarkup(btn)
                caption = (
                    f"ЁЯСЛ Hello {message.from_user.mention}\n\n"
                    "Yс┤Пс┤Ь ╩Ьс┤Ас┤ас┤З ╔┤с┤Пс┤Ы Jс┤П╔к╔┤с┤Зс┤Е с┤А╩Я╩Я с┤Пс┤Ь╩А Uс┤Шс┤Ес┤Ас┤Ыс┤Зs C╩Ьс┤А╔┤╔┤с┤З╩Яs.\n"
                    "P╩Яс┤Зс┤Аsс┤З с┤Д╩Я╔кс┤Дс┤Л с┤П╔┤ с┤Ы╩Ьс┤З **Jс┤П╔к╔┤ Uс┤Шс┤Ес┤Ас┤Ыс┤Зs C╩Ьс┤А╔┤╔┤с┤З╩Яs** ╩Щс┤Ьс┤Ыс┤Ыс┤П╔┤s ╩Щс┤З╩Яс┤Пс┤б с┤А╔┤с┤Е с┤Нс┤Ас┤Лс┤З sс┤Ь╩Ас┤З с┤Ыс┤П с┤Кс┤П╔к╔┤ **с┤А╩Я╩Я** с┤Д╩Ьс┤А╔┤╔┤с┤З╩Яs ╩Я╔кsс┤Ыс┤Зс┤Е.\n"
                    "A╥Ус┤Ыс┤З╩А с┤Ы╩Ьс┤Ас┤Ы, с┤Ш╩Яс┤Зс┤Аsс┤З с┤Ы╩А╩П с┤А╔вс┤А╔к╔┤.\n\n"
                    "рдЖрдкрдиреЗ рд╣рдорд╛рд░реЗ **рд╕рднреА Uс┤Шс┤Ес┤Ас┤Ыс┤Зs C╩Ьс┤А╔┤╔┤с┤З╩Яs** рдХреЛ рдЬреНрд╡рд╛рдЗрди рдирд╣реАрдВ рдХрд┐рдпрд╛ рд╣реИред\n"
                    "**Jс┤П╔к╔┤ Uс┤Шс┤Ес┤Ас┤Ыс┤Зs C╩Ьс┤А╔┤╔┤с┤З╩Яs** рд╡рд╛рд▓реЗ рдмрдЯрди рдкрд░ C╩Я╔кс┤Дс┤Л рдХрд░реЗрдВред рдФрд░ рд╕реБрдирд┐рд╢реНрдЪрд┐рдд рдХрд░реЗрдВ рдХрд┐ рдЖрдкрдиреЗ **рд╕рднреА рдЪреИрдирд▓реНрд╕** рдХреЛ рдЬреНрд╡рд╛рдЗрди рдХрд┐рдпрд╛ рд╣реИред\n"
                    "рдЗрд╕рдХреЗ рдмрд╛рдж рдЖрдк рдлрд┐рд░ рд╕реЗ с┤Ы╩А╩П рдХрд░реЗрдВред..")
                await message.reply_photo(
                    photo=random.choice(FSUB_PICS),
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                return
       
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
                    InlineKeyboardButton('ЁЯФ░ с┤Ас┤Ес┤Е с┤Нс┤З с┤Ыс┤П ╩Пс┤Пс┤Ь╩А ╔в╩Ас┤Пс┤Ьс┤Ш ЁЯФ░', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('ЁЯХ╡я╕ПтАНтЩВя╕П Tс┤Пс┤Ш Sс┤Зс┤А╩Ас┤Д╩Ь╔к╔┤╔в', callback_data="topsearch"),
                    InlineKeyboardButton(' sс┤Ьс┤Шс┤Шс┤П╩Ас┤Ы ЁЯФД', callback_data='channels')
                ],[
                    InlineKeyboardButton(' ╩Ьс┤З╩Яс┤Ш ЁЯЪи', callback_data='help'),
                    InlineKeyboardButton(' с┤А╩Щс┤Пс┤Ьс┤Ы тЭУ ', callback_data='about')
                ],[
                    InlineKeyboardButton('Dс┤П╔┤с┤Ас┤Ы╔кс┤П╔┤ ЁЯТ░', callback_data='donation'),
                    InlineKeyboardButton('Eс┤А╩А╔┤ с┤Нс┤П╔┤с┤З╩ПЁЯТ▓', callback_data="shortlink_info")
                ],[
                    InlineKeyboardButton('тЬи ╩Щс┤Ь╩П ъЬ▒с┤Ь╩ЩъЬ▒с┤Д╩А╔кс┤Шс┤Ы╔кс┤П╔┤ : ╩Ас┤Зс┤Нс┤Пс┤ас┤З с┤Ас┤ЕъЬ▒ тЬи', callback_data="premium_info")
                ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        curr_time = current_time.hour        
        if curr_time < 12:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Нс┤П╩А╔┤╔к╔┤╔в ЁЯСЛ" 
        elif curr_time < 17:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤А╥Ус┤Ыс┤З╩А╔┤с┤Пс┤П╔┤ ЁЯСЛ" 
        elif curr_time < 21:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Зс┤ас┤З╔┤╔к╔┤╔в ЁЯСЛ"
        else:
            gtxt = "╔вс┤Пс┤Пс┤Е ╔┤╔к╔в╩Ьс┤Ы ЁЯСЛ"
        m=await message.reply_text("тП│")
        await asyncio.sleep(0.4)
        await m.delete()        
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, gtxt, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if message.command[1].startswith("reff_"):
        try:
            user_id = int(message.command[1].split("_")[1])
        except ValueError:
            await message.reply_text("Invalid refer!")
            return
        if user_id == message.from_user.id:
            await message.reply_text("Hс┤З╩П Dс┤Ьс┤Ес┤З, Yс┤Пс┤Ь Cс┤А╔┤'с┤Ы Rс┤З╥Ус┤З╩А Yс┤Пс┤Ь╩Аsс┤З╩Я╥У ЁЯдг!\n\ns╩Ьс┤А╩Ас┤З ╩Я╔к╔┤с┤Л ╩Пс┤Пс┤Ь╩А ╥У╩А╔кс┤З╔┤с┤Е с┤А╔┤с┤Е ╔вс┤Зс┤Ы 10 ╩Ас┤З╥Ус┤З╩А╩Ас┤А╩Я с┤Шс┤П╔к╔┤с┤Ы ╔к╥У ╩Пс┤Пс┤Ь с┤А╩Ас┤З с┤Дс┤П╩Я╩Яс┤Зс┤Дс┤Ы╔к╔┤╔в 100 ╩Ас┤З╥Ус┤З╩А╩Ас┤А╩Я с┤Шс┤П╔к╔┤с┤Ыs с┤Ы╩Ьс┤З╔┤ ╩Пс┤Пс┤Ь с┤Дс┤А╔┤ ╔вс┤Зс┤Ы 1 с┤Нс┤П╔┤с┤Ы╩Ь ╥У╩Ас┤Зс┤З с┤Ш╩Ас┤Зс┤Н╔кс┤Ьс┤Н с┤Нс┤Зс┤Н╩Щс┤З╩Аs╩Ь╔кс┤Ш.")
            return
        if referdb.is_user_in_list(message.from_user.id):
            await message.reply_text("Yс┤Пс┤Ь ╩Ьс┤Ас┤ас┤З ╩Щс┤Зс┤З╔┤ с┤А╩Я╩Ас┤Зс┤Ас┤Е╩П ╔к╔┤с┤а╔кс┤Ыс┤Зс┤Е тЭЧ")
            return
        try:
            uss = await client.get_users(user_id)
        except Exception:
            return 	    
        referdb.add_user(message.from_user.id)
        fromuse = referdb.get_refer_points(user_id) + 10
        if fromuse == 100:
            referdb.add_refer_points(user_id, 0) 
            await message.reply_text(f"ЁЯОЙ ЁЭЧЦЁЭЧ╝ЁЭЧ╗ЁЭЧ┤ЁЭЧ┐ЁЭЧоЁЭШБЁЭШВЁЭЧ╣ЁЭЧоЁЭШБЁЭЧ╢ЁЭЧ╝ЁЭЧ╗ЁЭША! ЁЭЧмЁЭЧ╝ЁЭШВ ЁЭШДЁЭЧ╝ЁЭЧ╗ ЁЭЯнЁЭЯм ЁЭЧеЁЭЧ▓ЁЭЧ│ЁЭЧ▓ЁЭЧ┐ЁЭЧ┐ЁЭЧоЁЭЧ╣ ЁЭЧ╜ЁЭЧ╝ЁЭЧ╢ЁЭЧ╗ЁЭШБ ЁЭЧпЁЭЧ▓ЁЭЧ░ЁЭЧоЁЭШВЁЭШАЁЭЧ▓ ЁЭЧмЁЭЧ╝ЁЭШВ ЁЭЧ╡ЁЭЧоЁЭШГЁЭЧ▓ ЁЭЧпЁЭЧ▓ЁЭЧ▓ЁЭЧ╗ ЁЭЧжЁЭШВЁЭЧ░ЁЭЧ░ЁЭЧ▓ЁЭШАЁЭШАЁЭЧ│ЁЭШВЁЭЧ╣ЁЭЧ╣ЁЭШЖ ЁЭЧЬЁЭЧ╗ЁЭШГЁЭЧ╢ЁЭШБЁЭЧ▓ЁЭЧ▒ тШЮ {uss.mention}!")		    
            await message.reply_text(user_id, f"You have been successfully invited by {message.from_user.mention}!") 	
            seconds = 2592000
            if seconds > 0:
                expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
                user_data = {"id": user_id, "expiry_time": expiry_time}  # Using "id" instead of "user_id"  
                await db.update_user(user_data)  # Use the update_user method to update or insert user data		    
                await client.send_message(
                chat_id=user_id,
                text=f"<b>Hс┤З╩П {uss.mention}\n\nYс┤Пс┤Ь ╔вс┤Пс┤Ы 1 с┤Нс┤П╔┤с┤Ы╩Ь с┤Ш╩Ас┤Зс┤Н╔кс┤Ьс┤Н sс┤Ь╩Щsс┤Д╩А╔кс┤Шс┤Ы╔кс┤П╔┤ ╩Щ╩П ╔к╔┤с┤а╔кс┤Ы╔к╔┤╔в 10 с┤Ьsс┤З╩Аs тЭЧ", disable_web_page_preview=True              
                )
            for admin in ADMINS:
                await client.send_message(chat_id=admin, text=f"Sс┤Ьс┤Дс┤Дс┤Зss ╥Ус┤Ь╩Я╩Я╩П с┤Ыс┤Аsс┤Л с┤Дс┤Пс┤Нс┤Ш╩Яс┤Зс┤Ыс┤Зс┤Е ╩Щ╩П с┤Ы╩Ь╔кs с┤Ьsс┤З╩А:\n\nuser Nс┤Ас┤Нс┤З: {uss.mention}\n\nUsс┤З╩А ╔кс┤Е: {uss.id}!")	
        else:
            referdb.add_refer_points(user_id, fromuse)
            await message.reply_text(f"You have been successfully invited by {uss.mention}!")
            await client.send_message(user_id, f"ЁЭЧЦЁЭЧ╝ЁЭЧ╗ЁЭЧ┤ЁЭЧ┐ЁЭЧоЁЭШБЁЭШВЁЭЧ╣ЁЭЧоЁЭШБЁЭЧ╢ЁЭЧ╝ЁЭЧ╗ЁЭША! ЁЭЧмЁЭЧ╝ЁЭШВ ЁЭШДЁЭЧ╝ЁЭЧ╗ ЁЭЯнЁЭЯм ЁЭЧеЁЭЧ▓ЁЭЧ│ЁЭЧ▓ЁЭЧ┐ЁЭЧ┐ЁЭЧоЁЭЧ╣ ЁЭЧ╜ЁЭЧ╝ЁЭЧ╢ЁЭЧ╗ЁЭШБ ЁЭЧпЁЭЧ▓ЁЭЧ░ЁЭЧоЁЭШВЁЭШАЁЭЧ▓ ЁЭЧмЁЭЧ╝ЁЭШВ ЁЭЧ╡ЁЭЧоЁЭШГЁЭЧ▓ ЁЭЧпЁЭЧ▓ЁЭЧ▓ЁЭЧ╗ ЁЭЧжЁЭШВЁЭЧ░ЁЭЧ░ЁЭЧ▓ЁЭШАЁЭШАЁЭЧ│ЁЭШВЁЭЧ╣ЁЭЧ╣ЁЭШЖ ЁЭЧЬЁЭЧ╗ЁЭШГЁЭЧ╢ЁЭШБЁЭЧ▓ЁЭЧ▒ тШЮ{message.from_user.mention}!")
        return
        
    if len(message.command) == 2 and message.command[1] in ["premium"]:
        buttons = [[
                    InlineKeyboardButton('ЁЯУ▓ ъЬ▒с┤З╔┤с┤Е с┤Шс┤А╩Пс┤Нс┤З╔┤с┤Ы ъЬ▒с┤Д╩Ас┤Зс┤З╔┤ъЬ▒╩Ьс┤Пс┤Ы', url=OWNER_LNK)
                  ],[
                    InlineKeyboardButton('тЭМ с┤Д╩Яс┤ПъЬ▒с┤З тЭМ', callback_data='close_data')
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=(SUBSCRIPTION),
            caption=script.PREPLANS_TXT.format(message.from_user.mention, OWNER_UPI_ID, QR_CODE),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return  
    if len(message.command) == 2 and message.command[1].startswith('getfile'):
        movies = message.command[1].split("-", 1)[1] 
        movie = movies.replace('-',' ')
        message.text = movie 
        await auto_filter(client, message) 
        return
    
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""

    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("<b>Please wait...</b>")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
        if not msgs:
            file = await client.download_media(file_id)
            try:
                with open(file) as file_data:
                    msgs = json.loads(file_data.read())
            except:
                await sts.edit("FAILED")
                return await client.send_message(LOG_CHANNEL, "UNABLE TO OPEN FILE.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs

        for msg in msgs:
            title = msg.get("title")
            size = get_size(int(msg.get("size", 0)))
            f_caption = msg.get("caption", "")

            if BATCH_FILE_CAPTION:
                try:
                    f_caption = BATCH_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption = f_caption

            if f_caption is None:
                f_caption = f"{title}"

            if STREAM_MODE:
                btn = [
                    [InlineKeyboardButton('ЁЯЪА ъЬ░с┤АъЬ▒с┤Ы с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е / с┤бс┤Ас┤Ыс┤Д╩Ь с┤П╔┤╩Я╔к╔┤с┤З ЁЯЦея╕П', callback_data=f'generate_stream_link:{file_id}')],
                    [InlineKeyboardButton('ЁЯУМ с┤Кс┤П╔к╔┤ с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤ЗъЬ▒ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ЁЯУМ', url=DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK)]  # Keep this line unchanged
                ]
            else:
                btn = [
                    [InlineKeyboardButton('ЁЯУМ с┤Кс┤П╔к╔┤ с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤ЗъЬ▒ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ЁЯУМ', url=DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK)]
                ]
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=InlineKeyboardMarkup(btn)
                )
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
            await asyncio.sleep(1)

        await sts.delete()
        return


    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("<b>Please wait...</b>")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()

    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2] 
        fileid = data.split("-", 3)[3]
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=False
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            btn = [[
                InlineKeyboardButton("C╩Я╔кс┤Дс┤Л Hс┤З╩Ас┤З Tс┤П Gс┤Зс┤Ы F╔к╩Яс┤З..ЁЯНБ", url=f"https://telegram.me/{temp.U_NAME}?start=files_{fileid}")
            ],[
                InlineKeyboardButton("ЁЯПГBс┤Ас┤Дс┤Л Tс┤П G╩Ас┤Пс┤Ьс┤Ш", url=GRP_LNK)
            ]]
            await message.reply_photo(
                photo="https://graph.org/file/6928de1539e2e80e47fb8.jpg",
                caption=f"<b>Hey {message.from_user.mention},\n\nЁЭСМЁЭСЬЁЭСв ЁЭР┤ЁЭСЯЁЭСТ ЁЭСЖЁЭСвЁЭСРЁЭСРЁЭСТЁЭСаЁЭСаЁЭСУЁЭСвЁЭСЩ ЁЭСЙЁЭСТЁЭСЯЁЭСЦЁЭСУЁЭСЦЁЭСТЁЭСС ! ЁЭСБЁЭСЬЁЭСд ЁЭСМЁЭСЬЁЭСв ЁЭР╗ЁЭСОЁЭСгЁЭСТ ЁЭСИЁЭСЫЁЭСЩЁЭСЦЁЭСЪЁЭСЦЁЭСбЁЭСТЁЭСС ЁЭР┤ЁЭСРЁЭСРЁЭСТЁЭСаЁЭСа ЁЭР╣ЁЭСЬЁЭСЯ 24 ЁЭР╗ЁЭСЬЁЭСвЁЭСЯЁЭСа.\n\n<blockquote>рдЖрдк рд╕рдлрд▓рддрд╛рдкреВрд░реНрд╡рдХ рд╕рддреНрдпрд╛рдкрд┐рдд рд╣реЛ рдЧрдП рд╣реИрдВ рдЕрдм рдЖрдк 24 рдШрдВрдЯреЗ рддрдХ ЁЭР╖ЁЭСЦЁЭСЯЁЭСТЁЭСРЁЭСб ЁЭСАЁЭСЬЁЭСгЁЭСЦЁЭСТ рдХреА ЁЭР╣ЁЭСЦЁЭСЩЁЭСТЁЭСа рдкреНрд░рд╛рдкреНрдд рдХрд░ рд╕рдХрддреЗ рд╣реИрдВред</blockquote></b>",
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await verify_user(client, userid, token) 
            await vr_db.save_verification(message.from_user.id) 
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%Y-%m-%d")
            
            deendayal_message = (
                f"Name: {message.from_user.mention}\n"
                f"Time: {current_time}\n"
                f"Date: {current_date}\n"
                f"#verify_completed"
            )
            await client.send_message(chat_id=DEENDAYAL_VERIFIED_LOG, text=deendayal_message)

        else:
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=False
            )
    if data.startswith("sendfiles"):
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        curr_time = current_time.hour        
        if curr_time < 12:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Нс┤П╩А╔┤╔к╔┤╔в ЁЯСЛ" 
        elif curr_time < 17:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤А╥Ус┤Ыс┤З╩А╔┤с┤Пс┤П╔┤ ЁЯСЛ" 
        elif curr_time < 21:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Зс┤ас┤З╔┤╔к╔┤╔в ЁЯСЛ"
        else:
            gtxt = "╔вс┤Пс┤Пс┤Е ╔┤╔к╔в╩Ьс┤Ы ЁЯСЛ"
        chat_id = int("-" + file_id.split("-")[1])
        userid = message.from_user.id if message.from_user else None
        g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=allfiles_{file_id}")
        k = await client.send_message(chat_id=message.from_user.id,text=f"ЁЯлВ ╩Ьс┤З╩П {message.from_user.mention}, {gtxt}\n\nтА╝я╕П ╔вс┤Зс┤Ы с┤А╩Я╩Я ъЬ░╔к╩Яс┤ЗъЬ▒ ╔к╔┤ с┤А ъЬ▒╔к╔┤╔в╩Яс┤З ╩Я╔к╔┤с┤Л тА╝я╕П\n\nтЬЕ ╩Пс┤Пс┤Ь╩А ╩Я╔к╔┤с┤Л ╔къЬ▒ ╩Ас┤Зс┤Ас┤Е╩П, с┤Л╔к╔┤с┤Е╩Я╩П с┤Д╩Я╔кс┤Дс┤Л с┤П╔┤ с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е ╩Щс┤Ьс┤Ыс┤Ыс┤П╔┤.\n\n<u>тЪая╕П ╔┤с┤Пс┤Ыс┤З :- с┤Ы╩Ь╔къЬ▒ с┤Нс┤ЗъЬ▒ъЬ▒с┤А╔вс┤З ╔къЬ▒ с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╔к╔┤ 5 с┤Н╔к╔┤с┤Ьс┤Ыс┤ЗъЬ▒ с┤Ыс┤П с┤Ас┤ас┤П╔кс┤Е с┤Дс┤Пс┤Ш╩П╩А╔к╔в╩Ьс┤Ы..ъЬ▒с┤Ас┤ас┤З с┤Ы╩Ь╔къЬ▒ ╩Я╔к╔┤с┤Л с┤Ыс┤П ъЬ▒с┤Пс┤Нс┤Зс┤б╩Ьс┤З╩Ас┤З с┤З╩ЯъЬ▒с┤З</u>", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton('ЁЯУБ с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е ЁЯУБ', url=g)
                    ], [
                        InlineKeyboardButton('тЪб ╩Ьс┤Пс┤б с┤Ыс┤П с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е тЪб', url=await get_tutorial(chat_id))
                    ]
                ]
            )
        )
        await asyncio.sleep(300)
        await k.edit("<b>╩Пс┤Пс┤Ь╩А с┤Нс┤ЗъЬ▒ъЬ▒с┤А╔вс┤З ╔къЬ▒ с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е !\nс┤Л╔к╔┤с┤Е╩Я╩П ъЬ▒с┤Зс┤А╩Ас┤Д╩Ь с┤А╔вс┤А╔к╔┤.</b>")
        return
        
    elif data.startswith("short"):
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        curr_time = current_time.hour        
        if curr_time < 12:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Нс┤П╩А╔┤╔к╔┤╔в ЁЯСЛ" 
        elif curr_time < 17:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤А╥Ус┤Ыс┤З╩А╔┤с┤Пс┤П╔┤ ЁЯСЛ" 
        elif curr_time < 21:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Зс┤ас┤З╔┤╔к╔┤╔в ЁЯСЛ"
        else:
            gtxt = "╔вс┤Пс┤Пс┤Е ╔┤╔к╔в╩Ьс┤Ы ЁЯСЛ"        
        user_id = message.from_user.id
        if await db.has_premium_access(message.from_user.id):
            pass
        else:
            chat_id = temp.SHORT.get(user_id)
            files_ = await get_file_details(file_id)
            files = files_[0]
            g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
            k = await client.send_message(chat_id=user_id,text=f"ЁЯлВ ╩Ьс┤З╩П {message.from_user.mention}, {gtxt}\n\nтЬЕ ╩Пс┤Пс┤Ь╩А ╩Я╔к╔┤с┤Л ╔къЬ▒ ╩Ас┤Зс┤Ас┤Е╩П, с┤Л╔к╔┤с┤Е╩Я╩П с┤Д╩Я╔кс┤Дс┤Л с┤П╔┤ с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е ╩Щс┤Ьс┤Ыс┤Ыс┤П╔┤.\n\nтЪая╕П ъЬ░╔к╩Яс┤З ╔┤с┤Ас┤Нс┤З : <code>{files.file_name}</code> \n\nЁЯУе ъЬ░╔к╩Яс┤З ъЬ▒╔кс┤вс┤З : <code>{get_size(files.file_size)}</code>\n\n<u>тЪая╕П ╔┤с┤Пс┤Ыс┤З :- с┤Ы╩Ь╔къЬ▒ с┤Нс┤ЗъЬ▒ъЬ▒с┤А╔вс┤З ╔къЬ▒ с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╔к╔┤ 10 с┤Н╔к╔┤с┤Ьс┤Ыс┤ЗъЬ▒ с┤Ыс┤П с┤Ас┤ас┤П╔кс┤Е с┤Дс┤Пс┤Ш╩П╩А╔к╔в╩Ьс┤Ы..ъЬ▒с┤Ас┤ас┤З с┤Ы╩Ь╔къЬ▒ ╩Я╔к╔┤с┤Л с┤Ыс┤П ъЬ▒с┤Пс┤Нс┤Зс┤б╩Ьс┤З╩Ас┤З с┤З╩ЯъЬ▒с┤З</u>", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('ЁЯУБ с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е ЁЯУБ', url=g)
                        ], [
                            InlineKeyboardButton('тЪб ╩Ьс┤Пс┤б с┤Ыс┤П с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е тЪб', url=await get_tutorial(chat_id))
                        ]
                    ]
                )
            )
            await asyncio.sleep(600)
            await k.edit("<b>╩Пс┤Пс┤Ь╩А с┤Нс┤ЗъЬ▒ъЬ▒с┤А╔вс┤З ╔къЬ▒ с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е !\nс┤Л╔к╔┤с┤Е╩Я╩П ъЬ▒с┤Зс┤А╩Ас┤Д╩Ь с┤А╔вс┤А╔к╔┤.</b>")
            return    
    elif data.startswith("all"):
        files = temp.GETALL.get(file_id)
        if not files:
            return await message.reply('<b><i>╔┤с┤П ъЬ▒с┤Ьс┤Д╩Ь ъЬ░╔к╩Яс┤З с┤Зx╔къЬ▒с┤ЫъЬ▒ !</b></i>')
        filesarr = []
        for file in files:
            file_id = file.file_id
            files_ = await get_file_details(file_id)
            files1 = files_[0]
            title = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))
            size = get_size(files1.file_size)
            f_caption = files1.caption

            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption = f_caption

            if f_caption is None:
                f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files1.file_name.split()))}"
            if await db.has_premium_access(message.from_user.id):
                pass  
            else:
                if not await check_verification(client, message.from_user.id) and VERIFY == True:
                    btn = [[
                       InlineKeyboardButton("тЬЕ C╩Я╔кс┤Дс┤Л ╩Ьс┤З╩Ас┤З с┤Ыс┤П с┤ас┤З╩А╔к╥У╩П тЬЕ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id))
                       ],[
                       InlineKeyboardButton("тЪб Hс┤Пс┤б с┤Ыс┤П с┤ас┤З╩А╔к╥У╩П тЪб", url=HOW_TO_VERIFY)
                   ]]
                    l = await message.reply_text(
                        text="<b>тЩия╕П YOU ARE NOT VERIFIED !\nKINDLY VERIFY TO CONTINUE & YOU CAN GET UNLIMITED ACCESS FOR 24 HOURS тЬЕ\n\n<blockquote>тЪЬя╕П рдЗрд╕ BOT рд╕реЗ MOVIE рдкреНрд░рд╛рдкреНрдд рдХрд░рдиреЗ рдХреЗ рд▓рд┐рдП рдЖрдкрдХреЛ VERIFY рдХрд░рдирд╛ рдЖрд╡рд╢реНрдпрдХ рд╣реИ VERIFY рдХрд░рдиреЗ рдХреЗ рдмрд╛рдж рдЖрдк 24 рдШрдВрдЯреЗ рддрдХ UNLIMITED MOVIES рдкреНрд░рд╛рдкреНрдд рдХрд░ рд╕рдХрддреЗ рд╣реЛред</blockquote>\n\n<blockquote>ЁЯФе рдЕрдЧрд░ рдЖрдк VERIFY рдирд╣реАрдВ рдХрд░рдирд╛ рдЪрд╛рд╣рддреЗ рддреЛ рдЖрдк PREMIUM рд▓реЗ рд╕рдХрддреЗ рд╣реЛ, PREMIUM рд▓реЗрдиреЗ рдХреЗ рдмрд╛рдж рдЖрдк UNLIMITED MOVIES рдкреНрд░рд╛рдкреНрдд рдХрд░ рдкрд╛рдУрдЧреЗ рдФрд░ рдЖрдкрдХреЛ VERIFY рдХрд░рдиреЗ рдХреЛрдИ рдЬрд░реВрд░рдд рдирд╣реАрдВ рд╣реИ\n\nPLAN DETAILS рдХреЗ рд▓рд┐рдП CLICK рдХрд░реЗрдВ /plan</blockquote></b>",
                        protect_content=False,
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                    await asyncio.sleep(180)
                    await l.delete()
                    return
            if STREAM_MODE:
                btn = [
                    [InlineKeyboardButton('ЁЯЪА ъЬ░с┤АъЬ▒с┤Ы с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е / с┤бс┤Ас┤Ыс┤Д╩Ь с┤П╔┤╩Я╔к╔┤с┤З ЁЯЦея╕П', callback_data=f'generate_stream_link:{file_id}')],
                    [InlineKeyboardButton('ЁЯУМ с┤Кс┤П╔к╔┤ с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤ЗъЬ▒ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ЁЯУМ', url=DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK)]  # Keep this line unchanged  
                ]
            else:
                btn = [
                    [InlineKeyboardButton('ЁЯУМ с┤Кс┤П╔к╔┤ с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤ЗъЬ▒ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ЁЯУМ', url=DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK)]
                 
                ]

            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            filesarr.append(msg)
        k = await client.send_message(chat_id=message.from_user.id, text=f"<b><u>тЭЧя╕ПтЭЧя╕ПтЭЧя╕ПIMPORTANTтЭЧя╕Пя╕ПтЭЧя╕ПтЭЧя╕П</u></b>\n\nс┤Ы╩Ь╔къЬ▒ с┤Нс┤Пс┤а╔кс┤З ъЬ░╔к╩Яс┤З/с┤а╔кс┤Ес┤Зс┤П с┤б╔к╩Я╩Я ╩Щс┤З с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╔к╔┤<b><u>15 с┤Н╔к╔┤с┤Ьс┤Ыс┤ЗъЬ▒</u> ЁЯле <i></b>(с┤Ес┤Ьс┤З с┤Ыс┤П с┤Дс┤Пс┤Ш╩П╩А╔к╔в╩Ьс┤Ы ╔къЬ▒ъЬ▒с┤Ьс┤ЗъЬ▒)</i>.\n\n<b><i>с┤Ш╩Яс┤Зс┤АъЬ▒с┤З ъЬ░с┤П╩Ас┤бс┤А╩Ас┤Е с┤Ы╩Ь╔къЬ▒ ъЬ░╔к╩Яс┤З с┤Ыс┤П ъЬ▒с┤Пс┤Нс┤Зс┤б╩Ьс┤З╩Ас┤З с┤З╩ЯъЬ▒с┤З с┤А╔┤с┤Е ъЬ▒с┤Ыс┤А╩Ас┤Ы с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е╔к╔┤╔в с┤Ы╩Ьс┤З╩Ас┤З</i></b>")
        await asyncio.sleep(900)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>╩Пс┤Пс┤Ь╩А с┤А╩Я╩Я с┤а╔кс┤Ес┤Зс┤ПъЬ▒/ъЬ░╔к╩Яс┤ЗъЬ▒ с┤А╩Ас┤З с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П !\nс┤Л╔к╔┤с┤Е╩Я╩П ъЬ▒с┤Зс┤А╩Ас┤Д╩Ь с┤А╔вс┤А╔к╔┤</b>")
        return
    elif data.startswith("files"):
        current_time = datetime.now(pytz.timezone(TIMEZONE))
        curr_time = current_time.hour        
        if curr_time < 12:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Нс┤П╩А╔┤╔к╔┤╔в  ЁЯСЛ" 
        elif curr_time < 17:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤А╥Ус┤Ыс┤З╩А╔┤с┤Пс┤П╔┤  ЁЯСЛ" 
        elif curr_time < 21:
            gtxt = "╔вс┤Пс┤Пс┤Е с┤Зс┤ас┤З╔┤╔к╔┤╔в  ЁЯСЛ"
        else:
            gtxt = "╔вс┤Пс┤Пс┤Е ╔┤╔к╔в╩Ьс┤Ы  ЁЯСЛ"     
        user_id = message.from_user.id
        if temp.SHORT.get(user_id)==None:
            return await message.reply_text(text="<b>Please Search Again in Group</b>")
        else:
            chat_id = temp.SHORT.get(user_id)
        settings = await get_settings(chat_id)
        if not await db.has_premium_access(user_id) and settings['is_shortlink']: #Don't change anything without my permission @its_Raazz
            files_ = await get_file_details(file_id)
            files = files_[0]
            g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=file_{file_id}")
            k = await client.send_message(chat_id=message.from_user.id,text=f"ЁЯлВ ╩Ьс┤З╩П {message.from_user.mention}, {gtxt}\n\nтЬЕ ╩Пс┤Пс┤Ь╩А ╩Я╔к╔┤с┤Л ╔къЬ▒ ╩Ас┤Зс┤Ас┤Е╩П, с┤Л╔к╔┤с┤Е╩Я╩П с┤Д╩Я╔кс┤Дс┤Л с┤П╔┤ с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е ╩Щс┤Ьс┤Ыс┤Ыс┤П╔┤.\n\nтЪая╕П ъЬ░╔к╩Яс┤З ╔┤с┤Ас┤Нс┤З : <code>{files.file_name}</code> \n\nЁЯУе ъЬ░╔к╩Яс┤З ъЬ▒╔кс┤вс┤З : <code>{get_size(files.file_size)}</code>\n\n", reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('ЁЯУБ с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е ЁЯУБ', url=g)
                        ], [
                            InlineKeyboardButton('тЪб ╩Ьс┤Пс┤б с┤Ыс┤П с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е тЪб', url=await get_tutorial(chat_id))
                        ]
                    ]
                )
            )
            await asyncio.sleep(600)
            await k.edit("<b>╩Пс┤Пс┤Ь╩А с┤Нс┤ЗъЬ▒ъЬ▒с┤А╔вс┤З ╔къЬ▒ с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е !\nс┤Л╔к╔┤с┤Е╩Я╩П ъЬ▒с┤Зс┤А╩Ас┤Д╩Ь с┤А╔вс┤А╔к╔┤.</b>")
            return   
    user = message.from_user.id
    files_ = await get_file_details(file_id)        
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            if await db.has_premium_access(message.from_user.id): 
                pass 
            else:
               if not await check_verification(client, message.from_user.id) and VERIFY == True:
                   btn = [[
                       InlineKeyboardButton("тЬЕ C╩Я╔кс┤Дс┤Л ╩Ьс┤З╩Ас┤З с┤Ыс┤П с┤ас┤З╩А╔к╥У╩П тЬЕ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id))
                   ],[
                        InlineKeyboardButton("тЪб Hс┤Пс┤б с┤Ыс┤П с┤ас┤З╩А╔к╥У╩П тЪб", url=HOW_TO_VERIFY)
                   ]]
                   l = await message.reply_text(
                       text="<b>тЩия╕П YOU ARE NOT VERIFIED !\nKINDLY VERIFY TO CONTINUE & YOU CAN GET UNLIMITED ACCESS FOR 24 HOURS тЬЕ\n\n<blockquote>тЪЬя╕П рдЗрд╕ BOT рд╕реЗ MOVIE рдкреНрд░рд╛рдкреНрдд рдХрд░рдиреЗ рдХреЗ рд▓рд┐рдП рдЖрдкрдХреЛ VERIFY рдХрд░рдирд╛ рдЖрд╡рд╢реНрдпрдХ рд╣реИ VERIFY рдХрд░рдиреЗ рдХреЗ рдмрд╛рдж рдЖрдк 24 рдШрдВрдЯреЗ рддрдХ UNLIMITED MOVIES рдкреНрд░рд╛рдкреНрдд рдХрд░ рд╕рдХрддреЗ рд╣реЛред <blockquote>\n\n<blockquote>ЁЯФе рдЕрдЧрд░ рдЖрдк VERIFY рдирд╣реАрдВ рдХрд░рдирд╛ рдЪрд╛рд╣рддреЗ рддреЛ рдЖрдк PREMIUM рд▓реЗ рд╕рдХрддреЗ рд╣реЛ, PREMIUM рд▓реЗрдиреЗ рдХреЗ рдмрд╛рдж рдЖрдк UNLIMITED MOVIES рдкреНрд░рд╛рдкреНрдд рдХрд░ рдкрд╛рдУрдЧреЗ рдФрд░ рдЖрдкрдХреЛ VERIFY рдХрд░рдиреЗ рдХреЛрдИ рдЬрд░реВрд░рдд рдирд╣реА рд╣реИ\n\nPLAN DETAILS рдХреЗ рд▓рд┐рдП CLICK рдХрд░реЗрдВ /plan</blockquote></b>",
                       protect_content=False,
                       reply_markup=InlineKeyboardMarkup(btn)
                   )
                   await asyncio.sleep(180)
                   await l.delete()
                   return
            if STREAM_MODE:
                btn = [
                    [InlineKeyboardButton('ЁЯЪА ъЬ░с┤АъЬ▒с┤Ы с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е / с┤бс┤Ас┤Ыс┤Д╩Ь с┤П╔┤╩Я╔к╔┤с┤З ЁЯЦея╕П', callback_data=f'generate_stream_link:{file_id}')],
                    [InlineKeyboardButton('ЁЯУМ с┤Кс┤П╔к╔┤ с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤ЗъЬ▒ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ЁЯУМ', url=DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK)]  # Keep this line unchanged
             
                ]
            else:
                btn = [
                    [InlineKeyboardButton('ЁЯУМ с┤Кс┤П╔к╔┤ с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤ЗъЬ▒ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ЁЯУМ', url=DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK)]
                ]
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup(btn))

            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = '' + ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), file.file_name.split()))
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            btn = [[
                InlineKeyboardButton("тЭЧ ╔вс┤Зс┤Ы ъЬ░╔к╩Яс┤З с┤А╔вс┤А╔к╔┤ тЭЧ", callback_data=f'delfile#{file_id}')
            ]]
            k = await msg.reply("<b><u>тЭЧя╕ПтЭЧя╕ПтЭЧя╕ПIMPORTANTтЭЧя╕Пя╕ПтЭЧя╕ПтЭЧя╕П</u></b>\n\nс┤Ы╩Ь╔къЬ▒ с┤Нс┤Пс┤а╔кс┤З ъЬ░╔к╩Яс┤З/с┤а╔кс┤Ес┤Зс┤П с┤б╔к╩Я╩Я ╩Щс┤З с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╔к╔┤<b><u>15 с┤Н╔к╔┤с┤Ьс┤Ыс┤ЗъЬ▒ </u> ЁЯле <i></b>(с┤Ес┤Ьс┤З с┤Ыс┤П с┤Дс┤Пс┤Ш╩П╩А╔к╔в╩Ьс┤Ы ╔къЬ▒ъЬ▒с┤Ьс┤ЗъЬ▒)</i>.\n\n<b><i>с┤Ш╩Яс┤Зс┤АъЬ▒с┤З ъЬ░с┤П╩Ас┤бс┤А╩Ас┤Е с┤Ы╩Ь╔къЬ▒ ъЬ░╔к╩Яс┤З с┤Ыс┤П ъЬ▒с┤Пс┤Нс┤Зс┤б╩Ьс┤З╩Ас┤З с┤З╩ЯъЬ▒с┤З с┤А╔┤с┤Е ъЬ▒с┤Ыс┤А╩Ас┤Ы с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е╔к╔┤╔в с┤Ы╩Ьс┤З╩Ас┤З</i></b>",quote=True)
            await asyncio.sleep(900)
            await msg.delete()
            await k.edit_text("<b>╩Пс┤Пс┤Ь╩А с┤а╔кс┤Ес┤Зс┤П / ъЬ░╔к╩Яс┤З ╔къЬ▒ ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е !!</b>")
            return
        except:
            pass
        return await message.reply('╔┤с┤П ъЬ▒с┤Ьс┤Д╩Ь ъЬ░╔к╩Яс┤З с┤Зx╔къЬ▒с┤ЫъЬ▒ !')
    files = files_[0]
    title = '' + ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))
    size = get_size(files.file_size)
    f_caption = files.caption

    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption

    if f_caption is None:
        f_caption = ' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), files.file_name.split()))

    if await db.has_premium_access(message.from_user.id):
        pass
    else:
        if not await check_verification(client, message.from_user.id) and VERIFY == True:
            btn = [[
              InlineKeyboardButton("тЬЕ C╩Я╔кс┤Дс┤Л ╩Ьс┤З╩Ас┤З с┤Ыс┤П с┤ас┤З╩А╔к╥У╩П тЬЕ", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id))
           ],[
              InlineKeyboardButton("тЪб Hс┤Пс┤б с┤Ыс┤П с┤ас┤З╩А╔к╥У╩П тЪб", url=HOW_TO_VERIFY)
           ]]
            l = await message.reply_text(
                text="<b>тЩия╕П YOU ARE NOT VERIFIED !\nKINDLY VERIFY TO CONTINUE & YOU CAN GET UNLIMITED ACCESS FOR 24 HOURS тЬЕ\n\n<blockquote>тЪЬя╕П рдЗрд╕ BOT рд╕реЗ MOVIE рдкреНрд░рд╛рдкреНрдд рдХрд░рдиреЗ рдХреЗ рд▓рд┐рдП рдЖрдкрдХреЛ VERIFY рдХрд░рдирд╛ рдЖрд╡рд╢реНрдпрдХ рд╣реИ VERIFY рдХрд░рдиреЗ рдХреЗ рдмрд╛рдж рдЖрдк 24 рдШрдВрдЯреЗ рддрдХ UNLIMITED MOVIES рдкреНрд░рд╛рдкреНрдд рдХрд░ рд╕рдХрддреЗ рд╣реЛред</blockquote> \n\n<blockquote>ЁЯФе рдЕрдЧрд░ рдЖрдк VERIFY рдирд╣реАрдВ рдХрд░рдирд╛ рдЪрд╛рд╣рддреЗ рддреЛ рдЖрдк PREMIUM рд▓реЗ рд╕рдХрддреЗ рд╣реЛ, PREMIUM рд▓реЗрдиреЗ рдХреЗ рдмрд╛рдж рдЖрдк UNLIMITED MOVIES рдкреНрд░рд╛рдкреНрдд рдХрд░ рдкрд╛рдУрдЧреЗ рдФрд░ рдЖрдкрдХреЛ VERIFY рдХрд░рдиреЗ рдХреЛрдИ рдЬрд░реВрд░рдд рдирд╣реАрдВ рд╣реИ\n\nPLAN DETAILS рдХреЗ рд▓рд┐рдП CLICK рдХрд░реЗрдВ /plan</blockquote></b>",
                protect_content=False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            await asyncio.sleep(180)
            await l.delete()
            return
    if STREAM_MODE:
        btn = [
            [InlineKeyboardButton('ЁЯЪА ъЬ░с┤АъЬ▒с┤Ы с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е / с┤бс┤Ас┤Ыс┤Д╩Ь с┤П╔┤╩Я╔к╔┤с┤З ЁЯЦея╕П', callback_data=f'generate_stream_link:{file_id}')],
            [InlineKeyboardButton('ЁЯУМ с┤Кс┤П╔к╔┤ с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤ЗъЬ▒ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ЁЯУМ', url=DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK)]  # Keep this line unchanged
        ]
    else:
        btn = [
            [InlineKeyboardButton('ЁЯУМ с┤Кс┤П╔к╔┤ с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤ЗъЬ▒ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ЁЯУМ', url=DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK)]
        ]
    msg = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
        reply_markup=InlineKeyboardMarkup(btn)
    )
    btn = [[
            InlineKeyboardButton("тЭЧ ╔вс┤Зс┤Ы ъЬ░╔к╩Яс┤З с┤А╔вс┤А╔к╔┤ тЭЧ", callback_data=f'delfile#{file_id}')
        ]]
    k = await msg.reply("<b><u>тЭЧя╕ПтЭЧя╕ПтЭЧя╕ПIMPORTANTтЭЧя╕Пя╕ПтЭЧя╕ПтЭЧя╕П</u></b>\n\nс┤Ы╩Ь╔къЬ▒ с┤Нс┤Пс┤а╔кс┤З ъЬ░╔к╩Яс┤З/с┤а╔кс┤Ес┤Зс┤П с┤б╔к╩Я╩Я ╩Щс┤З с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╔к╔┤ <b><u>15 с┤Н╔к╔┤с┤Ьс┤Ыс┤ЗъЬ▒</u> ЁЯле <i></b>(с┤Ес┤Ьс┤З с┤Ыс┤П с┤Дс┤Пс┤Ш╩П╩А╔к╔в╩Ьс┤Ы ╔къЬ▒ъЬ▒с┤Ьс┤ЗъЬ▒)</i>.\n\n<b><i>с┤Ш╩Яс┤Зс┤АъЬ▒с┤З ъЬ░с┤П╩Ас┤бс┤А╩Ас┤Е с┤Ы╩Ь╔къЬ▒ ъЬ░╔к╩Яс┤З с┤Ыс┤П ъЬ▒с┤Пс┤Нс┤Зс┤б╩Ьс┤З╩Ас┤З с┤З╩ЯъЬ▒с┤З с┤А╔┤с┤Е ъЬ▒с┤Ыс┤А╩Ас┤Ы с┤Ес┤Пс┤б╔┤╩Яс┤Пс┤Ас┤Е╔к╔┤╔в с┤Ы╩Ьс┤З╩Ас┤З</i></b>",quote=True)
    await asyncio.sleep(900)
    await msg.delete()
    await k.edit_text("<b>╩Пс┤Пс┤Ь╩А с┤а╔кс┤Ес┤Зс┤П / ъЬ░╔к╩Яс┤З ╔къЬ▒ ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е !!</b>")
    return


@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("с┤Ь╔┤с┤Зxс┤Шс┤Зс┤Дс┤Ыс┤Зс┤Е с┤Ы╩Пс┤Шс┤З с┤ПъЬ░ с┤Д╩Ьс┤А╔┤╔┤с┤З╩ЯъЬ▒.")

    text = 'ЁЯУС **╔к╔┤с┤Ес┤Зxс┤Зс┤Е с┤Д╩Ьс┤А╔┤╔┤с┤З╩ЯъЬ▒ / ╔в╩Ас┤Пс┤Ьс┤ШъЬ▒ ╩Я╔къЬ▒с┤Ы :**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**с┤Ыс┤Пс┤Ыс┤А╩Я :** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TELEGRAM BOT.LOG')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("P╩Ас┤Пс┤Дс┤Зss╔к╔┤╔в...тП│", quote=True)
    else:
        await message.reply('Rс┤Зс┤Ш╩Я╩П с┤Ыс┤П ╥У╔к╩Яс┤З с┤б╔кс┤Ы╩Ь /delete с┤б╩Ь╔кс┤Д╩Ь ╩Пс┤Пс┤Ь с┤бс┤А╔┤с┤Ы с┤Ыс┤П с┤Ес┤З╩Яс┤Зс┤Ыс┤З', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('T╩Ь╔кs ╔кs ╔┤с┤Пс┤Ы sс┤Ьс┤Шс┤Шс┤П╩Ас┤Ыс┤Зс┤Е ╥У╔к╩Яс┤З ╥Ус┤П╩Ас┤Нс┤Ас┤Ы')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)
    if await Media.count_documents({'file_id': file_id}):
        result = await Media.collection.delete_one({
            '_id': file_id,
        })
    else:
        result = await Media2.collection.delete_one({
            '_id': file_id,
        })
    if result.deleted_count:
        await msg.edit('F╔к╩Яс┤З ╔кs sс┤Ьс┤Дс┤Дс┤Зss╥Ус┤Ь╩Я╩Я╩П с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╥У╩Ас┤Пс┤Н с┤Ес┤Ас┤Ыс┤А╩Щс┤Аsс┤З тЬЕ')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('F╔к╩Яс┤З ╔кs sс┤Ьс┤Дс┤Дс┤Зss╥Ус┤Ь╩Я╩Я╩П с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╥У╩Ас┤Пс┤Н с┤Ес┤Ас┤Ыс┤А╩Щс┤Аsс┤З тЬЕ')
        else:
            result = await Media2.collection.delete_many({
                'file_name': file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('F╔к╩Яс┤З ╔кs sс┤Ьс┤Дс┤Дс┤Зss╥Ус┤Ь╩Я╩Я╩П с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╥У╩Ас┤Пс┤Н с┤Ес┤Ас┤Ыс┤А╩Щс┤Аsс┤З')
            else:
                # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
                # have original file name.
                result = await Media.collection.delete_many({
                    'file_name': media.file_name,
                    'file_size': media.file_size,
                    'mime_type': media.mime_type
                })
                if result.deleted_count:
                    await msg.edit('F╔к╩Яс┤З ╔кs sс┤Ьс┤Дс┤Дс┤Зss╥Ус┤Ь╩Я╩Я╩П с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╥У╩Ас┤Пс┤Н с┤Ес┤Ас┤Ыс┤А╩Щс┤Аsс┤З тЬЕ')
                else:
                    result = await Media2.collection.delete_many({
                        'file_name': media.file_name,
                        'file_size': media.file_size,
                        'mime_type': media.mime_type
                    })
                    if result.deleted_count:
                        await msg.edit('F╔к╩Яс┤З ╔кs sс┤Ьс┤Дс┤Дс┤Зss╥Ус┤Ь╩Я╩Я╩П с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е ╥У╩Ас┤Пс┤Н с┤Ес┤Ас┤Ыс┤А╩Щс┤Аsс┤З тЬЕ')
                    else:
                        await msg.edit('F╔к╩Яс┤З ╔┤с┤Пс┤Ы ╥Ус┤Пс┤Ь╔┤с┤Е ╔к╔┤ с┤Ес┤Ас┤Ыс┤А╩Щс┤Аsс┤З тЭМ')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'с┤Ы╩Ь╔къЬ▒ с┤б╔к╩Я╩Я с┤Ес┤З╩Яс┤Зс┤Ыс┤З с┤А╩Я╩Я ╩Пс┤Пс┤Ь╩А ╔к╔┤с┤Ес┤Зxс┤Зс┤Е ъЬ░╔к╩Яс┤ЗъЬ▒ !\nс┤Ес┤П ╩Пс┤Пс┤Ь ъЬ▒с┤Ы╔к╩Я╩Я с┤бс┤А╔┤с┤Ы с┤Ыс┤П с┤Дс┤П╔┤с┤Ы╔к╔┤с┤Ьс┤З ?',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="тЪая╕П ╩Пс┤ЗъЬ▒ тЪая╕П", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="тЭМ ╔┤с┤П тЭМ", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await Media2.collection.drop()
    await message.answer("Eс┤ас┤З╩А╩Пс┤Ы╩Ь╔к╔┤╔в's Gс┤П╔┤с┤З")
    await message.message.edit('ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П с┤Ес┤З╩Яс┤Зс┤Ыс┤Зс┤Е с┤А╩Я╩Я ╔к╔┤с┤Ес┤Зxс┤Зс┤Е ъЬ░╔к╩Яс┤ЗъЬ▒ тЬЕ')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"╩Пс┤Пс┤Ь'╩Ас┤З с┤А╔┤с┤П╔┤╩Пс┤Нс┤Пс┤ЬъЬ▒ с┤Ас┤Ес┤Н╔к╔┤.\nс┤ЬъЬ▒с┤З /connect {message.chat.id} ╔к╔┤ с┤Шс┤Н.")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("с┤Нс┤Ас┤Лс┤З ъЬ▒с┤Ь╩Ас┤З ╔к'с┤Н с┤Ш╩Ас┤ЗъЬ▒с┤З╔┤с┤Ы ╔к╔┤ ╩Пс┤Пс┤Ь╩А ╔в╩Ас┤Пс┤Ьс┤Ш !!", quote=True)
                return
        else:
            await message.reply_text("╔к'с┤Н ╔┤с┤Пс┤Ы с┤Дс┤П╔┤╔┤с┤Зс┤Дс┤Ыс┤Зс┤Е с┤Ыс┤П с┤А╔┤╩П ╔в╩Ас┤Пс┤Ьс┤Ш !", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return
    
    settings = await get_settings(grp_id)

    try:
        if settings['max_btn']:
            settings = await get_settings(grp_id)
    except KeyError:
        await save_group_settings(grp_id, 'max_btn', False)
        settings = await get_settings(grp_id)
    if 'is_shortlink' not in settings.keys():
        await save_group_settings(grp_id, 'is_shortlink', False)
    else:
        pass

    if settings is not None:
        buttons = [        
                [
                InlineKeyboardButton(
                    '╩Ас┤ЗъЬ▒с┤Ь╩Яс┤Ы с┤Шс┤А╔вс┤З',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '╩Щс┤Ьс┤Ыс┤Ыс┤П╔┤' if settings["button"] else 'с┤Ыс┤Зxс┤Ы',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'ъЬ░╔к╩Яс┤З ъЬ▒с┤З╔┤с┤Е с┤Нс┤Пс┤Ес┤З',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'ъЬ▒с┤Ыс┤А╩Ас┤Ы' if settings["botpm"] else 'с┤Ас┤Ьс┤Ыс┤П',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'ъЬ░╔к╩Яс┤З ъЬ▒с┤Зс┤Дс┤Ь╩Ас┤З',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'с┤З╔┤с┤А╩Щ╩Яс┤З' if settings["file_secure"] else 'с┤Е╔къЬ▒с┤А╩Щ╩Яс┤З',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    '╔кс┤Нс┤Е╩Щ с┤Шс┤ПъЬ▒с┤Ыс┤З╩А',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'с┤З╔┤с┤А╩Щ╩Яс┤З' if settings["imdb"] else 'с┤Е╔къЬ▒с┤А╩Щ╩Яс┤З',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'ъЬ▒с┤Шс┤З╩Я╩Я с┤Д╩Ьс┤Зс┤Дс┤Л',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'с┤З╔┤с┤А╩Щ╩Яс┤З' if settings["spell_check"] else 'с┤Е╔къЬ▒с┤А╩Щ╩Яс┤З',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'с┤бс┤З╩Яс┤Дс┤Пс┤Нс┤З с┤НъЬ▒╔в',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'с┤З╔┤с┤А╩Щ╩Яс┤З' if settings["welcome"] else 'с┤Е╔къЬ▒с┤А╩Щ╩Яс┤З',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'с┤Ас┤Ьс┤Ыс┤П с┤Ес┤З╩Яс┤Зс┤Ыс┤З',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'с┤З╔┤с┤А╩Щ╩Яс┤З' if settings["auto_delete"] else 'с┤Е╔къЬ▒с┤А╩Щ╩Яс┤З',
                    callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'с┤Ас┤Ьс┤Ыс┤П ъЬ░╔к╩Яс┤Ыс┤З╩А',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'с┤З╔┤с┤А╩Щ╩Яс┤З' if settings["auto_ffilter"] else 'с┤Е╔къЬ▒с┤А╩Щ╩Яс┤З',
                    callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'с┤Нс┤Аx ╩Щс┤Ьс┤Ыс┤Ыс┤П╔┤ъЬ▒',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '10' if settings["max_btn"] else f'{MAX_B_TN}',
                    callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'ъЬ▒╩Ьс┤П╩Ас┤Ы╩Я╔к╔┤с┤Л',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'с┤З╔┤с┤А╩Щ╩Яс┤З' if settings["is_shortlink"] else 'с┤Е╔къЬ▒с┤А╩Щ╩Яс┤З',
                    callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton('тЗЛ с┤Д╩Яс┤ПъЬ▒с┤З ъЬ▒с┤Зс┤Ыс┤Ы╔к╔┤╔въЬ▒ с┤Нс┤З╔┤с┤Ь тЗЛ', 
                                     callback_data='close_data'
                                     )
            ]
        ]
        

        btn = [[
                InlineKeyboardButton("ЁЯСд с┤Пс┤Шс┤З╔┤ ╔к╔┤ с┤Ш╩А╔кс┤ас┤Ас┤Ыс┤З с┤Д╩Ьс┤Ас┤Ы ЁЯСд", callback_data=f"opnsetpm#{grp_id}")
              ],[
                InlineKeyboardButton("ЁЯСе с┤Пс┤Шс┤З╔┤ ╩Ьс┤З╩Ас┤З ЁЯСе", callback_data=f"opnsetgrp#{grp_id}")
              ]]

        reply_markup = InlineKeyboardMarkup(buttons)
        if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply_text(
                text="<b>с┤б╩Ьс┤З╩Ас┤З с┤Ес┤П ╩Пс┤Пс┤Ь с┤бс┤А╔┤с┤Ы с┤Ыс┤П с┤Пс┤Шс┤З╔┤ ъЬ▒с┤Зс┤Ыс┤Ы╔к╔┤╔въЬ▒ с┤Нс┤З╔┤с┤Ь ? тЪЩя╕П</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )
        else:
            await message.reply_text(
                text=f"<b>с┤Д╩Ьс┤А╔┤╔вс┤З ╩Пс┤Пс┤Ь╩А ъЬ▒с┤Зс┤Ыс┤Ы╔к╔┤╔въЬ▒ ъЬ░с┤П╩А {title} с┤АъЬ▒ ╩Пс┤Пс┤Ь с┤б╔къЬ▒╩Ь тЪЩ</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.id
            )



@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("с┤Д╩Ьс┤Зс┤Дс┤Л╔к╔┤╔в с┤Ыс┤Зс┤Нс┤Ш╩Яс┤Ас┤Ыс┤З...")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"╩Пс┤Пс┤Ь'╩Ас┤З с┤А╔┤с┤П╔┤╩Пс┤Нс┤Пс┤ЬъЬ▒ с┤Ас┤Ес┤Н╔к╔┤.\nс┤ЬъЬ▒с┤З /connect {message.chat.id} ╔к╔┤ с┤Шс┤Н.")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("с┤Нс┤Ас┤Лс┤З ъЬ▒с┤Ь╩Ас┤З ╔к'с┤Н с┤Ш╩Ас┤ЗъЬ▒с┤З╔┤с┤Ы ╔к╔┤ ╩Пс┤Пс┤Ь╩А ╔в╩Ас┤Пс┤Ьс┤Ш !!", quote=True)
                return
        else:
            await message.reply_text("╔к'с┤Н ╔┤с┤Пс┤Ы с┤Дс┤П╔┤╔┤с┤Зс┤Дс┤Ыс┤Зс┤Е с┤Ыс┤П с┤А╔┤╩П ╔в╩Ас┤Пс┤Ьс┤Ш !", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("╔┤с┤П ╔к╔┤с┤Шс┤Ьс┤Ы !")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"тЬЕ ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П с┤Д╩Ьс┤А╔┤╔вс┤Зс┤Е с┤Ыс┤Зс┤Нс┤Ш╩Яс┤Ас┤Ыс┤З ъЬ░с┤П╩А <code>{title}</code> с┤Ыс┤П\n\n{template}")


@Client.on_message((filters.command(["request", "Request"]) | filters.regex("#request") | filters.regex("#Request")) & filters.group)
async def requests(bot, message):
    if REQST_CHANNEL is None or SUPPORT_CHAT_ID is None: return # Must add REQST_CHANNEL and SUPPORT_CHAT_ID to use this feature
    if message.reply_to_message and SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.reply_to_message.text
        try:
            if REQST_CHANNEL is not None:
                btn = [[
                        InlineKeyboardButton('с┤а╔кс┤Зс┤б ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('ъЬ▒╩Ьс┤Пс┤б с┤Пс┤Шс┤Ы╔кс┤П╔┤ъЬ▒', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>ЁЯУЭ ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы : <u>{content}</u>\n\nЁЯУЪ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤Зс┤Е ╩Щ╩П : {mention}\nЁЯУЦ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤З╩А ╔кс┤Е : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('с┤а╔кс┤Зс┤б ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('ъЬ▒╩Ьс┤Пс┤б с┤Пс┤Шс┤Ы╔кс┤П╔┤ъЬ▒', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>ЁЯУЭ ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы : <u>{content}</u>\n\nЁЯУЪ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤Зс┤Е ╩Щ╩П : {mention}\nЁЯУЦ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤З╩А ╔кс┤Е : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>╩Пс┤Пс┤Ь с┤Нс┤ЬъЬ▒с┤Ы с┤Ы╩Пс┤Шс┤З с┤А╩Щс┤Пс┤Ьс┤Ы ╩Пс┤Пс┤Ь╩А ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы [с┤Н╔к╔┤╔кс┤Нс┤Ьс┤Н 3 с┤Д╩Ьс┤А╩Ас┤Ас┤Дс┤Ыс┤З╩АъЬ▒]. ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤ЫъЬ▒ с┤Дс┤А╔┤'с┤Ы ╩Щс┤З с┤Зс┤Нс┤Шс┤Ы╩П.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            pass
        
    elif SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.text
        keywords = ["#request", "/request", "#Request", "/Request"]
        for keyword in keywords:
            if keyword in content:
                content = content.replace(keyword, "")
        try:
            if REQST_CHANNEL is not None and len(content) >= 3:
                btn = [[
                        InlineKeyboardButton('с┤а╔кс┤Зс┤б ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы', url=f"{message.link}"),
                        InlineKeyboardButton('ъЬ▒╩Ьс┤Пс┤б с┤Пс┤Шс┤Ы╔кс┤П╔┤ъЬ▒', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>ЁЯУЭ ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы : <u>{content}</u>\n\nЁЯУЪ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤Зс┤Е ╩Щ╩П : {mention}\nЁЯУЦ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤З╩А ╔кс┤Е : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('с┤а╔кс┤Зс┤б ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы', url=f"{message.link}"),
                        InlineKeyboardButton('ъЬ▒╩Ьс┤Пс┤б с┤Пс┤Шс┤Ы╔кс┤П╔┤ъЬ▒', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>ЁЯУЭ ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы : <u>{content}</u>\n\nЁЯУЪ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤Зс┤Е ╩Щ╩П : {mention}\nЁЯУЦ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤З╩А ╔кс┤Е : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>╩Пс┤Пс┤Ь с┤Нс┤ЬъЬ▒с┤Ы с┤Ы╩Пс┤Шс┤З с┤А╩Щс┤Пс┤Ьс┤Ы ╩Пс┤Пс┤Ь╩А ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы [с┤Н╔к╔┤╔кс┤Нс┤Ьс┤Н 3 с┤Д╩Ьс┤А╩Ас┤Ас┤Дс┤Ыс┤З╩АъЬ▒]. ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤ЫъЬ▒ с┤Дс┤А╔┤'с┤Ы ╩Щс┤З с┤Зс┤Нс┤Шс┤Ы╩П.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            pass
     
    elif SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.text
        keywords = ["#request", "/request", "#Request", "/Request"]
        for keyword in keywords:
            if keyword in content:
                content = content.replace(keyword, "")
        try:
            if REQST_CHANNEL is not None and len(content) >= 3:
                btn = [[
                        InlineKeyboardButton('с┤а╔кс┤Зс┤б ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы', url=f"{message.link}"),
                        InlineKeyboardButton('ъЬ▒╩Ьс┤Пс┤б с┤Пс┤Шс┤Ы╔кс┤П╔┤ъЬ▒', callback_data=f'show_option#{reporter}')
                      ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>ЁЯУЭ ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы : <u>{content}</u>\n\nЁЯУЪ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤Зс┤Е ╩Щ╩П : {mention}\nЁЯУЦ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤З╩А ╔кс┤Е : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('с┤а╔кс┤Зс┤б ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы', url=f"{message.link}"),
                        InlineKeyboardButton('ъЬ▒╩Ьс┤Пс┤б с┤Пс┤Шс┤Ы╔кс┤П╔┤ъЬ▒', callback_data=f'show_option#{reporter}')
                      ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>ЁЯУЭ ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы : <u>{content}</u>\n\nЁЯУЪ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤Зс┤Е ╩Щ╩П : {mention}\nЁЯУЦ ╩Ас┤Зс┤Шс┤П╩Ас┤Ыс┤З╩А ╔кс┤Е : {reporter}\n\n</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>╩Пс┤Пс┤Ь с┤Нс┤ЬъЬ▒с┤Ы с┤Ы╩Пс┤Шс┤З с┤А╩Щс┤Пс┤Ьс┤Ы ╩Пс┤Пс┤Ь╩А ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы [с┤Н╔к╔┤╔кс┤Нс┤Ьс┤Н 3 с┤Д╩Ьс┤А╩Ас┤Ас┤Дс┤Ыс┤З╩АъЬ▒]. ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤ЫъЬ▒ с┤Дс┤А╔┤'с┤Ы ╩Щс┤З с┤Зс┤Нс┤Шс┤Ы╩П.</b>")
            if len(content) < 3:
                success = False
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            pass

    else:
        success = False
    
    if success:
        '''if isinstance(REQST_CHANNEL, (int, str)):
            channels = [REQST_CHANNEL]
        elif isinstance(REQST_CHANNEL, list):
            channels = REQST_CHANNEL
        for channel in channels:
            chat = await bot.get_chat(channel)
        #chat = int(chat)'''
        link = await bot.create_chat_invite_link(int(REQST_CHANNEL))
        btn = [[
                InlineKeyboardButton('с┤Кс┤П╔к╔┤ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я', url=link.invite_link),
                InlineKeyboardButton('с┤а╔кс┤Зс┤б ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы', url=f"{reported_post.link}")
              ]]
        await message.reply_text("<b>╩Пс┤Пс┤Ь╩А ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы ╩Ьс┤АъЬ▒ ╩Щс┤Зс┤З╔┤ с┤Ас┤Ес┤Ес┤Зс┤Е! с┤Ш╩Яс┤Зс┤АъЬ▒с┤З с┤бс┤А╔кс┤Ы ъЬ░с┤П╩А ъЬ▒с┤Пс┤Нс┤З с┤Ы╔кс┤Нс┤З.\n\nс┤Кс┤П╔к╔┤ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ъЬ░╔к╩АъЬ▒с┤Ы & с┤а╔кс┤Зс┤б ╩Ас┤З╟лс┤Ьс┤ЗъЬ▒с┤Ы.</b>", reply_markup=InlineKeyboardMarkup(btn))
    
@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Users Saved In DB Are:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>╩Пс┤Пс┤Ь╩А с┤Нс┤ЗъЬ▒ъЬ▒с┤А╔вс┤З ╩Ьс┤АъЬ▒ ╩Щс┤Зс┤З╔┤ ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П ъЬ▒с┤З╔┤с┤Ы с┤Ыс┤П {user.mention}.</b>")
            else:
                await message.reply_text("<b>с┤Ы╩Ь╔къЬ▒ с┤ЬъЬ▒с┤З╩А с┤Е╔кс┤Е╔┤'с┤Ы ъЬ▒с┤Ыс┤А╩Ас┤Ыс┤Зс┤Е с┤Ы╩Ь╔къЬ▒ ╩Щс┤Пс┤Ы ╩Пс┤Зс┤Ы !</b>")
        except Exception as e:
            await message.reply_text(f"<b>Error: {e}</b>")
    else:
        await message.reply_text("<b>с┤ЬъЬ▒с┤З с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е с┤АъЬ▒ с┤А ╩Ас┤Зс┤Ш╩Я╩П с┤Ыс┤П с┤А╔┤╩П с┤Нс┤ЗъЬ▒ъЬ▒с┤А╔вс┤З с┤ЬъЬ▒╔к╔┤╔в с┤Ы╩Ьс┤З с┤Ыс┤А╩А╔вс┤Зс┤Ы с┤Д╩Ьс┤Ас┤Ы ╔кс┤Е. ъЬ░с┤П╩А с┤З╔в:  /send с┤ЬъЬ▒с┤З╩А╔кс┤Е</b>")

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, This command won't work in groups. It only works on my PM !</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, Give me a keyword along with the command to delete files.</b>")
    k = await bot.send_message(chat_id=message.chat.id, text=f"<b>Fetching Files for your query {keyword} on DB... Please wait...</b>")
    files, total = await get_bad_files(keyword)
    await k.delete()
    #await k.edit_text(f"<b>Found {total} files for your query {keyword} !\n\nFile deletion process will start in 5 seconds !</b>")
    #await asyncio.sleep(5)
    btn = [[
       InlineKeyboardButton("тЪая╕П Yes, Continue ! тЪая╕П", callback_data=f"killfilesdq#{keyword}")
       ],[
       InlineKeyboardButton("тЭМ No, Abort operation ! тЭМ", callback_data="close_data")
    ]]
    await message.reply_text(
        text=f"<b>Found {total} files for your query {keyword} !\n\nDo you want to delete?</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("shortlink"))
async def shortlink(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"╩Пс┤Пс┤Ь'╩Ас┤З с┤А╔┤с┤П╔┤╩Пс┤Нс┤Пс┤ЬъЬ▒ с┤Ас┤Ес┤Н╔к╔┤, с┤Ыс┤Ь╩А╔┤ с┤ПъЬ░ъЬ░ с┤А╔┤с┤П╔┤╩Пс┤Нс┤Пс┤ЬъЬ▒ с┤Ас┤Ес┤Н╔к╔┤ с┤А╔┤с┤Е с┤Ы╩А╩П с┤Ы╩Ь╔къЬ▒ с┤А╔вс┤А╔к╔┤ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>╩Ьс┤З╩П {message.from_user.mention}, с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е с┤П╔┤╩Я╩П с┤бс┤П╩Ас┤ЛъЬ▒ ╔к╔┤ ╔в╩Ас┤Пс┤Ьс┤ШъЬ▒ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>╩Пс┤Пс┤Ь с┤Ес┤П╔┤'с┤Ы ╩Ьс┤Ас┤ас┤З с┤Ас┤Дс┤Дс┤ЗъЬ▒ъЬ▒ с┤Ыс┤П с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е !\nс┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е с┤П╔┤╩Я╩П с┤бс┤П╩Ас┤ЛъЬ▒ ъЬ░с┤П╩А ╔в╩Ас┤Пс┤Ьс┤Ш с┤Ас┤Ес┤Н╔к╔┤ъЬ▒.</b>")
    else:
        pass
    try:
        command, shortlink_url, api = data.split(" ")
    except:
        return await message.reply_text("<b>с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е ╔к╔┤с┤Дс┤Пс┤Нс┤Ш╩Яс┤Зс┤Ыс┤З !\n╔в╔кс┤ас┤З с┤Нс┤З с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е с┤А╩Яс┤П╔┤╔в с┤б╔кс┤Ы╩Ь ъЬ▒╩Ьс┤П╩Ас┤Ы╔┤с┤З╩А с┤бс┤З╩ЩъЬ▒╔кс┤Ыс┤З с┤А╔┤с┤Е с┤Ас┤Ш╔к.\n\nъЬ░с┤П╩Ас┤Нс┤Ас┤Ы : <code>/shortlink krishnalink.com c8dacdff6e91a8e4b4f093fdb4d8ae31bc273c1a</code>")
    reply = await message.reply_text("<b>с┤Ш╩Яс┤Зс┤АъЬ▒с┤З с┤бс┤А╔кс┤Ы...</b>")
    shortlink_url = re.sub(r"https?://?", "", shortlink_url)
    shortlink_url = re.sub(r"[:/]", "", shortlink_url)
    await save_group_settings(grpid, 'shortlink', shortlink_url)
    await save_group_settings(grpid, 'shortlink_api', api)
    await save_group_settings(grpid, 'is_shortlink', True)
    await reply.edit_text(f"<b>тЬЕ ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П с┤Ас┤Ес┤Ес┤Зс┤Е ъЬ▒╩Ьс┤П╩Ас┤Ы╩Я╔к╔┤с┤Л ъЬ░с┤П╩А <code>{title}</code>.\n\nъЬ▒╩Ьс┤П╩Ас┤Ы╩Я╔к╔┤с┤Л с┤бс┤З╩ЩъЬ▒╔кс┤Ыс┤З : <code>{shortlink_url}</code>\nъЬ▒╩Ьс┤П╩Ас┤Ы╩Я╔к╔┤с┤Л с┤Ас┤Ш╔к : <code>{api}</code></b>")

@Client.on_message(filters.command("setshortlinkoff") & filters.user(ADMINS))
async def offshortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е с┤бс┤П╩Ас┤ЛъЬ▒ с┤П╔┤╩Я╩П ╔к╔┤ ╔в╩Ас┤Пс┤Ьс┤ШъЬ▒ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    await save_group_settings(grpid, 'is_shortlink', False)
    ENABLE_SHORTLINK = False
    return await message.reply_text("ъЬ▒╩Ьс┤П╩Ас┤Ы╩Я╔к╔┤с┤Л ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П с┤Е╔къЬ▒с┤А╩Щ╩Яс┤Зс┤Е.")
    
@Client.on_message(filters.command("setshortlinkon") & filters.user(ADMINS))
async def onshortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е с┤бс┤П╩Ас┤ЛъЬ▒ с┤П╔┤╩Я╩П ╔к╔┤ ╔в╩Ас┤Пс┤Ьс┤ШъЬ▒ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    await save_group_settings(grpid, 'is_shortlink', True)
    ENABLE_SHORTLINK = True
    return await message.reply_text("ъЬ▒╩Ьс┤П╩Ас┤Ы╩Я╔к╔┤с┤Л ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П с┤З╔┤с┤А╩Щ╩Яс┤Зс┤Е.")


@Client.on_message(filters.command("shortlink_info"))
async def ginfo(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>{message.from_user.mention},\n\nс┤ЬъЬ▒с┤З с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е ╔к╔┤ ╩Пс┤Пс┤Ь╩А ╔в╩Ас┤Пс┤Ьс┤Ш.</b>")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    chat_id=message.chat.id
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
#     if 'shortlink' in settings.keys():
#         su = settings['shortlink']
#         sa = settings['shortlink_api']
#     else:
#         return await message.reply_text("<b>Shortener Url Not Connected\n\nYou can Connect Using /shortlink command</b>")
#     if 'tutorial' in settings.keys():
#         st = settings['tutorial']
#     else:
#         return await message.reply_text("<b>Tutorial Link Not Connected\n\nYou can Connect Using /set_tutorial command</b>")
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>с┤П╔┤╩Я╩П ╔в╩Ас┤Пс┤Ьс┤Ш с┤Пс┤б╔┤с┤З╩А с┤П╩А с┤Ас┤Ес┤Н╔к╔┤ с┤Дс┤А╔┤ с┤ЬъЬ▒с┤З с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е !</b>")
    else:
        settings = await get_settings(chat_id) #fetching settings for group
        if 'shortlink' in settings.keys() and 'tutorial' in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            st = settings['tutorial']
            return await message.reply_text(f"<b><u>с┤Дс┤Ь╩А╩Ас┤З╔┤с┤Ы  ъЬ▒с┤Ыс┤Ас┤Ыс┤ЬъЬ▒<u> ЁЯУК\n\nс┤бс┤З╩ЩъЬ▒╔кс┤Ыс┤З : <code>{su}</code>\n\nс┤Ас┤Ш╔к : <code>{sa}</code>\n\nс┤Ыс┤Ьс┤Ыс┤П╩А╔кс┤А╩Я : {st}</b>", disable_web_page_preview=True)
        elif 'shortlink' in settings.keys() and 'tutorial' not in settings.keys():
            su = settings['shortlink']
            sa = settings['shortlink_api']
            return await message.reply_text(f"<b><u>с┤Дс┤Ь╩А╩Ас┤З╔┤с┤Ы  ъЬ▒с┤Ыс┤Ас┤Ыс┤ЬъЬ▒<u> ЁЯУК\n\nс┤бс┤З╩ЩъЬ▒╔кс┤Ыс┤З : <code>{su}</code>\n\nс┤Ас┤Ш╔к : <code>{sa}</code>\n\nс┤ЬъЬ▒с┤З /set_tutorial с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е с┤Ыс┤П ъЬ▒с┤Зс┤Ы ╩Пс┤Пс┤Ь╩А с┤Ыс┤Ьс┤Ыс┤П╩А╔кс┤А╩Я.")
        elif 'shortlink' not in settings.keys() and 'tutorial' in settings.keys():
            st = settings['tutorial']
            return await message.reply_text(f"<b>с┤Ыс┤Ьс┤Ыс┤П╩А╔кс┤А╩Я : <code>{st}</code>\n\nс┤ЬъЬ▒с┤З  /shortlink  с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е  с┤Ыс┤П  с┤Дс┤П╔┤╔┤с┤Зс┤Дс┤Ы  ╩Пс┤Пс┤Ь╩А  ъЬ▒╩Ьс┤П╩Ас┤Ы╔┤с┤З╩А</b>")
        else:
            return await message.reply_text("ъЬ▒╩Ьс┤П╩Ас┤Ы╔┤с┤З╩А с┤А╔┤с┤Е с┤Ыс┤Ьс┤Ыс┤П╩А╔кс┤А╩Я с┤А╩Ас┤З ╔┤с┤Пс┤Ы с┤Дс┤П╔┤╔┤с┤Зс┤Дс┤Ыс┤Зс┤Е.\n\nс┤Д╩Ьс┤Зс┤Дс┤Л /set_tutorial  с┤А╔┤с┤Е  /shortlink  с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е.")

@Client.on_message(filters.command("set_tutorial"))
async def settutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"╩Пс┤Пс┤Ь'╩Ас┤З с┤А╔┤с┤П╔┤╩Пс┤Нс┤Пс┤ЬъЬ▒ с┤Ас┤Ес┤Н╔к╔┤, с┤Ыс┤Ь╩А╔┤ с┤ПъЬ░ъЬ░ с┤А╔┤с┤П╔┤╩Пс┤Нс┤Пс┤ЬъЬ▒ с┤Ас┤Ес┤Н╔к╔┤ с┤А╔┤с┤Е с┤Ы╩А╩П с┤А╔вс┤А╔к╔┤ с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е с┤бс┤П╩Ас┤ЛъЬ▒ с┤П╔┤╩Я╩П ╔к╔┤ ╔в╩Ас┤Пс┤Ьс┤ШъЬ▒ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return
    else:
        pass
    if len(message.command) == 1:
        return await message.reply("<b>╔в╔кс┤ас┤З с┤Нс┤З с┤А с┤Ыс┤Ьс┤Ыс┤П╩А╔кс┤А╩Я ╩Я╔к╔┤с┤Л с┤А╩Яс┤П╔┤╔в с┤б╔кс┤Ы╩Ь с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е.\n\nс┤ЬъЬ▒с┤А╔вс┤З : /set_tutorial <code>https://t.me/HowToOpenHP</code></b>")
    elif len(message.command) == 2:
        reply = await message.reply_text("<b>с┤Ш╩Яс┤Зс┤АъЬ▒с┤З с┤бс┤А╔кс┤Ы...</b>")
        tutorial = message.command[1]
        await save_group_settings(grpid, 'tutorial', tutorial)
        await save_group_settings(grpid, 'is_tutorial', True)
        await reply.edit_text(f"<b>тЬЕ ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П с┤Ас┤Ес┤Ес┤Зс┤Е с┤Ыс┤Ьс┤Ыс┤П╩А╔кс┤А╩Я\n\n╩Пс┤Пс┤Ь╩А ╔в╩Ас┤Пс┤Ьс┤Ш : {title}\n\n╩Пс┤Пс┤Ь╩А с┤Ыс┤Ьс┤Ыс┤П╩А╔кс┤А╩Я : <code>{tutorial}</code></b>")
    else:
        return await message.reply("<b>╩Пс┤Пс┤Ь с┤З╔┤с┤Ыс┤З╩Ас┤Зс┤Е ╔к╔┤с┤Дс┤П╩А╩Ас┤Зс┤Дс┤Ы ъЬ░с┤П╩Ас┤Нс┤Ас┤Ы !\nс┤Дс┤П╩А╩Ас┤Зс┤Дс┤Ы ъЬ░с┤П╩Ас┤Нс┤Ас┤Ы : /set_tutorial <code>https://t.me/HowToOpenHP</code></b>")

@Client.on_message(filters.command("remove_tutorial"))
async def removetutorial(bot, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"╩Пс┤Пс┤Ь'╩Ас┤З с┤А╔┤с┤П╔┤╩Пс┤Нс┤Пс┤ЬъЬ▒ с┤Ас┤Ес┤Н╔к╔┤, с┤Ыс┤Ь╩А╔┤ с┤ПъЬ░ъЬ░ с┤А╔┤с┤П╔┤╩Пс┤Нс┤Пс┤ЬъЬ▒ с┤Ас┤Ес┤Н╔к╔┤ с┤А╔┤с┤Е с┤Ы╩А╩П с┤А╔вс┤А╔к╔┤ с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е.")
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("с┤Ы╩Ь╔къЬ▒ с┤Дс┤Пс┤Нс┤Нс┤А╔┤с┤Е с┤П╔┤╩Я╩П с┤бс┤П╩Ас┤ЛъЬ▒ ╔к╔┤ ╔в╩Ас┤Пс┤Ьс┤ШъЬ▒ !")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return
    else:
        pass
    reply = await message.reply_text("<b>с┤Ш╩Яс┤Зс┤АъЬ▒с┤З с┤бс┤А╔кс┤Ы...</b>")
    await save_group_settings(grpid, 'is_tutorial', False)
    await reply.edit_text(f"<b>ъЬ▒с┤Ьс┤Дс┤Дс┤ЗъЬ▒ъЬ▒ъЬ░с┤Ь╩Я╩Я╩П ╩Ас┤Зс┤Нс┤Пс┤ас┤Зс┤Е с┤Ыс┤Ьс┤Ыс┤П╩А╔кс┤А╩Я ╩Я╔к╔┤с┤Л тЬЕ</b>")
    

@Client.on_callback_query(filters.regex("topsearch"))
async def topsearch_callback(client, callback_query):
    
    def is_alphanumeric(string):
        return bool(re.match('^[a-zA-Z0-9 ]*$', string))
    
    limit = 20  
    top_messages = await mdb.get_top_messages(limit)
    seen_messages = set()
    truncated_messages = []
    for msg in top_messages:
        msg_lower = msg.lower()
        if msg_lower not in seen_messages and is_alphanumeric(msg):
            seen_messages.add(msg_lower)
            
            if len(msg) > 35:
                truncated_messages.append(msg[:32] + "...")
            else:
                truncated_messages.append(msg)
    keyboard = [truncated_messages[i:i+2] for i in range(0, len(truncated_messages), 2)]
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        one_time_keyboard=True, 
        resize_keyboard=True, 
        placeholder="Most searches of the day"
    )
    await callback_query.message.reply_text("<b>Tс┤Пс┤Ш Sс┤Зс┤А╩Ас┤Д╩Ьс┤Зs O╥У T╩Ьс┤З Dс┤А╩П ЁЯСЗ</b>", reply_markup=reply_markup)
    await callback_query.answer()

@Client.on_message(filters.command('top_search'))
async def top(_, message):
    def is_alphanumeric(string):
        return bool(re.match('^[a-zA-Z0-9 ]*$', string))
    try:
        limit = int(message.command[1])
    except (IndexError, ValueError):
        limit = 20
    top_messages = await mdb.get_top_messages(limit)
    seen_messages = set()
    truncated_messages = []
    for msg in top_messages:
        if msg.lower() not in seen_messages and is_alphanumeric(msg):
            seen_messages.add(msg.lower())
            
            if len(msg) > 35:
                truncated_messages.append(msg[:35 - 3])
            else:
                truncated_messages.append(msg)
    keyboard = []
    for i in range(0, len(truncated_messages), 2):
        row = truncated_messages[i:i+2]
        keyboard.append(row)
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True, placeholder="Most searches of the day")
    await message.reply_text(f"<b>Tс┤Пс┤Ш Sс┤Зс┤А╩Ас┤Д╩Ьс┤Зs O╥У T╩Ьс┤З Dс┤А╩П ЁЯСЗ</b>", reply_markup=reply_markup)

    
@Client.on_message(filters.command('trendlist'))
async def trendlist(client, message):
    def is_alphanumeric(string):
        return bool(re.match('^[a-zA-Z0-9 ]*$', string))
    limit = 31
    if len(message.command) > 1:
        try:
            limit = int(message.command[1])
        except ValueError:
            await message.reply_text("Invalid number format.\nPlease provide a valid number after the /trendlist command.")
            return 
    try:
        top_messages = await mdb.get_top_messages(limit)
    except Exception as e:
        await message.reply_text(f"Error retrieving messages: {str(e)}")
        return  

    if not top_messages:
        await message.reply_text("No top messages found.")
        return 
    seen_messages = set()
    truncated_messages = []

    for msg in top_messages:
        if msg.lower() not in seen_messages and is_alphanumeric(msg):
            seen_messages.add(msg.lower())
            truncated_messages.append(msg[:32] + '...' if len(msg) > 35 else msg)

    if not truncated_messages:
        await message.reply_text("No valid top messages found.")
        return  
    formatted_list = "\n".join([f"{i+1}. <b>{msg}</b>" for i, msg in enumerate(truncated_messages)])
    additional_message = "тЪбя╕П ЁЭСиЁЭТНЁЭТН ЁЭТХЁЭТЙЁЭТЖ ЁЭТУЁЭТЖЁЭТФЁЭТЦЁЭТНЁЭТХЁЭТФ ЁЭТВЁЭТГЁЭТРЁЭТЧЁЭТЖ ЁЭТДЁЭТРЁЭТОЁЭТЖ ЁЭТЗЁЭТУЁЭТРЁЭТО ЁЭТШЁЭТЙЁЭТВЁЭТХ ЁЭТЦЁЭТФЁЭТЖЁЭТУЁЭТФ ЁЭТЙЁЭТВЁЭТЧЁЭТЖ ЁЭТФЁЭТЖЁЭТВЁЭТУЁЭТДЁЭТЙЁЭТЖЁЭТЕ ЁЭТЗЁЭТРЁЭТУ. ЁЭС╗ЁЭТЙЁЭТЖЁЭТЪ'ЁЭТУЁЭТЖ ЁЭТФЁЭТЙЁЭТРЁЭТШЁЭТП ЁЭТХЁЭТР ЁЭТЪЁЭТРЁЭТЦ ЁЭТЖЁЭТЩЁЭТВЁЭТДЁЭТХЁЭТНЁЭТЪ ЁЭТВЁЭТФ ЁЭТХЁЭТЙЁЭТЖЁЭТЪ ЁЭТШЁЭТЖЁЭТУЁЭТЖ ЁЭТФЁЭТЖЁЭТВЁЭТУЁЭТДЁЭТЙЁЭТЖЁЭТЕ, ЁЭТШЁЭТКЁЭТХЁЭТЙЁЭТРЁЭТЦЁЭТХ ЁЭТВЁЭТПЁЭТЪ ЁЭТДЁЭТЙЁЭТВЁЭТПЁЭТИЁЭТЖЁЭТФ ЁЭТГЁЭТЪ ЁЭТХЁЭТЙЁЭТЖ ЁЭТРЁЭТШЁЭТПЁЭТЖЁЭТУ."
    formatted_list += f"\n\n{additional_message}"
    reply_text = f"<b>Top {len(truncated_messages)} T╩Ас┤А╔┤с┤Е╔к╔┤╔в с┤П╥У с┤Ы╩Ьс┤З с┤Ес┤А╩П ЁЯСЗ:</b>\n\n{formatted_list}"
    await message.reply_text(reply_text)

@Client.on_message(filters.private & filters.command("pm_search") & filters.user(ADMINS))
async def set_pm_search(client, message):
    bot_id = client.me.id
    try:
        option = message.text.split(" ", 1)[1].strip().lower()
        enable_status = option in ['on', 'true']
    except (IndexError, ValueError):
        await message.reply_text("<b>ЁЯТФ Invalid option. Please send 'on' or 'off' after the command..</b>")
        return
    try:
        await db.update_pm_search_status(bot_id, enable_status)
        response_text = (
            "<b> с┤Шс┤Н ъЬ▒с┤Зс┤А╩Ас┤Д╩Ь с┤З╔┤с┤А╩Щ╩Яс┤Зс┤Е тЬЕ</b>" if enable_status 
            else "<b> с┤Шс┤Н ъЬ▒с┤Зс┤А╩Ас┤Д╩Ь с┤Е╔къЬ▒с┤А╩Щ╩Яс┤Зс┤Е тЭМ</b>"
        )
        await message.reply_text(response_text)
    except Exception as e:
        await log_error(client, f"Error in set_pm_search: {e}")
        await message.reply_text(f"<b>тЭЧ An error occurred: {e}</b>")

@Client.on_message(filters.private & filters.command("movie_update") & filters.user(ADMINS))
async def set_movie_update_notification(client, message):
    bot_id = client.me.id
    try:
        option = message.text.split(" ", 1)[1].strip().lower()
        enable_status = option in ['on', 'true']
    except (IndexError, ValueError):
        await message.reply_text("<b>ЁЯТФ Invalid option. Please send 'on' or 'off' after the command.</b>")
        return
    try:
        await db.update_movie_update_status(bot_id, enable_status)
        response_text = (
            "<b>с┤Нс┤Пс┤а╔кс┤З с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤З ╔┤с┤Пс┤Ы╔къЬ░╔кс┤Дс┤Ас┤Ы╔кс┤П╔┤ с┤З╔┤с┤А╩Щ╩Яс┤Зс┤Е тЬЕ</b>" if enable_status 
            else "<b>с┤Нс┤Пс┤а╔кс┤З с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤З ╔┤с┤Пс┤Ы╔къЬ░╔кс┤Дс┤Ас┤Ы╔кс┤П╔┤ с┤Е╔къЬ▒с┤А╩Щ╩Яс┤Зс┤Е тЭМ</b>"
        )
        await message.reply_text(response_text)
    except Exception as e:
        await log_error(client, f"Error in set_movie_update_notification: {e}")
        await message.reply_text(f"<b>тЭЧ An error occurred: {e}</b>")

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="<b><i>╩Щс┤Пс┤Ы ╔къЬ▒ ╩Ас┤ЗъЬ▒с┤Ыс┤А╩Ас┤Ы╔к╔┤╔в</i></b>", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("<b><i><u>╩Щс┤Пс┤Ы ╔къЬ▒ ╩Ас┤ЗъЬ▒с┤Ыс┤А╩Ас┤Ыс┤Зс┤Е</u> тЬЕ</i></b>")
    os.execl(sys.executable, sys.executable, *sys.argv)

async def log_error(client, error_message):
    """Logs errors to the specified LOG_CHANNEL."""
    try:
        await client.send_message(
            chat_id=LOG_CHANNEL, 
            text=f"<b>тЪая╕П Error Log:</b>\n<code>{error_message}</code>"
        )
    except Exception as e:
        print(f"Failed to log error: {e}")

@Client.on_message(filters.command("del_msg") & filters.user(ADMINS))
async def del_msg(client, message):
    user_id = message.from_user.id
    confirm_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data="confirm_del_yes"),
         InlineKeyboardButton("No", callback_data="confirm_del_no")]
    ])
    sent_message = await message.reply_text(
        "тЪая╕П A╩Ас┤З ╩Пс┤Пс┤Ь sс┤Ь╩Ас┤З ╩Пс┤Пс┤Ь с┤бс┤А╔┤с┤Ы с┤Ыс┤П с┤Д╩Яс┤Зс┤А╩А с┤Ы╩Ьс┤З с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤Зs с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ╩Я╔кsс┤Ы ?\n\n с┤Ес┤П ╩Пс┤Пс┤Ь ъЬ▒с┤Ы╔к╩Я╩Я с┤бс┤А╔┤с┤Ы с┤Ыс┤П с┤Дс┤П╔┤с┤Ы╔к╔┤с┤Ьс┤З ?",
        reply_markup=confirm_markup
    )
    await asyncio.sleep(60)
    try:
        await sent_message.delete()
    except Exception as e:
        print(f"Error deleting the message: {e}")

@Client.on_callback_query(filters.regex('^confirm_del_'))
async def confirmation_handler(client, callback_query):
    user_id = callback_query.from_user.id
    action = callback_query.data.split("_")[-1]  
    if action == "yes":
        await delete_all_msg(user_id)
        await callback_query.message.edit_text(
            'ЁЯз╣ с┤Ьс┤Шс┤Ес┤Ас┤Ыс┤ЗъЬ▒ с┤Д╩Ьс┤А╔┤╔┤с┤З╩Я ╩Я╔кsс┤Ы ╩Ьс┤Аs ╩Щс┤Зс┤З╔┤ с┤Д╩Яс┤Зс┤А╩Ас┤Зс┤Е sс┤Ьс┤Дс┤Дс┤Зss╥Ус┤Ь╩Я╩Я╩П тЬЕ'
        )
    elif action == "no":
        await callback_query.message.delete()
    await callback_query.answer()


