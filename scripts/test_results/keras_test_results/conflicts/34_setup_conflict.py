<<<<<<< HEAD
#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
=======
from setuptools import setup
from setuptools import find_packages
>>>>>>> remote

setup(name='Keras',
      version='0.0.1',
      description='Theano-based Deep Learning',
      author='Francois Chollet',
      author_email='francois.chollet@gmail.com',
      url='https://github.com/fchollet/keras',
      license='MIT',
      packages=find_packages(),
      # TODO: dependencies
)
