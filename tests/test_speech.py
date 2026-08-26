import base64

import httpx
import pytest
from trussium.capabilities.speech import SpeechRequest

from trussium_provider_piper import PiperSpeechCapability


@pytest.mark.anyio
async def test_speech_normalizes_wav_audio() -> None:
    capability = PiperSpeechCapability(
        client=httpx.AsyncClient(
            base_url="http://testserver",
            transport=httpx.MockTransport(lambda _: httpx.Response(200, content=b"RIFF-audio")),
        )
    )
    response = await capability.synthesize(
        SpeechRequest(model="en", input="Hello", voice="default", response_format="wav")
    )
    assert response.provider == "piper"
    assert base64.b64decode(response.audio) == b"RIFF-audio"


@pytest.mark.anyio
async def test_non_wav_output_is_rejected() -> None:
    capability = PiperSpeechCapability(client=httpx.AsyncClient(base_url="http://testserver"))
    with pytest.raises(Exception, match="only wav"):
        await capability.synthesize(
            SpeechRequest(model="en", input="Hello", voice="default", response_format="mp3")
        )
