# lantern-python

[Lantern](https://github.com/lanterndata/lantern) support for Python.

It is based on [pgvector](https://github.com/lanterndata/lantern)'s [Python client](https://github.com/pgvector/pgvector-python).

This library adds support for [Django](https://github.com/django/django), [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy), [SQLModel](https://github.com/tiangolo/sqlmodel), and [Peewee](https://github.com/coleifer/peewee). [Psycopg 3](https://github.com/psycopg/psycopg), [Psycopg 2](https://github.com/psycopg/psycopg2), and [asyncpg](https://github.com/MagicStack/asyncpg) are supported out of the box; installing this library is not necessary.

[![Build Status](https://github.com/lanterndata/lantern-python/workflows/build/badge.svg?branch=main)](https://github.com/lanterndata/lantern-python/actions)

## Installation

Run:

```sh
pip install lanterndb
```

And follow the instructions for your database library:

- [Django](#django)
- [SQLAlchemy](#sqlalchemy)
- [SQLModel](#sqlmodel)
- [Peewee](#peewee)


## Django

Create a migration to enable the extension(s)

```python
from django.db import migrations
from lanterndb.django import LanternExtension, LanternExtrasExtension

class Migration(migrations.Migration):
    operations = [
        LanternExtension(),
        LanternExtrasExtension(),
    ]
```

Add an embedding field to your model

```python
from django.db import models
from django.contrib.postgres.fields import ArrayField

class Book(models.Model):
    book_embedding = ArrayField(models.FloatField(), size=128)
```

Insert a vector

```python
book = Book(book_embedding=[1, 2, 3])
```

Find nearest rows with `L2Distance`, `MaxInnerProduct`, or `MinInnerProduct`

```python
from lanterndb.django import L2Distance

Book.objects.order_by(L2Distance('embedding', [3, 1, 2]))[:5]
```

Add a vector index

```python
from django.db import models
from lanterndb.django import HnswIndex

class Book(models.Model):
    class Meta:
        indexes = [
            HnswIndex(
                name='book_embedding_index',
                fields=['book_embedding'],
                m=2,
                ef_construction=10,
                ef=4,
                dim=3,
                opclasses=['dist_l2sq_ops']
            )
        ]
```

Generate one-off embeddings (note that these cannot be used unless the Lantern Extras extension is enabled as well)

```python
from django.db import models

results = Book.objects.annotate(
    text_embedding=TextEmbedding('BAAI/bge-small-en', 'My text input')
)
for result in results:
    print(result.text_embedding)
```

## SQLAlchemy

Enable the extension(s)

```python
session.execute(text('CREATE EXTENSION IF NOT EXISTS lantern'))
session.execute(text('CREATE EXTENSION IF NOT EXISTS lantern_extras'))
```

Add a vector column

```python
from pgvector.sqlalchemy import Vector

class Item(Base):
    embedding = mapped_column(Vector(3))
```

Insert a vector

```python
item = Item(embedding=[1, 2, 3])
session.add(item)
session.commit()
```

Get the nearest neighbors to a vector

```python
session.scalars(select(Item).order_by(Item.embedding.l2_distance([3, 1, 2])).limit(5))
```

Also supports `max_inner_product` and `cosine_distance`

Get the distance

```python
session.scalars(select(Item.embedding.l2_distance([3, 1, 2])))
```

Get items within a certain distance

```python
session.scalars(select(Item).filter(Item.embedding.l2_distance([3, 1, 2]) < 5))
```

Average vectors

```python
from sqlalchemy.sql import func

session.scalars(select(func.avg(Item.embedding))).first()
```

Also supports `sum`

Add an approximate index

```python
index = Index('my_index', Item.embedding,
    postgresql_using='hnsw',
    postgresql_with={'m': 16, 'ef_construction': 64},
    postgresql_ops={'embedding': 'vector_l2_ops'}
)

index.create(engine)
```

Use `vector_ip_ops` for inner product and `vector_cosine_ops` for cosine distance

## SQLModel

Enable the extension

```python
session.exec(text('CREATE EXTENSION IF NOT EXISTS vector'))
```

Add a vector column

```python
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column

class Item(SQLModel, table=True):
    embedding: List[float] = Field(sa_column=Column(Vector(3)))
```

Insert a vector

```python
item = Item(embedding=[1, 2, 3])
session.add(item)
session.commit()
```

Get the nearest neighbors to a vector

```python
session.exec(select(Item).order_by(Item.embedding.l2_distance([3, 1, 2])).limit(5))
```

Also supports `max_inner_product` and `cosine_distance`

## Psycopg 3

Enable the extension

```python
conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
```

Register the vector type with your connection

```python
from pgvector.psycopg import register_vector

register_vector(conn)
```

For [async connections](https://www.psycopg.org/psycopg3/docs/advanced/async.html), use

```python
from pgvector.psycopg import register_vector_async

await register_vector_async(conn)
```

Create a table

```python
conn.execute('CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3))')
```

Insert a vector

```python
embedding = np.array([1, 2, 3])
conn.execute('INSERT INTO items (embedding) VALUES (%s)', (embedding,))
```

Get the nearest neighbors to a vector

```python
conn.execute('SELECT * FROM items ORDER BY embedding <-> %s LIMIT 5', (embedding,)).fetchall()
```

## Psycopg 2

Enable the extension

```python
cur = conn.cursor()
cur.execute('CREATE EXTENSION IF NOT EXISTS lantern')
cur.execute('CREATE EXTENSION IF NOT EXISTS lantern_extras')
```

Register the vector type with your connection or cursor

```python
from pgvector.psycopg2 import register_vector

register_vector(conn)
```

Create a table

```python
cur.execute('CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3))')
```

Insert a vector

```python
embedding = np.array([1, 2, 3])
cur.execute('INSERT INTO items (embedding) VALUES (%s)', (embedding,))
```

Get the nearest neighbors to a vector

```python
cur.execute('SELECT * FROM items ORDER BY embedding <-> %s LIMIT 5', (embedding,))
cur.fetchall()
```

## asyncpg

Enable the extension

```python
await conn.execute('CREATE EXTENSION IF NOT EXISTS lantern')
await conn.execute('CREATE EXTENSION IF NOT EXISTS lantern_extras')
```

Register the vector type with your connection

```python
from pgvector.asyncpg import register_vector

await register_vector(conn)
```

or your pool

```python
async def init(conn):
    await register_vector(conn)

pool = await asyncpg.create_pool(..., init=init)
```

Create a table

```python
await conn.execute('CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3))')
```

Insert a vector

```python
embedding = np.array([1, 2, 3])
await conn.execute('INSERT INTO items (embedding) VALUES ($1)', embedding)
```

Get the nearest neighbors to a vector

```python
await conn.fetch('SELECT * FROM items ORDER BY embedding <-> $1 LIMIT 5', embedding)
```

## Peewee

Add a vector column

```python
from pgvector.peewee import VectorField

class Item(BaseModel):
    embedding = VectorField(dimensions=3)
```

Insert a vector

```python
item = Item.create(embedding=[1, 2, 3])
```

Get the nearest neighbors to a vector

```python
Item.select().order_by(Item.embedding.l2_distance([3, 1, 2])).limit(5)
```

Also supports `max_inner_product` and `cosine_distance`

Get the distance

```python
Item.select(Item.embedding.l2_distance([3, 1, 2]).alias('distance'))
```

Get items within a certain distance

```python
Item.select().where(Item.embedding.l2_distance([3, 1, 2]) < 5)
```

Average vectors

```python
from peewee import fn

Item.select(fn.avg(Item.embedding)).scalar()
```

Also supports `sum`

Add an approximate index

```python
Item.add_index('embedding vector_l2_ops', using='hnsw')
```

Use `vector_ip_ops` for inner product and `vector_cosine_ops` for cosine distance