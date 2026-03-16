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
            "/root/assets/json/quran.json",
            "assets/json/quran.json",
            os.path.join(os.path.dirname(__file__), "../assets/json/quran.json")
        ]

        json_path = None
        for path in possible_paths:
            if os.path.exists(path):
                json_path = path
                break
        
        if not json_path:
            logger.error("❌ CRITICAL: 'quran.json' NOT FOUND.")
            return

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self._quran_data = json.load(f)
            logger.info(f"✅ Successfully loaded Quran data for {len(self._quran_data)} Surahs.")
        except Exception as e:
            logger.error(f"❌ Error parsing JSON: {e}")

    def get_ayah_text(self, surah: int, ayah: int) -> str:
        """Fetch original text for a specific single Ayah."""
        try:
            surah_str = str(surah)
            if surah_str in self._quran_data:
                surah_ayahs = self._quran_data[surah_str]
                # Ayah numbers are 1-indexed, list is 0-indexed
                idx = ayah - 1
                if 0 <= idx < len(surah_ayahs):
                    return surah_ayahs[idx].get('text', "")
        except Exception as e:
            logger.error(f"Error fetching ayah {surah}:{ayah} - {e}")
        
        return ""

    def remove_tashkeel(self, text: str) -> str:
        """Normalizes Arabic text by removing diacritics and unifying characters."""
        if not text: return ""
        
        # 1. Unify Alefs (including Alef Wasla 0671 and Dagger Alef 0670 -> Regular Alef)
        text = re.sub(r'[\u0622\u0623\u0625\u0671\u0670]', '\u0627', text)
        
        # 2. Unify Ya / Alif Maqsura
        text = re.sub(r'[\u0649\u064A]', '\u064A', text) # Unify ى and ي to ي
        
        # 3. Unify Ta Marbuta
        text = re.sub(r'\u0629', '\u0647', text) # Unify ة to ه
        
        # 4. Remove Quranic Marks & Tashkeel
        # \u0610-\u061A : Honorifics/Marks
        # \u0640      : Tatweel
        # \u064B-\u065F : Harakat (Fathatan..Sukun..Shadda..etc)
        # \u06D6-\u06ED : Quranic Pauses/Marks (Sajdah, Rub, etc.)
        pattern = r'[\u0610-\u061A\u0640\u064B-\u065F\u06D6-\u06ED]'
        # Note: 0670 (Dagger Alef) is NOT removed here, it was mapped to Alef above.
        text = re.sub(pattern, '', text)
        
        # 5. Remove Punctuation
        text = re.sub(r'[،.؛:!؟?"\'\(\)\[\]\{\}-]', '', text)
        
        # 6. Fix Common Imla'i Exceptions (Where Dagger Alef should be dropped, not mapped to Alef)
        # Sequence: Dagger became Alif. e.g., 'الرحمان' -> 'الرحمن'
        # Note: We are operating on text with NO diacritics now.
        
        # Allah: ٱللَّهِ -> (Wasla->A) (Lam) (Lam) (Shadda->Gone) (Dagger->A) (Ha) -> ا ل ل ا ه
        # Standard: الله -> ا ل ل ه
        text = re.sub(r'الل\s*اه', 'الله', text) # Fix Allah
        
        # Rahman: ٱلرَّحۡمَٰنِ -> (Wasla->A) (Lam) (Ra) ... (Meem) (Dagger->A) (Noon) -> الرحمان
        # Standard: الرحمن
        text = re.sub(r'الرحمان', 'الرحمن', text)
        
        # Haza: هَٰذَا -> ه ا ذ ا -> هاذا
        # Standard: هذا
        text = re.sub(r'\bهاذا\b', 'هذا', text)
        
        # Zalik: ذَٰلِكَ -> ذالك
        # Standard: ذلك
        text = re.sub(r'\bذالك\b', 'ذلك', text)
        
        # Lakin: لَٰكِن -> لاكن
        # Standard: لكن
        text = re.sub(r'\bلاكن\b', 'لكن', text)
        
        # Ulaik: أُوْلَـٰٓئِكَ -> (Hamza->A) (Waw) (Lam) (Dagger->A) (Hamza-Yeh->Yeh) (Kaf) -> اولايىك?
        # Standard: اولئك
        # Complex. Let's see. 
        # Ref: أ 0623 -> A. 
        # Waw 0648 -> W.
        # Lam 0644 -> L.
        # Dagger 0670 -> A.
        # Hamza on Yeh 0626. kept? yes.
        # Result: ا و ل ا ئ ك (Awla'ik)
        # User: ا و ل ئ ك (Ula'ik).
        # Fix:
        text = re.sub(r'اولائك', 'اولئك', text)
        
        # Ilah: إِلَٰه -> (Hamza->A) (Lam) (Dagger->A) (Ha) -> ال اه -> الاه
        # Standard: اله (or إله) -> (Hamza->A) (Lam) (Ha) -> اله
        text = re.sub(r'\bالاه\b', 'اله', text)

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