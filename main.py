 # -*- coding: utf-8 -*-
'''Основной код: в начале мы создаём фунции, переменные. Стоит отметить функции с поиском новых фильмов и сериалов.
Затем мы "создаём" фильмы и сериалы и показываем их. Также мы прописываем код для сохранённых и всех клавиатур, которые
импортируем из другого файла, то есть нажатие на кнопки. Большинство кода заняло обновление списков фильмов и сериалов,
а также "перелистывание" их.
'''
import requests
import asyncio
import aiohttp
import json
from datetime import date
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from keyboards import *
from config import *
from pagination import InlinePagination, InlinePagination2, FavoritesPagination, NewsPagination
from db import Sqliter


bot = Bot(token=TOKEN, parse_mode='HTML')
admin_id = admin_id
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()
db = Sqliter('database.db')

category_list = {'films': 'Фильмы', 'serials': 'Сериалы', 'series': 'Сериалы', 'film': 'Фильмы'}
last_domain = ''

class GetUserInfo(StatesGroup):
    us_zapros_film = State()
    us_zapros_serial = State()
    us_zapros_film_number = State()
    us_zapros_serial_number = State()
    us_zapros_video = State()


database = open("users_id.txt", "r", encoding="utf-8")
datausers = set()
for line in database:
    datausers.add(line.strip())
database.close()


