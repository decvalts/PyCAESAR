from setuptools import setup

setup(name='caesarplotlib',
      version='0.1',
      description='A set of plotting tools for plotting output data \
                   from the CAESAR-Lislfood models and derived models.',
      url='http://github.com/decvalts/caesarplotlib',
      author='Declan A. Valters',
      author_email='dvalts@gmail.com',
      license='GNU GPL v3',
      packages=['caesarplotlib'],
      install_requires=[
                "matplotlib",
      ],
      zip_safe=False)

