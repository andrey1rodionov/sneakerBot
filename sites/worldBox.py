import requests
from bs4 import BeautifulSoup as bs
import psycopg2

connection = psycopg2.connect(dbname='rlkrficv', user='rlkrficv',
                              password='iMVbx_wb98BoIJCdR26L4Ki3wOBlSwxq',
                              host='rajje.db.elephantsql.com')


def inappropriatePartNumbers(list_for_id_site, type_of_section):
    global connection
    list_for_id_database = []
    cursor = connection.cursor()

    if type_of_section == 'New':
        try:
            cursor.execute("SELECT id_product FROM worldBoxNew")
            result = cursor.fetchall()
            all_result_from_db = [list(i) for i in result]
            for items in all_result_from_db:
                for item in items:
                    list_for_id_database.append(item)
        except (Exception, psycopg2.Error) as error:
            print('Error: ', error)
    elif type_of_section == 'Sale':
        try:
            cursor.execute("SELECT id_product FROM worldBoxSale")
            result = cursor.fetchall()
            all_result_from_db = [list(i) for i in result]
            for items in all_result_from_db:
                for item in items:
                    list_for_id_database.append(item)
        except (Exception, psycopg2.Error) as error:
            print('Error: ', error)
    else:
        print('Not found')

    cursor.close()
    # connection.close()

    return list(set(list_for_id_database) - set(list_for_id_site))


def worldBox_parser(self, category, headers, bot, chat_id):
    global connection
    list_for_id_site = []
    span_for_product = []
    connection.autocommit = True
    cursor = connection.cursor()
    session = requests.Session()
    product_list_request = session.get(self, headers=headers)

    if product_list_request.status_code == 200:
        product_list_soup = bs(product_list_request.content, 'html.parser')
        divs = product_list_soup.find_all('div', attrs={'class': 'block__flags product col-sm-6 col-md-4 col-xs-6'})

        for div in divs:
            product = div.find_all('a')

            for link_of_product in product:
                href = link_of_product.get('href')

            price = div.find('span', attrs={'class': 'price-tag'}).text
            title = div.find('p').text

            product_request = session.get(href, headers=headers)

            if product_request.status_code == 200:
                product_soup = bs(product_request.content, 'html.parser')
                span = product_soup.find_all('span', attrs={'class': 'size_box'})
                id_product = product_soup.find('h3', attrs={'class': 'product__code'}).find_next().text

                span_for_product.clear()
                for size_span in span:
                    for size in size_span:
                        span_for_product.append(size)

            list_for_id_site.append(id_product)
            title_without_qm = title.replace("'", "")
            if category == 'New':
                try:
                    cursor.execute(
                        f"INSERT INTO worldBoxNew VALUES ('{id_product}', '{title_without_qm}', "
                        f"'{', '.join(span_for_product)}', '{price}', '{href}', "
                        f"CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING")
                    print(f'{id_product} has been added')
                except (Exception, psycopg2.Error) as error:
                    print('Error: ', error)
            elif category == 'Sale':
                try:
                    cursor.execute(
                        f"INSERT INTO worldBoxSale VALUES ('{id_product}', '{title_without_qm}', "
                        f"'{', '.join(span_for_product)}', '{price}', '{href}', "
                        f"CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING")
                    print(f'{id_product} has been added')
                except (Exception, psycopg2.Error) as error:
                    print('Error: ', error)
            else:
                print('Not found')

    print(inappropriatePartNumbers(list_for_id_site, category))

    cursor.close()
    connection.close()

    # answer = 'Worldbox \n{0} \n{1} \n{2} \nРазмеры EU: {3}\n{4}'.format(category, href, title,
    #                                                                     ', '.join(span_for_product),
    #                                                                     price)
    #
    # bot.send_message(chat_id, answer)
