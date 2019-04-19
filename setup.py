from setuptools import setup

setup(
    name = 'imagemeta',
    version = '0.1.0',
    packages = ['imagemeta'],
    package_data={'': ['auth/client_secret_imagemeta.json']},
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'imagemeta = imagemeta.__main__:main'
        ]
    })
