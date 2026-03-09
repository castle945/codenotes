from setuptools import find_packages, setup

# with open('README.md', 'r') as fh:
#     long_description = fh.read()

if __name__ == '__main__':
    setup(
        name='mmdemo',
        version='0.0.0',
        packages=find_packages(exclude=['configs', 'tools']),
        author='city945',
        author_email='city945@njust.edu.cn',
        url='https://github.com/city945',
        description='A demo',
        # long_description=long_description,
        long_description_content_type='text/markdown',
        classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: OS Independent',
        ],
    )