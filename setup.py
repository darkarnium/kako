from setuptools import find_packages, setup, Command

setup(
    name='kako',
    version='1.0',
    description='Manifest driven IoT honeypots',
    author='Peter Adkins',
    author_email='peter.adkins@kernelpicnic.net',
    url='https://www.github.com/darkarnium/kako',
    packages=find_packages('src'),
    license='MIT',
    download_url='https://github.com/darkarnium/kako/archive/1.0.0.tar.gz',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    package_dir={
        'kako': 'src/kako',
    },
    scripts=[
        'src/kako-master'
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
    install_requires=[
        'click==6.6',
        'boto3==1.4.1',
        'PyYAML==3.12',
        'requests==2.11.1',
        'cerberus==1.0.1',
    ]
)
