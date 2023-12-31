import asyncio
import asyncpg
import numpy as np
import pytest


class TestAsyncpg:
    @pytest.mark.asyncio
    async def test_works(self):
        conn = await asyncpg.connect(database='postgres')
        await conn.execute('CREATE EXTENSION IF NOT EXISTS lantern')
        await conn.execute('DROP TABLE IF EXISTS items')
        await conn.execute('CREATE TABLE items (id SERIAL PRIMARY KEY, embedding real[3])')

        embedding = [1.5, 2, 3]
        await conn.execute("INSERT INTO items (embedding) VALUES ($1), (NULL)", embedding)

        res = await conn.fetch("SELECT * FROM items ORDER BY id")
        assert res[0]['id'] == 1
        assert res[1]['id'] == 2
        assert np.array_equal(res[0]['embedding'], embedding)
        assert res[1]['embedding'] is None

        await conn.close()

    @pytest.mark.asyncio
    async def test_pool(self):
        async def init(conn):
            await register_vector(conn)

        pool = await asyncpg.create_pool(database='postgres', init=init)

        async with pool.acquire() as conn:
            await conn.execute('CREATE EXTENSION IF NOT EXISTS lantern')
            await conn.execute('DROP TABLE IF EXISTS items')
            await conn.execute('CREATE TABLE items (id SERIAL PRIMARY KEY, embedding real[3])')

            embedding = np.array([1.5, 2, 3])
            await conn.execute("INSERT INTO items (embedding) VALUES ($1), (NULL)", embedding)

            res = await conn.fetch("SELECT * FROM items ORDER BY id")
            assert res[0]['id'] == 1
            assert res[1]['id'] == 2
            assert np.array_equal(res[0]['embedding'], embedding)
            assert res[1]['embedding'] is None