from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from app import keyboards as kb
from app import database as db
from newsapi import NewsApiClient
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import os

storage = MemoryStorage()
load_dotenv()
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)
newsapi = NewsApiClient(api_key=os.getenv('NEWS_TOKEN'))

async def on_startup(_):
    await db.db_start()
    print('Bot-ul a fost startat.')

class LatestNews(StatesGroup):
    type = State()
    name = State()

class SaveNews(StatesGroup):
    type = State()
    url = State()
    id = State()

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await db.cmd_start_db(message.from_user.id)
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        await message.answer_sticker('CAACAgIAAxkBAANeZFhm-IcgWy24u-tWL17dGwr1zvUAAhsAA8A2TxN9vYqDy0RNai8E')
        await message.answer(f'{message.from_user.first_name}, you are authorized as ADMIN! Welcome ADMIN!!!', 
                             reply_markup=kb.admin_panel)
    else:
        await message.answer_sticker('CAACAgIAAxkBAAM_ZFhN8x7crHy8d-rXdPR3F0b8AAGmAAIdAAPANk8TXtim3EE93kgvBA')
        await message.answer(f'{message.from_user.first_name}, hello and welcome to this bot!',
                            reply_markup=kb.main)

@dp.message_handler(commands=['id'])
async def cmd_id(message: types.Message):
    await message.answer(f'{message.from_user.id}')

@dp.message_handler(text='latest_news')
async def latest_news_fun(message: types.Message):
    await LatestNews.type.set()
    await message.answer('Latest news are:', reply_markup=kb.latest_news_list)

@dp.message_handler(text='save_news')
async def save_news_fun(message: types.Message):
    await SaveNews.type.set()
    await message.answer(f'Save important news:', reply_markup=kb.save_news_list)

@dp.message_handler(text='saved_news')
async def saved_news_fun(message: types.Message):
    x = await db.select_news_item()
    print(x)
    await message.answer(f'Saved URLs: \n\n{x}', reply_markup=kb.main)

@dp.message_handler(text='Contact_users')
async def contact_user(message: types.Message):
    if message.from_user.id == int(os.getenv('ADMIN_ID')):
        users_id = await db.all_users_id()
        print(users_id)
        for x1 in users_id:
            print(x1)
            await message.answer(f'User:\n {x1}', 
                            reply_markup=kb.admin_panel)



@dp.callback_query_handler(state=LatestNews.type)
async def add_item_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
    await call.message.answer('Write the topic you are interested', reply_markup=kb.cancel)
    await LatestNews.next()

@dp.message_handler(state=LatestNews.name)
async def add_item_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        top_headlines = newsapi.get_top_headlines(
        q=data['name'],
        language='en',
        )
        for article in top_headlines['articles']:
            t= article['title']
            d= article['description']
            await message.answer(f'Title: {t}\n\nDescription: {d}')
    await message.answer('Those are all the news.', reply_markup=kb.main)
    await state.finish()



@dp.callback_query_handler(state=SaveNews.type)
async def add_news_item_type(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = call.data
    await call.message.answer('Write the url of news you are interested', reply_markup=kb.cancel)
    await SaveNews.next()

@dp.message_handler(state=SaveNews.url)
async def add_news_item_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['url'] = message.text
    await message.answer('Please confirm', reply_markup=kb.self_confirm)
    await SaveNews.next()

@dp.message_handler(state=SaveNews.id)
async def add_news_item_user_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        u_id = await db.select_user_id(message.from_user.id)
        print(u_id)
        for x1 in u_id:
            print(x1)
            data['id'] = x1
    await db.add_item(state)
    await message.answer('URL news is saved.', reply_markup=kb.main)
    await state.finish()


@dp.message_handler(content_types=['document', 'photo'])
async def forward_message(message: types.Message):
    await bot.forward_message(os.getenv('GROUP_ID'), message.from_user.id, message.message_id)


@dp.message_handler(content_types=['sticker'])
async def check_sticker(message:types.Message):
    await message.answer(message.sticker.file_id)
    # await bot.send_message(message.from_user.id, message.chat.id)

@dp.message_handler()
async def answer(message: types.Message):
    await message.reply('This bot does not understand you.')

@dp.callback_query_handler()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    if callback_query.data == 'theme':
        await bot.send_message(chat_id=callback_query.from_user.id, text='You selected specific topic.')
    elif callback_query.data == 'url':
        await bot.send_message(chat_id=callback_query.from_user.id, text='You selected specific URL.')

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)