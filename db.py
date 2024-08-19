import os

import prisma
import c_folder
import c_gacha
import c_profile
import c_card
import c_user
import c_shop
import c_cooldown
import card_manager
import time


# the most time that a gacha history can stay
# rn its set to 6 months, after that it gets deleted
MAX_GACHA_HISTORY_SECONDS = 6 * 24 * 3600


all_existing_cards = [
        # removes file extension
        i.split('.')[0] \
        for i in os.listdir("cards")
    ]
db = prisma.Prisma()



async def connect():
    await db.connect()


def makeSure_userExists(func):
    async def wrapper(*args, **kwargs):
        user_id = args[0] if len(args) != 0 else kwargs["user_id"]

        try:
            return await func(*args, **kwargs)
        except prisma.errors.ForeignKeyViolationError:
            await get_user(
                user_id,
                include = {
                    "gacha_info": True,
                    "cards": True,
                    "shop": True,
                    "profile": True,
                    "folders": True
                }
            )
            await get_gacha_info(user_id)

        return await func(*args, **kwargs)

    return wrapper



async def get_user(user_id: int, createNewUser_ifNotFound: bool = True, include: dict = {}) -> c_user.User | None:
    user: c_user.User = await db.user.find_first(
        where = { "user_id" : user_id },
        include = include
    )


    if user is None:
        if createNewUser_ifNotFound:
            user = c_user.User(
                user_id = user_id,
                cards = [],
                profile = c_profile.Profile(user_id = user_id),
                folders = [],
                gacha_info = c_gacha.GachaInfo(user_id = user_id, gacha_history = [])
            )
            return await db.user.create(
                data = {
                    "user_id": user_id
                },
                include = {
                    "cards": True,
                    "profile": True,
                    "folders": True,
                    "shop": True,
                    "gacha_info": True
                })
        else:
            return None


    if "cards" in include and include["cards"] == True and user is not None:
        for card in user.cards:
            if card.card_id not in all_existing_cards:
                await delete_card(user_id, card.card_id)

        user: c_user.User = await db.user.find_first(
            where = { "user_id" : user_id },
            include = include
        )

    return user

async def update_user(user_id: int, new_data: dict, include: dict = {}) -> None:
    return await db.user.update(
        where = { "user_id" : user_id },
        data = new_data,
        include = include
    )

@makeSure_userExists
async def get_cooldown(user_id: int, createNewCooldown_ifNotFound: bool = True, include: dict = {}) -> c_cooldown.Cooldown | None:
    cooldown = await db.cooldown.find_first(
        where = { " user_id " : user_id },
        include = include
    )

    if cooldown is None:
        if createNewCooldown_ifNotFound:
            cooldown = c_cooldown.Cooldown()

            await db.cooldown.create({
                **cooldown.dict(),
                "user_id": user_id
            })
        else:
            return None

    return cooldown

@makeSure_userExists
async def update_cooldown(user_id: int, new_data: dict, include: dict = {}) -> None:
    return await db.cooldown.update(
        where = { "user_id" : user_id },
        data = new_data,
        include = include
    )


@makeSure_userExists
async def delete_card(user_id: int, card_id: str):
    await db.card.delete_many(
        where = {
            "user_id": user_id,
            "card_id": card_id
        }
    )


@makeSure_userExists
async def add_cards(user_id: int, card: c_card.Card, amount: int = 1) -> c_card.Card:
    if amount == 0:
        return
    user = await get_user(user_id, include = { "cards" : True })

    card_obj = card_manager.find_card(user, card.card_id)

    if card_obj is not None:
        if card_obj.amount + amount <= 0:
            await delete_card(user_id, card.card_id)
            return None
        else:
            return await db.card.update_many(
                where = {
                    "user_id": user_id,
                    "card_id": card.card_id
                },
                data = {
                    "amount": card_obj.amount + amount
                }
            )
    else:
        if amount < 0:
            return
        return await db.card.create(
            data = {
                "user_id": user_id,
                "card_id": card.card_id,
                "amount": amount
            }
        )


async def get_card_count(card_id: str) -> int:
    return await db.card.count(
        where = {
            "card_id": card_id
        }
    )


