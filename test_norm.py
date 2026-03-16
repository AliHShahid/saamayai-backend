import re

def normalize_text(text):
    # 1. Unify Alefs (including Alef Wasla 0671)
    # 0622(آ), 0623(أ), 0625(إ), 0627(ا), 0671(ٱ) -> 0627(ا)
    text = re.sub(r'[\u0622\u0623\u0625\u0671]', '\u0627', text)
    
    # 2. Unify Ya / Alef Maqsura
    # 0649(ى) -> 064A(ي)
    text = re.sub(r'\u0649', '\u064A', text)
    
    # 3. Unify Ta Marbuta
    # 0629(ة) -> 0647(ه)
    text = re.sub(r'\u0629', '\u0647', text)
    
    # 4. Remove all non-letter characters (Tashkeel, Quranic marks, Punctuation)
    # Keep only:
    # - 0621-064A (Standard Arabic Letters: Hamza to Yeh)
    # - 0627 (Alef - already normalized)
    # - Spaces matches
    
    # Construct regex: Keep [^...] -> Remove [^...]
    # We want to remove anything that is NOT a standard Arabic letter or space.
    # Note: \w in regex matches [a-zA-Z0-9_] usually. We need specific usage.
    
    # Strategy: Remove specific ranges of marks.
    # Harakat: 064B-0652
    # Quranic Marks: 06D6-06ED (approx)
    # Honorifics: 0610-0614
    # Superscript Alef: 0670
    
    # Let's try removing explicit blocks of known non-letters in Quran text.
    pattern = r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED]'
    text = re.sub(pattern, '', text)
    
    return text

reference = "بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ" 
# Hex: 628, 650, 633, 6e1 (Small High Dotless Head of Khah = Sukun), 645 ...
# My pattern above misses 06E1!
# 06E1 is in 06DF-06E8 range. So it SHOULD be caught.

normalized = normalize_text(reference)
print(f"Reference:  {reference}")
print(f"Normalized: {normalized}")

user_input = "بسم الله الرحمن الرحيم"
normalized_user = normalize_text(user_input)
print(f"User Trans: {user_input}")
print(f"Norm User:  {normalized_user}")

print(f"Match: {normalized == normalized_user}")
