import os


class Reader:

	def __init__(self, stream):
		self.stream = stream
		self.endian = 'little'

	def __bool__(self):
		# Let me know if there is a better way
		if self.stream.read(1):
			self.stream.seek(-1, os.SEEK_CUR)
			return True
		return False

	def bytes(self, size, wordSize=1):
		if self.endian == 'big' and wordSize > 1:
			b = bytearray()
			for _ in range(size // wordSize):
				b.extend(reversed(self.stream.read(wordSize)))
			b.extend(reversed(self.stream.read(size % wordSize)))
		else:
			b = self.stream.read(size)

		if len(b) != size:
			raise EOFError('Unexpected EOF')
		return b

	def uint32(self):
		return int.from_bytes(self.bytes(4), byteorder=self.endian, signed=False)

	def align(self, size):
		padding = (size - (self.stream.tell() % size)) % size
		self.bytes(padding)


class Writer:

	def __init__(self, stream):
		self.stream = stream
		self.endian = 'little'

	def bytes(self, b, wordSize=1):
		if self.endian == 'big' and wordSize > 1:
			for i in range(0, len(b), wordSize):
				self.stream.write(bytes(reversed(b[i:i+wordSize])))
		else:
			self.stream.write(b)

	def uint32(self, i):
		self.bytes(i.to_bytes(4, byteorder=self.endian, signed=False))

	def align(self, size):
		padding = (size - (self.stream.tell() % size)) % size
		self.bytes(b'\0' * padding)


def pctEncode(binary, allowPrintable=True):
	string = ''
	for b in binary:
		if allowPrintable and 0x20 <= b <= 0x7E and b not in b'%"\\':
			string += chr(b)
		else:
			string += f'%{b:02X}'
	return string


def pctDecode(string):
	binary = bytearray()
	i = 0
	while i < len(string):
		if string[i] == '%':
			binary.append(int(string[i+1:i+3], 16))
			i += 3
		elif 0x20 <= ord(string[i]) <= 0x7E:
			binary.append(ord(string[i]))
			i += 1
		else:
			raise ValueError('Invalid byte string encoding: ' + string)
	return bytes(binary)


def findPattern(b, maxLength):
	for length in range(1, maxLength + 1):
		if len(b) % length == 0:
			pattern = b[0:length]
			for offset in range(length, len(b), length):
				if b[offset:offset + length] != pattern:
					pattern = None
					break
			if pattern:
				return pattern
	return None


def nameToBytes(size, name, directory):
	if name.startswith('%'):
		pattern = pctDecode(name)
		repeats = size // len(pattern)
		if len(pattern)*repeats != size:
			raise ValueError('Pattern does not fit into image size: ' + name)
		return pattern * repeats
	else:
		return directory.joinpath(name).read_bytes()


def bytesToName(b, name, directory, maxInline):
	pattern = findPattern(b, maxInline)
	if pattern:
		return pctEncode(pattern, allowPrintable=False)
	else:
		if directory:
			directory.joinpath(name).write_bytes(b)
		return name
