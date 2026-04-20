import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch
from tts_web import smart_split, read_aloud, cleanup, tmp_files

# Test smart_split
def test_smart_split_basic():
    text = "Xin chào. Đây là một thử nghiệm."
    chunks = smart_split(text, 100)
    assert len(chunks) == 1
    assert chunks[0] == text

def test_smart_split_sentence_boundary():
    text = "Câu một! Câu hai? Câu ba."
    chunks = smart_split(text, 10)
    assert len(chunks) == 3
    assert chunks == ["Câu một!", "Câu hai?", "Câu ba."]

def test_smart_split_long_word():
    text = "Tô" * 1000 # 2000 chars
    chunks = smart_split(text, 1000)
    assert len(chunks) == 2
    assert len(chunks[0]) == 1000
    assert len(chunks[1]) == 1000

def test_smart_split_complex():
    text = "Một câu rất dài. Và một câu ngắn."
    chunks = smart_split(text, 20)
    assert len(chunks) == 2
    assert chunks[0] == "Một câu rất dài."
    assert chunks[1] == "Và một câu ngắn."

# Test read_aloud with mock client
@patch('tts_web.is_server_ready')
@patch('tts_web.synth_chunk')
def test_read_aloud_success(mock_synth, mock_ready):
    mock_ready.return_value = True
    # Mock synth_chunk to return a fake file path
    mock_synth.return_value = "fake_chunk0.wav"
    
    # read_aloud is now a generator
    gen = read_aloud("Test text", 1.0)
    
    # Get all yielded results
    results = list(gen)
    
    assert len(results) > 0
    paths, status, log = results[-1]
    
    assert "COMPLETE" in status.upper()
    assert len(paths) == 1
    assert paths[0] == "fake_chunk0.wav"

@patch('tts_web.is_server_ready')
def test_read_aloud_empty(mock_ready):
    mock_ready.return_value = True
    gen = read_aloud("", 1.0)
    results = list(gen)
    paths, status, log = results[0]
    assert paths == []
    assert "Enter text first!" in status

# Test cleanup
def test_cleanup():
    # Create fake temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        path = f.name
    
    from tts_web import tmp_files
    tmp_files.append(path)
    assert os.path.exists(path)
    
    cleanup()
    
    assert not os.path.exists(path)

if __name__ == "__main__":
    pytest.main([__file__])
