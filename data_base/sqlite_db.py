import sqlite3 as sq
from aiogram import types
import keyboards as kb
import bot
import config
parse = []
del_check = False
update_check = False
call_name = ""
call_phone = ""


def sql_start():
    global base, base2, cur, cur2
    base = sq.connect('users_req.db')
    base2 = sq.connect('users_calls.db')
    cur = base.cursor()
    cur2 = base2.cursor()
    if base:
        print('База1 подключена')
    if base2:
        print('База2 подключена')
    base.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER,name Text, contacts TEXT, estate TEXT, rooms TEXT, money TEXT, area TEXT)')
    base.commit()
    base2.execute(
        'CREATE TABLE IF NOT EXISTS calls(id INTEGER, name TEXT, contacts TEXT, message TEXT)')
    base2.commit()

# Добавление заявок на покупку


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?)',
                    (data['user_id'], data['name'], data['phone_num'], data['estates'], data['rooms'], data['money'], data['area']))
        base.commit()

# Добавление заказов на звонок


async def sql_add_call_command(state):
    async with state.proxy() as data:
        cur2.execute('INSERT INTO calls VALUES (?,?,?,?)',
                     (data['id'], data['name'], data['phone_num'], data['message_id']))
        base2.commit()


async def sql_view_call_command(bid_id):
    global call_name, call_phone
    revision = cur2.execute(
        "SELECT * FROM calls WHERE message == ?", [bid_id]).fetchone()
    if revision is not None:
        name = cur2.execute("SELECT name FROM calls WHERE message == ?", [
            bid_id]).fetchone()
        phone = cur2.execute("SELECT contacts FROM calls WHERE message == ?", [
            bid_id]).fetchone()
        call_name = name[0]
        call_phone = phone[0]


async def sql_parse_command():
    global parse
    google_sheet_db = cur.execute('SELECT * FROM users').fetchall()
    parse = google_sheet_db


async def sql_delete_command(user_id, message: types.Message, state):
    global del_check
    revision = cur.execute(
        "SELECT * FROM users WHERE id == ?", [user_id]).fetchone()
    if revision is not None:
        cur.execute('DELETE FROM users WHERE id == ?', [user_id])
        base.commit()
        del_check = True
    else:
        await message.reply("Заявки с таким ID не существует!", reply_markup=kb.admin_main_markup)
        await state.finish()
        del_check = False
