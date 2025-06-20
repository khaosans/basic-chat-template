"""
Test file for voice functionality
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

from src.core.app import text_to_speech, get_professional_audio_html

class TestVoiceFunctionality:
    """Test class for voice functionality"""
    
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
    
    def test_text_to_speech_creates_file(self):
        """Test that text_to_speech creates an audio file"""
        test_text = "Hello, this is a test message."
        
        # Generate audio file
        audio_file = text_to_speech(test_text)
        
        # Check that file was created
        assert audio_file is not None
        assert os.path.exists(audio_file)
        assert audio_file.endswith('.mp3')
        
        # Check file size (should be greater than 0)
        assert os.path.getsize(audio_file) > 0
    
    def test_text_to_speech_consistent_hash(self):
        """Test that same text produces same filename"""
        test_text = "Hello, this is a test message."
        
        # Generate audio file twice
        audio_file1 = text_to_speech(test_text)
        audio_file2 = text_to_speech(test_text)
        
        # Should be the same file
        assert audio_file1 == audio_file2
        
        # Verify the hash is correct
        expected_hash = hashlib.md5(test_text.encode()).hexdigest()
        expected_filename = f"temp_{expected_hash}.mp3"
        assert audio_file1 == expected_filename
    
    def test_text_to_speech_different_texts(self):
        """Test that different texts produce different files"""
        text1 = "Hello, this is message one."
        text2 = "Hello, this is message two."
        
        audio_file1 = text_to_speech(text1)
        audio_file2 = text_to_speech(text2)
        
        # Should be different files
        assert audio_file1 != audio_file2
        assert os.path.exists(audio_file1)
        assert os.path.exists(audio_file2)
    
    def test_text_to_speech_empty_text(self):
        """Test handling of empty text"""
        audio_file = text_to_speech("")
        
        # Should return None for empty text
        assert audio_file is None
    
    def test_text_to_speech_none_text(self):
        """Test handling of None text"""
        audio_file = text_to_speech(None)
        
        # Should return None for None text
        assert audio_file is None
    
    def test_text_to_speech_whitespace_text(self):
        """Test handling of whitespace-only text"""
        audio_file = text_to_speech("   \n\t   ")
        
        # Should return None for whitespace-only text
        assert audio_file is None
    
    def test_get_audio_html_creates_valid_html(self):
        """Test that get_audio_html creates valid HTML"""
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
    
    def test_get_audio_html_file_not_found(self):
        """Test handling of non-existent file"""
        non_existent_file = "temp_nonexistent_file.mp3"
        
        # Should handle gracefully and return error message
        html = get_professional_audio_html(non_existent_file)
        
        # Should return an error message
        assert html is not None
        assert "Audio file not found" in html
    
    def test_get_audio_html_none_file(self):
        """Test handling of None file path"""
        html = get_professional_audio_html(None)
        
        # Should return a message about no audio available
        assert html is not None
        assert "No audio available" in html
    
    def test_voice_integration(self):
        """Test the complete voice integration workflow"""
        test_text = "This is a comprehensive test of the voice functionality."
        
        # Step 1: Generate audio file
        audio_file = text_to_speech(test_text)
        assert audio_file is not None
        assert os.path.exists(audio_file)
        
        # Step 2: Generate HTML
        html = get_professional_audio_html(audio_file)
        assert html is not None
        assert '<audio' in html
        
        # Step 3: Verify file can be read
        with open(audio_file, 'rb') as f:
            data = f.read()
            assert len(data) > 0
        
        # Step 4: Verify base64 encoding works
        import base64
        b64_data = base64.b64encode(data).decode()
        assert len(b64_data) > 0
        assert b64_data in html
    
    @patch('app.gTTS')
    def test_text_to_speech_gtts_integration(self, mock_gtts):
        """Test integration with gTTS library"""
        test_text = "Hello, this is a test."
        
        # Mock gTTS instance and save method
        mock_tts_instance = MagicMock()
        mock_gtts.return_value = mock_tts_instance
        
        # Mock the save method to actually create a file
        def mock_save(filename):
            with open(filename, 'w') as f:
                f.write("mock audio content")
        
        mock_tts_instance.save.side_effect = mock_save
        
        # Test the function
        audio_file = text_to_speech(test_text)
        
        # Verify gTTS was called correctly
        mock_gtts.assert_called_once_with(text=test_text, lang='en', slow=False)
        mock_tts_instance.save.assert_called_once()
        
        # Verify file was created
        assert audio_file is not None
        assert os.path.exists(audio_file)
        
        # Cleanup
        if audio_file and os.path.exists(audio_file):
            os.remove(audio_file)
    
    def test_voice_with_special_characters(self):
        """Test voice generation with special characters"""
        test_text = "Hello! This has special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
        
        audio_file = text_to_speech(test_text)
        
        assert audio_file is not None
        assert os.path.exists(audio_file)
        assert os.path.getsize(audio_file) > 0
    
    def test_voice_with_long_text(self):
        """Test voice generation with longer text"""
        test_text = "This is a longer test message that should still work properly with the text-to-speech functionality. It contains multiple sentences and should generate a valid audio file that can be played back in the browser."
        
        audio_file = text_to_speech(test_text)
        
        assert audio_file is not None
        assert os.path.exists(audio_file)
        assert os.path.getsize(audio_file) > 0
    
    def test_voice_with_unicode(self):
        """Test voice generation with unicode characters"""
        test_text = "Hello! This has unicode: éñüñçåtion, 你好, مرحبا"
        
        audio_file = text_to_speech(test_text)
        
        assert audio_file is not None
        assert os.path.exists(audio_file)
        assert os.path.getsize(audio_file) > 0

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"]) 