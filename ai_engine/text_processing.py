import re

def preprocess_text(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    return text

def split_into_sentences(text):
    sentences = re.findall(r'[^.!?]+[.!?]', text)
    cleaned = []

    for s in sentences:
        s = s.strip()
        if len(s) > 20:
            cleaned.append(s)

    return cleaned
