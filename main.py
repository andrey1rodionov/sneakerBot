import telebot

import sites.worldBox as worldBox

bot = telebot.TeleBot("1098441995:AAGqy3iBI9ODvcIaGW3isg3BrSJe60wBU1I")

headers = {"accept": "*/*",
           "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36"}

update = bot.get_updates()
print(update)

last_update = update[-1]
message_from_user = last_update.message

print(message_from_user)
print(bot.get_me())


# bot.send_message(414407353, "Test message")


def log(message):
    print("\n -----")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1}. (id = {2}) \n Текст = {3}".format(message.from_user.first_name,
                                                                   message.from_user.last_name,
                                                                   str(message.from_user.id),
                                                                   message.text))


@bot.message_handler(commands=['start'])
def handle_text(message):
    answer = "Начало положено"
    log(message)
    bot.send_message(message.chat.id, answer)


@bot.message_handler(commands=['worldbox'])
def handle_text(message):
    log(message)
    wb = worldBox.worldBox
    # wb.worldBox_parseSale("https://worldbox.pl/products/obuwie-ostatnie-sztuki/category,2/flag,8/item,24?", headers,
    #                       # bot, message.chat.id)
    wb.worldBox_parseNew("https://worldbox.pl/products/obuwie-nowosc/category,2/flag,1/item,72/sort,1?", headers, bot,
                         message.chat.id)


bot.polling(none_stop=True, interval=0)
