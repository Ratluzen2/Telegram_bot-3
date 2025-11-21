# main.py
# Telegram bot for selling accounts with admin panel using aiogram

import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import CommandStart
import json
import os

TOKEN = "PUT_YOUR_TOKEN_HERE"
ADMIN_ID = 123456789  # Replace with owner Telegram ID

DATA_FILE = "storage.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"tiktok": [], "instagram": [], "telegram": [], "whatsapp": [], "youtube": [], "pubg": [], "pes": [], "other": []}, f, ensure_ascii=False, indent=2)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

bot = Bot(TOKEN)
dp = Dispatcher()

services = {
    "tiktok": "شراء حساب تيكتوك (ضمان100%)",
    "instagram": "شراء حساب انستغرام (ضمان100%)",
    "telegram": "شراء حساب تليجرام (ضمان100%)",
    "whatsapp": "شراء حساب واتساب (ضمان100%)",
    "youtube": "شراء حساب يوتيوب (ضمان100%)",
    "pubg": "شراء حساب ببجي (ضمان100%)",
    "pes": "شراء حساب بيس (ضمان100%)",
    "other": "شراء حسابات اخرى💡"
}

def user_menu():
    kb = InlineKeyboardBuilder()
    for key, name in services.items():
        kb.button(text=name, callback_data=f"buy_{key}")
    kb.adjust(1)
    return kb.as_markup()

def admin_panel():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ اضافه حسابات", callback_data="admin_add")
    kb.button(text="📦 المخزون", callback_data="admin_stock")
    kb.adjust(1)
    return kb.as_markup()

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("👑 أهلاً بك مالك البوت!", reply_markup=admin_panel())
    else:
        await message.answer("مرحباً بك! اختر الخدمة التي تريد شراء حساب منها:", reply_markup=user_menu())

@dp.callback_query(F.data.startswith("buy_"))
async def buy_category(callback: types.CallbackQuery):
    key = callback.data.split("_")[1]
    data = load_data()
    stock = data[key]

    if len(stock) == 0:
        await callback.message.answer("❌ لا توجد حسابات متوفرة حالياً لهذه الخدمة.")
    else:
        item = stock.pop(0)
        save_data(data)
        await callback.message.answer(f"✔️ تم حجز حساب لك:\n{item}")

    await callback.answer()

@dp.callback_query(F.data == "admin_add")
async def admin_add(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for key, name in services.items():
        kb.button(text=name, callback_data=f"add_{key}")
    kb.adjust(1)
    await callback.message.answer("اختر الخدمة لإضافة حساب:", reply_markup=kb.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("add_"))
async def admin_add_type(callback: types.CallbackQuery):
    key = callback.data.split("_")[1]
    await callback.message.answer(f"أرسل الكليشة الخاصة بحساب {services[key]}")
    dp.message.register(process_add_account, F.text, key=key)
    await callback.answer()

async def process_add_account(message: types.Message, key):
    data = load_data()
    data[key].append(message.text)
    save_data(data)
    await message.answer("✔️ تم حفظ الحساب داخل المخزون")
    dp.message.unregister(process_add_account)

@dp.callback_query(F.data == "admin_stock")
async def admin_stock(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for key, name in services.items():
        kb.button(text=name, callback_data=f"stock_{key}")
    kb.adjust(1)
    await callback.message.answer("اختر الخدمة لعرض المخزون:", reply_markup=kb.as_markup())
    await callback.answer()

@dp.callback_query(F.data.startswith("stock_"))
async def admin_show_stock(callback: types.CallbackQuery):
    key = callback.data.split("_")[1]
    data = load_data()
    items = data[key]

    if len(items) == 0:
        await callback.message.answer("❌ لا يوجد أي حساب في المخزون لهذا القسم.")
    else:
        text = "\n\n".join(items)
        await callback.message.answer(f"📦 مخزون {services[key]}:\n\n{text}")

    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
