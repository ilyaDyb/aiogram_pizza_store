import os
import pyshorteners

from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.utils.formatting import as_list, as_marked_section, Bold

from sqlalchemy.ext.asyncio import AsyncSession
from database.orm_query import orm_get_product, orm_get_products

from filters.chat_types import ChatTypeFilter

from kbrds import reply
from kbrds.inline import get_callback_btns

import stripe

user_private_router = Router()
user_private_router.message.filter(ChatTypeFilter(['private']))

@user_private_router.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("Привет, я виртуальный помощник",
                         reply_markup=reply.get_keyboard(
                             "Меню",
                             "О магазине",
                             "Варианты оплаты",
                             "Варианты доставки",
                             placeholder="Что вас интересует?",
                             sizes=(2,2)
                         ),
                    )


@user_private_router.message(or_f(Command("menu"), (F.text.lower() == "меню")))
async def menu_command(message: types.Message, session: AsyncSession):
    for product in await orm_get_products(session):
        await message.answer_photo(
            product.image,
            caption=f"Название: <strong>{product.name}</strong>\nОписание: {product.description}\nСтоимость: {round(product.price, 2)}",
            reply_markup=get_callback_btns(btns={"Купить": f"buyProduct_{product.id}"}, sizes=(1,))
        )

@user_private_router.callback_query(F.data.startswith("buyProduct_"))
async def buy_product(callback: types.CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]

    product = await orm_get_product(session, product_id=int(product_id))

    stripe.api_key = os.getenv("STRIPE_SK")
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        success_url="https://web.telegram.org/a/#6312125642",
        line_items=[
            {
                "price_data":{
                    "currency": "rub",
                    "unit_amount": int(product.price) * 100,
                    "product_data": {"name": str(product.name), "description": str(product.description)},
                },
                "quantity": 1,
            },
        ],
        mode="payment",
    )
    await callback.message.answer(f"Оплата тут:\n"+str(pyshorteners.Shortener().clckru.short(checkout_session["url"])))

@user_private_router.message(F.text.lower() == "о нас")
@user_private_router.message(Command("about"))
async def about_command(message: types.Message):
    await message.answer("О нас:")


@user_private_router.message(F.text.lower() == "варианты оплаты")
@user_private_router.message(Command("payment"))
async def payment_commant(message: types.Message):

    text = as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении картой/налом",
        "В заведении",
        marker="✅ "
    )
    await message.answer(text.as_html())


@user_private_router.message((F.text.lower().contains('доставк')) | (F.text.lower() == 'варианты доставки'))
@user_private_router.message(Command("shipping"))
async def shipping_command(message: types.Message):
    
    text = as_list(
        as_marked_section(
            Bold("Варианты доставки/заказа:"),
            "Курьер",
            "Самовынос",
            "Поем у вас",
            marker="✅ "
        ),
        as_marked_section(
            Bold("Нельзя: "),
            "Почта",
            "Голуби",
            marker="❌ "
        ),
        sep="\n--------------------\n"
    )

    await message.answer(text.as_html())# reply_markup=reply.test_kb


# @user_private_router.message(F.contact)
# async def get_contact(message: types.Message):
#     await message.answer("Номер получен")
#     await message.answer(str(message.contact))


# @user_private_router.message(F.location)
# async def get_location(message: types.Message):
#     await message.answer("Локация получена")
#     await message.answer(str(message.location))

