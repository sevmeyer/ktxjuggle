ktxjuggle
=========

Converts [KTX] texture files to [JSON] and back.

This is a debugging tool, to inspect and produce KTX test files.
For this purpose, the input data is preserved whenever possible,
even if it is nonsensical. Any detected nonsense is logged to stderr.


Usage
-----

    ktxjuggle --help            # Show available options
    ktxjuggle foo.ktx           # Print JSON to stdout
    ktxjuggle foo.ktx bar.json  # Write JSON file
    ktxjuggle bar.json qux.ktx  # Write KTX file

If the output argument is omitted, then JSON
is printed to stdout and no files are written.
If the output file is JSON, then the pixel data
is written to separate binary files.


Byte encoding
-------------

In JSON, the identifier and the key-value pairs
are stored as [Percent-encoded] ASCII strings.
Each byte is written as `%XX`, where X is a
case insensitive hexadecimal digit. Printable ASCII
characters (%20 - %7E) are written directly, except
for the percent (%25), double quote (%22), and backslash (%5C).

If an image consists of a short repeating byte pattern,
it is inlined in JSON as a percent-encoded string.
This can be turned off with `--inline 0`.


Endianness
----------

Binary files are little endian by default.
If the endianness marker is equal to `0x01020304`
(little endian byte sequence 0x04 0x03 0x02 0x01),
then a KTX file is read and written in big endian.

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
