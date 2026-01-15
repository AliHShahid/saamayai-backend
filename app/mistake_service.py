import json
import logging
import difflib
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class MistakeService:
    _instance = None
    _quran_data: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MistakeService, cls).__new__(cls)
            cls._instance._load_quran_data()
        return cls._instance

    def _load_quran_data(self):
        """Loads the Quran JSON file into memory."""
        try:
            # Adjust path as needed. Assuming it's in the same app folder or root assets.
            # Ideally, pass the path from config. Here we assume a standard location.
            # Compiling 'all_ayat.json' into a lookup dict.
            # You might need to upload this file to the backend folder too.
            with open("assets/json/all_ayat.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure we handle the structure correctly (e.g., if it's nested under "tafsir")
                self._quran_data = data.get("tafsir", data)
            logger.info("✅ Quran text data loaded successfully.")
        except Exception as e:
            logger.error(f"❌ Failed to load Quran data: {e}")
            self._quran_data = {}

    def get_reference_text(self, surah: int) -> str:
        """Concatenates all ayahs of a Surah into one string for comparison."""
        full_text = []
        # Basic loop - assumes standard ayah counts or just iterates available keys
        # A more robust way is to iterate keys starting with "{surah}_"
        prefix = f"{surah}_"
        sorted_keys = sorted([k for k in self._quran_data.keys() if k.startswith(prefix)], 
                             key=lambda x: int(x.split('_')[1]))
        
        for key in sorted_keys:
            full_text.append(self._quran_data[key]['text'])
        
        return " ".join(full_text)

    def detect_mistakes(self, transcribed_text: str, surah_number: int) -> Dict[str, Any]:
        """
        Compares transcribed text with reference Surah text.
        Returns a list of word-by-word diffs.
        """
        reference_text = self.get_reference_text(surah_number)
        
        # Simple normalization (remove punctuation, tashkeel if necessary)
        # For now, we assume Whisper output is close to reference
        
        user_words = transcribed_text.split()
        ref_words = reference_text.split()
        
        # Use SequenceMatcher to find differences
        matcher = difflib.SequenceMatcher(None, ref_words, user_words)
        diffs = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for word in ref_words[i1:i2]:
                    diffs.append({"word": word, "status": "correct"})
            elif tag == 'replace':
                for word in ref_words[i1:i2]:
                    diffs.append({"word": word, "status": "wrong", "said": user_words[j1:j2]})
            elif tag == 'delete':
                for word in ref_words[i1:i2]:
                    diffs.append({"word": word, "status": "missing"})
            elif tag == 'insert':
                # User added extra words not in Quran
                for word in user_words[j1:j2]:
                    diffs.append({"word": word, "status": "extra"})

        # Calculate accuracy score
        total_words = len(ref_words)
        correct_words = sum(1 for d in diffs if d['status'] == 'correct')
        accuracy = (correct_words / total_words) * 100 if total_words > 0 else 0

        return {
            "surah": surah_number,
            "accuracy": round(accuracy, 2),
            "diff": diffs,
            "transcription": transcribed_text
        }

# Singleton instance
mistake_service = MistakeService()