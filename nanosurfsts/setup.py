from setuptools import setup

with open("README.md", "r") as arq:
    readme = arq.read()

setup(name='nanosurf-sts',
    version='1.0.0',
    license='MIT License',
    author='Rafael Reis Barreto',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='rafinhareis17@gmail.com',
    keywords='nanosurf sts',
    description=u'Analise de sts para o stm da nanosurf',
    packages=['nanosurfsts'],
    install_requires=['pandas','numpy','scipy','matplotlib'],)