from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='lantern',
    version='0.0.0',
    description='Lantern support for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lanterndata/lantern-python',
    author='Di Qi',
    author_email='di@lantern.dev',
    license='MIT',
    packages=[
        'pgvector.asyncpg',
        'pgvector.django',
        'pgvector.peewee',
        'pgvector.psycopg',
        'pgvector.psycopg2',
        'pgvector.sqlalchemy',
        'pgvector.utils'
    ],
    python_requires='>=3.8',
    install_requires=[
        'numpy'
    ],
    zip_safe=False
)
