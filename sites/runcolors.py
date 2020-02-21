import requests
from bs4 import BeautifulSoup as bs
import psycopg2
from DB.database_connection import Database


class RunColors:
    list_for_id_site = []

    def __init__(self, link, category, headers):
        self.link = link
        self.category = category
        self.headers = headers

    def get_count_of_pages(self):
        session = requests.Session()
        if self.category == 'New':
            request = session.get(self.link + '1', headers=self.headers)
            soup = bs(request.content, 'html.parser')
            navigation = soup.find('div', attrs={'class': 'navigation'})
            count_of_pages = navigation.find_all('a')[-2].get_text()
            return int(count_of_pages)
        if self.category == 'Sale':
            request = session.get(self.link + '1', headers=self.headers)
            soup = bs(request.content, 'html.parser')
            navigation = soup.find('div', attrs={'class': 'navigation'})
            count_of_pages = navigation.find_all('a')[-2].get_text()
            return int(count_of_pages)

    def find_inappropriate_part_numbers(self, all_id):
        list_for_id_database = []
        if self.category == 'New':
            with Database() as db:
                try:
                    db.execute("SELECT id_product FROM runColorsNew")
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
                    db.execute("SELECT id_product FROM runColorsSale")
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

    def runcolors_parser(self):
        self.list_for_id_site.clear()
        product_size = []
        session = requests.Session()

        for page in range(1, self.get_count_of_pages()):
            product_list_request = session.get(self.link + str(page), headers=self.headers)

            if product_list_request.status_code == 200:
                product_list_soup = bs(product_list_request.content, 'html.parser')
                divs = product_list_soup.find_all('li', attrs={'class': 'pList__item'})

                with Database() as db:
                    for div in divs:
                        product = div.find_all('a')

                        for link_of_product in product:
                            href = link_of_product.get('href')

                        span = div.find_all('div',
                                            attrs={'class': 'pList__item_big__variants--item js--variant--item'})
                        img = div.find('img', attrs={'class': 'pList__picture__img'}).get('src')

                        full_link_of_product = f'https://runcolors.pl{href}'

                        product_request = session.get(full_link_of_product, headers=self.headers)

                        if product_request.status_code == 200:
                            product_soup = bs(product_request.content, 'html.parser')
                            section_check = product_soup.find('li', attrs={'class': 'first'}).find('a').text

                            if section_check == 'SNEAKERS':
                                title = product_soup.find('h1', attrs={'class': 'product__header__name'}).text
                                id_product = product_soup.find('span', attrs={'class': 'product__data__content'}).text
                                price = product_soup.find('p', attrs={'class': 'product__data__price__regular'}).text

                                product_size.clear()
                                for size_span in span:
                                    for size in size_span:
                                        product_size.append(size)

                                title_without_qm = title.replace("'", "")
                                self.list_for_id_site.append(id_product)

                                if 'New Balance' not in title_without_qm:
                                    if self.category == 'New':
                                        try:
                                            db.execute(
                                                f"INSERT INTO runColorsNew VALUES ('{id_product}', '"
                                                f"{title_without_qm}', "
                                                f"'{', '.join(product_size)}', '{price.strip()}', "
                                                f"'{full_link_of_product}', "
                                                f"'{img}', "f"CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING")
                                        except (Exception, psycopg2.Error) as error:
                                            print('Error:', error)
                                        print(f'{id_product} has been added')
                                    elif self.category == 'Sale':
                                        try:
                                            db.execute(
                                                f"INSERT INTO runColorsSale VALUES ('{id_product}', '"
                                                f"{title_without_qm}', "
                                                f"'{', '.join(product_size)}', '{price.strip()}', "
                                                f"'{full_link_of_product}', "
                                                f"'{img}', "f"CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING")
                                        except (Exception, psycopg2.Error) as error:
                                            print('Error:', error)
                                        print(f'{id_product} has been added')
                                    else:
                                        print('Not found')

    def delete_inappropriate_part_numbers(self):
        print(self.find_inappropriate_part_numbers(self.list_for_id_site))
        if self.category == 'New':
            if self.find_inappropriate_part_numbers(self.list_for_id_site):
                with Database() as db:
                    try:
                        db.execute("DELETE FROM runColorsNew WHERE id_product in ({0})".format(', '.join(
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
                        db.execute("DELETE FROM runColorsSale WHERE id_product in ({0})".format(', '.join(
                            "'{0}'".format(id_product) for id_product in
                            self.find_inappropriate_part_numbers(self.list_for_id_site))))
                    except (Exception, psycopg2.Error) as error:
                        print('Error:', error)
            else:
                print("List is empty")
        else:
            print('Not found')
