import requests
from bs4 import BeautifulSoup as bs
import psycopg2


class worldBox:
    def worldBox_parser(self, category, headers, bot, chat_id):
        connection = psycopg2.connect(dbname='rlkrficv', user='rlkrficv',
                                      password='iMVbx_wb98BoIJCdR26L4Ki3wOBlSwxq',
                                      host='rajje.db.elephantsql.com')
        connection.autocommit = True
        cursor = connection.cursor()
        span_for_product = []
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

                try:
                    cursor.execute(
                        f"INSERT INTO worldBoxNew VALUES (default, '{id_product}', '{title}', '{', '.join(span_for_product)}', '{price}', '{href}')")
                    print(f'{id_product} has been added')
                except (Exception, psycopg2.Error) as error:
                    print('Error: ', error)

                # answer = 'Worldbox \n{0} \n{1} \n{2} \nРазмеры EU: {3}\n{4}'.format(category, href, title,
                #                                                                     ', '.join(span_for_product),
                #                                                                     price)
                #
                # bot.send_message(chat_id, answer)

        cursor.close()
        connection.close()
