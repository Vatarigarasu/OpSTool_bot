import telebot
import math

from telebot import types
from config import TOKEN


class BotCore:
    def __init__(self):
        self.variable = {}
        self.result = None

    def record(self, key, item):
        self.variable[key] = item

    def hyper(self):
        self.result = self.variable['f'] + self.variable['f'] * self.variable['f'] / self.variable['pix'] / self.variable['sto']

    def fresnel(self):
        self.result = (self.variable['n'] - 1) ** 2 / (self.variable['n'] + 1) ** 2

    def transmission(self):
        if self.variable.get('abs') is None:
            if self.variable.get('tau') is not None:
                a = -math.log10(self.variable['tau']) / self.variable['bl']
                self.record('abs', a)
            elif self.variable.get('tau') is not None:
                a = self.variable['D'] / self.variable['bl']
                self.record('abs', a)
        tau = math.pow(10, (self.variable['abs'] * self.variable['l'] * -1))
        self.result = tau


def add_variable(msg, core, key):
    res = float(msg)
    core.record(key, res)


def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu

bot = telebot.TeleBot(TOKEN)
calc_core = BotCore()


@bot.message_handler(commands=['hyperfocal'])
def init_hyper(message):
    bot.send_message(message.from_user.id, 'Введите фокусное расстояние, мм:')  #ответ бота
    bot.register_next_step_handler(message, hyper_second)


def hyper_second(message):
    add_variable(message.text, calc_core, 'f')
    bot.send_message(message.from_user.id, 'Введите размер пикселя, мм:')  # ответ бота
    bot.register_next_step_handler(message, hyper_third)


def hyper_third(message):
    add_variable(message.text, calc_core, 'pix')
    bot.send_message(message.from_user.id, 'Введите диафрагменное число:')  # ответ бота
    bot.register_next_step_handler(message, hyper_result)


def hyper_result(message):
    add_variable(message.text, calc_core, 'sto')
    calc_core.hyper()
    bot.send_message(message.from_user.id, 'Рассчетное значение гиперфокального расстояния:`' + str(calc_core.result) + '` мм', parse_mode='Markdown')


@bot.message_handler(commands=['fresnel'])
def init_transmission(message):
    bot.send_message(message.from_user.id, 'Введите показатель преломления:')
    bot.register_next_step_handler(message, fresnel)


def fresnel(message):
    add_variable(message.text, calc_core, 'n')
    calc_core.fresnel()
    bot.send_message(message.from_user.id,
                     'Доля френелева отражения:`' + str(calc_core.result) + '`', parse_mode='Markdown')


@bot.message_handler(commands=['transmission'])
def init_transmission(message):
    button_list = [
        types.InlineKeyboardButton("Коэффициент поглощения", callback_data='btn1'),
        types.InlineKeyboardButton("Коэффициент пропускания", callback_data='btn2'),
        types.InlineKeyboardButton("Оптическая плотность", callback_data='btn3')
    ]
    reply_markup = types.InlineKeyboardMarkup(build_menu(button_list, n_cols=1))
    bot.send_message(message.from_user.id, 'Как задано пропускание?', reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    bot.answer_callback_query(call.id, 'Тык!')  # ответ бота
    chat_id = call.message.chat.id
    if call.data == "btn1":
        message = bot.send_message(chat_id, 'Введите коэффициент поглощения')
        bot.register_next_step_handler(message, get_absorption)
    elif call.data == "btn2":
        message = bot.send_message(chat_id, 'введите коэффициент пропускания')  # ответ бота
        bot.register_next_step_handler(message, get_transmission)
    elif call.data == "btn3":
        message = bot.send_message(chat_id, 'введите коэффициент пропускания')  # ответ бота
        bot.register_next_step_handler(message, get_density)


def get_density(message):
    add_variable(message.text, calc_core, 'D')
    bot.send_message(message.from_user.id, 'введите опорную толщину, мм:')
    bot.register_next_step_handler(message, base_length)


def get_absorption(message):
    add_variable(message.text, calc_core, 'abs')
    bot.send_message(message.from_user.id, 'введите требуюмую толщину, мм:')
    bot.register_next_step_handler(message, transmission_calc)


def get_transmission(message):
    add_variable(message.text, calc_core, 'tau')
    bot.send_message(message.from_user.id, 'введите опорную толщину, мм:')
    bot.register_next_step_handler(message, base_length)


def base_length(message):
    add_variable(message.text, calc_core, 'bl')
    bot.send_message(message.from_user.id, 'введите требуюмую толщину, мм:')
    bot.register_next_step_handler(message, transmission_calc)


def transmission_calc(message):
    add_variable(message.text, calc_core, 'l')
    calc_core.transmission()
    bot.send_message(message.from_user.id, 'Внутреннее пропускание:`' + str(calc_core.result) + '`', parse_mode='Markdown')


bot.infinity_polling()
