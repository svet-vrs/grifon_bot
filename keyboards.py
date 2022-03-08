from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню

about_us = KeyboardButton("Узнать о нас❔")
estate = KeyboardButton("Подобрать жилье🏡")
get_gift = KeyboardButton("Поздравления🎄")
managers = KeyboardButton("Менеджеры📱")

menu_markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
    about_us, estate, managers, get_gift)

# Запрос контакта
call_back_btn = KeyboardButton("Отмена")
send_contact = KeyboardButton("Отправить контакт☎️", request_contact=True)
contact_markup = ReplyKeyboardMarkup(
    resize_keyboard=True).add(send_contact, call_back_btn)

# Выбор количества комнат

num_room_one = KeyboardButton("1")
num_room_two = KeyboardButton("2")
num_room_three = KeyboardButton("3")
num_room_four = KeyboardButton("4+")
cancel_button = KeyboardButton("Назад")

rooms_markup = ReplyKeyboardMarkup(resize_keyboard=True,  one_time_keyboard=True).add(
    num_room_one, num_room_two, num_room_three, num_room_four, cancel_button)

# Выбор районов

suv_area = KeyboardButton("Суворовский")
prim_area = KeyboardButton("Приморский")
kiev_area = KeyboardButton("Киевский")
malin_area = KeyboardButton("Малиновский")

area_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    suv_area, prim_area, kiev_area, malin_area)

# Переход на сайт

site_btn = InlineKeyboardButton("Наш сайт", url="http://feniks.agency/")

site_markup = InlineKeyboardMarkup().add(site_btn)

# Операции с недвижимостью

buy_app = KeyboardButton("Приобрести недвижимость")
sell_app = KeyboardButton("Продать недвижимость")
rent_app = KeyboardButton("Снять жилье")
rent_out_app = KeyboardButton("Сдать в аренду жилье")
back_button = KeyboardButton("Назад")

app_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    buy_app, sell_app, rent_app, rent_out_app, back_button)

# Клавиатура админки

delete_user = KeyboardButton("Удалить заявку по ID")
cancel_admin = KeyboardButton("Отмена удаления")
admin_cancel_markup = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True).add(cancel_admin)
admin_markup = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True).add(delete_user)

# Клавиатура заказа звонка
order_call = KeyboardButton("Заказать звонок")
cancel_order = KeyboardButton("Назад")
call_markup = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True).add(order_call, cancel_order)

# Клавиатура аренды
price_rent_one = KeyboardButton("350-500")
price_rent_two = KeyboardButton("500-700")
price_rent_three = KeyboardButton("700-1000")
price_rent_four = KeyboardButton("1000-1500")
price_rent_five = KeyboardButton("Выше 1500")
rent_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    price_rent_one, price_rent_two, price_rent_three, price_rent_four, price_rent_five)

# Клавиатура продажи
price_buy_one = KeyboardButton("25000-45000")
price_buy_two = KeyboardButton("45000-65000")
price_buy_three = KeyboardButton("65000-90000")
price_buy_four = KeyboardButton("90000-130000")
price_buy_five = KeyboardButton("130000-250000")
buy_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    price_buy_one, price_buy_two, price_buy_three, price_buy_four, price_buy_five)
