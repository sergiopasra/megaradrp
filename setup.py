
from setuptools import find_packages, setup
from setuptools import setup, Extension

# try to handle gracefully Cython
try:
    from Cython.Distutils import build_ext
    ext1 = Extension('megaradrp.trace._traces',
                     ['megaradrp/trace/traces.pyx',
                      'megaradrp/trace/Trace.cpp'],
                     language='c++')
    cmdclass = {'build_ext': build_ext}
except ImportError:
    print('We do not have Cython, just using the generated files')
    ext1 = Extension('megaradrp.trace._traces',
                     ['megaradrp/trace/traces.cpp',
                      'megaradrp/trace/Trace.cpp'],
                     language='c++')
    cmdclass = {}

setup(name='megaradrp',
      version='0.5.dev',
      author='Sergio Pascual',
      author_email='sergiopr@fis.ucm.es',
      url='http://guaix.fis.ucm.es/hg/megaradrp',
      license='GPLv3',
      description='MEGARA Data Reduction Pipeline',
      packages=find_packages(),
      package_data={'megaradrp': ['drp.yaml', 'primary.txt']},
      install_requires=['numpy', 'astropy', 'scipy', 'numina>=0.13.0'],
      zip_safe=False,
      ext_modules=[ext1],
      cmdclass=cmdclass,
      entry_points = {
        'numina.pipeline.1': [
            'megara = megaradrp.loader:megara_drp_load',
            ]
        },
      classifiers=[
                   "Programming Language :: Python :: 2.7",
                   'Development Status :: 3 - Alpha',
                   "Environment :: Other Environment",
                   "Intended Audience :: Science/Research",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Operating System :: OS Independent",
                   "Topic :: Scientific/Engineering :: Astronomy",
                   ],
    long_description=open('README.txt').read()
)
