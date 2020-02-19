import requests
from bs4 import BeautifulSoup as bs
import psycopg2
from DB.database_connection import Database


class WorldBox(object):
    list_for_id_site = []

    def __init__(self, link, category, headers, bot, chat_id):
        self.link = link
        self.category = category
        self.headers = headers
        self.bot = bot
        self.chat_id = chat_id

    def find_inappropriate_part_numbers(self, all_id):
        list_for_id_database = []

        if self.category == 'New':
            with Database() as db:
                try:
                    db.execute("SELECT id_product FROM worldBoxNew")
                    result = db.fetchall()
                except (Exception, psycopg2.Error) as error:
                    print('Error:', error)
            all_result_from_db = [list(i) for i in result]
            for items in all_result_from_db:
                for item in items:
                    list_for_id_database.append(item)
        elif self.category == 'Sale':
            with Database() as db:
                try:
                    db.execute("SELECT id_product FROM worldBoxSale")
                    result = db.fetchall()
                except (Exception, psycopg2.Error) as error:
                    print('Error:', error)
            all_result_from_db = [list(i) for i in result]
            for items in all_result_from_db:
                for item in items:
                    list_for_id_database.append(item)
        else:
            print('Not found')

        return list(set(list_for_id_database) - set(all_id))

    def worldbox_parser(self):
        self.list_for_id_site.clear()
        product_size = []
        session = requests.Session()

        product_list_request = session.get(self.link, headers=self.headers)

        if product_list_request.status_code == 200:
            product_list_soup = bs(product_list_request.content, 'html.parser')
            divs = product_list_soup.find_all('div', attrs={'class': 'block__flags product col-sm-6 col-md-4 col-xs-6'})

            for div in divs:
                product = div.find_all('a')

                for link_of_product in product:
                    href = link_of_product.get('href')

                price = div.find('span', attrs={'class': 'price-tag'}).find_next().text
                title = div.find('p').text

                product_request = session.get(href, headers=self.headers, allow_redirects=False)

                if product_request.status_code == 200:
                    product_soup = bs(product_request.content, 'html.parser')
                    span = product_soup.find_all('span', attrs={'class': 'size_box'})
                    id_product = product_soup.find('h3', attrs={'class': 'product__code'}).find_next().text

                    product_size.clear()
                    for size_span in span:
                        for size in size_span:
                            product_size.append(size)

                correct_id_product = id_product.replace("-", "‑")
                self.list_for_id_site.append(correct_id_product)
                title_without_qm = title.replace("'", "")

                if self.category == 'New':
                    with Database() as db:
                        try:
                            db.execute(
                                f"INSERT INTO worldBoxNew VALUES ('{correct_id_product}', '{title_without_qm}', "
                                f"'{', '.join(product_size)}', '{price}', '{href}', "
                                f"CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING")
                        except (Exception, psycopg2.Error) as error:
                            print('Error:', error)
                    print(f'{correct_id_product} has been added')
                elif self.category == 'Sale':
                    with Database() as db:
                        try:
                            db.execute(
                                f"INSERT INTO worldBoxSale VALUES ('{correct_id_product}', '{title_without_qm}', "
                                f"'{', '.join(product_size)}', '{price}', '{href}', "
                                f"CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING")
                        except (Exception, psycopg2.Error) as error:
                            print('Error:', error)
                    print(f'{correct_id_product} has been added')
                else:
                    print('Not found')

    def delete_inappropriate_part_numbers(self):
        print(self.find_inappropriate_part_numbers(self.list_for_id_site))
        if self.category == 'New':
            if self.find_inappropriate_part_numbers(self.list_for_id_site):
                with Database() as db:
                    try:
                        db.execute("DELETE FROM worldBoxNew WHERE id_product in ({0})".format(', '.join(
                            "'{0}'".format(id_product) for id_product in
                            self.find_inappropriate_part_numbers(self.list_for_id_site))))
                    except (Exception, psycopg2.Error) as error:
                        print('Error:', error)
            else:
                print("List is empty")
        elif self.category == 'Sale':
            if self.find_inappropriate_part_numbers(self.list_for_id_site):
                with Database() as db:
                    try:
                        db.execute("DELETE FROM worldBoxSale WHERE id_product in ({0})".format(', '.join(
                            "'{0}'".format(id_product) for id_product in
                            self.find_inappropriate_part_numbers(self.list_for_id_site))))
                    except (Exception, psycopg2.Error) as error:
                        print('Error:', error)
            else:
                print("List is empty")
        else:
            print('Not found')

    def send_messages_to_user(self):
        with Database() as db:
            try:
                db.execute("SELECT * FROM worldBoxNew WHERE date_added = '2020-02-19'")
                worldbox_new = db.fetchall()
            except(Exception, psycopg2.Error) as error:
                print('Error:', error)
            for data in worldbox_new:
                new_sneakers = f'WorldBox - New\n{data[1]}\nРазмеры EU: {data[2]}\nЦена: {data[3]}\n{data[4]}'
                self.bot.send_message(self.chat_id, new_sneakers)
        with Database() as db:
            try:
                db.execute("SELECT * FROM worldBoxSale WHERE date_added = '2020-02-19'")
                worldbox_sale = db.fetchall()
            except(Exception, psycopg2.Error) as error:
                print('Error:', error)
            for data in worldbox_sale:
                sale_sneakers = f'WorldBox - Sale\n{data[1]}\nРазмеры EU: {data[2]}\nЦена: {data[3]}\n{data[4]}'
                self.bot.send_message(self.chat_id, sale_sneakers)
