from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


main = ReplyKeyboardMarkup(resize_keyboard=True)
main.add('latest_news').add('save_news').add('saved_news')

admin_panel = ReplyKeyboardMarkup(resize_keyboard=True)
admin_panel.add('latest_news').add('save_news').add('saved_news').add('Contact_users')

latest_news_list = InlineKeyboardMarkup(row_width=3)
latest_news_list.add(InlineKeyboardButton(text='Topic', callback_data='theme'))

save_news_list = InlineKeyboardMarkup(row_width=3)
save_news_list.add(InlineKeyboardButton(text='URL', callback_data='url'))

self_confirm = ReplyKeyboardMarkup(resize_keyboard=True)
self_confirm.add('Confirm')

cancel = ReplyKeyboardMarkup(resize_keyboard=True)
cancel.add('Anulare')