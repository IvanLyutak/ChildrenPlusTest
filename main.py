import telebot
from telebot import types
from data import config
from db.dbq import get_content_courses, get_my_courses, get_sequence_lessons, set_end_lesson, set_progress, get_result_course
from random import randint
from static.data import get_game, get_playlist_video, Message

# Telegram Bot Connection
bot = telebot.TeleBot(config.BOT_TOKEN)


polls = {}
results_test = {}


def update_keyboard(userId, text):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(types.KeyboardButton('📹 Видеоматериалы'), types.KeyboardButton('👨‍🏫 Курсы'),
               types.KeyboardButton('🎲 Игра'))
    bot.send_message(userId, text, reply_markup=markup)


def send_sticker(userId, href):
    bot.send_sticker(userId, open(href, 'rb'))


def add_video_category(userId):
    markup_inline = types.InlineKeyboardMarkup()
    for key, value in get_playlist_video().items():
        markup_inline.add(types.InlineKeyboardButton(text=value["title"], callback_data="video/" + key))
    bot.send_message(userId, "Выберите категорию", reply_markup=markup_inline)


def phone(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить телефон", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, 'Номер телефона', reply_markup=keyboard)


def presentation(call):
    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(types.InlineKeyboardButton(text="<", callback_data="previous"),
                      types.InlineKeyboardButton(text=">", callback_data="next"))
    bot.send_message(call.chat.id, "1 слайд", reply_markup=markup_inline)


def completion_course(call):
    bot.answer_callback_query(call.id, "Курс пройден")
    send_sticker(call.from_user.id, f'stickers/congratulations/{randint(1, 8)}.tgs')
    update_keyboard(call.from_user.id, "Курс пройден")


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        print(message.contact.phone_number)


@bot.message_handler(commands=["start"])
def welcome(message):
    send_sticker(message.chat.id, f'stickers/greetings/{randint(1,3)}.tgs')
    bot.send_message(message.chat.id,
                     "Добро пожаловать, {0.first_name}!\nВы получили доступ к обучающей платформе фонда Дети+".format(
                         message.from_user, bot.get_me()), parse_mode='html')
    bot.send_message(message.chat.id, f"Ваш ID = {message.chat.id}")
    get_my_courses(message.chat.id)
    update_keyboard(message.chat.id, "Выберите действие")

    # phone(message)
    # presentation(message)


@bot.message_handler(content_types=["text"])
def get_content(message):
    try:
        if message.text == "📹 Видеоматериалы":
            add_video_category(message.chat.id)

        elif message.text == "👨‍🏫 Курсы":
            markup_inline = types.InlineKeyboardMarkup()
            dictionary = get_my_courses(message.chat.id)
            if len(dictionary) > 0:
                for item in dictionary:
                    markup_inline.add(
                        types.InlineKeyboardButton(text=item['title'],
                                                   callback_data=f"course/{item['EducationItem']}"))
                bot.send_message(message.chat.id, "Выберите курс", reply_markup=markup_inline)
            else:
                bot.send_message(message.chat.id, "Для вас курсов нет", reply_markup=markup_inline)
        elif message.text == "🎲 Игра":
            bot.send_message(message.chat.id, Message.WELCOME_IN_GAME)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton('Начать игру'))
            bot.send_message(message.chat.id, "Давайте начнем?", reply_markup=markup)

        elif message.text == "Начать игру":
            game = get_game()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton(game["start"]["answer1"]))
            markup.add(types.KeyboardButton(game["start"]["answer2"]))
            bot.send_message(message.chat.id, game["start"]["question"], reply_markup=markup)

        elif message.text == "Завершить игру":
            update_keyboard(message.chat.id, "Классно поиграли")

        else:
            game = get_game()
            if message.text in game.keys():
                if game[message.text]["question"] == "":
                    update_keyboard(message.chat.id, "Игра завершилась")
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    markup.add(types.KeyboardButton(game[message.text]["answer1"]))
                    markup.add(types.KeyboardButton(game[message.text]["answer2"]))
                    bot.send_message(message.chat.id, game[message.text]["question"], reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Извините я вас не понял")
    except BaseException as err:
        print(f"Unexpected {err=}, {type(err)=}")


@bot.edited_message_handler(func=lambda poll: True)
def handler_function(message):
    print(message)


@bot.poll_answer_handler(func=lambda pollAnswer: True)
def handle_poll_answer(pollAnswer):
    global results_test
    data = polls[pollAnswer.user.id][pollAnswer.poll_id].data
    callback = get_content_courses('Тест', data.split(".")[1], int(data.split(".")[2]), int(data.split(".")[3])-1)

    assessment = 0
    for item in pollAnswer.option_ids:
        if callback["Answers"][item]["Assessment"] == 0:
            assessment -= 10
        else:
            assessment += callback["Answers"][item]["Assessment"]

    sum_assessment = 0
    for item in callback["Answers"]:
        sum_assessment += item["Assessment"]

    result = int((assessment/sum_assessment)*100)
    if pollAnswer.user.id in results_test:
        results_test[pollAnswer.user.id].append(result)
    else:
        results_test[pollAnswer.user.id] = [result]

    bot.stop_poll(polls[pollAnswer.user.id][pollAnswer.poll_id].from_user.id,
                  polls[pollAnswer.user.id][pollAnswer.poll_id].message_id)
    callback_query(polls[pollAnswer.user.id][pollAnswer.poll_id])


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        global polls, results_test
        typeContent = call.data.split('/')[0]
        data = call.data.split('/')[1]
        if typeContent == 'video':
            callbacks = get_playlist_video()
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(
                types.InlineKeyboardButton(text="Смотреть другие категории", callback_data="other_video/" + data))
            bot.answer_callback_query(call.id, callbacks[data]["title"])
            for i in range(len(callbacks[data]["url"]) - 1):
                bot.send_message(call.from_user.id, callbacks[data]["url"][i])
            bot.send_message(call.from_user.id, callbacks[data]["url"][len(callbacks[data]["url"]) - 1],
                             reply_markup=markup_inline)
            return

        elif typeContent == 'other_video':
            add_video_category(call.from_user.id)
            return

        elif typeContent == 'target group':
            markup_inline = types.InlineKeyboardMarkup()
            for item in get_content_courses('Курс', data):
                markup_inline.add(
                    types.InlineKeyboardButton(text=item["title"],
                                               callback_data="course/" + data + "." + str(item['id'])))
            bot.answer_callback_query(call.id, "Выберите курс")
            bot.send_message(call.from_user.id, "Выберите курс", reply_markup=markup_inline)

        elif typeContent == 'course':
            lesson = get_sequence_lessons(data.split(".")[0])
            bot.send_message(call.from_user.id, f"Урок "
                                                f"\"{get_content_courses('Урок', data.split('.')[0])[0]['title']}\"")
            typeContent = "lesson"
            data = data + f".{lesson[0]['id']}.0"

        if typeContent == 'lesson':
            # print("Data", data)
            callback = get_content_courses('Контент', data.split(".")[1], int(data.split(".")[2]))
            if callback is None:
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text="Завершить курс", callback_data="final/"))
                bot.answer_callback_query(call.id, Message.ERROR_LACK_OF_CONTENT)
                bot.send_message(call.from_user.id, Message.ERROR_LACK_OF_CONTENT, reply_markup=markup_inline)
                return

            set_progress(call.from_user.id,
                         data.split(".")[1],
                         int(data.split(".")[2]))

            if "finalStage" in callback:
                set_progress(call.from_user.id,
                             data.split(".")[1],
                             int(data.split(".")[2]),
                             finalStage=True)
                markup_inline = types.InlineKeyboardMarkup()

                lesson = get_sequence_lessons(data.split(".")[0])
                for i in range(len(lesson)):
                    if str(lesson[i]["id"]) == data.split(".")[1] and i < len(lesson) - 1:
                        if call.from_user.id in results_test:
                            result = 0
                            for item in results_test[call.from_user.id]:
                                if item >= 0:
                                    result += item

                            set_end_lesson(lesson[i]["id"],
                                           call.from_user.id,
                                           int(result/(len(results_test[call.from_user.id])*100)*100))

                            del polls[call.from_user.id]
                            del results_test[call.from_user.id]
                        else:
                            set_end_lesson(lesson[i]["id"], call.from_user.id)

                        markup_inline.add(
                            types.InlineKeyboardButton(text="Следующий урок",
                                                       callback_data="lesson/" + '.'.join(data.split(".")[:1]) + "." +
                                                                     str(lesson[i+1]["id"]) + ".0"))
                        bot.answer_callback_query(call.id, f"Урок \"{lesson[i]['title']}\" завершен")
                        bot.send_message(call.from_user.id, f"Урок \"{lesson[i]['title']}\" завершен, следующий урок "
                                                            f"\"{lesson[i+1]['title']}\"", reply_markup=markup_inline)
                        return
                    elif str(lesson[i]["id"]) == data.split(".")[1] and i == len(lesson) - 1:
                        if call.from_user.id in results_test:
                            result = 0
                            for item in results_test[call.from_user.id]:
                                if item >= 0:
                                    result += item

                            set_end_lesson(lesson[i]["id"],
                                           call.from_user.id,
                                           int(result/(len(results_test[call.from_user.id])*100)*100),
                                           finalCourse=True)

                            del polls[call.from_user.id]
                            del results_test[call.from_user.id]
                        else:
                            set_end_lesson(lesson[i]["id"], call.from_user.id, finalCourse=True)

                        message = "Подведем итоги\n"
                        flag = False
                        for item in get_result_course(data.split(".")[0], call.from_user.id):
                            if item["Result"] < 100:
                                message += f"❌ {item['Title']}\n"
                                flag = True
                            else:
                                message += f"✅ {item['Title']}\n"
                        if flag:
                            message += "\nЕсть ошибки. Пройдите курс заново 💪🏻"
                            bot.answer_callback_query(call.id, "Результаты")
                            bot.send_message(call.from_user.id, message)
                        else:
                            bot.answer_callback_query(call.id, "Результаты")
                            bot.send_message(call.from_user.id, message)
                            completion_course(call)

                        return

            if "Fragments" in callback:
                for i in range(len(callback["Fragments"])):
                    markup_inline = types.InlineKeyboardMarkup()
                    if i == len(callback["Fragments"]) - 1:
                        markup_inline.add(types.InlineKeyboardButton(text="Дальше",
                                                                     callback_data="lesson/"
                                                                                   + '.'.join(data.split('.')[:-1])
                                                                                   + "." + str(int(data.split(".")[2])
                                                                                               + 1)))
                    bot.answer_callback_query(call.id, callback['Title'])
                    bot.send_message(call.from_user.id, callback["Fragments"][i]["Content"], reply_markup=markup_inline)

            elif callback["Type"] == "media.txt" or callback["Type"] == "media.iframe":
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text="Дальше", callback_data="lesson/" + '.'.join(
                    data.split('.')[:-1]) + "." + str(int(data.split(".")[2]) + 1)))
                bot.answer_callback_query(call.id, callback['Title'])
                bot.send_message(call.from_user.id, callback["Content"], reply_markup=markup_inline)

            elif callback["Type"] == "media.img":
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text="Дальше", callback_data="lesson/" + '.'.join(
                    data.split('.')[:-1]) + "." + str(int(data.split(".")[2]) + 1)))
                bot.answer_callback_query(call.id, callback['Title'])
                bot.send_message(call.from_user.id, callback["Content"], reply_markup=markup_inline)

            elif callback["Type"] == "test":
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text="Начать тест", callback_data="test/" + '.'.join(
                    data.split('.')[:-1]) + "." + str(int(data.split(".")[2])) + "." + str(0)))
                bot.answer_callback_query(call.id, callback['Anchor'])
                bot.send_message(call.from_user.id, callback["Title"], reply_markup=markup_inline)

            elif callback["Type"] == 'media.html':
                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text="Дальше", callback_data="lesson/" + '.'.join(
                    data.split('.')[:-1]) + "." + str(int(data.split(".")[2]) + 1)))
                bot.answer_callback_query(call.id, callback['Title'])
                bot.send_message(call.from_user.id, "Для просмотра материала перейдите по следующей ссылке\n\n"
                                 + callback["Content"], reply_markup=markup_inline)

            elif callback["Type"] == "presentation":
                print("presentation")

        elif typeContent == 'test':
            callback = get_content_courses('Тест', data.split(".")[1], int(data.split(".")[2]), int(data.split(".")[3]))
            answers = []
            for item in callback["Answers"]:
                if len(item["Content"]) > 99 and callback["Answers"][0]["Type"] != "list":
                    answers.append(item["Content"][:97] + "...")
                else:
                    answers.append(item["Content"])

            if callback["Answers"][0]["Type"] == "list":
                string = "*" + callback["Question"] + "*\n\n"

                for i in range(len(answers)):

                    if results_test[call.from_user.id][i] == 100:
                        string = string + answers[i] + " ✅\n"
                    else:
                        string = string + answers[i] + " ❌\n"

                markup_inline = types.InlineKeyboardMarkup()
                markup_inline.add(types.InlineKeyboardButton(text="Завершить тестирование",
                                                             callback_data="lesson/" + '.'.join(data.split('.')[:-1])[
                                                                                       :-1] + str(
                                                                 int('.'.join(data.split('.')[:-1])[-1:]) + 1)))
                bot.send_message(call.from_user.id, string, reply_markup=markup_inline, parse_mode='Markdown')
                return

            elif callback["Answers"][0]["Type"] == "radio":
                poll = bot.send_poll(call.from_user.id, callback["Question"], options=answers, is_anonymous=False)
            else:
                poll = bot.send_poll(call.from_user.id, callback["Question"], options=answers, is_anonymous=False,
                                     allows_multiple_answers=True)

            call.data = "test/" + '.'.join(data.split('.')[:-1]) + "." + str(int(data.split(".")[3]) + 1)
            call.message_id = poll.message_id
            call.id = str(int(call.id) + 1)

            polls[call.from_user.id] = {
                poll.poll.id: call
            }

        elif typeContent == 'final':
            completion_course(call)
            return

        elif typeContent == 'therapy':
            if data == "yes":
                bot.answer_callback_query(call.id, "Отлично")
                send_sticker(call.from_user.id, f'stickers/congratulations/{randint(1,8)}.tgs')
                update_keyboard(call.from_user.id, "Отлично")
            else:
                bot.answer_callback_query(call.id, "Необходимо принять")
                update_keyboard(call.from_user.id, "Необходимо принять")
            return
        else:
            bot.answer_callback_query(call.id, Message.ERROR_UNKNOWN_REQUEST)
            bot.send_message(call.from_user.id, Message.ERROR_UNKNOWN_REQUEST)
    except BaseException as err:
        print(f"Unexpected {err=}, {typeContent(err)=}")


bot.infinity_polling()