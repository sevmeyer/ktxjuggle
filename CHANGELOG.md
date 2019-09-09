## Unreleased

- Automatically converts to big endian if marker is "0x01020304".
- Removed --endian option.
- Can now read JSON without "metadata" or "levels".
- Does not write empty "metadata" or "levels" to JSON.
- Switched from dict to array for "metadata", to preserve order and duplicates.
- Small or repetitive images are inlined in JSON as percent-encoded strings.
- Shortened option name --log-level to --log.

## 0.2.0 (2019-08-20)

- Creates target directory if it doesn't exist.
- Improved validation.

## 0.1.0 (2019-08-01)

- Initial release.
