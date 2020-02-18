import requests
from bs4 import BeautifulSoup as bs
import psycopg2

connection = psycopg2.connect(dbname='rlkrficv', user='rlkrficv',
                              password='iMVbx_wb98BoIJCdR26L4Ki3wOBlSwxq',
                              host='rajje.db.elephantsql.com')

list_for_id_site = []


class worldBox:
    def __init__(self, link, category, headers):
        self.link = link
        self.category = category
        self.headers = headers
        self.connection = connection
        self.cursor = self.connection.cursor()

    def findInappropriatePartNumbers(self, all_id):
        list_for_id_database = []

        if self.category == 'New':
            try:
                self.cursor.execute("SELECT id_product FROM worldBoxNew")
                result = self.cursor.fetchall()
                all_result_from_db = [list(i) for i in result]
                for items in all_result_from_db:
                    for item in items:
                        list_for_id_database.append(item)
            except (Exception, psycopg2.Error) as error:
                print('Error:', error)
        elif self.category == 'Sale':
            try:
                self.cursor.execute("SELECT id_product FROM worldBoxSale")
                result = self.cursor.fetchall()
                all_result_from_db = [list(i) for i in result]
                for items in all_result_from_db:
                    for item in items:
                        list_for_id_database.append(item)
            except (Exception, psycopg2.Error) as error:
                print('Error:', error)
        else:
            print('Not found')

        return list(set(list_for_id_database) - set(all_id))

    def worldBox_parser(self):
        global list_for_id_site
        list_for_id_site.clear()
        product_size = []
        self.connection.autocommit = True
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

                product_request = session.get(href, headers=self.headers)

                if product_request.status_code == 200:
                    product_soup = bs(product_request.content, 'html.parser')
                    span = product_soup.find_all('span', attrs={'class': 'size_box'})
                    id_product = product_soup.find('h3', attrs={'class': 'product__code'}).find_next().text

                    product_size.clear()
                    for size_span in span:
                        for size in size_span:
                            product_size.append(size)

                list_for_id_site.append(id_product)
                title_without_qm = title.replace("'", "")

                if self.category == 'New':
                    try:
                        self.cursor.execute(
                            f"INSERT INTO worldBoxNew VALUES ('{id_product}', '{title_without_qm}', "
                            f"'{', '.join(product_size)}', '{price}', '{href}', "
                            f"CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING")
                        print(f'{id_product} has been added')
                    except (Exception, psycopg2.Error) as error:
                        print('Error:', error)
                elif self.category == 'Sale':
                    try:
                        self.cursor.execute(
                            f"INSERT INTO worldBoxSale VALUES ('{id_product}', '{title_without_qm}', "
                            f"'{', '.join(product_size)}', '{price}', '{href}', "
                            f"CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING")
                        print(f'{id_product} has been added')
                    except (Exception, psycopg2.Error) as error:
                        print('Error:', error)
                else:
                    print('Not found')

        # answer = 'Worldbox \n{0} \n{1} \n{2} \nРазмеры EU: {3}\n{4}'.format(category, href, title,
        #                                                                     ', '.join(product_size),
        #                                                                     price)
        # bot.send_message(chat_id, answer)

    def deleteInappropriatePartNumbers(self):
        global list_for_id_site
        print(self.findInappropriatePartNumbers(list_for_id_site))
        if self.category == 'New':
            try:
                if self.findInappropriatePartNumbers(list_for_id_site):
                    self.cursor.execute("DELETE FROM worldBoxNew WHERE id_product in ({0})".format(', '.join(
                        "'{0}'".format(id_product) for id_product in
                        self.findInappropriatePartNumbers(list_for_id_site))))
                else:
                    print("List is empty")
            except (Exception, psycopg2.Error) as error:
                print('Error:', error)
        elif self.category == 'Sale':
            try:
                if self.findInappropriatePartNumbers(list_for_id_site):
                    self.cursor.execute("DELETE FROM worldBoxSale WHERE id_product in ({0})".format(', '.join(
                        "'{0}'".format(id_product) for id_product in
                        self.findInappropriatePartNumbers(list_for_id_site))))
                else:
                    print("List is empty")
            except (Exception, psycopg2.Error) as error:
                print('Error:', error)
        else:
            print('Not found')

    def __del__(self):
        self.cursor.close()
        self.connection.close()
