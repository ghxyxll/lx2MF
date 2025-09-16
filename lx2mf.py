#!/usr/bin/env python3
"""
lx2MF - Convert lxmusic playlists to MusicFree format

This tool converts playlist files from lxmusic format to MusicFree format,
allowing users to migrate their music playlists between these applications.
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any


class PlaylistConverter:
    """Main class for converting playlists between lxmusic and MusicFree formats."""
    
    def __init__(self):
        self.supported_extensions = ['.json', '.lxmusic']
    
    def load_lxmusic_playlist(self, file_path: Path) -> Dict[str, Any]:
        """Load and parse an lxmusic playlist file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in lxmusic playlist file: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Playlist file not found: {file_path}")
    
    def convert_to_musicfree(self, lxmusic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert lxmusic playlist data to MusicFree format."""
        # Basic conversion structure - will need to be refined based on actual formats
        musicfree_playlist = {
            "version": "1.0",
            "type": "playlist",
            "name": lxmusic_data.get("name", "Imported Playlist"),
            "description": lxmusic_data.get("description", ""),
            "songs": []
        }
        
        # Convert songs
        songs = lxmusic_data.get("songs", lxmusic_data.get("list", []))
        for song in songs:
            converted_song = self.convert_song(song)
            if converted_song:
                musicfree_playlist["songs"].append(converted_song)
        
        return musicfree_playlist
    
    def convert_song(self, song: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single song from lxmusic to MusicFree format."""
        # Basic song conversion - will need refinement
        return {
            "title": song.get("name", song.get("title", "")),
            "artist": song.get("singer", song.get("artist", "")),
            "album": song.get("album", ""),
            "duration": song.get("interval", song.get("duration", 0)),
            "source": song.get("source", ""),
            "url": song.get("url", ""),
            "id": song.get("id", "")
        }
    
    def save_musicfree_playlist(self, data: Dict[str, Any], output_path: Path) -> None:
        """Save the converted playlist in MusicFree format."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise IOError(f"Failed to save MusicFree playlist: {e}")
    
    def convert_playlist(self, input_path: Path, output_path: Path) -> None:
        """Main conversion method."""
        print(f"Loading lxmusic playlist from: {input_path}")
        lxmusic_data = self.load_lxmusic_playlist(input_path)
        
        print("Converting to MusicFree format...")
        musicfree_data = self.convert_to_musicfree(lxmusic_data)
        
        print(f"Saving MusicFree playlist to: {output_path}")
        self.save_musicfree_playlist(musicfree_data, output_path)
        
        song_count = len(musicfree_data.get("songs", []))
        print(f"✅ Successfully converted {song_count} songs!")


def main():
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Convert lxmusic playlists to MusicFree format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lx2mf.py playlist.json -o musicfree_playlist.json
  python lx2mf.py my_songs.lxmusic --output converted_playlist.json
        """
    )
    
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the lxmusic playlist file"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output path for the MusicFree playlist (default: input name with .musicfree.json extension)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="lx2MF 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input.exists():
        print(f"❌ Error: Input file does not exist: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    # Set default output path if not provided
    if not args.output:
        args.output = args.input.with_suffix('.musicfree.json')
    
    # Ensure output directory exists
    args.output.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        converter = PlaylistConverter()
        converter.convert_playlist(args.input, args.output)
    except (ValueError, FileNotFoundError, IOError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()