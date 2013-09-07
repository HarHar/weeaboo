#!/usr/bin/env python
"""
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import subprocess
import sys
import os

import inspect
def curDir():
	return os.path.dirname(inspect.getsourcefile(curDir)) + os.path.sep

class colors():
    def __init__(self):
        self.enable()
    def enable(self):
    	if os.name == 'nt':
    		self.disable()
    		return
        self.header = '\033[95m'
        self.blue = '\033[94m'
        self.green = '\033[92m'
        self.warning = '\033[93m'
        self.fail = '\033[91m'
        self.bold = '\033[1m'
        self.default = '\033[0m'
    def disable(self):
        self.header = ''
        self.blue = ''
        self.green = ''
        self.warning = ''
        self.fail = ''
        self.default = ''
        self.bold = ''

c = colors()

if '--compile-kakasi' in sys.argv:
	from time import sleep
	import urllib2

	workdir = os.path.join(curDir(), 'kakasi/')

	print('Creating directory for working in ('+ workdir +')')
	subprocess.Popen(['rm', '-r', workdir], stdout=-1, stderr=-1, stdin=-1).wait()
	os.mkdir(workdir)
	os.chdir(workdir)

	sys.stdout.write('Downloading kakasi (about 1073KB)...')
	sys.stdout.flush()
	data = urllib2.urlopen('http://kakasi.namazu.org/stable/kakasi-2.3.4.tar.gz').read()
	f = open('kakasi-2.3.4.tar.gz', 'w')
	f.write(data)
	f.close()
	sys.stdout.write(' done\n')
	sys.stdout.flush()

	print('Extracting kakasi-2.3.4.tar.gz...')
	sleep(1)
	subprocess.Popen(['tar', 'xfvz', 'kakasi-2.3.4.tar.gz']).wait()
	print('')

	print('Running ./configure')
	sleep(1)
	os.chdir('kakasi-2.3.4')
	if subprocess.Popen(['./configure'], shell=True).wait() != 0:
		print 'Something failed'
		exit(1)
	print('')

	print('Compiling...')
	sleep(2)
	if subprocess.Popen(['make']).wait() != 0:
		print 'Something failed'
		exit(1)
	print('')

	print('\n\nDONE!')
	exit(0)

jTransliterateURLs = {'https://raw.github.com/ryanmcgrath/jTransliterate/master/jTransliterate/__init__.py': 'jTransliterate.py',
                      'https://raw.github.com/ryanmcgrath/jTransliterate/master/jTransliterate/translation_maps.py': 'translation_maps.py'}

if (subprocess.Popen(['which', 'kakasi'], stdout=-1, stderr=-1).wait() != 0) or (os.path.exists(os.path.join(curDir(), 'kakasi/'))):
	sys.stderr.write('kakasi not found, falling back to hiragana/katakana table\n')
	if not os.path.exists(os.path.join(curDir(), '.nokakasi')):
		sys.stderr.write('without kakasi kanji will not get transliterated,\n')
		sys.stderr.write('you can get it from http://kakasi.namazu.org/\n')
		sys.stderr.write('if you want me to download and compile it for you, use the --compile-kakasi parameter\n')
		sys.stderr.write('this message will not appear again\n')
		open(os.path.join(curDir(), '.nokakasi'), 'w').close()

	kakasi = False

	try:
		from jTransliterate import JapaneseTransliterator
	except ImportError:
		sys.stderr.write('jTransliterate not found, downloading...')
		import urllib2
		import os

		for URL in jTransliterateURLs:
			data = urllib2.urlopen(URL).read()
			f = open(os.path.join(curDir(), jTransliterateURLs[URL]), 'w')
			f.write(data)
			f.close()
			del data

		from jTransliterate import JapaneseTransliterator
		sys.stderr.write(' done!\n')
else:
	kakasi = True


try:
	import translate
except ImportError:
	sys.stderr.write('translate not found, downloading...')
	import urllib2
	import os

	data = urllib2.urlopen('https://raw.github.com/terryyin/google-translate-python/master/translate.py').read()
	f = open(os.path.join(curDir(), 'translate.py'), 'w')
	f.write(data)
	f.close()
	del data

	import translate
	sys.stderr.write(' done!\n')

kakasipath = subprocess.Popen(['which', 'kakasi'], stdin=-1, stdout=-1, stderr=-1).communicate()[0].replace('\n', '')
if os.path.exists(os.path.join(curDir(), 'kakasi/')):
	kakasipath = os.path.join(curDir(), 'kakasi/kakasi-2.3.4/src/kakasi')

def transliterate(text):
	if kakasi:
		iconv = subprocess.Popen(['iconv', '-f', 'utf8', '-t', 'eucjp'], stdin=-1, stdout=-1, stderr=-1).communicate(text.encode('utf8'))
		k = subprocess.Popen([kakasipath, '-i', 'euc', '-Ha', '-Ka', '-Ja', '-Ea', '-ka'], stdin=-1, stdout=-1).communicate(iconv[0])
		return k[0]
	else:
		return JapaneseTransliterator(text).transliterate_from_hrkt_to_latn()

if len(sys.argv) == 1:
	print c.warning + 'Usage: ' + c.default + sys.argv[0] + ' <moonrunes>'
else:
	t = ' '.join(sys.argv[1:])
	print c.header + 'Original:    ' + c.default + ' '.join(t.decode('utf8'))
	print c.header + 'Romaji:      ' + c.default + transliterate(' '.join(t.decode('utf8')))

	translator = translate.Translator(to_lang='en', from_lang='jp')
	print c.header + 'Translation: ' + c.default + translator.translate(t)
	print ''