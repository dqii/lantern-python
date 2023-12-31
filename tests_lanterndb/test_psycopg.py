import numpy as np
import psycopg
import pytest

conn = psycopg.connect(
    dbname='postgres',
    user='postgres',
    password='postgres',
    host='localhost',
    port='5432',
    autocommit=True
)

conn.execute('CREATE EXTENSION IF NOT EXISTS lantern')
conn.execute('DROP TABLE IF EXISTS items')
conn.execute('CREATE TABLE items (id bigserial PRIMARY KEY, embedding REAL[3])')

register_vector(conn)


class TestPsycopg:
    def setup_method(self, test_method):
        conn.execute('DELETE FROM items')

    def test_works(self):
        embedding = np.array([1.5, 2, 3])
        conn.execute('INSERT INTO items (embedding) VALUES (%s), (NULL)', (embedding,))

        res = conn.execute('SELECT * FROM items ORDER BY id').fetchall()
        assert np.array_equal(res[0][1], embedding)
        assert res[1][1] is None

    @pytest.mark.asyncio
    async def test_async(self):
        conn = await psycopg.AsyncConnection.connect(
            dbname='postgres',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432',
            autocommit=True
        )

        await conn.execute('CREATE EXTENSION IF NOT EXISTS lantern')
        await conn.execute('DROP TABLE IF EXISTS items')
        await conn.execute('CREATE TABLE items (id bigserial PRIMARY KEY, embedding REAL[3])')

        await register_vector_async(conn)

        embedding = np.array([1.5, 2, 3])
        await conn.execute('INSERT INTO items (embedding) VALUES (%s), (NULL)', (embedding,))

        async with conn.cursor() as cur:
            await cur.execute('SELECT * FROM items ORDER BY id')
            res = await cur.fetchall()
            assert np.array_equal(res[0][1], embedding)
            assert res[1][1] is None
