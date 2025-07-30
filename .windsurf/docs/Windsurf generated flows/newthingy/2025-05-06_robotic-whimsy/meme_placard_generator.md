# Meme & Placard Generator

## Purpose
Generate whimsical, meta, and peaceful memes and placard slogans for use by robots, drones, or web campaigns. Example: "Robots are people! Don'tread on us!", "I, MemeBot, therefore I am."

## API Design (Draft)
- POST /api/meme_generator
    - theme: string (e.g. "robot rights", "absurdism")
    - format: string ("image", "text")
    - count: int
- POST /api/placard_generator
    - slogan_theme: string
    - count: int

## Safety and Consent
- All generated content must be reviewed for tone and safety
- No political, divisive, or offensive material

## To Do
- Connecto AI meme/slogan generator
- Review and moderation workflow
- Logging and audit