@makeSure_userExists
async def get_profile(user_id: int, createNewProfile_ifNotFound: bool = True, include: dict = {}) -> c_profile.Profile | None:
    profile = await db.profile.find_first(
        where = { " user_id " : user_id },
        include = include
    )

    if profile is None:
        if createNewProfile_ifNotFound:
            profile = c_profile.Profile(
                user_id = user_id
            )

            await db.profile.create({
                **profile.dict(),
                "user_id": user_id
            })
        else:
            return None

    return profile


@makeSure_userExists
async def update_profile(user_id: int, new_data: dict, include: dict = {}) -> None:
    return await db.profile.update(
        where = { "user_id" : user_id },
        data = new_data,
        include = include
    )


@makeSure_userExists
async def get_shop(user_id: int, createNewShop_ifNotFound: bool = True, include: dict = {}) -> c_shop.Shop | None:
    shop = await db.shop.find_first(
        where = { " user_id " : user_id },
        include = include
    )

    if shop is None:
        if createNewShop_ifNotFound:
            shop = c_shop.Shop(
                cards = [],
                user_id = user_id
            )

            await db.shop.create({
                **{i: v for i, v in shop.dict().items() if i != "cards"},
                "user_id": user_id
            })
            shop.cards = {}
        else:
            return None

    return shop


@makeSure_userExists
async def update_shop(user_id: int, new_data: dict, include: dict = {}) -> None:
    return await db.shop.update(
        where = { "user_id" : user_id },
        data = new_data,
        include = include
    )


@makeSure_userExists
async def add_to_shop(
        user_id: int,
        card_id: str,
        amount: int,
        price: int
    ):

    await db.soldcards.create(
        data = {
            "user_id": user_id,
            "card_id": card_id,
            "amount": amount,
            "price": price
        }
    )


async def get_sold_card(card_id: int) -> c_card.SoldCard | None:
    try:
        return await db.soldcards.find_first(
            where = {
                "item_id": card_id
            }
        )
    except prisma.errors.FieldNotFoundError:
        return None


async def update_sold_cards(card_id: int, new_data: dict, include: dict = {}):
    new_card = await db.soldcards.update(
        where = {
            "item_id": card_id
        },
        data = new_data,
        include = include
    )

    if new_card.amount <= 0:
        await db.soldcards.delete(where = { "item_id" : card_id })


@makeSure_userExists
async def create_folder(user_id: int, folder_name: str, cards: list[str]):
    return await db.folder.create(
        data = {
            "user_id": user_id,
            "name": folder_name,
            "cards": " ".join(cards).upper()
        }
    )

@makeSure_userExists
async def delete_folder(user_id: int, folder_name: str):
    return await db.folder.delete_many(
        where = {
            "user_id": user_id,
            "name": {
                "contains": folder_name,
                "mode": "insensitive"
            }
        }
    )


@makeSure_userExists
async def get_folder(user_id: int, folder_name: str) -> c_folder.Folder:
    result = await db.folder.find_many(
        where = {
            "user_id": user_id,
            "name": {
                "contains": folder_name,
                "mode": "insensitive"
            }
        }
    )

    return result[0]


@makeSure_userExists
async def get_gacha_info(user_id: int, createNewInfo_ifNotFound: bool = True, include: dict = {}) -> c_gacha.GachaInfo | None:
    gacha_info = await db.gachainfo.find_first(
        where = { " user_id " : user_id },
        include = include
    )

    if gacha_info is None:
        if createNewInfo_ifNotFound:
            gacha_info = c_gacha.GachaInfo(
                user_id = user_id,
                gacha_history = []
            )

            await db.gachainfo.create({"user_id": user_id})
        else:
            return None

    return gacha_info


@makeSure_userExists
async def delete_old_gacha_history(user_id: int):
    oldest_allowed = int(time.time() - MAX_GACHA_HISTORY_SECONDS)
    await db.gachahistory.delete_many(
        where = {
            "time": {
                "lt": oldest_allowed
            }
        }
    )


@makeSure_userExists
async def create_gacha_history(user_id: int, rewards: str) -> c_gacha.GachaHistory:
    await delete_old_gacha_history(user_id)
    await db.gachahistory.create(
        data = {
            "user_id": user_id,
            "time": int(time.time()),
            "rewards": rewards
        }
    )

@makeSure_userExists
async def update_gacha_info(user_id: int, new_data: dict, include: dict = {}):
    new_card = await db.gachainfo.update(
        where = {
            "user_id": user_id
        },
        data = new_data,
        include = include
    )
