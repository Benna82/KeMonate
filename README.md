# KeMonate

A local, creator-centred archive of African stories. Built from `goal.md`, `master.md` and the supplied `requirements.md`.

## Start on Windows

Install Python 3.10 or newer from python.org, including the Python launcher. Extract the ZIP, open a terminal inside the extracted `kemonate` folder, and run:

```powershell
py run.py
```

On macOS / Linux:

```bash
python3 run.py
```

Open **http://127.0.0.1:8000** if the browser does not open automatically. Keep the terminal open. Stop with Ctrl+C. If port 8000 is in use, run `py run.py --port 8010` (or `python3 run.py --port 8010`).

The launcher creates a Python environment, installs dependencies and prepares SQLite. The built frontend is included: **Node.js is not needed to run the delivered app**. Internet is required for first-time Python dependency installation, and for optional AI calls. Images, fonts (system fonts) and map data are local. No accounts or passwords are preloaded: select **Create your account**.

This runs on your computer only. The preview used during development is separate; a localhost URL in someone else's environment cannot start an app on your PC.

## Optional AI

1. Copy `.env.example` to `.env` in the project root.
2. Add your own OpenAI API key as `OPENAI_API_KEY=...`. Keep it private. A ChatGPT subscription is separate from API billing.
3. Restart `run.py`.
4. In the studio, explicitly grant permission to send that story's material to OpenAI.
5. Choose **Transcribe / describe** for audio, video or pictures. For pictures, the model describes visible artwork and extracts visible text; it cannot recover a spoken language or an artist's biography from appearance.
6. Choose **Detect language & translate** to identify the language of the resulting source text and translate it to English.
7. Choose **Create story drafts** to produce a biography, article, timeline, tags, cultural context, podcast outline and documentary outline.

For video transcription install **FFmpeg** from ffmpeg.org and ensure `ffmpeg` is on PATH. Audio uploads do not require FFmpeg. All uploads are capped at 24 MB. Extracted audio must also fit the API limit. Use short clips for the demo. MP4 and MOV are the supported video containers; WebM is supported when the browser provides the correct media type. Codec playback depends on the browser.

Defaults are `gpt-4.1-mini` for text and image understanding and `gpt-4o-mini-transcribe` for audio. Set `OPENAI_TEXT_MODEL` or `OPENAI_TRANSCRIPTION_MODEL` to compatible models if needed. AI calls use the server-side SDK; no API key is sent to the frontend. Responses use `store=False`; this setting is not a promise of zero data retention by a provider. Evaluate the applicable service data terms before using sensitive interviews.

AI is real when configured, not simulated. Without a key, capture, manual transcripts, manual translations, editing, review, publishing and export work normally. AI accuracy varies by language, dialect, noise and recording quality. Human review is required. Podcast and documentary outputs are **written outlines**, not rendered audio or video. AI integrations were checked with mocked service responses and missing-key tests; no live paid API call was made during this build.

## A first story

1. Create a username and password; passwords are hashed by Django.
2. Open Creator Studio, enter a story title and creator name, and create a private draft.
3. Set the location, art form and source language. Upload one source file, or record audio in a browser that supports MediaRecorder. Recording requires permission and localhost / a secure browser context.
4. Add the original transcript or notes. Run the optional AI steps, or edit everything manually.
5. **Save draft**, then confirm review of the saved material. Any changes to source, translation, drafts or media clear the review and return the story to private status.
6. Confirm publication permission. Resolve any cultural restrictions with the appropriate people; do not simply clear a restriction to bypass it. Nonempty restrictions block publication.
7. Select **Publish story**. It appears in Discover Stories and the atlas filters.
8. **Withdraw from archive** or revoke permission to make it private again. This cannot recall copies someone already exported.
9. Export the JSON record from the studio. Open a published story to print / save a PDF or copy its text.

Draft files are available only through permission-checked API routes. Public stories are visible to any visitor to that running local instance. The app does not verify that a submitter has actually obtained consent; the current controls record their attestation.

## Included

- Django 5.2, SQLite, React + TypeScript, Tailwind CSS and Framer Motion.
- Responsive layouts, light/dark mode, keyboard focus, reduced-motion support and modal focus trapping.
- Username/password registration, login, logout, password validation, sessions and CSRF protection.
- Private story records; image/audio/video upload validation; browser audio recording.
- Optional speech transcription, image description/OCR, text language identification and English translation.
- Editable original text, translation and generated drafts kept separately.
- Separate permissions for AI processing and public sharing; review and cultural restriction gates.
- Discovery search, language and art form filters, and a clickable country map with region filtering.
- Four sourced editorial artist profiles: Miriam Makeba, Johnny Clegg, Lena Hugo and Mbali Tshabalala.
- Story JSON exports with audit events, and browser PDF printing of published stories.

## Data and backups

Your local data is in:

- `backend/db.sqlite3`: accounts, story text, consent flags and audit events.
- `backend/media/`: source uploads.
- `backend/.local-secret`: local session signing secret, created at first launch.

Stop the server and back up these three items together. Keep `.env` separately and securely. Exported JSON does **not** contain the uploaded media bytes. To restore, stop the server, replace the data files and restart. Permanent deletion removes a story and its current upload; independent backups and exported copies remain until you remove those yourself.

## Development

Requires Node.js 20.19+ (22.12+ recommended) and Python 3.10+. After `run.py` has installed Python dependencies:

```bash
cd frontend
npm ci
npm run build
cd ..
```

For live frontend development, run Django in one terminal:

```bash
# Windows
.venv\Scripts\python backend\manage.py runserver 127.0.0.1:8000
# macOS / Linux
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

Then in another terminal:

```bash
cd frontend
npm run dev
```

Open Vite's printed URL. Its development proxy forwards `/api` to Django and normalises Origin for local CSRF checks. This proxy and Django's development server are for local use only. Do not expose them to the internet.

Run backend integration tests with:

```bash
# Windows
.venv\Scripts\python backend\manage.py test archive
# macOS / Linux
.venv/bin/python backend/manage.py test archive
```

## Before a real launch

See `PRODUCT_NOTES.md` for recommended decisions and the differences between this local MVP and the wider master vision. In particular: this is not a hardened, backed-up, moderated production archive. Use a production server, HTTPS, independent media storage, request quotas, account recovery, moderation and community governance before real public use.

## Sources and attribution

Each artist profile links to its biography source and photo source. See `IMAGE_CREDITS.md` for licences and image credits. Featured artists are editorial references, not claimed members, customers or endorsers. Lena Hugo and Mbali Tshabalala photographs are included as local demonstration references; their rights remain with their respective rights holders. Obtain appropriate permission or replacements before redistributing or publicly deploying them.
