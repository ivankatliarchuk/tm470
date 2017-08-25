from setuptools import setup, find_packages

setup(
    name='tm470webapp',
    version='1.0',
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask-admin',
        'psycopg2',
        'SQLAlchemy',
    ],
)