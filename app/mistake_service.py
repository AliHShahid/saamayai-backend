import json
import logging
import difflib
import os
import re
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("saamay-backend")

class MistakeService:
    _instance = None
    _quran_data: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MistakeService, cls).__new__(cls)
            cls._instance._load_quran_data()
        return cls._instance

    def _load_quran_data(self):
        """Loads the Quran JSON file into memory with robust path finding."""
        possible_paths = [
            "/root/assets/json/all_ayat.json",
            "assets/json/all_ayat.json",
            os.path.join(os.path.dirname(__file__), "../assets/json/all_ayat.json")
        ]

        json_path = None
        for path in possible_paths:
            if os.path.exists(path):
                json_path = path
                break
        
        if not json_path:
            logger.error("❌ CRITICAL: 'all_ayat.json' NOT FOUND.")
            return

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # The JSON structure has a 'tafsir' key containing Ayah mappings
                self._quran_data = data.get("tafsir", data)
            logger.info(f"✅ Successfully loaded {len(self._quran_data)} Ayahs.")
        except Exception as e:
            logger.error(f"❌ Error parsing JSON: {e}")

    def get_ayah_text(self, surah: int, ayah: int) -> str:
        """Fetch original text for a specific single Ayah."""
        key = f"{surah}_{ayah}"
        return self._quran_data.get(key, {}).get('text', "")

    def remove_tashkeel(self, text: str) -> str:
        """Normalizes Arabic text by removing diacritics and unifying characters."""
        if not text: return ""
        # Remove Tashkeel (vowel marks)
        text = re.sub(r'[\u0617-\u061A\u064B-\u0652]', '', text)
        # Remove Tatweel (decoration)
        text = re.sub(r'\u0640', '', text)
        # Unify Alifs
        text = re.sub(r'[أإآ]', 'ا', text)
        # Unify Ya / Alif Maqsura
        text = re.sub(r'ى', 'ي', text)
        # Unify Ta Marbuta
        text = re.sub(r'ة', 'ه', text)
        # Remove punctuation
        text = re.sub(r'[،.؛:!؟?"\'\(\)\[\]\{\}-]', '', text)
        return text

    def detect_mistakes(self, transcribed_text: str, surah: int, ayah: int) -> Dict[str, Any]:
        """
        Compare user transcription vs a specific reference Ayah.
        Returns word-by-word status and absolute accuracy percentage.
        """
        reference_text = self.get_ayah_text(surah, ayah)
        
        if not reference_text:
            return {"error": "Ayah not found"}

        # Normalize for comparison
        norm_ref = self.remove_tashkeel(reference_text)
        norm_user = self.remove_tashkeel(transcribed_text)
        
        user_words = norm_user.strip().split()
        ref_words = norm_ref.strip().split()
        original_ref_words = reference_text.strip().split()

        matcher = difflib.SequenceMatcher(None, ref_words, user_words)
        diffs = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                for k in range(i1, i2):
                    word = original_ref_words[k] if k < len(original_ref_words) else ref_words[k]
                    diffs.append({"word": word, "status": "correct"})
            elif tag == 'replace':
                for k in range(i1, i2):
                    word = original_ref_words[k] if k < len(original_ref_words) else ref_words[k]
                    said_word = " ".join(user_words[j1:j2])
                    diffs.append({"word": word, "status": "wrong", "said": said_word})
            elif tag == 'delete':
                is_trailing = (i2 == len(ref_words))
                status = "pending" if is_trailing else "missing"
                for k in range(i1, i2):
                    word = original_ref_words[k] if k < len(original_ref_words) else ref_words[k]
                    diffs.append({"word": word, "status": status})
            elif tag == 'insert':
                for word in user_words[j1:j2]:
                    diffs.append({"word": word, "status": "extra"})

        # Calculate Accuracy (ignoring pending words at the end)
        effective_ref_words = [d for d in diffs if d['status'] != 'pending']
        total_effective = len(effective_ref_words)
        correct = sum(1 for d in effective_ref_words if d['status'] == 'correct')
        accuracy = (correct / total_effective) * 100 if total_effective > 0 else 0

        return {
            "surah": surah,
            "ayah": ayah,
            "accuracy": round(accuracy, 2),
            "diff": diffs,
            "transcription": transcribed_text
        }

    def detect_mistakes_continuous(self, transcript: str, surah: int, start_ayah_hint: int = 1) -> Dict[str, Any]:
        """
        Real-time matching logic for streaming audio.
        Uses a search window to automatically detect which Ayah the user is reciting.
        """
        normalized_transcript = self.remove_tashkeel(transcript.strip())
        if not normalized_transcript or len(normalized_transcript) < 5:
            return {}

        best_match_ayah = None
        best_ratio = 0.0

        # Look ahead 4 verses from the hint for better coverage
        search_range = range(start_ayah_hint, start_ayah_hint + 4)

        for ayah_num in search_range:
            ref_text = self.get_ayah_text(surah, ayah_num)
            if not ref_text: continue

            norm_ref = self.remove_tashkeel(ref_text)
            matcher = difflib.SequenceMatcher(None, norm_ref, normalized_transcript)
            ratio = matcher.ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_match_ayah = ayah_num

        # Match threshold (40% similarity)
        if best_match_ayah and best_ratio > 0.4:
            logger.info(f"🎯 Match Found! Ayah {best_match_ayah} (Score: {best_ratio:.2f})")
            return self.detect_mistakes(transcript, surah, best_match_ayah)
        
        return {}

mistake_service = MistakeService()