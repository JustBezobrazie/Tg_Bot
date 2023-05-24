from typing import List, Union                  # встроенные клавиатуры
import operator

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
'''В этом файле создаётся класс, отвечающий за перелестывание фильмов, сериалов. Также здесь создана функция 
добавления в сохранённые фильмов и сериалов. Посмотрев на название файла, можно добавить, что мы пронумеровываем страницы
при их пролистывании.
p.s. тут было очень много ошибок ;/'''

class InlinePagination:
    def __init__(self, button_datas: list, func_name=operator.itemgetter(1),
                 func_callback=operator.itemgetter(0),
                 callback_prefix="item_", width: int = 2, height: int = 5,
                 back_button: str = "⏪", next_button: str = "⏩", back_prefix="b_", next_prefix="n_",
                 page_prefix="p_", page_button: str = "{cur_page}/{all_pages}"):
        self.button_datas = button_datas
        self.func_name = func_name
        self.func_callback = func_callback
        self.callback_prefix = callback_prefix
        self.back_prefix = back_prefix
        self.next_prefix = next_prefix
        self.page_prefix = page_prefix
        self.width = width
        self.height = height
        self.back_button = back_button
        self.next_button = next_button
        self.page_button = page_button

        if width > 3:
            self.kb = InlineKeyboardMarkup(row_width=width)
        else:
            self.kb = InlineKeyboardMarkup(row_width=3)

    def get_page_data(self, cur_page: int) -> list:
        return self.button_datas[
               (cur_page - 1) * self.width * self.height: self.width * self.height * cur_page
               ]

    def get_page_buttons(self, page_data: list) -> List[InlineKeyboardButton]:
        return [
            InlineKeyboardButton(callback_data=self.callback_prefix + str(self.func_name(data)), text=self.func_callback(data))
            for data in page_data
        ]

    def get_page_info_buttons(self, cur_page: int) -> List[InlineKeyboardButton]:
        if len(self.button_datas) % (self.width * self.height) == 0:
            all_pages = len(self.button_datas) // (self.width * self.height)
        else:
            all_pages = len(self.button_datas) // (self.width * self.height) + 1

        page_button = InlineKeyboardButton(
            callback_data=self.page_prefix + str(cur_page),
            text=self.page_button.format(cur_page=cur_page,
                                         all_pages=all_pages)
        )
        if all_pages == 1:
            return [page_button]
        if cur_page == all_pages:
            back_button = InlineKeyboardButton(
                callback_data=self.back_prefix + str(cur_page - 1), text=self.back_button
            )
            return [back_button, page_button]
        elif cur_page == 1:
            next_button = InlineKeyboardButton(
                callback_data=self.next_prefix + str(cur_page + 1), text=self.next_button
            )
            return [page_button, next_button]
        else:
            next_button = InlineKeyboardButton(
                callback_data=self.next_prefix + str(cur_page + 1), text=self.next_button
            )
            back_button = InlineKeyboardButton(
                callback_data=self.back_prefix + str(cur_page - 1), text=self.back_button
            )
            return [back_button, page_button, next_button]

    def get_page_keyboard(self, cur_page: Union[int, str]):
        cur_page = self.format_page(cur_page)
        page_data = self.get_page_data(cur_page)
        page_buttons = self.get_page_buttons(page_data)
        info_page_buttons = self.get_page_info_buttons(cur_page)
        for btns in self.grouped(page_buttons, self.width):
            self.kb.add(*btns)
        self.kb.row(*info_page_buttons)
        self.kb.row(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back"))
        return self.kb

    @staticmethod
    def grouped(data: list, n: int):
        items = list(zip(*[iter(data)] * n))
        if len(data) % n:
            items.append(tuple(data[(len(data) % n) * -1:]))
            return items
        return items

    def format_page(self, cur_page: Union[int, str]):
        if isinstance(cur_page, str):
            return int(cur_page.split(self.next_prefix)[-1]) if cur_page.startswith(
                self.next_prefix) else int(cur_page.split(self.back_prefix)[-1])
        return cur_page

class InlinePagination2:
    def __init__(self, films: list, func_name=operator.itemgetter(1),
                 func_callback=operator.itemgetter(0),
                 callback_prefix="item_", width: int = 2, height: int = 5,
                 back_button: str = "⏪", next_button: str = "⏩", back_prefix="b2_", next_prefix="n2_",
                 page_prefix="p2_", page_button: str = "{cur_page}/{all_pages}"):
        self.films = films
        self.func_name = func_name
        self.func_callback = func_callback
        self.callback_prefix = callback_prefix
        self.back_prefix = back_prefix
        self.next_prefix = next_prefix
        self.page_prefix = page_prefix
        self.width = width
        self.height = height
        self.back_button = back_button
        self.next_button = next_button
        self.page_button = page_button

        if width > 3:
            self.kb = InlineKeyboardMarkup(row_width=width)
        else:
            self.kb = InlineKeyboardMarkup(row_width=3)

    def get_page_data(self, cur_page: int) -> list:
        return self.button_datas[
               (cur_page - 1) * self.width * self.height: self.width * self.height * cur_page
               ]

    def get_page_buttons(self, page_data: list) -> List[InlineKeyboardButton]:
        return [
            InlineKeyboardButton(callback_data=self.callback_prefix + str(self.func_name(data)), text=self.func_callback(data))
            for data in page_data
        ]

    def get_page_info_buttons(self, cur_page: int, collection_id: int) -> List[InlineKeyboardButton]:
        all_pages = len(self.films)

        page_button = InlineKeyboardButton(
            callback_data=self.page_prefix + str(cur_page),
            text=self.page_button.format(cur_page=cur_page,
                                         all_pages=all_pages)
        )
        if all_pages == 1:
            return [page_button]
        if cur_page == all_pages:
            back_button = InlineKeyboardButton(
                callback_data= f"{self.back_prefix}{collection_id}_" + str(cur_page - 1), text=self.back_button
            )
            return [back_button, page_button]
        elif cur_page == 1:
            next_button = InlineKeyboardButton(
                callback_data=f"{self.next_prefix}{collection_id}_" + str(cur_page + 1), text=self.next_button
            )
            return [page_button, next_button]
        else:
            next_button = InlineKeyboardButton(
                callback_data=f"{self.next_prefix}{collection_id}_" + str(cur_page + 1), text=self.next_button
            )
            back_button = InlineKeyboardButton(
                callback_data=f"{self.back_prefix}{collection_id}_" + str(cur_page - 1), text=self.back_button
            )
            return [back_button, page_button, next_button]

    def get_page_keyboard(self, cur_page: Union[int, str], collection_id: int, fave_status: bool):

        cur_page = self.format_page(cur_page)
        info_page_buttons = self.get_page_info_buttons(cur_page, collection_id)
        film_id = self.films[cur_page-1][1]
        if fave_status:
            self.kb.row(InlineKeyboardButton(text="❌ Удалить из ❤️Сохранённых", callback_data=f'del_favorite|{film_id}'))
        else:
            self.kb.row(InlineKeyboardButton(text="➕ Добавить в ❤️Сохранённые", callback_data=f'add_favorite|{film_id}'))
        self.kb.row(*info_page_buttons)
        return self.kb

    @staticmethod
    def grouped(data: list, n: int):
        items = list(zip(*[iter(data)] * n))
        if len(data) % n:
            items.append(tuple(data[(len(data) % n) * -1:]))
            return items
        return items

    def format_page(self, cur_page: Union[int, str]):
        if isinstance(cur_page, str):
            return int(cur_page.split(self.next_prefix)[1].split('_')[-1]) if cur_page.startswith(
                self.next_prefix) else int(cur_page.split(self.back_prefix)[1].split('_')[-1])
        return cur_page

class FavoritesPagination:
    def __init__(self, films: list, func_name=operator.itemgetter(1),
                 func_callback=operator.itemgetter(0),
                 callback_prefix="item_", width: int = 2, height: int = 5,
                 back_button: str = "⏪", next_button: str = "⏩", back_prefix="faveback_", next_prefix="favenext_",
                 page_prefix="p3_", page_button: str = "{cur_page}/{all_pages}"):
        self.films = films
        self.func_name = func_name
        self.func_callback = func_callback
        self.callback_prefix = callback_prefix
        self.back_prefix = back_prefix
        self.next_prefix = next_prefix
        self.page_prefix = page_prefix
        self.width = width
        self.height = height
        self.back_button = back_button
        self.next_button = next_button
        self.page_button = page_button

        if width > 3:
            self.kb = InlineKeyboardMarkup(row_width=width)
        else:
            self.kb = InlineKeyboardMarkup(row_width=3)

    def get_page_data(self, cur_page: int) -> list:
        return self.button_datas[
               (cur_page - 1) * self.width * self.height: self.width * self.height * cur_page
               ]

    def get_page_buttons(self, page_data: list) -> List[InlineKeyboardButton]:
        return [
            InlineKeyboardButton(callback_data=self.callback_prefix + str(self.func_name(data)), text=self.func_callback(data))
            for data in page_data
        ]

    def get_page_info_buttons(self, cur_page: int) -> List[InlineKeyboardButton]:
        all_pages = len(self.films)

        page_button = InlineKeyboardButton(
            callback_data=self.page_prefix + str(cur_page),
            text=self.page_button.format(cur_page=cur_page,
                                         all_pages=all_pages)
        )
        if all_pages == 1:
            return [page_button]
        if cur_page == all_pages:
            back_button = InlineKeyboardButton(
                callback_data= f"{self.back_prefix}" + str(cur_page - 1), text=self.back_button
            )
            return [back_button, page_button]
        elif cur_page == 1:
            next_button = InlineKeyboardButton(
                callback_data=f"{self.next_prefix}" + str(cur_page + 1), text=self.next_button
            )
            return [page_button, next_button]
        else:
            next_button = InlineKeyboardButton(
                callback_data=f"{self.next_prefix}" + str(cur_page + 1), text=self.next_button
            )
            back_button = InlineKeyboardButton(
                callback_data=f"{self.back_prefix}" + str(cur_page - 1), text=self.back_button
            )
            return [back_button, page_button, next_button]

    def get_page_keyboard(self, cur_page: Union[int, str]):

        cur_page = self.format_page(cur_page)
        info_page_buttons = self.get_page_info_buttons(cur_page)
        film_id = self.films[cur_page-1][0]

        self.kb.row(InlineKeyboardButton(text="❌ Удалить из закладок", callback_data=f'del_favorite|{film_id}'))
        self.kb.row(*info_page_buttons)
        self.kb.row(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back"))
        return self.kb

    @staticmethod
    def grouped(data: list, n: int):
        items = list(zip(*[iter(data)] * n))
        if len(data) % n:
            items.append(tuple(data[(len(data) % n) * -1:]))
            return items
        return items

    def format_page(self, cur_page: Union[int, str]):
        if isinstance(cur_page, str):
            return int(cur_page.split(self.next_prefix)[-1]) if cur_page.startswith(
                self.next_prefix) else int(cur_page.split(self.back_prefix)[-1])
        return cur_page

class NewsPagination:
    def __init__(self, films: list, func_name=operator.itemgetter(1),
                 func_callback=operator.itemgetter(0),
                 callback_prefix="newsitem_", width: int = 2, height: int = 5,
                 back_button: str = "⏪", next_button: str = "⏩", back_prefix="newsback_", next_prefix="newsnext_",
                 page_prefix="p3_", page_button: str = "{cur_page}/{all_pages}"):
        self.films = films

        self.func_name = func_name
        self.func_callback = func_callback

        self.callback_prefix = callback_prefix
        self.back_prefix = back_prefix
        self.next_prefix = next_prefix
        self.page_prefix = page_prefix

        self.width = width
        self.height = height

        self.back_button = back_button
        self.next_button = next_button
        self.page_button = page_button

        if width > 3:
            self.kb = InlineKeyboardMarkup(row_width=width)
        else:
            self.kb = InlineKeyboardMarkup(row_width=3)

    def get_page_data(self, cur_page: int) -> list:
        return self.button_datas[
               (cur_page - 1) * self.width * self.height: self.width * self.height * cur_page
               ]

    def get_page_buttons(self, page_data: list) -> List[InlineKeyboardButton]:
        return [
            InlineKeyboardButton(callback_data=self.callback_prefix + str(self.func_name(data)), text=self.func_callback(data))
            for data in page_data
        ]

    def get_page_info_buttons(self, cur_page: int) -> List[InlineKeyboardButton]:
        all_pages = len(self.films)

        page_button = InlineKeyboardButton(
            callback_data=self.page_prefix + str(cur_page),
            text=self.page_button.format(cur_page=cur_page,
                                         all_pages=all_pages)
        )
        if all_pages == 1:
            return [page_button]
        if cur_page == all_pages:
            back_button = InlineKeyboardButton(
                callback_data= f"{self.back_prefix}" + str(cur_page - 1), text=self.back_button
            )
            return [back_button, page_button]
        elif cur_page == 1:
            next_button = InlineKeyboardButton(
                callback_data=f"{self.next_prefix}" + str(cur_page + 1), text=self.next_button
            )
            return [page_button, next_button]
        else:
            next_button = InlineKeyboardButton(
                callback_data=f"{self.next_prefix}" + str(cur_page + 1), text=self.next_button
            )
            back_button = InlineKeyboardButton(
                callback_data=f"{self.back_prefix}" + str(cur_page - 1), text=self.back_button
            )
            return [back_button, page_button, next_button]

    def get_page_keyboard(self, cur_page: Union[int, str], fave_status: bool):

        cur_page = self.format_page(cur_page)
        info_page_buttons = self.get_page_info_buttons(cur_page)
        film_id = self.films[cur_page-1]["id"]


        if fave_status:
            self.kb.row(InlineKeyboardButton(text="❌ Удалить из сохранённых", callback_data=f'del_favorite|{film_id}'))
        else:
            self.kb.row(InlineKeyboardButton(text="➕ Добавить в сохранённые", callback_data=f'add_favorite|{film_id}'))
        self.kb.row(*info_page_buttons)
        self.kb.row(InlineKeyboardButton(text="◀️ Назад в меню", callback_data="back"))
        return self.kb

    @staticmethod
    def grouped(data: list, n: int):
        items = list(zip(*[iter(data)] * n))
        if len(data) % n:
            items.append(tuple(data[(len(data) % n) * -1:]))
            return items
        return items

    def format_page(self, cur_page: Union[int, str]):
        if isinstance(cur_page, str):
            return int(cur_page.split(self.next_prefix)[-1]) if cur_page.startswith(
                self.next_prefix) else int(cur_page.split(self.back_prefix)[-1])
        return cur_page
