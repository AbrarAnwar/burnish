from setuptools import setup, find_packages

from burnish import __version__

extra_math = [
    'returns-decorator',
]

extra_bin = [
]

extra_test = [

]
extra_dev = [
]

extra_ci = [

]


from setuptools import setup, find_packages

CLASSIFIERS = [
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
]

setup(
    name='burnish',
    version=__version__,
    description='A package for running jobs easily for SLURM',

    url='',
    author='Abrar Anwar',
    author_email='abraranw@usc.edu',
    entry_points={"console_scripts": ["burnish = burnish:cli"]},
    packages=find_packages(),
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    zip_safe=False,
    classifiers=CLASSIFIERS,
    install_requires=[
        'pandas', 'argparse'
    ],
 )