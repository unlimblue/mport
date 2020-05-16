import mport
from setuptools import setup, find_packages


setup(
    name='mport',
    version=mport.__version__,
    description='Python port mapping tool.',
    author='Shuaipeng Li',
    author_email='sli@mail.bnu.edu.cn',
    packages=find_packages()
)
