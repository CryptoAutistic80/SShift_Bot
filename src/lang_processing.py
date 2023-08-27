import re
import langid
import logging

async def is_english(text):
    try:
        lang, _ = langid.classify(text)
        return lang == 'en'
    except Exception as e:
        logging.error(f"Error in is_english: {e}")
        return False

async def preprocess_message(text):
    try:
        # Remove mentions
        cleaned_text = re.sub(r'@\\w+', '', text)
        return cleaned_text.strip()
    except Exception as e:
        logging.error(f"Error in preprocess_message: {e}")
        return text

async def should_translate(text):
    try:
        cleaned_text = await preprocess_message(text)
        
        if not cleaned_text or cleaned_text in ['!fetch', '!reply']:
            return False

        if cleaned_text.startswith('!reply '):
            return False

        if await is_english(cleaned_text):
            return False

        # Check for non-Latin scripts
        non_latin_patterns = [
            r'[\u0600-ۿ]',  # Arabic
            r'[ঀ-\u09ff]',  # Bengali
            r'[一-\u9fff𠀀-\U0002a6df]',  # Chinese
            r'[Ѐ-ӿ]',  # Cyrillic
            r'[ऀ-ॿ]',  # Devanagari
            r'[Ͱ-Ͽ]',  # Greek
            r'[\u0a80-૿]',  # Gujarati
            r'[\u0a00-\u0a7f]',  # Gurmukhi
            r'[\u0590-\u05ff]',  # Hebrew
            r'[\u3040-ヿ㐀-\u4dbf]',  # Japanese
            r'[ಀ-\u0cff]',  # Kannada
            r'[가-\ud7af]',  # Korean
            r'[ഀ-ൿ]',  # Malayalam
            r'[\u0b00-\u0b7f]',  # Oriya (Odia)
            r'[\u0d80-\u0dff]',  # Sinhala
            r'[\u0b80-\u0bff]',  # Tamil
            r'[ఀ-౿]',  # Telugu
            r'[\u0e00-\u0e7f]',  # Thai
            r'[ༀ-\u0fff]',   # Tibetan
            r'[\u1400-\u167F]'  # Inuktitut
        ]
        for pattern in non_latin_patterns:
            if re.search(pattern, cleaned_text):
                return True

        if len(cleaned_text.split()) < 4:
            return False

        url_regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\\\(\\\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
        if re.search(url_regex, cleaned_text):
            return False

        return True
    except Exception as e:
        logging.error(f"Error in should_translate: {e}")
        return False 

