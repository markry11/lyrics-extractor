from setuptools import setup

setup(
    name='lyrics_extractor',
    version='0.0.1',
    description='package allowing to retrieve song lyrics.',
    url='git@github.com:markry11/lyrics-extractor.git',
    author='Marek Kryska',
    author_email='kryska.marek@gmail.com',
    license='MIT',
    packages=['lyrics_extractor'],
    install_requires=["requests", "beautifulsoup4", "lxml", "scrape-search-engine"],
    zip_safe=False
)