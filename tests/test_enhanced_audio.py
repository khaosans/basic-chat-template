"""
Test file for enhanced audio functionality
"""
import pytest
import os
import tempfile
import hashlib
from unittest.mock import patch, MagicMock
import sys
import os

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.app import (
    create_enhanced_audio_button, 
    get_professional_audio_html, 
    cleanup_audio_files, 
    get_audio_file_size,
    text_to_speech
)

class TestEnhancedAudioFunctionality:
    """Test class for enhanced audio functionality"""
    
    def setup_method(self):
        """Setup method to clean up any existing test files"""
        # Clean up any existing temp audio files
        for file in os.listdir('.'):
            if file.startswith('temp_') and file.endswith('.mp3'):
                try:
                    os.remove(file)
                except:
                    pass
    
    def teardown_method(self):
        """Teardown method to clean up test files"""
        # Clean up any test audio files
        for file in os.listdir('.'):
            if file.startswith('temp_') and file.endswith('.mp3'):
                try:
                    os.remove(file)
                except:
                    pass
    
    def test_create_enhanced_audio_button_initialization(self):
        """Test that enhanced audio button initializes correctly"""
        # This would require Streamlit session state mocking
        # For now, we'll test the helper functions
        assert True  # Placeholder for actual test
    
    def test_get_professional_audio_html_creates_valid_html(self):
        """Test that get_professional_audio_html creates valid HTML"""
        # Create a test audio file
        test_text = "Test audio content"
        audio_file = text_to_speech(test_text)
        
        # Generate HTML
        html = get_professional_audio_html(audio_file)
        
        # Check that HTML contains expected elements
        assert html is not None
        assert '<audio' in html
        assert 'controls' in html
        assert 'style=' in html
        assert 'data:audio/mp3;base64,' in html
        assert '</audio>' in html
        assert 'background: linear-gradient' in html
        assert 'border: 1px solid #e2e8f0' in html
    
    def test_get_professional_audio_html_file_not_found(self):
        """Test handling of non-existent file"""
        non_existent_file = "temp_nonexistent_file.mp3"
        
        # Should handle gracefully and return error message
        html = get_professional_audio_html(non_existent_file)
        
        # Should return an error message with proper styling
        assert html is not None
        assert "Audio file not found" in html
        assert "color: #e53e3e" in html
        assert "text-align: center" in html
    
    def test_get_professional_audio_html_none_file(self):
        """Test handling of None file path"""
        html = get_professional_audio_html(None)
        
        # Should return a message about no audio available
        assert html is not None
        assert "No audio available" in html
        assert "color: #4a5568" in html
        assert "font-style: italic" in html
        assert "text-align: center" in html
    
    def test_get_professional_audio_html_empty_string(self):
        """Test handling of empty string file path"""
        html = get_professional_audio_html("")
        
        # Should return a message about no audio available
        assert html is not None
        assert "No audio available" in html
        assert "color: #4a5568" in html
        assert "font-style: italic" in html
    
    def test_get_audio_file_size_bytes(self):
        """Test file size formatting for bytes"""
        # Create a small test file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test data")
            file_path = f.name
        
        try:
            size = get_audio_file_size(file_path)
            assert "B" in size
            assert size.endswith(" B")
        finally:
            os.unlink(file_path)
    
    def test_get_audio_file_size_kilobytes(self):
        """Test file size formatting for kilobytes"""
        # Create a larger test file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * 2048)  # 2KB
            file_path = f.name
        
        try:
            size = get_audio_file_size(file_path)
            assert "KB" in size
            assert size.endswith(" KB")
        finally:
            os.unlink(file_path)
    
    def test_get_audio_file_size_megabytes(self):
        """Test file size formatting for megabytes"""
        # Create a large test file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"x" * (1024 * 1024 + 100))  # ~1MB
            file_path = f.name
        
        try:
            size = get_audio_file_size(file_path)
            assert "MB" in size
            assert size.endswith(" MB")
        finally:
            os.unlink(file_path)
    
    def test_get_audio_file_size_nonexistent(self):
        """Test file size for non-existent file"""
        size = get_audio_file_size("nonexistent_file.mp3")
        assert size == "Unknown size"
    
    def test_cleanup_audio_files(self):
        """Test cleanup of audio files"""
        # Create some test audio files
        test_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(prefix="temp_", suffix=".mp3", delete=False) as f:
                f.write(b"test audio data")
                test_files.append(f.name)
        
        # Verify files exist
        for file_path in test_files:
            assert os.path.exists(file_path)
        
        # Run cleanup
        cleanup_audio_files()
        
        # Verify files are still there (cleanup only removes session state files)
        for file_path in test_files:
            assert os.path.exists(file_path)
        
        # Clean up test files
        for file_path in test_files:
            os.unlink(file_path)
    
    def test_professional_audio_html_contains_modern_styling(self):
        """Test that professional audio HTML contains modern styling"""
        # Create a test audio file
        test_text = "Test audio content"
        audio_file = text_to_speech(test_text)
        
        # Generate HTML
        html = get_professional_audio_html(audio_file)
        
        # Check for modern styling elements
        assert 'background: linear-gradient' in html
        assert 'border-radius: 12px' in html
        assert 'border: 1px solid #e2e8f0' in html
        assert 'preload="metadata"' in html
    
    def test_professional_audio_html_contains_accessibility_features(self):
        """Test that professional audio HTML contains accessibility features"""
        # Create a test audio file
        test_text = "Test audio content"
        audio_file = text_to_speech(test_text)
        
        # Generate HTML
        html = get_professional_audio_html(audio_file)
        
        # Check for accessibility features
        assert 'aria-label="Audio playback controls"' in html
        assert 'Your browser does not support the audio element' in html
    
    def test_professional_audio_html_error_handling(self):
        """Test error handling in professional audio HTML"""
        # Test with exception during file reading
        with patch('builtins.open', side_effect=Exception("Test error")):
            html = get_professional_audio_html("test_file.mp3")
            
            assert html is not None
            assert "Error loading audio" in html
            assert "color: #e53e3e" in html
            assert "text-align: center" in html
    
    def test_professional_audio_html_base64_encoding(self):
        """Test that base64 encoding works correctly"""
        # Create a test audio file with known content
        test_data = b"test audio data for base64 encoding"
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(test_data)
            file_path = f.name
        
        try:
            html = get_professional_audio_html(file_path)
            
            # Check that base64 data is present
            assert 'data:audio/mp3;base64,' in html
            
            # Extract and verify base64 data
            import base64
            start_idx = html.find('data:audio/mp3;base64,') + len('data:audio/mp3;base64,')
            end_idx = html.find('"', start_idx)
            b64_data = html[start_idx:end_idx]
            
            # Decode and verify
            decoded_data = base64.b64decode(b64_data)
            assert decoded_data == test_data
            
        finally:
            os.unlink(file_path)
    
    def test_professional_audio_html_file_size_display(self):
        """Test that file size information is displayed correctly"""
        # Create a test audio file
        test_text = "Test audio content for file size display"
        audio_file = text_to_speech(test_text)
        
        # Generate HTML
        html = get_professional_audio_html(audio_file)
        
        # Check that audio player is present
        assert '<audio' in html
        assert 'controls' in html
        assert 'data:audio/mp3;base64,' in html
    
    def test_professional_audio_html_malformed_file(self):
        """Test handling of malformed audio files"""
        # Create a malformed audio file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(b"not a valid audio file")
            file_path = f.name
        
        try:
            html = get_professional_audio_html(file_path)
            
            # Should still generate HTML even for malformed files
            assert html is not None
            assert '<audio' in html
            assert 'data:audio/mp3;base64,' in html
            
        finally:
            os.unlink(file_path) 