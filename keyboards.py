from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# -------Админская часть-------

# Клавиатура главной админки
btnDelete = InlineKeyboardButton(
    "Удалить заявку", callback_data='admin_delete')
btnAdminExit = InlineKeyboardButton(
    "Выйти с панели админа", callback_data='admin_exit')
btnBids = InlineKeyboardButton(
    "Заявки", url='https://docs.google.com/spreadsheets/d/1vkBpMw2fpXL5yUM1jQL8IBihddWtDmwCTF1covW7dm8/edit')
admin_main_markup = InlineKeyboardMarkup(
    row_width=2).add(btnBids, btnDelete, btnAdminExit)

# Клавиатура удаления в админке
btnAdminCancel = InlineKeyboardButton(
    "❌ Отмена", callback_data='adminsub_cancel')
admin_sub_markup = InlineKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True).add(btnAdminCancel)

# Клавиатура принятия заявки
btnConnect = InlineKeyboardButton(
    "✅ Принять заявку", callback_data="bid_connect")
admin_chat_markup = InlineKeyboardMarkup().add(btnConnect)
# -------Клиентская часть-------

# Главное меню
btnAbout = InlineKeyboardButton("❔ Узнать о нас", callback_data='menu_about')
btnEstate = InlineKeyboardButton(
    "🏡 Подобрать жилье", callback_data='menu_estate')
btnManagers = InlineKeyboardButton(
    "📱 Менеджеры", callback_data='menu_managers')
btnCatalog = InlineKeyboardButton(
    "🏘 Каталог объектов", url='https://www.olx.ua/nedvizhimost/od/')
menu_markup = InlineKeyboardMarkup(row_width=2).add(
    btnAbout, btnEstate, btnManagers, btnCatalog)

# Раздел О нас
btnSite = InlineKeyboardButton(
    "🌐 Наш сайт", url="https://www.grifonagency.com/")
btnAboutBack = InlineKeyboardButton("◀ Назад", callback_data='about_back')
about_markup = InlineKeyboardMarkup(row_width=2).add(btnSite, btnAboutBack)

# Раздел Подобрать жилье

btnBuy = InlineKeyboardButton(
    "Купить недвижимость", callback_data='estate_buy')
btnSell = InlineKeyboardButton(
    "Продать недвижимость", callback_data='estate_sell')
btnRent = InlineKeyboardButton("Снять жилье", callback_data='estate_rent')
btnRentOut = InlineKeyboardButton(
    "Сдать в аренду жилье", callback_data='estate_rent_out')
btnEstateBack = InlineKeyboardButton("◀ Назад", callback_data='estate_back')
estate_markup = InlineKeyboardMarkup(resize_keyboard=True).add(
    btnBuy, btnSell, btnRent, btnRentOut, btnEstateBack)

# Выбор количества комнат

btnRoomOne = InlineKeyboardButton("1", callback_data='room_1')
btnRoomTwo = InlineKeyboardButton("2", callback_data='room_2')
btnRoomThree = InlineKeyboardButton("3", callback_data='room_3')
btnRoomFour = InlineKeyboardButton("4+", callback_data='room_4more')
btnRoomBack = InlineKeyboardButton("◀ Назад", callback_data='room_back')

rooms_markup = InlineKeyboardMarkup(resize_keyboard=True).add(
    btnRoomOne, btnRoomTwo, btnRoomThree, btnRoomFour, btnRoomBack)

# Выбор районов

suv_area = KeyboardButton("Суворовский")
prim_area = KeyboardButton("Приморский")
kiev_area = KeyboardButton("Киевский")
malin_area = KeyboardButton("Малиновский")

area_markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(
    suv_area, prim_area, kiev_area, malin_area)


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

# Запрос контакта
call_back_btn = KeyboardButton("❌ Отмена")
send_contact = KeyboardButton("☎️ Отправить контакт", request_contact=True)
contact_markup = ReplyKeyboardMarkup(
    resize_keyboard=True, one_time_keyboard=True).add(send_contact, call_back_btn)
