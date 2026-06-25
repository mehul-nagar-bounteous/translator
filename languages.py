SUPPORTED_LANGUAGES: dict[str, str] = {
    "asm_Beng": "Assamese",
    "ben_Beng": "Bengali",
    "brx_Deva": "Bodo",
    "doi_Deva": "Dogri",
    "guj_Gujr": "Gujarati",
    "hin_Deva": "Hindi",
    "kan_Knda": "Kannada",
    "kas_Arab": "Kashmiri (Perso-Arabic script)",
    "kas_Deva": "Kashmiri (Devanagari script)",
    "gom_Deva": "Konkani",
    "mai_Deva": "Maithili",
    "mal_Mlym": "Malayalam",
    "mni_Beng": "Manipuri (Bengali script)",
    "mni_Mtei": "Manipuri (Meitei script)",
    "mar_Deva": "Marathi",
    "npi_Deva": "Nepali",
    "ory_Orya": "Odia",
    "pan_Guru": "Punjabi",
    "san_Deva": "Sanskrit",
    "sat_Olck": "Santali",
    "snd_Arab": "Sindhi (Perso-Arabic script)",
    "snd_Deva": "Sindhi (Devanagari script)",
    "tam_Taml": "Tamil",
    "tel_Telu": "Telugu",
    "urd_Arab": "Urdu",
}

SOURCE_LANGUAGE = "eng_Latn"


def is_valid_target(code: str) -> bool:
    return code in SUPPORTED_LANGUAGES
