from setuptools import setup, find_packages

setup(
    name="premier_league",
    version="0.1",
    author="Michael Li",
    description="Premier League data Scrapping package",
    packages=find_packages(),
    install_requires=[
        'reportlab==4.0.4',
        'requests>=2.28.1',
        'lxml>=4.9.1',
        'beautifulsoup4>=4.11.0',
        'prettytable==3.11.0'
    ],
    python_requires='>=3.11',
)