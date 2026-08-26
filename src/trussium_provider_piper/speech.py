"""Piper text-to-speech adapter."""

import base64
from uuid import uuid4

import httpx
from trussium.capabilities.speech import SpeechCapability, SpeechRequest, SpeechResponse


class PiperProviderError(Exception):
    """Raised when Piper cannot provide speech audio."""


class PiperSpeechCapability(SpeechCapability):
    """Normalize Piper's JSON text endpoint into Trussium speech contracts."""

    provider_name = "piper"

    def __init__(
        self, *, base_url: str = "http://127.0.0.1:5000", client: httpx.AsyncClient | None = None
    ) -> None:
        self._client = client or httpx.AsyncClient(base_url=base_url.rstrip("/"))
        self._owns_client = client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def synthesize(self, request: SpeechRequest) -> SpeechResponse:
        if request.response_format != "wav":
            raise PiperProviderError("Piper adapter supports only wav output")
        try:
            response = await self._client.post(
                "/", json={"text": request.input, "voice": request.voice, "speed": request.speed}
            )
            response.raise_for_status()
            audio = response.content
            if not audio:
                raise ValueError("empty audio")
        except httpx.TimeoutException as error:
            raise PiperProviderError("Piper request timed out") from error
        except httpx.HTTPStatusError as error:
            raise PiperProviderError("Piper rejected the request") from error
        except (httpx.RequestError, ValueError) as error:
            raise PiperProviderError("Piper returned an invalid response") from error
        return SpeechResponse(
            id=f"speech-{uuid4().hex}",
            provider=self.provider_name,
            model=request.model,
            audio=base64.b64encode(audio).decode("ascii"),
            response_format="wav",
        )
