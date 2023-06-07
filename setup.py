from setuptools import setup

setup(name='picozk',
      version='0.2',
      description='PicoZK library & compiler for writing zero-knowledge statements',
      url='none',
      author='Joe Near',
      author_email='jnear@uvm.edu',
      license='GPLv3',
      packages=['picozk'],
      install_requires=[],
      packages=['picozk', 'picozk/poseidon_hash'],
      zip_safe=False)
