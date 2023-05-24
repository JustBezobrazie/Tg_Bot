'''В этом файле мы забираем нужное из бд, а также добавляем в неё фильмы и сериалы, при обновлении их списка '''

import sqlite3

class Sqliter:
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.db.cursor()

    def db_table_val(self, user_id, user_name, user_register):
        self.cursor.execute('INSERT INTO users (user_id, user_name, user_register) VALUES (?, ?, ?)', (user_id, user_name, user_register))
        self.db.commit()

    def update_domain(self, domain):
        self.cursor.execute("SELECT * FROM collections_films")
        collections_films = self.cursor.fetchall()
        print(len(collections_films))
        data = [(collections_film[1], collections_film[5].split('/embed/')[1]) for collections_film in collections_films if not collections_film[5].startswith(domain)]
        data = list(set(data))
        print(len(data))
        for collections_film in data:
            domain_url_l = collections_film[1]
            domain_url = domain+'/embed/'+domain_url_l
            self.update_iframe_url(collections_film[0], domain_url)
        self.cursor.execute("SELECT * FROM favorites")
        favorite_films = self.cursor.fetchall()
        data2 = [(favorite_film[0], favorite_film[5].split('/embed/')[1]) for favorite_film in favorite_films if not favorite_film[5].startswith(domain)]
        data2 = list(set(data2))
        print(len(data2))
        for favorite_film in data2:
            domain_url_l = favorite_film[1]
            domain_url = domain+'/embed/'+domain_url_l
            self.update_favorite_url(favorite_film[0], domain_url)

    def update_iframe_url(self,id, domain):
        self.cursor.execute("UPDATE collections_films SET url = ? WHERE id = ?", (domain, id))
        self.db.commit()

    def update_favorite_url(self,id, domain):
        self.cursor.execute("UPDATE favorites SET url = ? WHERE film_id = ?", (domain, id))
        self.db.commit()

    def get_films(self, collection_id: int):
        self.cursor.execute("SELECT * FROM collections_films WHERE collection_id = ?", (collection_id,))
        collections_films = self.cursor.fetchall()
        return collections_films

    def get_film_by_id(self, film_id: int):
        self.cursor.execute("SELECT * FROM collections_films WHERE id = ?", (film_id,))
        first_film = self.cursor.fetchall()
        return first_film

    def add_film(self, data: list):
        self.cursor.execute('INSERT INTO collections_films (collection_id, id, name, genre, date, url, poster, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', data)
        self.db.commit()

    def get_users_day_reg(self, date):
        self.cursor.execute(f"SELECT user_id FROM users WHERE user_register = ?", (date,))
        result = self.cursor.fetchall()
        return len(result)

    def get_favorites(self, user_id):
        self.cursor.execute(f"SELECT * FROM favorites WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchall()
        return result

    def add_favorite(self, data: list):
        self.cursor.execute('INSERT INTO favorites (film_id, user_id, name, date, genre, url, poster, type) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', data)
        self.db.commit()

    def del_favorite(self, film_id):
        self.cursor.execute('DELETE FROM favorites WHERE film_id = ?', (film_id,))
        self.db.commit()
