# Trussium Piper provider

Standalone adapter for a self-hosted Piper HTTP service. It implements
Trussium's provider-neutral `SpeechCapability` and returns base64-encoded WAV
audio; it does not install or manage Piper.

```python
from trussium_provider_piper import PiperSpeechCapability

capability = PiperSpeechCapability(base_url="http://piper:5000")
```
