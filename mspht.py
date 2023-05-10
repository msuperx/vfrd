import telebot
import config
import random
import sqlite3
import pygismeteo
import datetime as dt
from telebot import types
bot = telebot.TeleBot(config.TOKEN)
gtg = []
with open('fd.txt') as cdc:
    cities = cdc.readlines()
    cities = [city.replace('\n', '').capitalize() for city in cities]


def sortcities(letter):
    dfg = []
    for line in cities:
        if line[0] == letter and line not in gtg:
            dfg.append(line)
    return dfg


def forecast(long, town):
    if long == 'td':
        gmt = pygismeteo.Gismeteo()
        search_results = gmt.search.by_query(town)
        city_id = search_results[0].id
        step3 = gmt.step3.by_id(city_id, days=3)
        ext = f'06:00 12:00 18:00\n{"{:4d}".format(round(step3[2].temperature.air.c))}°C  ' \
              f'{"{:4d}".format(round(step3[4].temperature.air.c))}°C  ' \
              f'{"{:4d}".format(round(step3[6].temperature.air.c))}°C'
        return ext
    elif long == 'nd':
        gmt = pygismeteo.Gismeteo()
        search_results = gmt.search.by_query(town)
        city_id = search_results[0].id
        step3 = gmt.step3.by_id(city_id, days=3)
        ext = f'06:00 12:00 18:00\n{"{:4d}".format(round(step3[9].temperature.air.c))}°C  ' \
              f'{"{:4d}".format(round(step3[11].temperature.air.c))}°C  ' \
              f'{"{:4d}".format(round(step3[13].temperature.air.c))}°C'
        return ext
    elif long == 'wk':
        nx = int(dt.datetime.now().day)
        gmt = pygismeteo.Gismeteo()
        search_results = gmt.search.by_query(town)
        city_id = search_results[0].id
        step24 = gmt.step24.by_id(city_id, days=7)
        ext = f'{"{:8d}".format(nx)} {"{:8d}".format(nx + 1)} {"{:8d}".format(nx + 2)}' \
              f'{"{:8d}".format(nx + 3)} {"{:8d}".format(nx + 4)} {"{:8d}".format(nx + 5)}' \
              f'{"{:8d}".format(nx + 6)}' \
              f'\n{str(round(step24[0].temperature.air.avg.c))}°C  ' \
              f'{"{:4d}".format(round(step24[1].temperature.air.avg.c))}°C  ' \
              f'{"{:4d}".format(round(step24[2].temperature.air.avg.c))}°C  ' \
              f'{"{:4d}".format(round(step24[3].temperature.air.avg.c))}°C  ' \
              f'{"{:4d}".format(round(step24[4].temperature.air.avg.c))}°C  ' \
              f'{"{:4d}".format(round(step24[5].temperature.air.avg.c))}°C  ' \
              f'{"{:4d}".format(round(step24[6].temperature.air.avg.c))}°C  '
        return ext


@bot.message_handler(commands=['start'])
def start(message):
    sti = open('static/yaemiko.jpg', 'rb')
    bot.send_sticker(message.chat.id, sti)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Сыграем в города?")
    item2 = types.KeyboardButton("О погоде")
    markup.add(item1, item2)
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nЯ - <b>{1.first_name}</b>,"
                     " бот созданный чтобы подсказывать погоду и играть в города."
                     "\n/register город - регистрация\n/help - помощь".format(
                         message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['register'])
def register(message):
    gmt = pygismeteo.Gismeteo()
    search_results = gmt.search.by_query(message.text.replace('/register ', ''))
    if search_results:
        con = sqlite3.connect("uss.db")
        cur = con.cursor()
        xcv = []
        for ex in cur.execute(f"""SELECT id FROM users""").fetchall():
            xcv.append(ex[0])
        con.close()
        if message.from_user.id not in xcv:
            con = sqlite3.connect("uss.db")
            cur = con.cursor()
            cityx = search_results[0].name
            cur.execute("""INSERT INTO users VALUES (?, ?, ?, ?)""", (message.from_user.id, cityx, 0, 0))
            con.commit()
            con.close()
            bot.send_message(message.chat.id, "Вы успешно зарегистрировались")
        else:
            bot.send_message(message.chat.id, "Вы уже зарегистрированы")
    else:
        bot.send_message(message.chat.id,
                         "Введите /register город ещё раз, с корректным значением города.")


@bot.message_handler(commands=['help'])
def tghelp(message):
    bot.send_message(message.chat.id,
                     "С помощью этого бота вы можете узнать погоду и сыграть в города,"
                     " увы, я пока отвечаю только российскими городами.\nКоманды:\n"
                     "/stopgame - завершить игру\n"
                     "/settings - настройки\n"
                     "/help - помощь\n"
                     "/register город - регистрация")


