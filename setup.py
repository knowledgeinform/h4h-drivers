from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'takbridge'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    package_data={
        package_name: [
            'config/config.yaml',
            'certs/*',
            'certs/files/*'
        ]
    },
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'config'),
            ['takbridge/config/config.yaml']),
        (os.path.join('share', package_name, 'certs'),
            glob('takbridge/certs/*.p12')),
        (os.path.join('share', package_name, 'certs/files'),
            glob('takbridge/certs/files/*')),

        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),
    ],
    install_requires=[
        'setuptools',
        'PyTAK',
        'cryptography',
        'numpy',  
        'tf-transformations'  
    ],
    zip_safe=True,
    maintainer='wimbime1',
    maintainer_email='miguel.wimbish@jhuapl.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'uvp_cot_bridge = takbridge.upv_cot_bridge:main',
        ],
    },
)

