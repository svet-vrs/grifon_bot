import config
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from states import Estate
from states import Admin
from a1range import A1Range
import keyboards as kb
from data_base import sqlite_db
bot = Bot(config.TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# Глобальные переменные

appart_info = ""
request_id = 1
number_of_rooms = 0
money = 0
area = ""
phone_number = ""
ID = None
disc = ""

# Взаимодействие с таблицей

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'credentials.json')
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SAMPLE_SPREADSHEET_ID = ''
SAMPLE_RANGE_NAME = 'Лист1'
service = build(
    'sheets', 'v4', credentials=credentials).spreadsheets().values()
result = service.get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                     range=SAMPLE_RANGE_NAME).execute()
data_from_sheet = result.get('values', [])
batch_clear_values_request_body = {
    'ranges': ["Лист1!A2:H1000"],
}

# Подключение базы данных


async def on_startup(_):
    print("Бот вышел в онлайн")
    sqlite_db.sql_start()

# Очистка гугл таблицы перед парсингом


async def clear_gs():
    clear_response = service.batchClear(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                        body=batch_clear_values_request_body).execute()

# ////Админская часть////


@dp.message_handler(commands=['moderator'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    global ID
    ID = message.from_user.id
    admin_name = message.from_user.first_name
    await bot.send_message(chat_id="-713436137", text="Уважаемый <b>"+str(admin_name)+"</b>, вы получили права модератора, для администрирования перейдите в бота", parse_mode='HTML')
    await bot.send_message(message.from_user.id, 'Вам доступна панель модератора', reply_markup=kb.admin_markup)


@dp.message_handler(lambda message: message.text == "Удалить заявку по ID", state=None)
async def enter_req_id(message: types.Message):
    if message.from_user.id == ID:
        await Admin.delete_id.set()
        await message.reply("Введите ID заявки, которую нужно удалить:", reply_markup=kb.admin_cancel_markup)

# Команда отменад


@dp.message_handler(lambda message: message.text == "Отмена удаления", state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await message.reply('Вы вышли с панели модератора,для продолжения администрирования вернитесь в час администраторов', reply_markup=ReplyKeyboardRemove())
        await state.finish()


@dp.message_handler(state=Admin.delete_id)
async def delete_request(message: types.Message, state: FSMContext):
    if message.from_user.id == ID:
        async with state.proxy() as data:
            data['delete_id'] = message.text
        await sqlite_db.sql_delete_command(data['delete_id'], message, state)
        await sqlite_db.sql_parse_command()
        await clear_gs()
        if sqlite_db.del_check == True:
            if sqlite_db.parse != []:
                array = {'values': sqlite_db.parse}
                range_ = A1Range.create_a1range_from_list(
                    'Лист1', 2, 1, array['values']).format()
                response = service.update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                          range=range_,
                                          valueInputOption='RAW', body=array).execute()
                await message.reply("Вы успешно удалили зявку с ID: " + data['delete_id'], reply_markup=kb.admin_markup)
                await state.finish()
            else:
                await message.reply("Вы успешно удалили зявку с ID: " + data['delete_id'], reply_markup=kb.admin_markup)
                await state.finish()
        else:
            if sqlite_db.parse != []:
                array = {'values': sqlite_db.parse}
                range_ = A1Range.create_a1range_from_list(
                    'Лист1', 2, 1, array['values']).format()
                response = service.update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                          range=range_,
                                          valueInputOption='RAW', body=array).execute()
            else:
                return


# ////Клиентская часть////

# Приветствие и появление меню

@dp.message_handler(commands=['start', 'help'], state=None)
async def welcome(message: types.Message):
    await bot.send_sticker(message.from_user.id, r'CAACAgIAAxkBAAEDWy9hnqt1ch_H4nLtqTSEW6gF4pmgzQACkxcAAspJ0Eh8w0UdKNUtnSIE')
    await bot.send_message(message.from_user.id, "Добро пожаловать, " + message.from_user.first_name + " 👋\nЯ - <b>твой личный ассистент Phoenix</b>, Мы организация, предоставляющая услуги быстрого и качественного подбора недвижимости!",
                           parse_mode='html', reply_markup=kb.menu_markup)

# Реакция на кнопки меню


@dp.message_handler(content_types=['text'])
async def menu_buttons(message: types.Message, state=FSMContext):
    global disc
    if message.text == "Узнать о нас❔" or message.text == "Поздравления🎄" or message.text == "Менеджеры📱" or message.text == "Подобрать жилье🏡":
        if message.text == "Узнать о нас❔":
            await message.answer("Агенство недвижимости Феникс является гарантией качества и надежности для наших клиентов. Постоянная растущая собственная база объектов включает в себя более 400 домов, и более 1000 квартир Одессы, множество коммерческих помещений и эксклюзивных предложений от застройщиков нашего города", reply_markup=kb.site_markup,)
        elif message.text == "Поздравления🎄":
            disc = "Скидка активна"
            await Estate.estates.set()
            await message.answer("Расскажите о ваших планах на 2022 и получите подарок:", reply_markup=kb.app_markup)
        if message.text == "Менеджеры📱":
            await Admin.order_phone_num.set()
            await message.answer("Тут вы можете оставить свой номер и в течении нескольких минут с вами свяжется менеджер", reply_markup=kb.contact_markup)
        elif message.text == "Подобрать жилье🏡":
            disc = ""
            await Estate.estates.set()
            await message.answer("Что вас интересует?", reply_markup=kb.app_markup)
    else:
        await message.reply("Вы дали некорректый ответ, пожалуйста воспользуйтесь кнопками меню!", reply_markup=kb.menu_markup)

# Реакция на кнопку отмены отправки телефона менеджерам


@dp.message_handler(state=Admin.order_phone_num)
async def check_call_request(message: types.Message, state=FSMContext):
    if message.text == "Отмена":
        await state.finish()
        await message.reply('Вы отменили действие', reply_markup=kb.menu_markup)


@dp.message_handler(content_types=['contact'], state=Admin.order_phone_num)
async def create_call_order(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['order_name'] = message.from_user.first_name
    async with state.proxy() as data:
        data['order_phone_num'] = message.contact.phone_number
    phone = data['order_phone_num']
    if phone.startswith("+"):
        order_num = str(phone)
    else:
        order_num = "+"+str(phone)
    await message.answer("Вы заказали звонок,в скором времени с вами свяжутся✅", reply_markup=kb.menu_markup)
    await bot.send_message(chat_id="-713436137", text="Поступила заявка на звонок \nФИО: "+str(data['order_name'])+"\nНомер: "+order_num, parse_mode='Markdown')
    await state.finish()


# Реакция на кнопки взаимодействия с недвижимостью


@dp.message_handler(state=Estate.estates)
async def estate_buttons(message: types.Message, state: FSMContext):
    global disc
    if message.text == "Приобрести недвижимость" or message.text == "Продать недвижимость" or message.text == "Снять жилье" or message.text == "Сдать в аренду жилье" or message.text == "Назад":
        async with state.proxy() as data:
            data['plan'] = disc
        disc = ""
        if message.text == "Приобрести недвижимость":
            async with state.proxy() as data:
                data['user_id'] = message.from_user.id
            async with state.proxy() as data:
                data['name'] = message.from_user.first_name
            async with state.proxy() as data:
                data['estates'] = message.text
            await Estate.next()
            await message.answer("Сколько комнат вас интересует?", reply_markup=kb.rooms_markup)
        elif message.text == "Продать недвижимость":
            async with state.proxy() as data:
                data['user_id'] = message.from_user.id
            async with state.proxy() as data:
                data['name'] = message.from_user.first_name
            async with state.proxy() as data:
                data['estates'] = message.text
            await Estate.next()
            await message.answer("Сколько комнат в вашей собственности?", reply_markup=kb.rooms_markup)
        if message.text == "Снять жилье":
            async with state.proxy() as data:
                data['user_id'] = message.from_user.id
            async with state.proxy() as data:
                data['name'] = message.from_user.first_name
            async with state.proxy() as data:
                data['estates'] = message.text
            await Estate.next()
            await message.answer("Сколько комнат вас интересует?", reply_markup=kb.rooms_markup)
        elif message.text == "Сдать в аренду жилье":
            async with state.proxy() as data:
                data['user_id'] = message.from_user.id
            async with state.proxy() as data:
                data['name'] = message.from_user.first_name
            async with state.proxy() as data:
                data['estates'] = message.text
            await Estate.next()
            await message.answer("Сколько комнат в вашей собственности?", reply_markup=kb.rooms_markup)
        if message.text == "Назад":
            await state.finish()
            await message.reply('Вы отменили действие', reply_markup=kb.menu_markup)
    else:
        await message.reply("Вы дали некорректый ответ, пожалуйста нажмите на кнопку!", reply_markup=kb.app_markup)

# Результат первого вопроса покупки/аренды жилья


@dp.message_handler(state=Estate.rooms)
async def first_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['rooms'] = message.text
    if message.text != "Назад":
        if data['rooms'] == "1" or data['rooms'] == "2" or data['rooms'] == "3" or data['rooms'] == "4+":
            await Estate.next()
            if data['estates'] == "Приобрести недвижимость" or data['estates'] == "Продать недвижимость":
                await message.reply("На какой бюджет в USD💲 вы расчитываете?", reply_markup=kb.buy_markup)
            elif data['estates'] == "Снять жилье" or data['estates'] == "Сдать в аренду жилье":
                await message.reply("На какую сумму в USD💲 вы расчитываете?", reply_markup=kb.rent_markup)
        else:
            await message.reply("Вы дали некорректый ответ, пожалуйста нажмите на кнопку!", reply_markup=kb.rooms_markup)
    else:
        await state.finish()
        await message.reply('Вы отменили действие', reply_markup=kb.menu_markup)

# Результат второго вопроса покупки/аренды жилья


@dp.message_handler(state=Estate.money)
async def second_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['money'] = message.text
    if data['estates'] == "Приобрести недвижимость" or data['estates'] == "Продать недвижимость":
        if data['money'] == "25000-45000" or data['money'] == "45000-65000" or data['money'] == "65000-90000" or data['money'] == "90000-130000" or data['money'] == "130000-250000":
            await Estate.next()
            if data['estates'] == "Приобрести недвижимость" or data['estates'] == "Снять жилье":
                await message.reply("Какой район вас интересует?", reply_markup=kb.area_markup)
            elif data['estates'] == "Продать недвижимость" or data['estates'] == "Сдать в аренду жилье":
                await message.reply("В каком районе ваша недвижимость?", reply_markup=kb.area_markup)
        else:
            await message.reply("Вы дали некорректый ответ, пожалуйста нажмите на кнопку!", reply_markup=kb.buy_markup)
    elif data['estates'] == "Снять жилье" or data['estates'] == "Сдать в аренду жилье":
        if data['money'] == "300-500" or data['money'] == "500-700" or data['money'] == "700-1000" or data['money'] == "1000-1500" or data['money'] == "Выше 1500":
            await Estate.next()
            if data['estates'] == "Приобрести недвижимость" or data['estates'] == "Снять жилье":
                await message.reply("Какой район вас интересует?", reply_markup=kb.area_markup)
            elif data['estates'] == "Продать недвижимость" or data['estates'] == "Сдать в аренду жилье":
                await message.reply("В каком районе ваша недвижимость?", reply_markup=kb.area_markup)
        else:
            await message.reply("Вы дали некорректый ответ, пожалуйста нажмите на кнопку!", reply_markup=kb.rent_markup)


# Результат третьего вопроса


@dp.message_handler(state=Estate.area)
async def third_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['area'] = message.text
    if data['area'] == "Суворовский" or data['area'] == "Приморский" or data['area'] == "Киевский" or data['area'] == "Малиновский":
        await Estate.next()
        await bot.send_message(message.from_user.id, "Предоставьте пожалуйста свой номер телефона, менеджер свяжется с вами в ближайшее время", reply_markup=kb.contact_markup)
    else:
        await message.reply("Вы дали некорректый ответ, пожалуйста нажмите на кнопку!", reply_markup=kb.area_markup)

# Запрос контакта


@dp.message_handler(state=Estate.phone_num)
async def check_call_request(message: types.Message, state=FSMContext):
    if message.text == "Отмена":
        await state.finish()
        await message.reply('Вы отменили действие', reply_markup=kb.menu_markup)


@dp.message_handler(content_types=['contact'], state=Estate.phone_num)
async def fourth_question(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['phone_num'] = message.contact.phone_number
    async with state.proxy() as data:
        if 'plan' not in data.keys():
            data['plan'] = ""
    await sqlite_db.sql_add_command(state)
    await sqlite_db.sql_parse_command()
    await clear_gs()
    array = {'values': sqlite_db.parse}
    range_ = A1Range.create_a1range_from_list(
        'Лист1', 2, 1, array['values']).format()
    response = service.update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                              range=range_,
                              valueInputOption='RAW',
                              body=array).execute()
    if data['plan'] != "":
        await state.finish()
        await bot.send_message(message.from_user.id, "Поздравляем, вы получили скидку в размере 20% на услуги нашей компании!🎁", reply_markup=kb.menu_markup)
    else:
        await state.finish()
        await bot.send_message(message.from_user.id, "Ваша заявка принята и вскоре будет рассмотрена ✅", reply_markup=kb.menu_markup)


# ***********************************Запуск бота***********************************

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
