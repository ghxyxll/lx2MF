# lx2MF - lxmusic to MusicFree Playlist Converter

A simple tool to convert playlists from lxmusic format to MusicFree format, allowing users to migrate their music playlists between these applications.

## Features

- Convert lxmusic playlist files (JSON format) to MusicFree format
- Preserve song metadata including title, artist, album, and duration
- Command-line interface for easy usage
- Support for batch conversion
- Proper error handling and validation

## Installation

1. Clone this repository:
```bash
git clone https://github.com/ghxyxll/lx2MF.git
cd lx2MF
```

2. Make sure you have Python 3.6+ installed

## Usage

### Basic Usage

Convert a single playlist:
```bash
python lx2mf.py input_playlist.json
```

This will create `input_playlist.musicfree.json` in the same directory.

### Specify Output File

```bash
python lx2mf.py input_playlist.json -o my_converted_playlist.json
```

### Help

```bash
python lx2mf.py --help
```

## File Formats

### lxmusic Format (Input)
```json
{
  "name": "Playlist Name",
  "description": "Playlist description",
  "list": [
    {
      "id": "unique_id",
      "name": "Song Title",
      "singer": "Artist Name",
      "album": "Album Name",
      "interval": 240000,
      "source": "local",
      "url": "https://example.com/song"
    }
  ]
}
```

### MusicFree Format (Output)
```json
{
  "version": "1.0",
  "type": "playlist",
  "name": "Playlist Name",
  "description": "Playlist description",
  "songs": [
    {
      "title": "Song Title",
      "artist": "Artist Name",
      "album": "Album Name",
      "duration": 240000,
      "source": "local",
      "url": "https://example.com/song",
      "id": "unique_id"
    }
  ]
}
```

## Examples

See `example_lxmusic_playlist.json` for a sample input file.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Feel free to submit issues and pull requests to improve this tool.
