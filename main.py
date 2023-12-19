import telebot
import openai
import textwrap
import time
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from settings import settings_tg
from settings import settings_ai
from gpt import gpt4_free


token = settings_tg['Token']
openai.api_key = settings_ai['Token']
bot=telebot.TeleBot(token)
schedule_dict = {}


class Schedule:
    def __init__(self, subject):
        self.subject = subject
        self.count = None
        self.time = None
        self.extra = None


@bot.message_handler(commands=['start'])
def greetings(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    button_schedule = InlineKeyboardButton('Создать расписание', callback_data='Создать расписание')
    button_recommendations = InlineKeyboardButton('Получить рекомендации', callback_data='Получить рекомендации')
    button_questions = InlineKeyboardButton('Задать вопрос', callback_data='Задать вопрос')
    button_reminder = InlineKeyboardButton('Установить/отключить напоминания', callback_data='Установить/отключить напоминания')
    button_ChatGPT = InlineKeyboardButton('Свободная генерация текста', callback_data='ChatGPT')
    markup.add(button_schedule, button_recommendations, button_questions, button_reminder, button_ChatGPT)
    bot.send_message(chat_id=message.chat.id, text='Добро пожаловать', reply_markup=markup)

reminders = {}
@bot.message_handler(func=lambda message: message.text == "Установить/отключить напоминания")
def set_interval(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите интервал напоминания в минутах:")

    # Ожидаем ответ с интервалом
    bot.register_next_step_handler(message, set_reminder_interval)

@bot.message_handler(commands=['stopreminder'])
def stop_reminder(message):
    chat_id = message.chat.id
    if chat_id in reminders:
        del reminders[chat_id]
        bot.send_message(chat_id, "Напоминания о задачах отключены.")
    else:
        bot.send_message(chat_id, "Напоминания о задачах не были включены.")
def set_reminder_interval(message):
    chat_id = message.chat.id
    try:
        interval = int(message.text) * 60
        reminders[chat_id] = {'interval': interval , 'last_reminder': time.time()}
        bot.send_message(chat_id, f"Интервал напоминаний установлен на {interval / 60} минут. Если хотите выключить напоминания введите /stopreminder")

        reminder_thread = Thread(target=send_reminders, args=(chat_id,))
        reminder_thread.start()

    except ValueError:
        bot.send_message(chat_id, "Пожалуйста, введите корректное число.")


def send_reminders(chat_id):
    while chat_id in reminders:
        current_time = time.time()
        interval = reminders[chat_id]['interval']
        last_reminder = reminders[chat_id]['last_reminder']

        if current_time - last_reminder >= interval:
            bot.send_message(chat_id, "Напоминание о задаче!")
            reminders[chat_id]['last_reminder'] = current_time

        time.sleep(1)

@bot.message_handler(func=lambda message: message.text == "Получить рекомендации")
def button_recommendations(message):
    msg = bot.send_message(message.chat.id, 'Опишите свое текущее расписание и условия учебы:')
    bot.register_next_step_handler(msg, process_user_text)


def process_user_text(message):
    chat_id = message.chat.id
    user_text = message.text

    # Вызываем функцию для получения рекомендаций по тексту пользователя
    get_recommendations(chat_id, user_text)


def get_recommendations(chat_id, user_text):
    result = gpt4_free(textwrap.dedent(f'''\
    Пользователь жалуется на учебу и запрашивает советы по оптимизации продуктивности и сохранению здоровья, а именно: {user_text}.
    Прошу предоставить рекомендации и советы, которые могут помочь ему эффективнее учиться, справляться со стрессом и поддерживать физическое и эмоциональное здоровье.
    Пожалуйста, включите в рекомендации упражнения, питание, сон, планирование учебного времени и другие факторы, которые могут быть полезными. Ответ должен не превышать 500 символов
    '''))

    bot.send_message(chat_id, result)
@bot.message_handler(func=lambda message: message.text == "Создать расписание")
def schedule_step(message):
    msg = bot.send_message(message.chat.id, 'Какие у вас есть предметы?')
    bot.register_next_step_handler(msg, subject_step)


def subject_step(message):
    chat_id = message.chat.id
    subject = message.text
    schedule = Schedule(subject)
    schedule_dict[chat_id] = schedule  
    keyboard_count = InlineKeyboardMarkup(row_width=1)
    batton_count_1 = InlineKeyboardButton(text='1', callback_data='1')
    batton_count_2 = InlineKeyboardButton(text='2', callback_data='2')
    batton_count_3 = InlineKeyboardButton(text='3', callback_data='3')
    batton_count_4 = InlineKeyboardButton(text='4', callback_data='4')    
    keyboard_count.add(batton_count_1, batton_count_2, batton_count_3, batton_count_4,)
    bot.send_message(chat_id=message.chat.id, text='Сколько предметов в день вам комофртно изучать?', reply_markup=keyboard_count)


@bot.callback_query_handler(func=lambda callback: callback.data in ['1', '2', '3', '4']) 
def count_step(callback):
    chat_id = callback.from_user.id
    count = callback.data
    schedule = schedule_dict[chat_id]
    schedule.count = count
    keyboard_time = InlineKeyboardMarkup(row_width=1)
    batton_time_1 = InlineKeyboardButton(text='8:30', callback_data='8:30')
    batton_time_2 = InlineKeyboardButton(text='14:15', callback_data='14:15')
    batton_time_3 = InlineKeyboardButton(text='16:00', callback_data='16:00')
    keyboard_time.add(batton_time_1, batton_time_2, batton_time_3)
    bot.send_message(chat_id=callback.from_user.id, text='С какого времени будет начинаться учеба?', reply_markup=keyboard_time)


@bot.callback_query_handler(func=lambda callback: callback.data in ['8:30', '14:15', '16:00'])
def time_step(callback):
    chat_id = callback.from_user.id
    time = callback.data
    schedule = schedule_dict[chat_id]
    schedule.time = time
    msg = bot.send_message(chat_id=callback.from_user.id, text='Расскажите подробнее что вам нужно еще учесть при создании расписания')
    bot.register_next_step_handler(msg, extra_step)


def extra_step(message):
    chat_id = message.chat.id
    extra = message.text
    schedule = schedule_dict[chat_id]
    schedule.extra = extra
    result = gpt4_free(textwrap.dedent(f'''\
                            Помоги мне сделать расписание для студента. В расписании у меня есть {schedule.subject}. 
                            Очень важно чтобы количество предметов в день в расписании не должно превышать {schedule.count}. 
                            Учебный день должен начинаться с {schedule.time}. Перерыв между предметами должен быть 15 минут. 
                            Один предмет идет полтора часа. {schedule.extra}. 
                            Предметы в расписании не должны повторяться. 
                            Мне нужно только расписание без рекомендаций.
                            Расписание должно быть составлено на русском языке.
                            '''))
    bot.send_message(message.chat.id, result)



@bot.message_handler(func=lambda message: message.text == "Задать вопрос")
def quest_step(message):
    msg = bot.send_message(message.chat.id, 'Задайте свой вопрос')
    bot.register_next_step_handler(msg, Answer_GPT)


def Answer_GPT(message):
    reply = (
        f"Ты исполняешь роль учителя и наставника. Я введу несколько тем, связанных с наукой или искусством, а ты объяснишь их в доступной для восприятия форме. Можно приводить примеры, задавать вопросы или разбивать сложные идеи на более мелкие части, которые легче понять. Ответ должен быть не больше 2 или 3 коротких предложенийМой запрос:{message.text}")
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=reply,
        max_tokens=500,
        temperature=0.7,
        n=2,
        stop=None
    )

    if response and response.choices:
        reply = response.choices[0].text.strip()
    else:
        reply = 'Что-то пошло не так. Повторите попытку позже'

    bot.send_message(message.chat.id, reply)


@bot.message_handler(func=lambda message: message.text == "Свободная генерация текста")
def responce_step(message):
    msg = bot.send_message(message.chat.id, 'Ждем вашего запроса')
    bot.register_next_step_handler(msg, ChatGPT)


def ChatGPT(message):
    reply = message.text
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=reply,
        max_tokens=1000,
        temperature=0.7,
        n=2,
        stop=None
    )

    if response and response.choices:
        reply = response.choices[0].text.strip()
    else:
        reply = 'Что-то пошло не так. Повторите попытку позже'

    bot.send_message(message.chat.id, reply)



bot.infinity_polling()