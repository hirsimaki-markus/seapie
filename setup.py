from distutils.core import setup
setup(
  name = 'seapie',
  packages = ['seapie'],
  version = '2.0',
  license='Unlisence',
  description = 'Seapie is easy to use python debugger',
  author = 'Markus Hirsimäki',
  author_email = 'hirsimaki.markus@gmail.com',
  url = 'https://github.com/hirsimaki-markus/SEAPIE',
  download_url = 'https://github.com/hirsimaki-markus/SEAPIE/archive/v2.0.tar.gz',
  keywords = ['debugger', 'seapie', 'interactive', 'injection', 'inject', 'repl', 'debg', 'exec'],
  install_requires=[],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: Other/Proprietary License',
    'Programming Language :: Python :: 3.7',
  ],
)