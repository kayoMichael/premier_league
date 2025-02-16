from setuptools import setup, find_packages

setup(
    name="premier_league",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    author="Michael Li",
    description="Premier League Data Analysis Package",
    packages=find_packages(exclude=["test*", "build*", "dist*", "files*", "venv*"]),
    install_requires=[
        "reportlab==4.0.4",
        "requests==2.28.1",
        "lxml==4.9.1",
        "beautifulsoup4>=4.11.0",
        "prettytable==3.11.0",
        "flask==3.0.0",
        "flask-caching==2.3.0",
        "flask-cors==5.0.0",
        "flask-limiter==1.4.0",
        "PyYAML==6.0.2",
        "gunicorn==23.0.0",
        "appdirs==1.4.4",
        "SQLAlchemy==2.0.38",
        "pandas==2.2.3",
        "tqdm==4.67.1",
    ],
    include_package_data=True,
    python_requires=">=3.11",
)
