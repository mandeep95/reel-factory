# Setup in 5 simple steps

No code knowledge needed. You do steps 1 and 2 once. Steps 3 to 5 are for every reel.

## Step 1: Make a repo on GitHub (once)

1. Go to github.com/new in your browser. Sign in if needed.
2. Repository name: type `reel-factory` (or any name you like).
3. Choose **Public**. Public = unlimited Actions minutes. Private = 2,000 free minutes a month.
4. Do NOT tick "Add a README". Leave everything else as it is.
5. Click **Create repository**.
6. GitHub will show you a page with a link like `https://github.com/YOURNAME/reel-factory.git`.
   Copy that link. You need it in Step 2.

I cannot make the repo for you, and I cannot add secrets for you. GitHub only
lets the account owner do those two things. Everything else is in this zip.

## Step 2: Push this folder to that repo (once)

1. Download the zip, unzip it, and open the folder you get.
   On your laptop, open a terminal in that folder.
   - Mac/Linux: right-click the folder, or in Terminal type `cd` then drag the folder in, then Enter.
   - Windows: open the folder, click the address bar, type `cmd`, then Enter.
2. Run the push script, and paste your repo link when it asks:
   - Mac/Linux: `bash push.sh`
   - Windows: double-click `push.bat`, or type `push.bat` in the cmd window.
   The script asks for your repo link, then runs git init, add, commit, and push.
   If git is not installed, install it first: Mac `brew install git`,
   Windows `winget install Git.Git`, Linux `sudo apt install git`.
3. Refresh your repo page on GitHub. You should see these files:
   `make_reel.py`, `generate_script.py`, `narrate_chatterbox.py`,
   `README.md`, and a folder `.github/workflows/make-reel.yml`.
   If you do not see `.github`, the workflow will not run. Check that you
   pushed the whole folder, including hidden files, not just the .py files.

## Step 3: Add your Groq key as a secret (once, only if you use topics)

Skip this step if you always paste your own script. Groq is only needed for topics.

1. Get a free key: go to console.groq.com, sign up, create an API key.
   No card is needed for the free tier.
2. Go to your repo on GitHub, then:
   Settings -> Secrets and variables -> Actions -> New repository secret.
   If you cannot find it on mobile, use this direct link and change the names:
   `https://github.com/YOURNAME/reel-factory/settings/secrets/actions`
3. Name: type exactly `GROQ_API_KEY`
   Secret: paste your key, then click Add secret.
4. Never paste the key in code, in a script file, in a chat message, or in
   a workflow input box. Secrets stay hidden in GitHub.

## Step 4: Make a reel (every time)

1. Go to your repo on GitHub, click the **Actions** tab.
2. On the left, click **Make a reel**, then click **Run workflow** on the right.
3. Fill in ONLY ONE of these:
   - Topic: e.g. `Subah jaldi uthne ke fayde` (needs the Groq secret), OR
   - Script: paste your full Hindi script in Devanagari.
4. Reel id: type a short slug in small letters and dashes, e.g. `subah-jaldi`.
   Use a new id for every reel. If you reuse an old id, the run will fail.
5. Voice engine: choose `chatterbox` for the real Hindi voice (slow, 15-40 min),
   or `gtts` for a fast test voice.
6. Click the green **Run workflow** button.
7. Wait. Do not close the tab if you want to watch it, but you do not need to
   keep your laptop busy. The work runs on GitHub's computer, not yours.

## Step 5: Download your video (every time)

1. On the Actions run page, wait until the green tick appears.
2. Scroll down to **Artifacts**. Click `reel-<your-reel-id>`.
3. It downloads a zip. Unzip it. Inside is your `<reel-id>.mp4` and `script.md`.
4. Watch the MP4, then post it. If the run has a red cross, click the failed
   step, read the last lines, and check the common problems below.

## Common problems, in plain words

- "GROQ_API_KEY is not set": you used a topic but did not do Step 3, or the
  secret name is spelled wrong. It must be exactly `GROQ_API_KEY`.
- "reel id already exists": you used the same reel id twice. Use a new slug.
- Run is slow: normal. Chatterbox on a CPU runner is slow. First run is the
  slowest, because it downloads torch, the model, Whisper, and the browser.
  Later runs use the cache and are faster.
- Run fails at the start: check that `.github/workflows/make-reel.yml` is in
  the repo. If it is missing, the Actions tab will not show "Make a reel".

## Bookmarks for later

- Groq console (free key): https://console.groq.com
- Chatterbox demo (manual Hindi voice, if you ever want it by hand):
  https://huggingface.co/spaces/ResembleAI/Chatterbox-Multilingual-TTS
- Your repo Actions page:
  https://github.com/YOURNAME/reel-factory/actions
