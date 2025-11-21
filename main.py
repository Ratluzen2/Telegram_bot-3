import asyncio
import os
import json
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


# ==============================
#          الإعدادات
# ==============================

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

DATA_FILE = "storage.json"
USERS_FILE = "users.json"
LAST_MSG_FILE = "last_messages.json"


# ==============================
#   دوال حفظ وقراءة الملفات
# ==============================

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "tiktok": [], "instagram": [], "telegram": [], "whatsapp": [],
                "youtube": [], "pubg": [], "pes": [], "other": []
            }, f, ensure_ascii=False, indent=2)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_users():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_last():
    if not os.path.exists(LAST_MSG_FILE):
        with open(LAST_MSG_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

    with open(LAST_MSG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_last(data):
    with open(LAST_MSG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


# ==============================
#         القوائم
# ==============================

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


def user_main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 شراء حساب", callback_data="buy_menu")
    kb.button(text="💳 رصيدي", callback_data="my_balance")
    kb.adjust(1)
    return kb.as_markup()


def admin_panel():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ إضافة حساب", callback_data="admin_add")
    kb.button(text="📦 المخزون", callback_data="admin_stock")
    kb.adjust(1)
    return kb.as_markup()


# ==============================
#      نظام الحالات FSM
# ==============================

class AddAccount(StatesGroup):
    waiting_for_text = State()


# ==============================
#          أوامر البوت
# ==============================

bot = Bot(TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_cmd(message: types.Message):

    uid = str(message.from_user.id)
    last = load_last()

    # حذف رسالة الستارت السابقة إذا كانت موجودة
    if uid in last:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=last[uid])
        except:
            pass  # إذا لم يستطع حذفها لا مشكلة

    # المالك
    if message.from_user.id == ADMIN_ID:
        sent = await message.answer("👑 أهلاً بك مالك البوت!", reply_markup=admin_panel())
    else:
        users = load_users()
        if uid not in users:
            users[uid] = 0
            save_users(users)

        sent = await message.answer("مرحباً بك! ماذا تريد؟", reply_markup=user_main_menu())

    # حفظ آخر رسالة
    last[uid] = sent.message_id
    save_last(last)


# ==============================
#         رصيدي
# ==============================

@dp.callback_query(F.data == "my_balance")
async def my_balance(callback: types.CallbackQuery):
    users = load_users()
    uid = str(callback.from_user.id)

    balance = users.get(uid, 0)

    await callback.message.answer(f"💰 رصيدك الحالي: {balance} نقطة")
    await callback.answer()


# ==============================
#        شراء حساب
# ==============================

@dp.callback_query(F.data == "buy_menu")
async def open_buy_menu(callback: types.CallbackQuery):
    await callback.message.answer(
        "اختر الخدمة التي تريد شراء حساب منها:",
        reply_markup=user_menu()
    )
    await callback.answer()


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
        await callback.message.answer(f"✔️ تم تسليم الحساب:\n\n{item}")

    await callback.answer()


# ==============================
#         إضافة حساب
# ==============================

@dp.callback_query(F.data == "admin_add")
async def admin_add(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for key, name in services.items():
        kb.button(text=name, callback_data=f"add_{key}")
    kb.adjust(1)

    await callback.message.answer("اختر نوع الحساب الذي تريد إضافته:", reply_markup=kb.as_markup())
    await callback.answer()


@dp.callback_query(F.data.startswith("add_"))
async def admin_add_type(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.split("_")[1]
    await state.update_data(service_key=key)

    await callback.message.answer(
        f"أرسل الآن كليشة الحساب ليتم حفظه داخل مخزون:\n{services[key]}"
    )

    await state.set_state(AddAccount.waiting_for_text)
    await callback.answer()


@dp.message(AddAccount.waiting_for_text)
async def process_add_account(message: types.Message, state: FSMContext):
    data = await state.get_data()
    key = data["service_key"]

    db = load_data()
    db[key].append(message.text)
    save_data(db)

    await message.answer("✔ تم حفظ الحساب داخل المخزون بنجاح!")
    await state.clear()


# ==============================
#          عرض المخزون
# ==============================

@dp.callback_query(F.data == "admin_stock")
async def admin_stock(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    for key, name in services.items():
        kb.button(text=name, callback_data=f"stock_{key}")
    kb.adjust(1)

    await callback.message.answer("اختر نوع الخدمة:", reply_markup=kb.as_markup())
    await callback.answer()


@dp.callback_query(F.data.startswith("stock_"))
async def admin_show_stock(callback: types.CallbackQuery):
    key = callback.data.split("_")[1]
    data = load_data()
    items = data[key]

    if len(items) == 0:
        await callback.message.answer("❌ لا يوجد أي حساب داخل المخزون.")
    else:
        text = "\n\n".join(items)
        await callback.message.answer(f"📦 مخزون {services[key]}:\n\n{text}")

    await callback.answer()


# ==============================
#          تشغيل البوت
# ==============================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
