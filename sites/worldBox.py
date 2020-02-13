import requests
from bs4 import BeautifulSoup as bs


class worldBox:
    def worldBox_parseSale(self, headers, bot, chat_id):
        span_for_product = []
        session = requests.Session()
        first_request = session.get(self, headers=headers)

        if first_request.status_code == 200:
            first_soup = bs(first_request.content, 'html.parser')
            divs = first_soup.find_all('div', attrs={'class': 'block__flags product col-sm-6 col-md-4 col-xs-6'})

            for div in divs:
                product = div.find_all('a')

                for link_of_product in product:
                    href = link_of_product.get('href')

                list_of_img = div.find_all('img')
                price = div.find('span', attrs={'class': 'price-tag'}).text
                title = div.find('p').text

                for first_pic in list_of_img:
                    img = first_pic.get('data-echo')

                second_request = session.get(href, headers=headers)

                if second_request.status_code == 200:
                    second_soup = bs(second_request.content, 'html.parser')
                    li = second_soup.find_all('span', attrs={'class': 'size_box'})

                    for size_span in li:
                        for span in size_span:
                            span_for_product.append(span)

                answer = "Worldbox \nSale \n{0} \n{1} \n{2}\n{3}".format(title, img, span_for_product, price)

                bot.send_message(chat_id, answer)

    def worldBox_parseNew(self, headers, bot, chat_id):
        span_for_product = []
        session = requests.Session()
        first_request = session.get(self, headers=headers)

        if first_request.status_code == 200:
            first_soup = bs(first_request.content, 'html.parser')
            divs = first_soup.find_all('div', attrs={'class': 'block__flags product col-sm-6 col-md-4 col-xs-6'})

            for div in divs:
                product = div.find_all('a')

                for link_of_product in product:
                    href = link_of_product.get('href')

                list_of_img = div.find_all('img')
                price = div.find('span', attrs={'class': 'price-tag'}).text
                title = div.find('p').text

                for first_pic in list_of_img:
                    img = first_pic.get('data-echo')

                second_request = session.get(href, headers=headers)

                if second_request.status_code == 200:
                    second_soup = bs(second_request.content, 'html.parser')
                    li = second_soup.find_all('span', attrs={'class': 'size_box'})

                    for size_span in li:
                        for span in size_span:
                            span_for_product.append(span)

                answer = "Worldbox \nNew \n{0} \n{1} \n{2}\n{3}".format(title, img, span_for_product, price)

                bot.send_message(chat_id, answer)
