#!/usr/bin/env python3
"""
Converts each .ktx from the data directory to .json and back,
and compares the resulting .ktx file against the original.
"""

import filecmp
import pathlib
import subprocess


EXECUTABLE   = 'ktxjuggle'
SOURCE_FILES = pathlib.Path('data').glob('**/*.ktx')
TARGET_DIR   = pathlib.Path('temp/roundtrip')


def testKtxRoundtrip(source, target):
	json = target.with_suffix('.json')
	target.parent.mkdir(parents=True, exist_ok=True)
	subprocess.run([EXECUTABLE, '--log-level=WARNING', source, json])
	subprocess.run([EXECUTABLE, '--log-level=WARNING', json, target])
	return filecmp.cmp(source, target)


summary = '  OK'
for source in sorted(SOURCE_FILES):
	if testKtxRoundtrip(source, TARGET_DIR/source):
		print('  ok ', source)
	else:
		print(' fail', source)
		summary = ' FAIL'
print(summary)
