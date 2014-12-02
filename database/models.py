from peewee import *
import os


db = SqliteDatabase(os.path.join(os.path.dirname(__file__), "topera.db"))

class BaseModel(Model):
    class Meta:
        database = db


class Lexicon(BaseModel):
    id = PrimaryKeyField()
    word = CharField(index=True, unique=True)
#    font_size = IntegerField()


class Documents(BaseModel):
    id = PrimaryKeyField()
    document = CharField(unique=True)
    page_rank = DecimalField(default=0.0)

class InvertedIndex(BaseModel):
    word = ForeignKeyField(Lexicon, index=True)
    document = ForeignKeyField(Documents)

    class Meta:
        primary_key = CompositeKey("word", "document")

class Links(BaseModel):
    from_doc = ForeignKeyField(Documents, related_name="from")
    to_doc = ForeignKeyField(Documents, related_name="to")
    num_link = IntegerField(default=1)

    class Meta:
        primary_key = CompositeKey("from_doc", "to_doc")

def create_tables():
    Lexicon.create_table()
    Documents.create_table()
    InvertedIndex.create_table()
    Links.create_table()