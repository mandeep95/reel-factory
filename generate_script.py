#!/usr/bin/env python3
"""Generate a Hindi reel script from a topic, using Groq's free tier.

No extra dependencies: stdlib urllib only.

    GROQ_API_KEY=... python generate_script.py --topic "Subah jaldi uthne ke fayde"
    python generate_script.py --topic "X" --dry-run   # print the prompt, no API call

Output is JSON on stdout:
    {"script": "...full spoken Hindi...", "title": "...",
     "lines": ["...", "...", "..."], "keyword": "SAVE",
     "caption": "...", "hashtags": ["#..."]}

Free-tier facts, check them before you rely on them:
- Groq has a free tier with no card, but you DO need a free API key from
  console.groq.com, and rate limits apply (requests/day and tokens/min).
  Put the key in a GitHub Actions secret named GROQ_API_KEY, never in code.
- Default model llama-3.1-8b-instant is a fast free-tier model. If Groq
  retires it, change --model to another free model listed on console.groq.com.
- If you pass --script-file to make_reel.py, this script is never called,
  so a reel costs nothing at all.
"""
import argparse, json, os, sys, urllib.request

PROMPT = """You write short Hindi Instagram reels. Reply with JSON ONLY, no markdown, no explanation.
Topic: {topic}

Rules:
- script: full spoken text in Hindi Devanagari, one paragraph, 120-160 words,
  under 60 seconds when spoken. Start with a hook in the first 3 seconds.
  Then 3 clear points, then a call to action asking viewers to comment the keyword.
  No emojis, no English words except the keyword, no invented statistics.
- title: the hook in at most 7 Hindi words, for the on-screen title card.
- lines: exactly 3 short lines, one per point, at most 6 words each, for cards.
- keyword: ONE English word, uppercase, for the comment CTA.
- caption: 2 lines in Hindi for the Instagram caption, plus the keyword CTA.
- hashtags: 5-8 Hindi/English hashtags, no spaces inside a hashtag.

JSON shape:
{{"script": "...", "title": "...", "lines": ["...", "...", "..."],
  "keyword": "SAVE", "caption": "...", "hashtags": ["#..."]}}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True)
    ap.add_argument("--model", default="llama-3.1-8b-instant")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    prompt = PROMPT.format(topic=args.topic)
    if args.dry_run:
        print(prompt)
        return

    key = os.environ.get("GROQ_API_KEY")
    if not key:
        print("ERROR: GROQ_API_KEY is not set. Get a free key at console.groq.com "
              "and set it as an env var, or as a GitHub secret GROQ_API_KEY. "
              "Or skip Groq: pass --script-file to make_reel.py instead.", file=sys.stderr)
        sys.exit(2)

    body = json.dumps({
        "model": args.model,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": "You write Hindi Instagram reel scripts. Reply with JSON only."},
            {"role": "user", "content": prompt},
        ],
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.load(r)
    except Exception as e:
        print(f"ERROR: Groq request failed: {e}", file=sys.stderr)
        sys.exit(1)

    text = data["choices"][0]["message"]["content"].strip()
    # Tolerate a model that wraps JSON in ```json fences.
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    try:
        out = json.loads(text)
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        out = json.loads(text[start:end + 1])
    for k in ("script", "title", "lines", "keyword"):
        if k not in out:
            print(f"ERROR: Groq reply is missing field {k}: {text[:300]}", file=sys.stderr)
            sys.exit(1)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
