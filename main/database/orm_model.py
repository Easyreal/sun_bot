from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    InternalError,
    Model,
    PrimaryKeyField,
    SqliteDatabase,
    BooleanField
)

db = SqliteDatabase("basic.db")


class User(Model):
    __tablename__ = "user"
    user_id = PrimaryKeyField(null=False, unique=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    admin = BooleanField(null=False)

    class Meta:
        database = db


class History(Model):
    __tablename__ = "history"
    id = IntegerField(null=False, primary_key=True)
    datetime = DateTimeField()
    user_id = ForeignKeyField(
        User, backref="history", on_delete="cascade", on_update="cascade"
    )
    text = CharField()

    class Meta:
        database = db  # This model uses the "people.db" database.


def db_start():
    try:
        db.connect()
        User.create_table()
    except InternalError as px:
        print(str(px))
    try:
        History.create_table()
    except InternalError as px:
        print(str(px))

