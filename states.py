from aiogram.dispatcher.filters.state import StatesGroup, State

class Estate(StatesGroup):
    user_id = State()    
    name = State()
    plan = State()
    estates = State()
    rooms = State()
    money = State()
    area = State()
    phone_num = State()
    cancel = State()

class Admin(StatesGroup):
    delete_id = State()
    order_name = State()
    order_phone_num = State()