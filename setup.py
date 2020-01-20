from distutils.core import setup
setup(
  name = 'seapie',
  packages = ['seapie'],
  version = '1.2.1',
  license='Unlisence',
  description = 'Seapie is debugger like tool with ability to escape scopes in call stack',
  author = 'Markus Hirsimäki',
  author_email = 'hirsimaki.markus@gmail.com',
  url = 'https://github.com/hirsimaki-markus/SEAPIE',
  download_url = 'https://github.com/hirsimaki-markus/SEAPIE/archive/v_1_2.tar.gz',
  keywords = ['debugger', 'seapie', 'interactive', 'injection', 'inject', 'repl'],
  install_requires=[],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: Other/Proprietary License',
    'Programming Language :: Python :: 3.7',
  ],
)