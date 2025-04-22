import asyncio

from jinja2.async_utils import auto_await
from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession, async_engine_from_config
from sqlalchemy.orm import joinedload, selectinload

from core.models import (
    db_helper,
    User,
    Post,
    Profile,
    Order,
    Product,
    OrderProductAssociation,
)


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    print(user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    # result: Result = await session.execute(stmt)
    # user: User | None = result.scalar_one_or_none()
    # user: User | None = result.scalar_one()
    user: User | None = await session.scalar(stmt)
    print("found user", username, user)
    return user


async def create_user_profile(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    bio: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        bio=bio,
    )
    session.add(profile)
    await session.commit()
    return profile


async def show_users_with_profiles(session: AsyncSession):
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    # result: Result = await session.execute(stmt)
    # users = result.scalars()
    users = await session.scalars(stmt)
    for user in users:
        print(user)
        print(user.profile.last_name)


async def create_posts(
    session: AsyncSession,
    user_id: int,
    *posts_titles: str,
) -> list[Post]:
    posts = [Post(title=title, user_id=user_id) for title in posts_titles]
    session.add_all(posts)
    await session.commit()
    print(posts)
    return posts


async def get_users_with_posts(session: AsyncSession):
    # stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
    # users = await session.scalars(stmt)
    # result: Result = await session.execute(stmt)
    # users = result.scalars()
    users = await session.scalars(stmt)

    # for user in users.unique():  # type: # User
    for user in users:  # type: User
        print("**" * 10)
        print(user)
        for post in user.posts:
            print("-", post)


async def get_users_with_posts_and_profiles(session: AsyncSession):
    stmt = (
        select(User)
        .options(
            joinedload(User.profile),
            selectinload(User.posts),
        )
        .order_by(User.id)
    )

    users = await session.scalars(stmt)

    for user in users:  # type: User
        print("**" * 10)
        print(user, user.profile and user.profile.first_name)
        for post in user.posts:
            print("-", post)


async def get_posts_with_authors(session: AsyncSession):
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts = await session.scalars(stmt)

    for post in posts:
        print("**" * 10)
        print("POST", post)
        print("AUTHOR", post.user.username)
        print("**" * 10)
        print("\n\n")


async def get_profile_with_users_and_with_posts(session: AsyncSession):
    stmt = (
        select(Profile)
        .join(Profile.user)
        .options(
            joinedload(Profile.user).selectinload(User.posts),
        )
        .where(User.username == "Adi")
        .order_by(Profile.id)
    )

    profiles = await session.scalars(stmt)
    for profile in profiles:
        print("**" * 10)
        print(profile.first_name, profile.user)
        print(profile.user.posts)


async def create_order(
    session: AsyncSession,
    promo_code: str | None = None,
) -> Order:
    order = Order(promo_code=promo_code)
    session.add(order)
    await session.commit()
    return order


async def create_product(
    session: AsyncSession,
    name: str,
    price: int,
    description: str,
) -> Product:
    product = Product(name=name, price=price, description=description)
    session.add(product)
    await session.commit()
    return product


async def create_orders_and_products(session: AsyncSession):
    order_one = await create_order(session=session)
    order_promo = await create_order(session=session, promo_code="promo")

    mouse = await create_product(
        session=session,
        name="Mouse",
        description="Great gaming mouse",
        price=123,
    )

    keyboard = await create_product(
        session=session,
        name="Keyboard",
        description="Great gaming keyboard",
        price=150,
    )

    display = await create_product(
        session=session,
        name="Display",
        description="Office display",
        price=350,
    )

    order_one = await session.scalar(
        select(Order)
        .where(Order.id == order_one.id)
        .options(
            selectinload(Order.products),
        ),
    )

    order_promo = await session.scalar(
        select(Order)
        .where(Order.id == order_promo.id)
        .options(
            selectinload(Order.products),
        ),
    )

    order_one.products.append(mouse)
    order_one.products.append(keyboard)
    # order_promo.products.append(display)
    # order_promo.products.append(keyboard)

    order_promo.products = [keyboard, display]

    await session.commit()


async def get_orders_with_products(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products),
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)
    return list(orders)


async def demo_get_orders_with_products_through_secondary(session: AsyncSession):
    orders = await get_orders_with_products(session=session)
    for order in orders:
        print(order.id, order.promo_code, order.created_at, "products:")
        for product in order.products:
            print("-", product.id, product.name, product.price, product.description)


async def get_orders_with_products_assoc(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products_details).joinedload(
                OrderProductAssociation.product
            ),
        )
        .order_by(Order.id)
    )
    orders = await session.scalars(stmt)
    return list(orders)


async def demo_get_orders_with_products_with_assoc(session: AsyncSession):
    orders = await get_orders_with_products_assoc(session=session)

    for order in orders:
        print(order.id, order.promo_code, order.created_at, "products:")
        for order_product_details in order.products_details:
            print(
                "-",
                order_product_details.product.id,
                order_product_details.product.name,
                order_product_details.product.price,
                "qty",
                order_product_details.count,
            )


async def main_relations(session: AsyncSession):
    # await create_user(session=session, username="Adi")
    # await create_user(session=session, username="Damke")
    # user_nurs = await get_user_by_username(session=session, username="Nurs")
    # user_adi = await get_user_by_username(session=session, username="Adi")
    #
    # await create_user_profile(
    #     session=session,
    #     user_id=user_nurs.id,
    #     first_name="Nursultan",
    # )
    # await create_user_profile(
    #     session=session,
    #     user_id=user_adi.id,
    #     first_name="Adilet",
    #     last_name="Estebes uulu",
    # )
    # await show_users_with_profiles(session=session)
    # await create_posts(
    #     session,
    #     user_nurs.id,
    #     "Nurs Post 1",
    #     "Nurs Post 2",
    # )
    # await create_posts(
    #     session,
    #     user_adi.id,
    #     "ADI POST 1",
    #     "ADI POST 2",
    # )
    # await get_users_with_posts(session=session)
    # await get_posts_with_authors(session=session)
    # await get_users_with_posts_and_profiles(session=session)
    await get_profile_with_users_and_with_posts(session=session)


async def create_gift_product_for_existing_orders(session: AsyncSession):
    orders = await get_orders_with_products_assoc(session=session)
    gift_product = await create_product(
        session,
        name="Gift",
        description="Gift for you",
        price=0,
    )

    for order in orders:
        order.products_details.append(
            OrderProductAssociation(
                product=gift_product,
                count=1,
                unit_price=0,
            )
        )
    await session.commit()


async def demo_m2m(session: AsyncSession):
    # await create_orders_and_products(session=session)
    # await demo_get_orders_with_products_through_secondary(session=session)
    await demo_get_orders_with_products_with_assoc(session=session)
    # await create_gift_product_for_existing_orders(session=session)


async def main():
    async with db_helper.session_factory() as session:
        # await main_relations(session=session)
        await demo_m2m(session=session)


if __name__ == "__main__":
    asyncio.run(main())
