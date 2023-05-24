'''В этом файле мы создаём встроенные клавиатуры. '''
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
inlinekeyboard = InlineKeyboardMarkup()
inlinekeyboard.add(InlineKeyboardButton(text="🆕 Новинки", callback_data="news_menu"),
InlineKeyboardButton(text="🔥 Популярное", callback_data="popular_menu"))
inlinekeyboard.add(InlineKeyboardButton(text="💡 Где я?", callback_data="about"))
inlinekeyboard.add(InlineKeyboardButton(text="❤️ Сохранённые", callback_data="favorites"))
news_menu_kb = InlineKeyboardMarkup()
news_menu_kb.add(InlineKeyboardButton(text="Фильмы", callback_data="news_films"), InlineKeyboardButton(text="Сериалы", callback_data="news_serials"))
news_menu_kb.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))
popular_menu_kb = InlineKeyboardMarkup()
popular_menu_kb.add(InlineKeyboardButton(text="Фильмы", callback_data="popular_films"), InlineKeyboardButton(text="Сериалы", callback_data="popular_series"))
popular_menu_kb.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))
inlinekeyboard3 = InlineKeyboardMarkup()
inlinekeyboard3.add(InlineKeyboardButton(text="◀️ Вернуться назад", callback_data="categories"),
InlineKeyboardButton(text="🏠 Меню", callback_data="back"))
exit = InlineKeyboardMarkup()
exit.add(InlineKeyboardButton(text="🏠 Главное меню", callback_data="back"))
gotohome = InlineKeyboardMarkup()
gotohome.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))
category = InlineKeyboardMarkup()
category.add(InlineKeyboardButton(text="Фильмы", callback_data="films"),
InlineKeyboardButton(text="Сериалы", callback_data="serials"))
category.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))
about = InlineKeyboardMarkup()
about.add(InlineKeyboardButton(text="◀️ Назад", callback_data="back"))


