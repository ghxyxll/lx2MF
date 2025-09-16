#!/usr/bin/env python3
"""
Tests for lx2MF playlist converter
"""

import json
import tempfile
import unittest
from pathlib import Path
import sys
import os

# Add the current directory to the path so we can import our module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lx2mf import PlaylistConverter


class TestPlaylistConverter(unittest.TestCase):
    """Test cases for the PlaylistConverter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.converter = PlaylistConverter()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Sample lxmusic playlist data
        self.sample_lxmusic_data = {
            "name": "Test Playlist",
            "description": "A test playlist",
            "version": "1.0",
            "list": [
                {
                    "id": "test1",
                    "name": "Test Song 1",
                    "singer": "Test Artist 1",
                    "album": "Test Album 1",
                    "interval": 240000,
                    "source": "local",
                    "url": ""
                },
                {
                    "id": "test2",
                    "name": "Test Song 2", 
                    "singer": "Test Artist 2",
                    "album": "Test Album 2",
                    "interval": 180000,
                    "source": "streaming",
                    "url": "https://example.com/test2"
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        for file in self.temp_dir.glob("*"):
            file.unlink()
        self.temp_dir.rmdir()
    
    def test_convert_to_musicfree(self):
        """Test conversion from lxmusic to MusicFree format."""
        result = self.converter.convert_to_musicfree(self.sample_lxmusic_data)
        
        # Check basic structure
        self.assertEqual(result["name"], "Test Playlist")
        self.assertEqual(result["description"], "A test playlist")
        self.assertEqual(result["version"], "1.0")
        self.assertEqual(result["type"], "playlist")
        self.assertEqual(len(result["songs"]), 2)
        
        # Check first song conversion
        song1 = result["songs"][0]
        self.assertEqual(song1["title"], "Test Song 1")
        self.assertEqual(song1["artist"], "Test Artist 1")
        self.assertEqual(song1["album"], "Test Album 1")
        self.assertEqual(song1["duration"], 240000)
        self.assertEqual(song1["source"], "local")
        self.assertEqual(song1["id"], "test1")
    
    def test_convert_song(self):
        """Test individual song conversion."""
        lxmusic_song = {
            "id": "test_song",
            "name": "Test Title",
            "singer": "Test Singer", 
            "album": "Test Album",
            "interval": 300000,
            "source": "web",
            "url": "https://example.com/song"
        }
        
        result = self.converter.convert_song(lxmusic_song)
        
        self.assertEqual(result["title"], "Test Title")
        self.assertEqual(result["artist"], "Test Singer")
        self.assertEqual(result["album"], "Test Album")
        self.assertEqual(result["duration"], 300000)
        self.assertEqual(result["source"], "web")
        self.assertEqual(result["url"], "https://example.com/song")
        self.assertEqual(result["id"], "test_song")
    
    def test_load_lxmusic_playlist(self):
        """Test loading lxmusic playlist from file."""
        # Create a temporary test file
        test_file = self.temp_dir / "test_playlist.json"
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(self.sample_lxmusic_data, f)
        
        result = self.converter.load_lxmusic_playlist(test_file)
        self.assertEqual(result["name"], "Test Playlist")
        self.assertEqual(len(result["list"]), 2)
    
    def test_save_musicfree_playlist(self):
        """Test saving MusicFree playlist to file."""
        musicfree_data = {
            "version": "1.0",
            "type": "playlist", 
            "name": "Test Output",
            "songs": []
        }
        
        output_file = self.temp_dir / "test_output.json"
        self.converter.save_musicfree_playlist(musicfree_data, output_file)
        
        # Verify file was created and contains correct data
        self.assertTrue(output_file.exists())
        with open(output_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data["name"], "Test Output")
        self.assertEqual(loaded_data["type"], "playlist")
    
    def test_full_conversion_process(self):
        """Test the complete conversion process."""
        # Create input file
        input_file = self.temp_dir / "input.json"
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(self.sample_lxmusic_data, f)
        
        # Set output file
        output_file = self.temp_dir / "output.musicfree.json"
        
        # Perform conversion
        self.converter.convert_playlist(input_file, output_file)
        
        # Verify output file exists and has correct content
        self.assertTrue(output_file.exists())
        with open(output_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        self.assertEqual(result["name"], "Test Playlist")
        self.assertEqual(len(result["songs"]), 2)
        self.assertEqual(result["songs"][0]["title"], "Test Song 1")
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON input."""
        # Create file with invalid JSON
        invalid_file = self.temp_dir / "invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json content")
        
        with self.assertRaises(ValueError):
            self.converter.load_lxmusic_playlist(invalid_file)
    
    def test_missing_file_handling(self):
        """Test handling of missing input file."""
        missing_file = self.temp_dir / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError):
            self.converter.load_lxmusic_playlist(missing_file)


if __name__ == "__main__":
    unittest.main()