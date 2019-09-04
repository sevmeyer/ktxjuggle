import collections
import io
import json
import logging
import math

from ktxjuggle import binary
from ktxjuggle import opengl as gl


logger = logging.getLogger(__name__)


class Ktx:

	IDENTIFIER = b'\xABKTX 11\xBB\r\n\x1A\n'

	def __init__(self):
		self.identifier            = None
		self.endianness            = None
		self.glType                = None
		self.glTypeSize            = None
		self.glFormat              = None
		self.glInternalFormat      = None
		self.glBaseInternalFormat  = None
		self.pixelWidth            = None
		self.pixelHeight           = None
		self.pixelDepth            = None
		self.numberOfArrayElements = None
		self.numberOfFaces         = None
		self.numberOfMipmapLevels  = None
		self.bytesOfKeyValueData   = None
		self.metadata              = []  # [(bytes, bytes)]
		self.levels                = []  # [(int, [bytes])]

	@classmethod
	def fromBinary(cls, stream):
		ktx = cls()
		reader = binary.Reader(stream)

		ktx.identifier = reader.bytes(12)
		ktx.endianness = reader.uint32()
		if ktx.endianness == 0x01020304:
			reader.endian = 'big'
			logger.info('Input is big endian')

		ktx.glType                = reader.uint32()
		ktx.glTypeSize            = reader.uint32()
		ktx.glFormat              = reader.uint32()
		ktx.glInternalFormat      = reader.uint32()
		ktx.glBaseInternalFormat  = reader.uint32()
		ktx.pixelWidth            = reader.uint32()
		ktx.pixelHeight           = reader.uint32()
		ktx.pixelDepth            = reader.uint32()
		ktx.numberOfArrayElements = reader.uint32()
		ktx.numberOfFaces         = reader.uint32()
		ktx.numberOfMipmapLevels  = reader.uint32()
		ktx.bytesOfKeyValueData   = reader.uint32()

		metaBytes  = reader.bytes(ktx.bytesOfKeyValueData)
		metaStream = io.BytesIO(metaBytes)
		metaReader = binary.Reader(metaStream)
		metaReader.endian = reader.endian
		while metaReader:
			try:
				keyAndValueByteSize = metaReader.uint32()
				keyAndValue = metaReader.bytes(keyAndValueByteSize)
				metaReader.align(4)
				if b'\0' in keyAndValue:
					key, value = keyAndValue.split(b'\0', maxsplit=1)
					ktx.metadata.append((key, value))
				else:
					logger.warning('keyAndValue is missing a NUL separator')
			except EOFError:
				logger.warning('keyAndValueByteSize overruns bytesOfKeyValueData')
				break

		levelCount = ktx.numberOfMipmapLevels
		if levelCount == 0 or ktx.isOESCPT():
			levelCount = 1
		for mipmap_level in range(levelCount):
			try:
				imageSize = reader.uint32()
				images = []
				for face in range(6 if ktx.isNonArrayCubemap() else 1):
					images.append(reader.bytes(imageSize, ktx.glTypeSize))
					reader.align(4)
				ktx.levels.append((imageSize, images))
			except EOFError:
				logger.warning('Unexpected EOF while reading image data')
				break

		if reader:
			logger.warning('Unexpected bytes after last image')

		ktx.validate()
		return ktx

	@classmethod
	def fromJson(cls, stream, imageDir):
		ktx = cls()
		js = json.load(stream, object_pairs_hook=collections.OrderedDict)

		if js['format'] != "KTX 11":
			raise ValueError('Unkown format: ' + js['format'])

		header = js['header']
		ktx.identifier            = binary.pctDecode(header['identifier'])
		ktx.endianness            = int(header['endianness'], 0)
		ktx.glType                = gl.getValue(header['glType'])
		ktx.glTypeSize            = int(header['glTypeSize'])
		ktx.glFormat              = gl.getValue(header['glFormat'])
		ktx.glInternalFormat      = gl.getValue(header['glInternalFormat'])
		ktx.glBaseInternalFormat  = gl.getValue(header['glBaseInternalFormat'])
		ktx.pixelWidth            = int(header['pixelWidth'])
		ktx.pixelHeight           = int(header['pixelHeight'])
		ktx.pixelDepth            = int(header['pixelDepth'])
		ktx.numberOfArrayElements = int(header['numberOfArrayElements'])
		ktx.numberOfFaces         = int(header['numberOfFaces'])
		ktx.numberOfMipmapLevels  = int(header['numberOfMipmapLevels'])
		ktx.bytesOfKeyValueData   = int(header['bytesOfKeyValueData'])

		if 'metadata' in js:
			for key, value in js['metadata'].items():
				ktx.metadata.append((binary.pctDecode(key), binary.pctDecode(value)))

		if 'levels' in js:
			for level in js['levels']:
				imageSize = int(level['imageSize'])
				images = []
				for image in level['images']:
					images.append(imageDir.joinpath(image).read_bytes())
				ktx.levels.append((imageSize, images))

		ktx.validate()
		return ktx

	def toBinary(self, stream):
		writer = binary.Writer(stream)

		writer.bytes(self.identifier)
		writer.uint32(self.endianness)
		if self.endianness == 0x01020304:
			writer.endian = 'big'
			logger.info('Output is big endian')

		writer.uint32(self.glType)
		writer.uint32(self.glTypeSize)
		writer.uint32(self.glFormat)
		writer.uint32(self.glInternalFormat)
		writer.uint32(self.glBaseInternalFormat)
		writer.uint32(self.pixelWidth)
		writer.uint32(self.pixelHeight)
		writer.uint32(self.pixelDepth)
		writer.uint32(self.numberOfArrayElements)
		writer.uint32(self.numberOfFaces)
		writer.uint32(self.numberOfMipmapLevels)
		writer.uint32(self.bytesOfKeyValueData)

		for key, value in self.metadata:
			keyAndValue = key + b'\0' + value
			writer.uint32(len(keyAndValue))
			writer.bytes(keyAndValue)
			writer.align(4)

		for imageSize, images in self.levels:
			writer.uint32(imageSize)
			for image in images:
				writer.bytes(image, self.glTypeSize)
				writer.align(4)

	def toJson(self, stream, imageDir, imageStem):
		stream.write(
			f'{{\n'
			f'  "format": "KTX 11",\n'
			f'  "header": {{\n'
			f'    "identifier":            "{binary.pctEncode(self.identifier)}",\n'
			f'    "endianness":            "0x{self.endianness:08x}",\n'
			f'    "glType":                "{gl.getName(self.glType)}",\n'
			f'    "glTypeSize":            {self.glTypeSize},\n'
			f'    "glFormat":              "{gl.getName(self.glFormat)}",\n'
			f'    "glInternalFormat":      "{gl.getName(self.glInternalFormat)}",\n'
			f'    "glBaseInternalFormat":  "{gl.getName(self.glBaseInternalFormat)}",\n'
			f'    "pixelWidth":            {self.pixelWidth},\n'
			f'    "pixelHeight":           {self.pixelHeight},\n'
			f'    "pixelDepth":            {self.pixelDepth},\n'
			f'    "numberOfArrayElements": {self.numberOfArrayElements},\n'
			f'    "numberOfFaces":         {self.numberOfFaces},\n'
			f'    "numberOfMipmapLevels":  {self.numberOfMipmapLevels},\n'
			f'    "bytesOfKeyValueData":   {self.bytesOfKeyValueData}\n'
			f'  }}')

		if self.metadata:
			stream.write(',\n  "metadata": {')
			for i, (key, value) in enumerate(self.metadata):
				stream.write(',\n' if i > 0 else '\n')
				stream.write(f'    "{binary.pctEncode(key)}": "{binary.pctEncode(value)}"')
			stream.write('\n  }')

		if self.levels:
			stream.write(',\n  "levels": [')
			maxSizeLen = len(str(max(self.levels)[0]))
			for mip, (imageSize, images) in enumerate(self.levels):
				stream.write(',\n' if mip > 0 else '\n')
				stream.write(f'    {{"imageSize": {imageSize: >{maxSizeLen}}, "images": [')
				for face, image in enumerate(images):
					if len(images) == 1:
						name = f'{imageStem}.{mip}.bin'
					else:
						name = f'{imageStem}.{mip}.{face}.bin'
						stream.write(',\n      ' if face > 0 else '\n      ')
					stream.write(f'"{name}"')

					# Write binary image file
					if imageDir:
						imageDir.joinpath(name).write_bytes(image)

				stream.write(']}')
			stream.write('\n  ]')

		stream.write('\n')
		stream.write('}\n')

	# Helpers

	def isOESCPT(self):
		return 0x8B90 <= self.glInternalFormat <= 0x8B99

	def isNonArrayCubemap(self):
		return self.numberOfArrayElements == 0 and self.numberOfFaces == 6

	def validate(self):
		# NOTE: This validation is incomplete. Some missing checks:
		# - Correct combination of types and formats
		# - Correct imageSize according to format

		if self.identifier != Ktx.IDENTIFIER:
			logger.warning('Invalid identifier')

		if self.endianness != 0x04030201 and self.endianness != 0x01020304:
			logger.warning('Invalid endianness')

		if self.glTypeSize == 0:
			logger.warning('glTypeSize should never be 0')

		if self.pixelWidth == 0:
			logger.warning('pixelWidth should never be 0')

		if self.pixelHeight == 0 and self.pixelDepth != 0:
			logger.warning('pixelHeight should not be 0, because pixelDepth is not 0')

		if self.numberOfFaces != 1 and self.numberOfFaces != 6:
			logger.warning('numberOfFaces should be 1 or 6')

		if self.numberOfFaces != 1 and self.isOESCPT():
			logger.warning('numberOfFaces should be 1 because glInternalFormat is GL_PALETTE*')

		if not self.isOESCPT():
			if max(1, self.numberOfMipmapLevels) != len(self.levels):
				logger.warning('numberOfMipmapLevels does not match actual number of levels')

		maxDimension = max(self.pixelWidth, self.pixelHeight, self.pixelDepth)
		if self.numberOfMipmapLevels > math.floor(math.log2(maxDimension)) + 1:
			logger.warning('Too many mipmap levels')

		if self.bytesOfKeyValueData == 0 and self.metadata:
			logger.warning('bytesOfKeyValueData should not be 0 because there is metadata')
		if self.bytesOfKeyValueData != 0 and not self.metadata:
			logger.warning('bytesOfKeyValueData should be 0 because there is no metadata')

		prevKeys = set()
		for key, value in self.metadata:
			if not key:
				logger.info('metadata contains empty key (allowed, but weird)')
			if not value:
				logger.info('metadata contains empty value (allowed, but weird)')
			if key in prevKeys:
				logger.info('metadata contains duplicate key (allowed, but weird)')
			if key.startswith(b'KTX') or key.startswith(b'ktx'):
				if key == b'KTXorientation':
					if value not in (b'S=r,T=d\x00', b'S=r,T=u\x00', b'S=r,T=d,R=i\x00', b'S=r,T=u,R=o\x00'):
						logger.info('KTXorientation uses unrecommended value: %s', binary.pctEncode(value))
				else:
					logger.info('Unknown key name with reserved KTX prefix: %s', binary.pctEncode(key))
			prevKeys.add(key)

		prevImageSize = 0xffffffff
		for imageSize, images in self.levels:
			if self.numberOfFaces != len(images):
				logger.warning('number of images in mipmap layer does not match numberOfFaces')
			if imageSize > prevImageSize:
				logger.warning('imageSize should be in decreasing order')
			for image in images:
				if imageSize != len(image):
					logger.warning('imageSize does not match actual image size')
				if self.glTypeSize != 0 and len(image) % self.glTypeSize != 0:
					logger.warning('imageSize is not multiple of glTypeSize')
			prevImageSize = imageSize
