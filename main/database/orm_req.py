from datetime import datetime
from peewee import IntegrityError
from main.database.orm_model import History, User


def create_user(message, admin=False) -> None:
    id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    User.create(
        user_id=id,
        first_name=first_name,
        last_name=last_name,
        admin=admin
    )


def create_history(message) -> None:
    user_id = message.from_user.id
    text = message.text
    History.create(datetime=datetime.now(), user_id=user_id, text=text)


def get_history() -> str:
    query = History.select()
    results = "".join(
        [f'Время: {elem.datetime} --- текст: "{elem.text}\nПользователь: {elem.user_id} \n\n"' for elem in query]
    )
    return results


def get_all_user() -> str:
    users = User.select()
    results = "".join(
        [f'Id: {user.user_id} | first_name: "{user.first_name}\nlast_name: {user.last_name}" | is admin {user.admin}\n\n' for user in users]
    )
    return results



def get_admins():
    query = User.select().where(
        User.admin == True
    ).order_by(User.admin)
    admins_list = [elem.user_id for elem in query]
    return admins_list


def update_user_to_admin(id) -> bool:
    try:
        id = id
        user = User.update({User.admin:1}).where(User.user_id == id)
        user.execute()
        return True
    except IntegrityError:
        return False


def update_user_to_no_admin(id) -> bool:
    try:
        id = id
        user = User.update({User.admin:0}).where(User.user_id == id)
        user.execute()
        return True
    except IntegrityError:
        return False


