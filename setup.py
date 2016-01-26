from distutils.core import setup

setup(
        # Application name:
        name='PPPoEDI',

        # Version number (initial):
        version="0.0.91",

        # Application author details:
        author="LAR",
        author_email="monitores@inf.ufes.br",

        # Packages
        packages=["app"],

        # Include additional files into the package
        include_package_data=True,

        # Details
        url="http://www.suporte.inf.ufes.br",
        license="LICENSE.txt",
        description="Interface grafica escrita em Python para conexao ao servidor PPPoE do DI.",

        # long_description=open("README.txt").read(),

        # Dependent packages (distributions)
        # install_requires=[
        #    'gi',
        # ],
)
