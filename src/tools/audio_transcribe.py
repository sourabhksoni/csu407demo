"""Raw voice and call recordings.

Reserved for sources whose artifact actually arrives as audio, for example a
call centre recording export or a field interview. Whisper (Devanagari and
regional language capable, matching the OCR path's language coverage)
transcribes the recording to text, and the same model based field extractor
used for the PDF path then maps that text onto schema fields.

Most Phase 1 voice sources are not this path. The ICAR KCC-CHAKSHU archive of
Kisan Call Centre queries, for example, is distributed by ICAR-IASRI as
already transcribed query and answer text keyed by state, district and date,
so it arrives as .csv/.json and is read deterministically through
tools.api_csv instead. This module exists for the case where the underlying
audio itself is obtained directly rather than a pre-transcribed export of it.

Everything from this path is written with extraction_confidence = low, for
the same reason as the OCR path: transcription error compounds with
extraction error, and Phase 3 analysis should be able to exclude it and
report the difference rather than assume it away.
"""

from __future__ import annotations

from src.tools.base import ExtractionUnit, ModalityTool, register


@register
class AudioTranscribeTool(ModalityTool):
    name = "audio_transcribe"
    needs_llm = True

    def read(self, path: str, **kwargs) -> list[ExtractionUnit]:
        raise NotImplementedError("Phase 2 implementation.")
