# Loudspeaker Truck Control

## Purpose
Remotely control DIY loudspeaker trucks to play surreal audio messages, AI-generated music, or meme content in public (with consent and safety).

## API Design (Draft)
- POST /api/loudspeaker_truck
    - audio_url: string (or message text for TTS)
    - location: string
    - volume: int
    - duration: int (seconds)
    - consent_required: bool

## Safety and Consent
- Only operate in permitted areas
- All content must be reviewed for tone and safety
- Human-in-the-loop for activation

## To Do
- Simulation/test harness for loudspeaker scenarios
- Consent workflow integration
- Logging and audit
