from setuptools import setup

setup(name='picozk',
      version='0.2',
      description='PicoZK library & compiler for writing zero-knowledge statements',
      url='none',
      author='Joe Near',
      author_email='jnear@uvm.edu',
      license='GPLv3',
      install_requires=[
          "ecdsa==0.18.0",
          "numpy==1.21.6",
          "pandas==1.3.5"],
      packages=['picozk', 'picozk/poseidon_hash'],
      zip_safe=False)
