from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'my_gazebo_learn'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'worlds'),
         glob('worlds/*.world')),
        (os.path.join('share', package_name, 'config'),
         glob('config/*.yaml')),
        (os.path.join('share', package_name, 'urdf'),
         glob('urdf/*.xacro')),
        ('share/' + package_name + '/urdf', ['urdf/panda.urdf']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Bin-SR',
    maintainer_email='1072235132@qq.com',
    description='Panda robot arm Gazebo simulation for embodied AI learning',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [],
    },
)
