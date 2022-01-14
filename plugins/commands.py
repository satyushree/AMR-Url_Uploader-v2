import os
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
from translation import Translation
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#######################################################################################
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from sample_config import Config
from database.users_chats_db import db
from sample_config import temp
from pyrogram.errors import ChatAdminRequired


#######################################################################################


@Client.on_message(filters.command(["start"]) & filters.private)
async def start(bot, update):
    if not await bot.db.is_user_exist(update.chat.id):
        await bot.db.add_user(update.chat.id)
        await bot.send_message(
            Config.LOG_CHANNEL,
            f"New User [{update.from_user.first_name}](tg://user?id={update.chat.id}) started."
        )
        
    await update.reply_text(
        text=Translation.START_TEXT.format(update.from_user.mention),
        disable_web_page_preview=True,
        reply_markup=Translation.START_BUTTONS
    )


@Client.on_message(filters.command(["help"]) & filters.private)
async def help(bot, update):
    await update.reply_text(
        text=Translation.HELP_TEXT,
        disable_web_page_preview=True,
        reply_markup=Translation.HELP_BUTTONS
    )

@Client.on_message(filters.command(["about"]) & filters.private)
async def about(bot, update):
    await update.reply_text(
        text=Translation.ABOUT_TEXT,
        disable_web_page_preview=True,
        reply_markup=Translation.ABOUT_BUTTONS
    )

@Client.on_message(filters.command(["donate"]) & filters.private)
async def dobate(bot, update):
        await update.message.edit_text(
            text=Translation.DONATE_TEXT,
            reply_markup=Translation.DONATE_BUTTONS,
            disable_web_page_preview=True
    )
        
#######################################################################################


@Client.on_message(filters.command(["ban"]) & filters.user(Config.ADMINS))
async def ban_a_user(bot, message):
    # https://t.me/GetTGLink/4185
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("This might be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"{k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"Successfully banned {k.mention}")


    
@Client.on_message(filters.command(["unban"]) & filters.user(Config.ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("This is an invalid user, make sure ia have met him before.")
    except IndexError:
        return await message.reply("Thismight be a channel, make sure its a user.")
    except Exception as e:
        return await message.reply(f'Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"{k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"Successfully unbanned {k.mention}")


    
@Client.on_message(filters.command(["users"]) & filters.user(Config.ADMINS))
async def list_users(bot, message):
    # https://t.me/GetTGLink/4184
    raju = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users") 
        
        
#######################################################################################        
    
@Client.on_message(filters.private & filters.command(["total"]))
async def sts(bot, message):
    if message.from_user.id != Config.ADMINS:
        return 
    total_users = await db.total_users_count()
    await message.reply_text(text=f"Total user(s) {total_users}", quote=True)

