#!/usr/bin/env python3
"""Hindi narration with Chatterbox Multilingual, generalised for reuse.

This is a generalised version of the user's narrate_chatterbox.py (Diwali reel).
What changed, and why:
- The Diwali version had 9 hardcoded scenes and a fixed video to mux into.
  A reusable factory cannot do that: a new reel's length must ADAPT to its
  voice, so scenes, timings and the --video mux step are removed.
- Input is now any text file (or --text). Output is one wav, not a finished mp4.
  The Reel Studio Kit then re-syncs captions to this wav and renders the video,
  so its duration is last-word-end + 0.8s automatically.

Run on a machine with a GPU if you can (Mac MPS, Colab GPU, or a CUDA PC).
CPU works but is slow: expect several minutes for a 60s narration, and torch
CPU install is large. GitHub Actions CPU runners work, they are just slow;
see .github/workflows/make-reel.yml for the cached setup.

    pip install chatterbox-tts torchaudio
    # CPU-only torch (much smaller download than the CUDA build):
    #   pip install torch --index-url https://download.pytorch.org/whl/cpu
    python narrate_chatterbox.py --text-file script-hi.txt --out vo.wav
    # optional: --voice my_reference_voice.wav  (10-20 s clean sample, to clone a voice)
    # optional: --device cpu | mps | cuda  (default: cuda if available, else cpu)

Sentence splitting: Hindi danda (।) plus . ? ! . Long sentences are split
on commas so no single generation is very long. Sentences are joined with
0.35s of silence, the same gap used in the user's locked Chatterbox workflow.
"""
import argparse, re, sys

GAP = 0.35


def split_sentences(text):
    text = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[।.?!])\s+", text)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # Split over-long sentences on commas, keeping the comma with the chunk.
        while len(p) > 250:
            cut = p.rfind(",", 0, 250)
            if cut < 50:
                break
            out.append(p[:cut + 1].strip())
            p = p[cut + 1:].strip()
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text-file", default=None)
    ap.add_argument("--text", default=None)
    ap.add_argument("--out", required=True)
    ap.add_argument("--voice", default=None, help="optional reference wav for voice cloning")
    ap.add_argument("--device", default=None)
    ap.add_argument("--language", default="hi")
    ap.add_argument("--exaggeration", type=float, default=0.5)
    ap.add_argument("--cfg", type=float, default=0.5)
    ap.add_argument("--gap", type=float, default=GAP)
    args = ap.parse_args()

    if args.text_file:
        text = open(args.text_file, encoding="utf-8").read()
    elif args.text:
        text = args.text
    else:
        print("ERROR: pass --text-file or --text", file=sys.stderr)
        sys.exit(2)
    sentences = split_sentences(text)
    if not sentences:
        print("ERROR: no sentences found in the script", file=sys.stderr)
        sys.exit(2)

    import torch, torchaudio as ta
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"loading Chatterbox multilingual on {device}")
    model = ChatterboxMultilingualTTS.from_pretrained(device=device)

    chunks = []
    for i, s in enumerate(sentences):
        print(f"  [{i + 1}/{len(sentences)}] {s[:60]}")
        wav = model.generate(s, language_id=args.language, audio_prompt_path=args.voice,
                             exaggeration=args.exaggeration, cfg_weight=args.cfg)
        chunks.append(wav.cpu())
        if i < len(sentences) - 1:
            chunks.append(torch.zeros(1, int(model.sr * args.gap)))
    out = torch.cat(chunks, dim=1)
    ta.save(args.out, out, model.sr)
    print(f"done -> {args.out} ({out.shape[1] / model.sr:.1f}s, {len(sentences)} sentences)")


if __name__ == "__main__":
    main()
