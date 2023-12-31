import numpy as np
import psycopg2

conn = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='postgres',
    host='localhost',
    port='5432'
)
conn.autocommit = True

cur = conn.cursor()
cur.execute('CREATE EXTENSION IF NOT EXISTS lantern')
cur.execute('DROP TABLE IF EXISTS items')
cur.execute('CREATE TABLE items (id bigserial PRIMARY KEY, embedding REAL[3])')

class TestPsycopg2:
    def setup_method(self, test_method):
        cur.execute('DELETE FROM items')

    def test_works(self):
        embedding = np.array([1.5, 2.0, 3.0])
        cur.execute('INSERT INTO items (embedding) VALUES (%s), (NULL)', (embedding,))

        cur.execute('SELECT * FROM items ORDER BY id')
        res = cur.fetchall()
        assert np.array_equal(res[0][1], embedding)
        assert res[1][1] is None
