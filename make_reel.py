#!/usr/bin/env python3
"""Reusable reel factory: topic OR script in, MP4 out.

    # Script you already wrote (Hindi, Devanagari):
    python make_reel.py --script-file dummy-script-hi.txt --id subah-jaldi --voice-engine gtts
    # Topic only (needs GROQ_API_KEY, free tier, see generate_script.py):
    python make_reel.py --topic "Subah jaldi uthne ke fayde" --voice-engine chatterbox
    # Chatterbox is the default voice engine. gtts is only a fast local fallback
    # for testing on a machine with no GPU; it is NOT a voice clone.

    # Only on this VM (Chromium cannot fetch Google Fonts through its proxy):
    python make_reel.py --script-file dummy-script-hi.txt --id test1 --voice-engine gtts --font-patch

Pipeline, in order:
  1. script: from --script-file, or from Groq via generate_script.py --topic
  2. new reel: kit `npm run new -- <id>` (generic template, duration adapts to voice)
  3. voice: Chatterbox (narrate_chatterbox.py, Hindi) or gTTS, then kit
     `npm run voice -- <id> --provider own --file <audio>` (converts to 44.1kHz mono wav)
  4. sync: kit `npm run sync -- <id> --lang hi` (local faster-whisper, free,
     re-times YOUR words, so captions match the new voice; see the kit's README)
  5. render: kit `npm run render -- <id>` -> kit/out/<id>.mp4, copied to ./out/<id>.mp4

Requirements: Node 18+, ffmpeg, Python 3.11-3.13, and a Reel Studio Kit folder
(--kit-dir, default: ../reel-studio-kit-demo/reel-studio-kit relative to this
file, or ./reel-studio-kit if that exists). The kit itself is free (MIT);
download reel-studio-kit.zip from https://getanimo.io/blog/reel-studio-kit
and unzip it if you do not have it yet. Do NOT commit node_modules or out/.
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(cmd, cwd, what):
    print(f"$ {' '.join(str(c) for c in cmd)}")
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode != 0:
        print(f"ERROR: {what} failed (exit {r.returncode})", file=sys.stderr)
        sys.exit(r.returncode)


def slugify(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "reel"


def find_kit(explicit):
    if explicit:
        p = Path(explicit).expanduser()
    else:
        for cand in (HERE.parent / "reel-studio-kit-demo" / "reel-studio-kit",
                     HERE / "reel-studio-kit"):
            if (cand / "package.json").exists():
                p = cand
                break
        else:
            p = HERE / "reel-studio-kit"
    if not (p / "package.json").exists():
        print(f"ERROR: Reel Studio Kit not found at {p}. Download reel-studio-kit.zip "
              "from https://getanimo.io/blog/reel-studio-kit, unzip it, and pass "
              "--kit-dir <folder> (the folder containing package.json).", file=sys.stderr)
        sys.exit(2)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default=None)
    ap.add_argument("--script-file", default=None)
    ap.add_argument("--id", default=None, help="reel slug, e.g. subah-jaldi (must be new in the kit)")
    ap.add_argument("--kit-dir", default=None)
    ap.add_argument("--voice-engine", choices=["chatterbox", "gtts"], default="chatterbox")
    ap.add_argument("--voice-reference", default=None, help="wav for Chatterbox voice cloning")
    ap.add_argument("--groq-model", default="llama-3.1-8b-instant")
    ap.add_argument("--font-patch", action="store_true", help="VM-only: use system fonts for render")
    ap.add_argument("--skip-render", action="store_true")
    ap.add_argument("--force", action="store_true", help="reuse an existing reel id in the kit")
    args = ap.parse_args()

    if bool(args.topic) == bool(args.script_file):
        print("ERROR: pass exactly one of --topic or --script-file", file=sys.stderr)
        sys.exit(2)
    kit = find_kit(args.kit_dir)
    print(f"kit: {kit}")

    # 1. Script
    meta = {}
    if args.script_file:
        script = Path(args.script_file).read_text(encoding="utf-8").strip()
        script = re.sub(r"\s+", " ", script)
        # Card lines from the script itself, so a script-only reel is not
        # left with the template's "First point" placeholders.
        sentences = [s.strip() for s in re.split(r"[।.?!]\s+", script) if s.strip()]
        card_lines = [" ".join(s.split()[:6]) for s in sentences[1:4]]
        meta = {"title": " ".join(script.split()[:7]), "lines": card_lines, "keyword": "KIT"}
    else:
        r = subprocess.run([sys.executable, str(HERE / "generate_script.py"),
                            "--topic", args.topic, "--model", args.groq_model],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout, r.stderr, file=sys.stderr)
            sys.exit(r.returncode)
        meta = json.loads(r.stdout)
        script = re.sub(r"\s+", " ", meta["script"]).strip()
    words = script.split()
    print(f"script: {len(words)} words")
    if len(words) > 220:
        print("WARNING: script is long for a <60s reel; consider shortening it.", file=sys.stderr)
    reel_id = args.id or slugify(args.topic or Path(args.script_file).stem)
    if (kit / "src" / "reels" / reel_id).exists() and not args.force:
        print(f"ERROR: reel id {reel_id} already exists in the kit. Pass --id <new-slug>.", file=sys.stderr)
        sys.exit(2)

    # 2. New reel in the kit
    if not (kit / "src" / "reels" / reel_id).exists():
        run(["npm", "run", "new", "--", reel_id], cwd=kit, what="kit new reel")
    proj = kit / "projects" / reel_id
    (proj / "voice.txt").write_text(script, encoding="utf-8")
    (proj / "captions.txt").write_text(script, encoding="utf-8")
    (proj / "script.md").write_text(
        f"# {meta.get('title', reel_id)}\n\n{script}\n\n"
        f"Keyword: {meta.get('keyword', 'KIT')}\n"
        f"Caption: {meta.get('caption', '')}\n"
        f"Hashtags: {' '.join(meta.get('hashtags', []))}\n", encoding="utf-8")
    # Fill the generic template's title/cards from the script, so a new reel
    # is not just placeholders. Scene timing stays word-based, so it adapts.
    reel_tsx = kit / "src" / "reels" / reel_id / "Reel.tsx"
    t = reel_tsx.read_text(encoding="utf-8")
    title = meta.get("title") or " ".join(words[:7])
    t = t.replace('text="Your hook, max 7 words"', f'text="{title}"')
    lines = meta.get("lines") or []
    if len(lines) >= 2:
        t = t.replace("First point", lines[0]).replace("Second point", lines[1])
    t = t.replace('keyword="KEYWORD"', f'keyword="{meta.get("keyword", "KIT")}"')
    reel_tsx.write_text(t, encoding="utf-8")

    # 3. Voice
    tmp_audio = Path("/tmp") / f"{reel_id}-vo.mp3"
    if args.voice_engine == "chatterbox":
        tmp_wav = Path("/tmp") / f"{reel_id}-vo.wav"
        cmd = [sys.executable, str(HERE / "narrate_chatterbox.py"),
               "--text-file", str(proj / "voice.txt"), "--out", str(tmp_wav)]
        if args.voice_reference:
            cmd += ["--voice", args.voice_reference]
        run(cmd, cwd=HERE, what="Chatterbox narration")
        tmp_audio = tmp_wav
    else:
        try:
            from gtts import gTTS
        except ImportError:
            print("ERROR: gtts is not installed. pip install gtts (in a venv).", file=sys.stderr)
            sys.exit(2)
        gTTS(text=script, lang="hi", slow=False).save(str(tmp_audio))
        print(f"gTTS voice -> {tmp_audio}")
    run(["npm", "run", "voice", "--", reel_id, "--provider", "own", "--file", str(tmp_audio)],
        cwd=kit, what="kit voice import")

    # 4. Sync (install the caption venv once, if needed)
    if not (kit / "tools" / ".venv" / "bin" / "python").exists():
        print("Caption venv missing, running kit setup (once, downloads faster-whisper)...")
        run(["npm", "run", "setup:captions"], cwd=kit, what="kit caption setup")
    run(["npm", "run", "sync", "--", reel_id, "--lang", "hi"], cwd=kit, what="caption sync")

    # 5. Render
    if args.skip_render:
        print("Skipped render (--skip-render). Voice + sync are done.")
        return
    fonts_path = kit / "src" / "fonts.ts"
    orig_fonts = fonts_path.read_text(encoding="utf-8") if args.font_patch else None
    try:
        if args.font_patch:
            fonts_path.write_text(
                'export const FONTS = { Inter: "Noto Sans, sans-serif", '
                'SpaceGrotesk: "Noto Sans, sans-serif", Nunito: "Noto Sans, sans-serif" } as const;\n'
                'export type FontName = keyof typeof FONTS;\n', encoding="utf-8")
        run(["npm", "run", "render", "--", reel_id], cwd=kit, what="kit render")
    finally:
        if orig_fonts is not None:
            fonts_path.write_text(orig_fonts, encoding="utf-8")
            print("fonts.ts restored (font patch was render-only)")

    src_mp4 = kit / "out" / f"{reel_id}.mp4"
    out_dir = HERE / "out"
    out_dir.mkdir(exist_ok=True)
    dst = out_dir / f"{reel_id}.mp4"
    shutil.copyfile(src_mp4, dst)
    size = dst.stat().st_size / 1e6
    print(f"\nDONE -> {dst} ({size:.1f} MB)")
    print(f"Also in kit: {src_mp4}")
    print("Next: watch it, then change brand in kit/src/brand.ts or the script and re-run.")


if __name__ == "__main__":
    main()
