# Reel Factory: topic or script in, Hindi reel out

Yes, this is possible, all with free tiers. The short answer is at the top,
the working code is in this folder, and the catches are listed honestly below.

## Short answer

- **Chatterbox Hindi voice: yes.** `narrate_chatterbox.py` is your uploaded
  Diwali narration code, generalised: no hardcoded scenes, no fixed video.
  Any Hindi text in, one wav out. Your locked default voice stays Chatterbox.
- **Only enter a topic or a script: yes.** `make_reel.py` does the rest:
  topic -> Groq script -> Chatterbox voice -> Whisper caption sync -> Remotion render.
  Script -> skip Groq, everything else is the same.
- **Groq for free script/code generation: yes, with a free key.**
  Groq's free tier needs a key from console.groq.com, no card, but rate limits
  apply. The key goes in an env var locally, or a GitHub secret in Actions,
  never in code. If Groq retires a model, change `--groq-model`.
- **GitHub Actions for free generation: yes, slow.**
  `.github/workflows/make-reel.yml` runs on `workflow_dispatch` with a topic
  or script input, and uploads the MP4 as an artifact. Public repos get
  unlimited Actions minutes, private repos get 2,000 free minutes a month.
  A CPU runner has no GPU, so Chatterbox on CPU is the bottleneck:
  roughly 15-40 minutes per reel, inside the 6-hour job limit.

## Use it locally

```bash
# 1. Kit (once): download reel-studio-kit.zip from
#    https://getanimo.io/blog/reel-studio-kit and unzip it next to this folder,
#    or pass --kit-dir to the folder containing package.json.
#    This factory already looks in ../reel-studio-kit-demo/reel-studio-kit.

# 2. Script you wrote (no Groq, no cost):
python make_reel.py --script-file dummy-script-hi.txt --id subah-jaldi --voice-engine gtts

# 3. Topic only (needs GROQ_API_KEY):
GROQ_API_KEY=... python make_reel.py --topic "Subah jaldi uthne ke fayde" --voice-engine chatterbox

# 4. Chatterbox alone, for any Hindi text:
python narrate_chatterbox.py --text-file dummy-script-hi.txt --out vo.wav
#    --voice my-voice.wav   # optional, your own 10-20s sample, to clone your voice
#    --device cpu | mps | cuda

# 5. Groq script alone (prints JSON):
GROQ_API_KEY=... python generate_script.py --topic "Subah jaldi uthne ke fayde"
```

Output: `./out/<id>.mp4` and the kit's `out/<id>.mp4`.
Change the look in the kit's `src/brand.ts` (colours, font, handle).

## Use it on GitHub Actions

Push this folder as a repo, add a secret `GROQ_API_KEY` (only for topics),
then Actions -> Make a reel -> Run workflow. Fill in topic OR script,
a reel id, and the voice engine. Download the MP4 from Artifacts.
See the comments at the top of `.github/workflows/make-reel.yml`.

## Manual mode (fastest for Chatterbox)

If Actions CPU is too slow, run `narrate_chatterbox.py` on your Mac
(8GB, MPS) or on Colab GPU, then run the kit steps by hand:

```bash
npm run new -- my-reel
# put script in projects/my-reel/voice.txt and captions.txt (exact same words)
npm run voice -- my-reel --provider own --file vo.wav
npm run sync -- my-reel --lang hi
npm run render -- my-reel
```

## What this factory does NOT do

- It does not clone anyone else's voice. Use `--voice-reference` only with
  your own recording, or a voice you have permission to clone.
- It does not make AI video clips (Sora/Runway style). It renders the Reel
  Studio Kit's 2D code scenes, timed to the voice, with karaoke captions.
  That is the free route; real AI video generation is not free unlimited.
- It does not silently fall back to another voice. If Chatterbox fails,
  `make_reel.py` stops and says so. Pass `--voice-engine gtts` explicitly
  if you want the fast test voice instead.
- On this VM only, Remotion cannot fetch Google Fonts through the proxy
  (Chromium TLS error). `--font-patch` swaps in a system font for that render
  and restores the kit file afterwards. On your Mac and on GitHub runners,
  Google Fonts work normally, so do not use `--font-patch` there.

## Files

- `make_reel.py` - orchestrator: script -> new reel -> voice -> sync -> render
- `generate_script.py` - Groq free-tier script generator (stdlib only)
- `narrate_chatterbox.py` - generalised Chatterbox Hindi narration
- `dummy-script-hi.txt` - example Hindi script, for testing without Groq
- `.github/workflows/make-reel.yml` - free Actions generation
- `.env.example`, `.gitignore`
# reel-factory
