import psycopg2
from DB.database_connection import Database


def send_messages_to_user(bot, chat_id):
    with Database() as db:
        try:
            db.execute("SELECT * FROM worldBoxNew WHERE date_added = CURRENT_DATE")
            worldbox_new = db.fetchall()
        except(Exception, psycopg2.Error) as error:
            print('Error:', error)
        for data in worldbox_new:
            new_sneakers = f'WorldBox - New\n{data[1]}\nРазмеры EU: {data[2]}\nЦена: {data[3]}\n{data[4]}'
            bot.send_message(chat_id, new_sneakers)
    with Database() as db:
        try:
            db.execute("SELECT * FROM worldBoxSale WHERE date_added = CURRENT_DATE")
            worldbox_sale = db.fetchall()
        except(Exception, psycopg2.Error) as error:
            print('Error:', error)
        for data in worldbox_sale:
            sale_sneakers = f'WorldBox - Sale\n{data[1]}\nРазмеры EU: {data[2]}\nЦена: {data[3]}\n{data[4]}'
            bot.send_message(chat_id, sale_sneakers)
