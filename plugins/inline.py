# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, temp, get_poster
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from database.connections_mdb import active_connection

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME

async def inline_users(query: InlineQuery):
    if AUTH_USERS:
        if query.from_user and query.from_user.id in AUTH_USERS:
            return True
        else:
            return False
    if query.from_user and query.from_user.id not in temp.BANNED_USERS:
        return True
    return False

@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for given inline query"""
    chat_id = await active_connection(str(query.from_user.id))
    
    if not await inline_users(query):
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text='Access Denied',
            switch_pm_parameter="no_access"
        )
        return

    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text='Subscribe to use this bot',
            switch_pm_parameter="subscribe"
        )
        return

    results = []
    string = query.query.strip()
    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(query=string)

    # دریافت اطلاعات فیلم از IMDb
    imdb_info = await get_poster(string) if string else None

    # دریافت فایل‌ها از دیتابیس
    files, next_offset, total = await get_search_results(chat_id, string, file_type=None, max_results=10, offset=offset)

    # اضافه کردن اطلاعات IMDb در بالای نتایج
    if imdb_info:
        caption = (
            "⭐ IMDb: " + str(imdb_info.get('rating', 'N/A')) + "\n"
            "🎭 Genre: " + str(imdb_info.get('genres', 'N/A')) + "\n"
            "📖 " + str(imdb_info.get('plot', 'No plot available'))[:200] + "..."
        )
        
        results.append(
            InlineQueryResultCachedDocument(
                title="🎬 " + str(imdb_info.get('title', 'Unknown')) + " (" + str(imdb_info.get('year', 'N/A')) + ")",
                document_file_id=files[0]['file_id'] if files else "",
                caption=caption,
                description="🔗 IMDb: " + str(imdb_info.get('rating', 'N/A')),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 View on IMDb", url=imdb_info.get('url', '#'))]
                ])
            )
        )

    # اضافه کردن فایل‌های موجود
    for file in files:
        title = file['file_name']
        size = get_size(file['file_size'])
        f_caption = title + "\nSize: " + size

        results.append(
            InlineQueryResultCachedDocument(
                title=title,
                document_file_id=file['file_id'],
                caption=f_caption,
                description='Size: ' + size,
                reply_markup=reply_markup
            )
        )

    # ارسال نتایج اینلاین
    if results:
        await query.answer(
            results=results,
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text="🔍 " + str(total) + " results found for " + string,
            switch_pm_parameter="start",
            next_offset=str(next_offset)
        )
    else:
        await query.answer(
            results=[],
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text='❌ No results found!',
            switch_pm_parameter="no_results"
        )

def get_reply_markup(query):
    buttons = [[
        InlineKeyboardButton('🔍 Search again', switch_inline_query_current_chat=query)
    ]]
    return InlineKeyboardMarkup(buttons)