@bot.message_handler(commands=['stopgame'])
def stop(message):
    global gtg
    con = sqlite3.connect("uss.db")
    cur = con.cursor()
    if cur.execute(f"""SELECT gm FROM users WHERE id={message.from_user.id}""").fetchone()[0] == 1:
        gtg = []
        bot.send_message(message.chat.id, "Игра завершена")
        cur.execute(f"""UPDATE users SET gm=0 WHERE id={message.from_user.id}""")
        ex = cur.execute(f"""SELECT gameamount FROM users WHERE id={message.from_user.id}""").fetchone()[0] + 1
        cur.execute(f"""UPDATE users SET gameamount={ex} WHERE id={message.from_user.id}""")
        con.commit()
    con.close()


@bot.message_handler(commands=['change_city'])
def change_city(message):
    gmt = pygismeteo.Gismeteo()
    search_results = gmt.search.by_query(message.text.replace('/change_city ', ''))
    if search_results:
        con = sqlite3.connect("uss.db")
        cur = con.cursor()
        cityx = search_results[0].name
        cur.execute(f"""UPDATE users SET city='{cityx}' WHERE id={message.from_user.id}""")
        con.commit()
        con.close()
        bot.send_message(message.chat.id, "Город обновлён.")
    else:
        bot.send_message(message.chat.id,
                         "Введите /change_city город ещё раз, с корректным значением города.")


@bot.message_handler(commands=['number_of_games'])
def nog(message):
    con = sqlite3.connect("uss.db")
    cur = con.cursor()
    xc = cur.execute(f"""SELECT gameamount FROM users WHERE id={message.from_user.id}""").fetchone()[0]
    con.close()
    bot.send_message(message.chat.id, 'Ваше количество игр: ' + str(xc))


