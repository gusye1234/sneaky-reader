import setuptools

vars2find = ['__author__', '__version__', '__url__']
vars_project = {}
with open('./sneaky_reader/__init__.py') as f:
    for line in f.readlines():
        for v in vars2find:
            if line.startswith(v):
                line = line.replace(' ', '').replace("\"", '').replace("\'", '').strip()
                vars_project[v] = line.split('=')[1]

with open('readme.md', 'r') as fh:
    long_description = fh.read()
print(long_description)
setuptools.setup(
    name='sneaky_reader',
    url=vars_project['__url__'],
    version=vars_project['__version__'],
    author=vars_project['__author__'],
    description='undercover book-reader in your terminal',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['sneaky_reader'],
    package_data={
        "": ["./sneaky_reader/*.css"]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    include_package_data=True,
    python_requires='>=3.6',
    install_requires=["textual"],
    entry_points={
        'console_scripts': [
            'sneaky_reader = sneaky_reader:main',
        ]
    },
)