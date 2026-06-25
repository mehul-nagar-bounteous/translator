import time

import torch
from IndicTransToolkit.processor import IndicProcessor
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from languages import SOURCE_LANGUAGE

MODEL_NAME = "ai4bharat/indictrans2-en-indic-1B"


class TranslationResult:
    def __init__(
        self,
        translated_text: str,
        time_taken_ms: float,
        input_tokens: int,
        output_tokens: int,
    ):
        self.translated_text = translated_text
        self.time_taken_ms = time_taken_ms
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens


class TranslationService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if self.device == "cuda" else torch.float32

        self.tokenizer = AutoTokenizer.from_pretrained(
            MODEL_NAME, trust_remote_code=True
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME,
            trust_remote_code=True,
            torch_dtype=dtype,
        ).to(self.device)
        self.model.eval()

        self.ip = IndicProcessor(inference=True)

    def translate(self, text: str, tgt_lang: str) -> TranslationResult:
        start = time.perf_counter()

        preprocessed = self.ip.preprocess_batch(
            [text], src_lang=SOURCE_LANGUAGE, tgt_lang=tgt_lang
        )

        batch = self.tokenizer(
            preprocessed,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        ).to(self.device)

        input_tokens = int(batch["attention_mask"][0].sum().item())

        with torch.no_grad():
            output_ids = self.model.generate(
                **batch,
                num_beams=5,
                max_length=256,
                length_penalty=1.0,
                early_stopping=True,
            )

        output_tokens = len(output_ids[0])

        decoded = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        final = self.ip.postprocess_batch(decoded, lang=tgt_lang)

        elapsed_ms = (time.perf_counter() - start) * 1000

        return TranslationResult(
            translated_text=final[0],
            time_taken_ms=round(elapsed_ms, 2),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