@bot.message_handler(commands=['settings'])
def settings(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton("Cменить город", callback_data='chg')
    item2 = types.InlineKeyboardButton("Кол-во игр", callback_data='numb')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Настройки:', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def msg(message):
    global cx, n
    if message.chat.type == 'private':
        con = sqlite3.connect("uss.db")
        cur = con.cursor()
        xcd = []
        for ex in cur.execute(f"""SELECT id FROM users""").fetchall():
            xcd.append(ex[0])
        if message.from_user.id not in xcd:
            if message.text == 'О погоде':
                bot.send_message(message.chat.id, 'Введите город:')
            elif message.text != 'Сыграем в города?':
                gmt = pygismeteo.Gismeteo()
                search_results = gmt.search.by_query(message.text)
                if search_results:
                    cityx = search_results[0].name
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    item1 = types.InlineKeyboardButton("На сегодня", callback_data='td ' + cityx)
                    item2 = types.InlineKeyboardButton("На завтра", callback_data='nd ' + cityx)
                    item3 = types.InlineKeyboardButton("На неделю", callback_data='wk ' + cityx)
                    markup.add(item1, item2, item3)
                    bot.send_message(message.chat.id, 'Прогноз:', reply_markup=markup)
                    cur.execute(f"""UPDATE users SET gm=0 WHERE id={message.from_user.id}""")
                    con.commit()
                else:
                    bot.send_message(message.chat.id, 'Некорректное имя города. Введите город ещё раз.')
        else:
            if message.text == 'О погоде' and \
                    not cur.execute(f"""SELECT gm FROM users WHERE id={message.from_user.id}""").fetchone()[0]:
                markup = types.InlineKeyboardMarkup(row_width=2)
                item1 = types.InlineKeyboardButton("В своем городе", callback_data='tc')
                item2 = types.InlineKeyboardButton("В другом городе", callback_data='nc')
                markup.add(item1, item2)
                bot.send_message(message.chat.id, 'Прогноз:', reply_markup=markup)
            elif cur.execute(f"""SELECT gm FROM users WHERE id={message.from_user.id}""").fetchone()[0] == 2:
                gmt = pygismeteo.Gismeteo()
                search_results = gmt.search.by_query(message.text)
                if search_results:
                    cityx = search_results[0].name
                    markup = types.InlineKeyboardMarkup(row_width=3)
                    item1 = types.InlineKeyboardButton("На сегодня", callback_data='td ' + cityx)
                    item2 = types.InlineKeyboardButton("На завтра", callback_data='nd ' + cityx)
                    item3 = types.InlineKeyboardButton("На неделю", callback_data='wk ' + cityx)
                    markup.add(item1, item2, item3)
                    bot.send_message(message.chat.id, 'Прогноз:', reply_markup=markup)
                    cur.execute(f"""UPDATE users SET gm=0 WHERE id={message.from_user.id}""")
                    con.commit()
                else:
                    bot.send_message(message.chat.id, 'Некорректное имя города. Введите город ещё раз.')
            elif message.text == 'Сыграем в города?' and \
                    not cur.execute(f"""SELECT gm FROM users WHERE id={message.from_user.id}""").fetchone()[0] \
                    and message.from_user.id in xcd:
                if random.randint(0, 100) % 2 == 0:
                    cx = True
                    bot.send_message(message.chat.id, 'Начинайте')
                else:
                    cx = False
                    bot.send_message(message.chat.id, 'Я начинаю')
                    df = random.choice(cities)
                    gtg.append(df.capitalize())
                    bot.send_message(message.chat.id, df)
                    if 'ь' == df[-1].lower():
                        n = df[-2].lower()
                    else:
                        n = df[-1].lower()
                cur.execute(f"""UPDATE users SET gm=1 WHERE id={message.from_user.id}""")
                con.commit()
            elif cur.execute(f"""SELECT gm FROM users WHERE id={message.from_user.id}""").fetchone()[0] == 1 and \
                    message.text not in ('Сыграем в города?', 'О погоде'):
                if not cx:
                    if n != message.text[0].lower():
                        bot.send_message(message.chat.id, 'Попробуйте снова')
                    elif message.text.capitalize() in gtg:
                        bot.send_message(message.chat.id, 'Такой город уже был')
                    else:
                        if message.text[-1] == 'ь':
                            x = message.text[-2]
                        else:
                            x = message.text[-1]
                        gtg.append(message.text.capitalize())
                        xb = random.choice(sortcities(x.upper()))
                        gtg.append(xb.capitalize())
                        bot.send_message(message.chat.id, xb)
                        if xb[-1].lower() in ('ы', 'ь'):
                            n = xb[-2].lower()
                        else:
                            n = xb[-1].lower()
                else:
                    if message.text[-1] in ('ь', 'ы'):
                        x = message.text[-2]
                    else:
                        x = message.text[-1]
                    gtg.append(message.text.capitalize())
                    xb = random.choice(sortcities(x.upper()))
                    gtg.append(xb.capitalize())
                    bot.send_message(message.chat.id, xb)
                    if xb[-1].lower() in ('ы', 'ь'):
                        n = xb[-2].lower()
                    else:
                        n = xb[-1].lower()
                cx = False
            else:
                bot.send_message(message.chat.id, 'Я не знаю что ответить 😢')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.message:
            if call.data[:2] == 'td':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Прогноз на сегодня в городе {call.data[3:]}е:", reply_markup=None)
                bot.send_message(call.message.chat.id, forecast('td', call.data[3:]))
            elif call.data[:2] == 'nd':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Прогноз на завтра в городе {call.data[3:]}:", reply_markup=None)
                bot.send_message(call.message.chat.id, forecast('nd', call.data[3:]))
            elif call.data[:2] == 'wk':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Прогноз на неделю в городе {call.data[3:]}:", reply_markup=None)
                bot.send_message(call.message.chat.id, forecast('wk', call.data[3:]))
            elif call.data == 'tc':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Погода:", reply_markup=None)
                con = sqlite3.connect("uss.db")
                cur = con.cursor()
                cityx = cur.execute(f"""SELECT city FROM users WHERE
                 id={call.message.chat.id}""").fetchone()[0]
                con.close()
                markup = types.InlineKeyboardMarkup(row_width=3)
                item1 = types.InlineKeyboardButton("На сегодня", callback_data='td ' + cityx)
                item2 = types.InlineKeyboardButton("На завтра", callback_data='nd ' + cityx)
                item3 = types.InlineKeyboardButton("На неделю", callback_data='wk ' + cityx)
                markup.add(item1, item2, item3)
                bot.send_message(call.message.chat.id, 'Прогноз:', reply_markup=markup)
            elif call.data == 'nc':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Погода:", reply_markup=None)
                bot.send_message(call.message.chat.id, 'Введите город:')
                con = sqlite3.connect("uss.db")
                cur = con.cursor()
                cur.execute(f"""UPDATE users SET gm=2 WHERE id={call.message.chat.id}""")
                con.commit()
                con.close()
            elif call.data == 'chg':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Настройки:", reply_markup=None)
                bot.send_message(call.message.chat.id, "Введите: /change_city город")
            elif call.data == 'numb':
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Настройки:", reply_markup=None)
                bot.send_message(call.message.chat.id, "Введите: /number_of_games")
    except Exception as e:
        print(repr(e))


# RUN
bot.polling(none_stop=True)
