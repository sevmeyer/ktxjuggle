ktxjuggle
=========

Converts [KTX] texture files to [JSON] and back.

This is a debugging tool, to inspect and produce KTX test files.
For this purpose, the input data is preserved whenever possible,
even if it is nonsensical. Any detected nonsense is logged to stderr.


Usage
-----

    ktxjuggle [--help] [--version] [--endian STR] [--log-level STR] IN [OUT]

If the output argument is omitted, then JSON
is printed to stdout and no files are written.
If the output file is JSON, then the pixel data
is written to separate binary files.

    ktxjuggle foo.ktx           # Print JSON to stdout
    ktxjuggle foo.ktx bar.json  # Write JSON file
    ktxjuggle bar.json qux.ktx  # Write KTX file


Byte encoding
-------------

In JSON, the identifier and the key-value pairs
are stored as [Percent-encoded] ASCII strings.
Each byte is written as `%XX`, where X is a
case insensitive hexadecimal digit. Printable ASCII
characters (%20 - %7E) are written directly, except
for the percent (%25), double quote (%22), and backslash (%5C).


Endianness
----------

Binary files are read and written in little endian by default.
KTX input files are automatically converted to little endian
when the endianness marker is equal to `0x01020304`.
To write a big endian KTX file, use the option `--endian big`.

Note that little endian is mandatory for [KTX2].


Installation
------------

Requires Python 3.6 or later.

To install, run pip3 from this directory.
For a local installation without root access, use option `--user`.

    pip3 install --user .
    pip3 uninstall ktxjuggle



[KTX]: https://www.khronos.org/opengles/sdk/tools/KTX/file_format_spec/
[KTX2]: https://github.com/KhronosGroup/KTX-Specification
[JSON]: https://json.org/
[Percent-encoded]: https://en.wikipedia.org/wiki/Percent_encoding
