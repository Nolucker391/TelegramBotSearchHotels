from peewee import AutoField, BooleanField,CharField,DateField, ForeignKeyField, IntegerField, Model, SqliteDatabase


from config import DATE_FORMAT, date_base_path

db = SqliteDatabase(date_base_path)

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    username = CharField()
    first_name = CharField()
    last_name = CharField(null=True)

def create_models():
    db.create_tables(BaseModel.__subclasses__())