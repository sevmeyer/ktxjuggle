"""
Converts KTX texture files to JSON and back.
If the output argument is omitted, then JSON
is printed to stdout and no files are written.
If the output file is JSON, then the pixel data
is written to separate binary files.
"""

import argparse
import logging
import pathlib
import sys

import ktxjuggle


logger = logging.getLogger(__name__)


def main():

	parser = argparse.ArgumentParser(
		description=__doc__,
		formatter_class=argparse.RawDescriptionHelpFormatter)
	parser.add_argument(
		'--version',
		action='version',
		version=ktxjuggle.__version__)
	parser.add_argument(
		'--log-level',
		type=str,
		metavar='STR',
		choices=['DEBUG', 'WARNING', 'ERROR', 'OFF'],
		default='DEBUG',
		help='set log level to <DEBUG>, WARNING, ERROR, or OFF')
	parser.add_argument('IN', help='input file name')
	parser.add_argument('OUT', nargs='?', default='', help='output file name')
	args = parser.parse_args()

	if args.log_level != 'OFF':
		logging.basicConfig(format='%(levelname)s: %(message)s', level=args.log_level)

	try:
		# Input
		inPath = pathlib.Path(args.IN)
		if inPath.suffix == '.ktx':
			with open(inPath, mode='rb') as inStream:
				ktx = ktxjuggle.Ktx.fromBinary(inStream)
		elif inPath.suffix == '.json':
			with open(inPath, mode='r') as inStream:
				ktx = ktxjuggle.Ktx.fromJson(inStream, inPath.parent)
		else:
			raise ValueError('Input file must be .ktx or .json')

		# Output
		if not args.OUT:
			ktx.toJson(sys.stdout, None, inPath.stem)
		else:
			outPath = pathlib.Path(args.OUT)
			outPath.parent.mkdir(parents=True, exist_ok=True)
			if outPath.suffix == '.ktx':
				with open(outPath, mode='wb') as outStream:
					ktx.toBinary(outStream)
			elif outPath.suffix == '.json':
				with open(outPath, mode='w') as outStream:
					ktx.toJson(outStream, outPath.parent, outPath.stem)
			else:
				raise ValueError('Output file must be .ktx or .json')
	except Exception as e:
		logger.error(e)
		raise SystemExit(1)


if __name__ == '__main__':
	main()
