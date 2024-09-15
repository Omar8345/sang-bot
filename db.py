import os
import prisma
import achievements_manager
import c_achievements
import c_folder
import c_gacha
import c_profile
import c_card
import c_user
import c_shop
import c_cooldown
import card_manager
import card_info
import time
import reminder_handler

# the most time that a gacha history can stay
# rn its set to 6 months, after that it gets deleted
MAX_GACHA_HISTORY_SECONDS = 6 * 24 * 3600


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

            await get_shop(
                user_id
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
            if card.card_id not in card_info.all_cards:
                await delete_card(user_id, card.card_id)

        user: c_user.User = await db.user.find_first(
            where = { "user_id" : user_id },
            include = include
        )

    if "achievements" in include:
        if include["achievements"] == True:
            user.achievements = await get_achievements(user_id = user_id)

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
        where = { "user_id" : user_id },
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
    thing = await db.cooldown.update(
        where = { "user_id" : user_id },
        data = new_data,
        include = include
    )

    reminder = None
    for _reminder in reminder_handler.reminder_times.keys():
        if _reminder in new_data:
            reminder = _reminder

    if reminder is not None:
        result = await db.reminder.find_first(
            where = {
                "user_id": user_id,
                reminder: 2
            }
        )
        if result is not None:
            await update_reminder(
                user_id = user_id,
                new_data = {
                    reminder: 1
                }
            )
    return thing


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


async def get_card_count(card_id: str = None, user_id: str = None, filters: dict | None = {}) -> int:
    where = {}
    if user_id is not None:
        where["user_id"] = user_id

    if card_id is not None:
        where["card_id"] = card_id

    by = []
    if user_id is not None:
        by.append("user_id")

    if card_id is not None:
        by.append("card_id")

    where.update(filters)

    result =  await db.card.group_by(
        by = by,
        where = where,
        sum = {
            "amount": True
        }
    )

    if len(result) == 0:
        return 0
    return result[0]['_sum']['amount']

@makeSure_userExists
async def get_profile(user_id: int, createNewProfile_ifNotFound: bool = True, include: dict = {}) -> c_profile.Profile | None:
    profile = await db.profile.find_first(
        where = { "user_id" : user_id },
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
        where = { "user_id" : user_id },
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

    if new_card.amount <= 0 and not (new_card.user_id == -1 and new_card.amount != 0):
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
        where = { "user_id" : user_id },
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


@makeSure_userExists
async def update_reminder(user_id: int, new_data: dict, include: dict = {}):
    result = await db.reminder.update(
        where = {
            "user_id": user_id
        },
        data = new_data,
        include = include
    )

    if result is None:
        await db.reminder.create(
            data={
                "user_id": user_id,
                **new_data
            },
            include = include
        )

@makeSure_userExists
async def get_achievements(user_id: int, createNewAchievements_ifNotFound: bool = True, include: dict = {"achievements": True}) -> c_achievements.Achievements | None:
    achievements_ = await db.achievements.find_first(
        where={"user_id": user_id},
        include=include
    )

    if achievements_ is None:
        if createNewAchievements_ifNotFound:
            await db.achievements.create({
                "user_id": user_id
            })

            for achievement in achievements_manager.achievement_names.keys():
                await db.achievement.create(
                    {
                        "user_id": user_id,
                        "name": achievement
                    }
                )

            achievements_ = await db.achievements.find_first(
                where={"user_id": user_id},
                include=include
            )
        else:
            return None

    return achievements_

async def update_achievement(user_id: int, achievement: str, new_data: dict) -> c_achievements.Achievement:
    return await db.achievement.update_many(
        where = {
            "user_id": user_id,
            "name": achievement
        },
        data = new_data
    )


@makeSure_userExists
async def get_achievement(user_id: int, achievement: str, new_data = {}, include: dict = {}) -> c_achievements.Achievement:
    result = await db.achievement.find_many(
        where = {
            "user_id": user_id,
            "name": achievement
        }
    )

    if result is None or len(result) == 0:
        return None

    return result[0]
