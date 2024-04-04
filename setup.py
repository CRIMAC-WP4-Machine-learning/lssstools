from setuptools import setup

setup(name='ektools',
      version='0.1.0',
      description='Utilities to read exports from LSSS',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      url='https://github.com/CRIMAC-WP4-Machine-learning/lssstools',
      author='Nils Olav Handegard',
      author_email='nilsolav@hi.no',
      license='MIT',
      packages=['lssstools'],
      scripts=[],
      install_requires=['json', 'pandas'],
      zip_safe=False)
