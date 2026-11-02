# Voice test (Oct 28, 2026)

Book 18 page 3, read by four ElevenLabs voices through Krea (`elevenlabs/tts`, `eleven_v4`, about 21 credits each).
Krea accepts ElevenLabs **library** voice IDs, not only the built-in English voices it lists.

| File | Voice | ID | Notes |
| --- | --- | --- | --- |
| 1-Matilda-current.mp3 | Matilda (current narrator) | XrExE9yKIg1WjnnlVkGX | English voice + "[European Portuguese accent, from Lisbon, calm storyteller]" tag |
| 2-Joana.mp3 | Joana | nJ5NFqyKb8kn9JBPmo6i | native European Portuguese, female, "natural and gentle" |
| 3-Marta.mp3 | Marta | bBNhdwrIjl4fcVYiRbT2 | native European Portuguese, female, "warm, confident" |
| 4-Pedro-Madeira.mp3 | Pedro | XxTHUwWTW2conYBz0vvk | native European Portuguese, male, from Madeira — candidate for men's dialogue |

Native voices were sent the plain text (no accent tag). More European Portuguese library voices:
Vasco pjqwOzrEUZ3n3m4rMWWL (m), Diogo RlGHmE2fztwdBDat0jYf (m), Daniela IZipF5JhqPlWzpduTV0E (f), Adilson A26KfvFuSKaMzhhYkSlQ (m)
(source: json2video.com ElevenLabs voice list, Portuguese · European).

Result: waiting for the user's choice. Changing the narrator means re-recording all books' narration and word clips
for consistency (or using the new voice from book 19 on) — decide with the user.

## OmniVoice (free, local) — Nov 1, 2026
The engine behind VoiceStudio (github.com/debpalash/VoiceStudio): `pip install omnivoice`, weights `k2-fsa/OmniVoice`
(Apache-2.0), Portuguese = one language `pt` (~16,900 training hours, likely mostly Brazilian).
Voice design accepts only fixed items (female/male, age, pitch, a generic "portuguese accent"), not "European".

| File | Settings |
| --- | --- |
| 5-OmniVoice-female.mp3 | `instruct='female, young adult, moderate pitch'`, `language='pt'` |
| 6-OmniVoice-male.mp3 | `instruct='male, middle-aged, low pitch'`, `language='pt'` |

Speed in the cloud workspace (2 CPU cores, no GPU): model load ~20 s, about 2¼ minutes per page.
The way to a reliably European (or Madeiran) voice is cloning from a short, clean recording of a real speaker
who gives permission (`ref_audio` + `ref_text`).
