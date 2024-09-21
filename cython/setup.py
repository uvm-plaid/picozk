from setuptools import setup

from Cython.Build import cythonize
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(ext_modules=cythonize([Extension("emp_bridge",
                                       ["emp_bridge.pyx"],
                                       language='c++',
                                       #libraries=['libemp-tool'],
                                       libraries=['crypto'],
                                       extra_objects=["/usr/local/lib/libemp-tool.so",
                                                      "/usr/local/lib/libemp-zk.so"],
                                       extra_compile_args=["-march=native", "-maes", "-mrdseed"],
                                       #gdb_debug=True
                                       )]))
