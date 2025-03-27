from setuptools import setup


setup(
    name='lexibank_analysed',
    version='2.1',
    description='Lexibank Analysed',
    author='',
    author_email='',
    long_description=open('README.md', encoding='utf8').read(),
    long_description_content_type='text/markdown',
    keywords='',
    license='MIT',
    url='https://github.com/lexibank/lexibank-analysed',
    py_modules=['lexibank_lexibank_analysed'],
    packages=['lexibank_analysed_commands'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'lexibank-analysed=lexibank_lexibank_analysed:Dataset',
        ],
        'cldfbench.commands': [
            'lexibank-analysed=lexibank_analysed_commands',
        ],
    },
    platforms='any',
    python_requires='>=3.8',
    install_requires=[
        'cldfbench>=1.7.2',
        'cltoolkit>=0.1.1',
        'cldfviz>=0.3.0',
        'cldfzenodo',
        'pylexibank',
        'cartopy',
        'pillow',
        'matplotlib',
        'scipy',
    ],
    extras_require={
        'dev': ['flake8', 'wheel', 'twine'],
        'test': [
            'pytest>=6',
            'pytest-mock',
            'pytest-cov',
            'pytest-cldf',
            'coverage',
        ],
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
