import sqlite3 as sq
from aiogram import types
import keyboards as kb
import bot

parse = []
del_check = False
update_check = False


def sql_start():
    global base, cur
    base = sq.connect('users_req.db')
    cur = base.cursor()
    if base:
        print('База подключена')
    base.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER,name Text, contacts TEXT, estate TEXT, rooms TEXT, money TEXT, area TEXT, plans TEXT)')
    base.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?,?)',
                    (data['user_id'], data['name'], data['phone_num'], data['estates'], data['rooms'], data['money'], data['area'], data['plan']))
        base.commit()


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
