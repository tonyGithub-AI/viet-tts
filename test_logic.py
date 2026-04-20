import re

def smart_split(text, max_chars=4000):
    """Split into natural sentence chunks (~4K chars)."""
    sentences = re.split(r'(?<=[\.!\?])\s+', text)
    chunks, current = [], ""
    for sent in sentences:
        if len(sent) > max_chars:
            # If current chunk has something, add it first
            if current.strip():
                chunks.append(current.strip())
                current = ""
            # Handle exceptionally long sentence by splitting by words
            words = sent.split()
            temp_chunk = ""
            for word in words:
                if len(word) > max_chars:
                    # If even a single word is too long, split it by index
                    if temp_chunk.strip():
                        chunks.append(temp_chunk.strip())
                        temp_chunk = ""
                    for i in range(0, len(word), max_chars):
                        chunks.append(word[i:i+max_chars])
                elif len(temp_chunk + word) < max_chars:
                    temp_chunk += word + " "
                else:
                    chunks.append(temp_chunk.strip())
                    temp_chunk = word + " "
            current = temp_chunk
        elif len((current + sent).strip()) < max_chars:
            current += sent + " "
        else:
            chunks.append(current.strip())
            current = sent + " "
    
    if current.strip():
        chunks.append(current.strip())
    return chunks

# Test 1: Short text
text1 = "Xin chào. Đây là một thử nghiệm."
print(f"Test 1: {smart_split(text1, 100)}")

# Test 2: Text that needs splitting at sentence boundary
text2 = "Câu một! Câu hai? Câu ba."
print(f"Test 2 (10 chars limit): {smart_split(text2, 10)}")

# Test 3: Long sentence that needs word splitting
text3 = "Một câu rất dài không có dấu chấm phẩy gì cả."
print(f"Test 3 (10 chars limit): {smart_split(text3, 10)}")

# Test 4: 20K char simulation (long word/sentence)
text4 = "Tô" * 10000 # 20K chars string
chunks4 = smart_split(text4, 4000)
print(f"Test 4 (20K chars, 4000 limit): {len(chunks4)} chunks")
for i, c in enumerate(chunks4):
    print(f"  Chunk {i}: {len(c)} chars")