async def add_news_films(data):
    with open('news_films.json', 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

async def add_news_serials(data):
    with open('news_serials.json', 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


async def add_popular_films(data):
    with open('popular_films.json', 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

async def add_popular_series(data):
    with open('popular_series.json', 'w', encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


async def update_popular():
    print('update_popular | Начинаю проверку на наличие новых популярных фильмов.')
    await bot.send_message(chat_id=admin_id, text='🔃 Пожалуйста подождите..')
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api1673051707.bhcesh.me/list?token=3794a7638b5863cc60d7b2b9274fa32e&sort=-views&type=films&limit=50&year=2023', timeout=None) as response:
            response = await response.json()
    popular_films = []
    results = response['results']
    for result in results:
        film_id = result['id']
        name = result['name']
        type = category_list[result['type']]
        year = result["year"]
        poster = result["poster"]
        try:
            kinopoisk = result["kinopoisk"]
        except KeyError:
            kinopoisk = None
        try:
            imdb = result["imdb"]
        except KeyError:
            imdb = None
        try:
            quality = result["quality"]
        except KeyError:
            quality = None
        try:
            country = result["country"].values()
            country = ', '.join(country)
        except:
            country = ''
        try:
            genre = result['genre'].values()
            genre = ', '.join(genre)
        except KeyError:
            genre = ''
        popular_films.append({'id':film_id, 'name': name, 'year': year,'quality':quality,'genre':genre, 'type':type,'country':country,'poster':poster, 'kinopoisk': kinopoisk, 'imdb': imdb})
    data = {'data': popular_films}
    await add_popular_films(data)
    print('update_popular | Начинаю проверку на наличие новых популярных сериалов.')
    await bot.send_message(chat_id=admin_id, text='🔃 Пожалуста подождите..')
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api1673051707.bhcesh.me/list?token=3794a7638b5863cc60d7b2b9274fa32e&sort=-views&type=serials&join_seasons=false&limit=50&year=2023', timeout=None) as response:
            response = await response.json()
    popular_series = []
    results = response['results']
    for result in results:
        film_id = result['id']
        name = result['name']
        type = category_list[result['type']]
        year = result["year"]
        poster = result["poster"]
        try:
            kinopoisk = result["kinopoisk"]
        except KeyError:
            kinopoisk = None
        try:
            imdb = result["imdb"]
        except KeyError:
            imdb = None
        try:
            quality = result["quality"]
        except KeyError:
            quality = None
        try:
            country = result["country"].values()
            country = ', '.join(country)
        except:
            country = ''
        try:
            genre = result['genre'].values()
            genre = ', '.join(genre)
        except KeyError:
            genre = ''
        popular_series.append({'id':film_id, 'name': name, 'year': year,'quality':quality,'genre':genre, 'type':type,'country':country,'poster':poster, 'kinopoisk': kinopoisk, 'imdb': imdb})
    data = {'data': popular_series}
    current_date = date.today()
    await add_popular_series(data)
    print('update_popular | Проверка завершена.')
    await bot.send_message(text=f'✅ <b>{current_date}</b> | Проверка раздела <b>«Популярное»</b> успешно завершена.')

# ------------------------------------------------------------------------------------------------------------------------
async def update_domain():
    global last_domain
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api1665331096.bhcesh.me/embed-domain?token=3794a7638b5863cc60d7b2b9274fa32e') as response:
            response = await response.json()
    domain = response["domain"]
    if domain != last_domain:
        db.update_domain(domain)
        last_domain = domain

async def update_news_films():
    print('update_news_films | Начинаю проверку на наличие новых фильмов.')
    await bot.send_message(chat_id=admin_id, text='🔃 Запущена проверка на наличие новых фильмов.\n🕘 Пожалуйста, подождите..')
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api1664409738.bhcesh.me/video/news?limit=50&type=films&token=3794a7638b5863cc60d7b2b9274fa32e&year=2023', timeout=None) as response:
            response = await response.json()
    results = response['results']
    print(len(results))
    results = [result1['id'] for result1 in results]
    results = list(set(results))
    print(len(results))
    news_films = []
    for result in results:
        film_id = result
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api1663355922.bhcesh.me/franchise/details?token=3794a7638b5863cc60d7b2b9274fa32e&id={film_id}', timeout=None) as response:
                film_data = await response.json()
        name = film_data['name']
        type = category_list[film_data['type']]
        year = film_data["year"]
        poster = film_data["poster"]
        try:
            kinopoisk = film_data["kinopoisk"]
        except KeyError:
            kinopoisk = None
        try:
            imdb = film_data["imdb"]
        except KeyError:
            imdb = None
        try:
            quality = film_data["quality"]
        except KeyError:
            quality = None
        try:
            country = film_data["country"].values()
            country = ', '.join(country)
        except:
            country = ''
        print(name)
        try:
            genre = film_data['genre'].values()
            genre = ', '.join(genre)
        except:
            genre = ''
        news_films.append({'id':film_id, 'name': name, 'year': year,'quality':quality,'genre':genre, 'type':type,'country':country,'poster':poster, 'imdb': imdb, 'kinopoisk': kinopoisk})
        await asyncio.sleep(3)
    news_films = {'data': news_films}
    current_date = date.today()
    await add_news_films(news_films)
    print('update_news_films | Проверка завершена.')
    await bot.send_message(text=f'✅ <b>{current_date} 🆕 Новые <b>фильмы</b> добавлены.')

async def update_news_serials():
    print('update_news_serials | Начинаю проверку на наличие новых сериалов.')
    await bot.send_message(chat_id=admin_id, text='🕘 Пожалуйста, подождите..')
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api1664409738.bhcesh.me/video/news?limit=50&join_seasons=false&type=serials&token=3794a7638b5863cc60d7b2b9274fa32e&year=2023', timeout=None) as response:
            response = await response.json()
    results = response['results']
    print(len(results))
    results = [result1['id'] for result1 in results]
    results = list(set(results))
    print(len(results))
    news_serials = []
    for result in results:
        film_id = result
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://api1663355922.bhcesh.me/franchise/details?token=3794a7638b5863cc60d7b2b9274fa32e&id={film_id}&join_seasons=false', timeout=None) as response:
                film_data = await response.json()
        name = film_data['name']
        type = category_list[film_data['type']]
        year = film_data["year"]
        poster = film_data["poster"]
        try:
            kinopoisk = film_data["kinopoisk"]
        except KeyError:
            kinopoisk = None
        try:
            imdb = film_data["imdb"]
        except KeyError:
            imdb = None
        try:
            quality = film_data["quality"]
        except KeyError:
            quality = None
        try:
            country = film_data["country"].values()
            country = ', '.join(country)
        except:
            country = ''
        print(name)
        try:
            genre = film_data['genre'].values()
            genre = ', '.join(genre)
        except:
            genre = ''
        news_serials.append({'id':film_id, 'name': name, 'year': year,'quality':quality,'genre':genre, 'type':type,'country':country,'poster':poster, 'imdb': imdb, 'kinopoisk': kinopoisk})
        await asyncio.sleep(3)
    news_serials = {'data': news_serials}
    current_date = date.today()
    await add_news_serials(news_serials)
    print('update_news_serials | Проверка завершена.')
    await bot.send_message(text=f'✅ <b>{current_date} 🆕 Новые <b>сериалы</b> добавлены.\n')





@dp.message_handler(commands=['start'], state="*")
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    file = open('users_id.txt', 'r')
    text = file.read()
    if not str(message.from_user.id) in text:
        all_id = open("users_id.txt", "a", encoding="utf-8")
        all_id.write(str(f"{message.from_user.id}\n"))
        datausers.add(message.from_user.id)
        current_date = date.today()
        db.db_table_val(user_id=message.from_user.id, user_name=message.from_user.username, user_register=current_date)
    text = f'<a href="https://png.pngtree.com/thumb_back/fh260/background/20210902/pngtree-movie-film-black-minimalist-background-image_785429.jpg">🎞️</a> Этот бот поможет вам скрасить ваш вечер!'
    await bot.send_message(message.from_user.id, f'{text}', reply_markup=inlinekeyboard)

@dp.callback_query_handler(text="popular_menu", state="*")
async def popular_menu(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text= '<a href="https://png.pngtree.com/thumb_back/fh260/background/20210902/pngtree-movie-film-black-minimalist-background-image_785429.jpg">🚀</a> Вы перешли в раздел <b>🔥 Популярное</b>, здесь находятся фильмы и сериалы, которые популярны на текущий год.', reply_markup=popular_menu_kb)

# Новинки (Фильмы)
@dp.callback_query_handler(text="news_menu", state="*")
async def news_menu(call: types.CallbackQuery):
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text= '<a href="https://png.pngtree.com/thumb_back/fh260/background/20210902/pngtree-movie-film-black-minimalist-background-image_785429.jpg">🆕</a> Вы перешли в раздел <b>«Новинки»</b>, здесь находятся новые фильмы и сериалы, которые были добавлены в течении последних суток.', reply_markup=news_menu_kb)
@dp.callback_query_handler(text="news_films", state="*")
async def news_menu(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    with open('news_films.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']

    film_data = popular_films[0]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="news_films_back_", next_prefix="news_films_next_")
    kb = pagination.get_page_keyboard(cur_page=1, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("news_films_next_"))
async def next(call: types.CallbackQuery):
    with open('news_films.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    number_film = int(call.data.split('news_films_next_')[1])-1

    film_data = popular_films[number_film]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="news_films_back_", next_prefix="news_films_next_")
    kb = pagination.get_page_keyboard(cur_page=call.data, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("news_films_back_"))
async def next(call: types.CallbackQuery):
    with open('news_films.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    number_film = int(call.data.split('news_films_back_')[1])-1

    film_data = popular_films[number_film]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="news_films_back_", next_prefix="news_films_next_")
    kb = pagination.get_page_keyboard(cur_page=call.data, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

# Новинки (Сериалы)
@dp.callback_query_handler(text="news_serials", state="*")
async def news_menu(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    with open('news_serials.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']

    film_data = popular_films[0]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="news_serials_back_", next_prefix="news_serials_next_")
    kb = pagination.get_page_keyboard(cur_page=1, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("news_serials_next_"))
async def next(call: types.CallbackQuery):
    with open('news_serials.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    number_film = int(call.data.split('news_serials_next_')[1])-1

    film_data = popular_films[number_film]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="news_serials_back_", next_prefix="news_serials_next_")
    kb = pagination.get_page_keyboard(cur_page=call.data, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("news_serials_back_"))
async def next(call: types.CallbackQuery):
    with open('news_serials.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    number_film = int(call.data.split('news_serials_back_')[1])-1

    film_data = popular_films[number_film]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="news_serials_back_", next_prefix="news_serials_next_")
    kb = pagination.get_page_keyboard(cur_page=call.data, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

# Популярные фильмы
@dp.callback_query_handler(text="popular_films", state="*")
async def popular_menu(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    with open('popular_films.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']

    film_data = popular_films[0]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="popular_filmsback_", next_prefix="popular_filmsnext_")
    kb = pagination.get_page_keyboard(cur_page=1, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("popular_filmsnext_"))
async def next(call: types.CallbackQuery):
    with open('popular_films.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    number_film = int(call.data.split('popular_filmsnext_')[1])-1

    film_data = popular_films[number_film]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="popular_filmsback_", next_prefix="popular_filmsnext_")
    kb = pagination.get_page_keyboard(cur_page=call.data, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("popular_filmsback_"))
async def next(call: types.CallbackQuery):
    with open('popular_films.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    number_film = int(call.data.split('popular_filmsback_')[1])-1

    film_data = popular_films[number_film]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="popular_filmsback_", next_prefix="popular_filmsnext_")
    kb = pagination.get_page_keyboard(cur_page=call.data, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

# Популярные сериалы
@dp.callback_query_handler(text="popular_series", state="*")
async def popular_menu(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    with open('popular_series.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']

    film_data = popular_films[0]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="popular_seriesback_", next_prefix="popular_seriesnext_")
    kb = pagination.get_page_keyboard(cur_page=1, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("popular_seriesnext_"))
async def next(call: types.CallbackQuery):
    with open('popular_series.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    number_film = int(call.data.split('popular_seriesnext_')[1])-1

    film_data = popular_films[number_film]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="popular_seriesback_", next_prefix="popular_seriesnext_")
    kb = pagination.get_page_keyboard(cur_page=call.data, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>?? Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("popular_seriesback_"))
async def next(call: types.CallbackQuery):
    with open('popular_series.json', 'r', encoding="utf-8") as f:
        popular_films = json.load(f)['data']
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [int(i[0]) for i in favorite_films]
    number_film = int(call.data.split('popular_seriesback_')[1])-1

    film_data = popular_films[number_film]
    film_id = film_data['id']
    poster = film_data['poster']
    name = film_data['name']
    year = film_data['year']
    imdb = film_data["imdb"]
    country = film_data['country']
    type = film_data['type']
    genre = film_data['genre']
    quality = film_data['quality']
    kinopoisk = film_data['kinopoisk']

    pagination = NewsPagination(films=popular_films, width=2, back_prefix="popular_seriesback_", next_prefix="popular_seriesnext_")
    kb = pagination.get_page_keyboard(cur_page=call.data, fave_status=film_id in favorite_ids)
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>🏅 КП:</b> {kinopoisk} | <b>IMDb:</b> {imdb}\n<b>🌍 Страна:</b> {country}\n<b>📀 Качество:</b> {quality}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)


# Сохранённые
@dp.callback_query_handler(text="favorites")
async def send(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    if len(favorite_films) == 0:
        await call.answer('‼ Вы ещё ничего не добавляли в ваши ❤ сохранённые.\n\nСамое время это исправить!', show_alert=True)
    else:
        film_id = favorite_films[0][0]
        name = favorite_films[0][2]
        poster = favorite_films[0][6]
        year = favorite_films[0][3]
        genre = favorite_films[0][4]
        url = favorite_films[0][5]
        type = category_list[favorite_films[0][7]]
        pagination = FavoritesPagination(films=favorite_films, width=2)
        kb = pagination.get_page_keyboard(cur_page=1)
        await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("del_favorite|"))
async def next(call: types.CallbackQuery):
    film_id = call.data.split('|')[1]
    # print(film_id)
    favorites = db.get_favorites(call.message.chat.id)
    favorites_ids = [film[0] for film in favorites]
    if str(film_id) in favorites_ids:
        db.del_favorite(film_id)
        await call.answer('🗑 Успешно удалено из ваших ❤ сохранённых!', show_alert=True)
    else:
        await call.answer('‼ Не находится в ваших ❤ сохранённых!', show_alert=True)

@dp.callback_query_handler(lambda c: c.data.startswith("add_favorite|"))
async def next(call: types.CallbackQuery):
    film_id = call.data.split('|')[1]
    favorites = db.get_favorites(call.message.chat.id)
    favorites_ids = [str(film[0]) for film in favorites]
    if film_id not in favorites_ids:
        film_data = db.get_film_by_id(film_id)
        if len(film_data) == 0:
            params = {"id": film_id}
            film_data = requests.get("https://api1663355922.bhcesh.me/franchise/details?token=3794a7638b5863cc60d7b2b9274fa32e", params=params).json()
            try:
                genre = film_data['genre'].values()
                genre = ', '.join(genre)
            except KeyError:
                genre = ''
            data = [film_id, call.message.chat.id, film_data['name'], film_data['year'], genre, film_data["iframe_url"], film_data['poster'], film_data['type']]
        else:
            film_data = film_data[0]
            data = [film_id, call.message.chat.id, film_data[2], film_data[4], film_data[3], film_data[5], film_data[6], film_data[7]]
        db.add_favorite(data)
        await call.answer('✅ Успешно добавлен в ваши ❤ сохранённые!', show_alert=True)
    else:
        await call.answer('‼ Уже находится в ваших ❤ сохранённых!', show_alert=True)

@dp.callback_query_handler(lambda c: c.data.startswith("favenext_"))
async def next(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    number_film = int(call.data.split('favenext_')[1])-1
    pagination = FavoritesPagination(films=favorite_films, width=2)
    kb = pagination.get_page_keyboard(cur_page=call.data)

    film_id = favorite_films[number_film][0]
    name = favorite_films[number_film][2]
    poster = favorite_films[number_film][6]
    year = favorite_films[number_film][3]
    genre = favorite_films[number_film][4]
    url = favorite_films[number_film][5]
    type = favorite_films[number_film][7]
    type = category_list[type]
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("faveback_"))
async def next(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    number_film = int(call.data.split('faveback_')[1])-1
    pagination = FavoritesPagination(films=favorite_films, width=2)
    kb = pagination.get_page_keyboard(cur_page=call.data)

    film_id = favorite_films[number_film][0]
    name = favorite_films[number_film][2]
    poster = favorite_films[number_film][6]
    year = favorite_films[number_film][3]
    genre = favorite_films[number_film][4]
    url = favorite_films[number_film][5]
    type = favorite_films[number_film][7]
    type = category_list[type]
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("item_"))
async def next(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [str(i[0]) for i in favorite_films]
    collection_id = call.data.split('item_')[1]
    collections_films = db.get_films(collection_id)
    collections_films.reverse()
    film_id = str(collections_films[0][1])
    name = collections_films[0][2]
    poster = collections_films[0][6]
    year = collections_films[0][4]
    genre = collections_films[0][3]
    url = collections_films[0][5]
    type = collections_films[0][7]
    type = category_list[type]
    pagination = InlinePagination2(films=collections_films, width=2)

    kb = pagination.get_page_keyboard(cur_page=1, collection_id=collection_id, fave_status=film_id in favorite_ids)

    kb.row(InlineKeyboardButton(text="🏠 Вернуться в меню", callback_data="back"))
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("n2_"))
async def next(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [str(i[0]) for i in favorite_films]
    collection_id = call.data.split('n2_')[1].split('_')[0]
    number_film = int(call.data.split('n2_')[1].split('_')[1])-1
    collections_films = db.get_films(collection_id)
    collections_films.reverse()
    pagination = InlinePagination2(films = collections_films, width=2)
    film_id = collections_films[number_film][1]
    name = collections_films[number_film][2]
    poster = collections_films[number_film][6]
    year = collections_films[number_film][4]
    genre = collections_films[number_film][3]
    url = collections_films[number_film][5]
    type = collections_films[number_film][7]
    type = category_list[type]
    kb = pagination.get_page_keyboard(cur_page=call.data, collection_id=collection_id, fave_status=film_id in favorite_ids)
    kb.row(InlineKeyboardButton(text="🏠 Вернуться в меню", callback_data="back"))
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("b2_"))
async def back_pag(call: types.CallbackQuery):
    favorite_films = db.get_favorites(call.message.chat.id)
    favorite_ids = [i[0] for i in favorite_films]
    collection_id = call.data.split('b2_')[1].split('_')[0]
    number_film = int(call.data.split('b2_')[1].split('_')[1])-1
    collections_films = db.get_films(collection_id)
    collections_films.reverse()
    pagination = InlinePagination2(films = collections_films, width=2)
    film_id = collections_films[number_film][1]
    name = collections_films[number_film][2]
    poster = collections_films[number_film][6]
    year = collections_films[number_film][4]
    genre = collections_films[number_film][3]
    url = collections_films[number_film][5]
    type = collections_films[number_film][7]
    type = category_list[type]
    kb = pagination.get_page_keyboard(cur_page=call.data, collection_id=collection_id, fave_status=film_id in favorite_ids)
    kb.row(InlineKeyboardButton(text="🏠 Вернуться в меню", callback_data="back"))
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'<b><a href="{poster}">▶️</a> Название:</b> {name}\n<b>📁 Категория:</b> {type}\n<b>🎦 Жанр:</b> {genre}\n<b>🗓️ Год:</b> {year}', reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data.startswith("b_"))
async def back_pag(call: types.CallbackQuery):
    with open('collections.json', 'r', encoding="utf-8") as f:
        collections = json.load(f)
    pagination = InlinePagination(button_datas=[(collection_items[1], collection_items[0]) for collection_items in collections['data']], width=2)
    kb = pagination.get_page_keyboard(cur_page=call.data)

    await call.message.edit_reply_markup(reply_markup=kb)

@dp.callback_query_handler(text="about", state="*")
async def send(call: types.CallbackQuery):
  await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Этот бот был создан для просмотра и поиска фильмов и сериалов, которые вы сможете найти здесь.\n\n 📝Возможности и плюсы данного бота:\n - Всегда под рукой,\n - Обновление новинок,\n - Вы всегда сможете найти понравившиеся фильмы в ваших сохранённых.\n Надеюсь, этот бот скрасит ваше время вечером! ', reply_markup=about)


@dp.message_handler(content_types=['text'])
async def send_all(message):
  await bot.send_message(message.from_user.id, f'Что-то пошло не так:/\n <i>Вернитесь в <b>главное меню</b></i>.', reply_markup=exit)

@dp.callback_query_handler(text="back", state="*")
async def back(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text= '🏠 Вы вернулись в <b>главное меню</b>.\n\n<a href="https://png.pngtree.com/thumb_back/fh260/background/20210902/pngtree-movie-film-black-minimalist-background-image_785429.jpg">🎦</a> Здесь вы можете выбрать <b>раздел</b>, в котором желаете найти или выбрать видеоматериал для просмотра.', reply_markup=inlinekeyboard, inline_message_id=call.inline_message_id)
# небольшой декор
async def on_startup(dp: Dispatcher):
    await bot.send_message(chat_id=admin_id, text='🚀 <b>Ваш Bot</b> успешно запущен!\nДля запуска бота введите <b>/start</b>')
    scheduler.add_job(update_news_films, 'cron', hour=11, minute=16)
    scheduler.add_job(update_news_serials, 'cron', hour=12, minute=29)
    scheduler.add_job(update_popular, 'cron', hour=1, minute=10)

#
if __name__ == "__main__":
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup)

