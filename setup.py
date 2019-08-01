import pathlib
import setuptools


def readVersion(relativePath):
	path = pathlib.Path(__file__).parent / relativePath
	with open(path) as stream:
		for line in stream:
			if line.startswith('__version__'):
				return line.replace('"', "'").split("'")[1]
		raise RuntimeError('Could not find version string')


setuptools.setup(
	name='ktxjuggle',
	version=readVersion('ktxjuggle/__init__.py'),
	description='Converts KTX texture files to JSON and back',
	url='https://github.com/sevmeyer/ktxjuggle',
	author='Severin Meyer',
	author_email='hello@sev.dev',
	license='Boost Software License 1.0',

	packages=['ktxjuggle'],
	entry_points={'console_scripts': ['ktxjuggle=ktxjuggle.__main__:main']},
	python_requires='>=3.6',
)
