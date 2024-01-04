from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='lantern-django',
    version='0.0.0',
    description='Lantern support for Django',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/lanterndata/lantern-python',
    author='Di Qi',
    author_email='di@lantern.dev',
    license='BSL 1.1',
    project_urls = {
        "Bug Tracker": "https://github.com/lanterndata/lantern-python/issues",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy'
    ]
)
