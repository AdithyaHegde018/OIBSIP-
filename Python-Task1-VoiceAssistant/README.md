# Python Voice Assistant

A desktop voice assistant built in Python that listens to spoken commands,
understands intent using a lightweight NLU layer, performs useful actions
(time, date, weather, web search, email, reminders, general knowledge,
custom commands), and responds through both text-to-speech and the
terminal.

> Developed as part of the **Oasis Infobyte Python Programming Internship
> (OIBSIP) — Task 1: Voice Assistant**.

---

## Features

### Beginner features implemented
- Capture voice input from the microphone
- Responds to greetings ("Hello", "Hi", "Hey")
- Tells the current time and date
- Performs web searches based on spoken queries
- Opens common websites (Google, YouTube, GitHub, LinkedIn)
- Speaks all responses using `pyttsx3` (offline TTS)
- Gracefully handles unrecognized speech
- Handles microphone and network errors without crashing
- Gives feedback in both terminal and voice ("Listening...", "Processing...", etc.)

### Advanced features implemented
- **Natural language intent detection** — recognizes phrasing variations,
  not just exact keywords (regex-pattern based, in `intent_handler.py`)
- **Email** — voice-guided recipient/subject/message flow via `smtplib`
- **Reminders** — natural-language duration parsing + background timers
  via `threading`, so the assistant keeps working while waiting
- **Weather** — OpenWeatherMap integration with temperature, feels-like,
  humidity, condition, and wind speed
- **General knowledge Q&A** — local knowledge base + DuckDuckGo Instant
  Answer API fallback, with an honest "I don't know" instead of guessing
- **Custom commands** — user-defined phrase → URL mappings loaded from
  `custom_commands.json`, no hard-coding required. Matching checks the
  longest phrase first, so a specific command like "open github
  repositories" is matched correctly instead of falling through to the
  shorter "open github"

---

## Technology stack

| Purpose               | Library                     |
|------------------------|------------------------------|
| Speech-to-text          | `SpeechRecognition`, `PyAudio` |
| Text-to-speech          | `pyttsx3` (offline)          |
| HTTP requests            | `requests`                   |
| Environment variables    | `python-dotenv`               |
| Email                   | `smtplib` (standard library)  |
| Reminders                | `threading` (standard library)|
| Date/time                 | `datetime` (standard library) |
| Web actions               | `webbrowser` (standard library) |
| Config/custom commands    | `json` (standard library)     |

---

## Project architecture

```text
Python-Task1-VoiceAssistant/
│
├── main.py               # Entry point — the conversation loop
├── config.py              # Loads .env, holds constants
├── voice_input.py          # Microphone capture + speech-to-text
├── speech_output.py        # pyttsx3 wrapper (speak / status)
├── intent_handler.py        # NLU — text -> intent + entities
├── commands.py             # Dispatcher — intent -> feature module
├── weather.py              # OpenWeatherMap integration
├── email_service.py         # smtplib voice-guided email flow
├── reminder.py              # Duration parsing + threaded timers
├── knowledge.py             # General Q&A (local KB + DuckDuckGo)
├── custom_commands.py        # Loads/executes custom_commands.json
├── custom_commands.json
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── screenshots/
```

**Data flow:** `main.py` → `voice_input.listen()` → `intent_handler.detect_intent()`
(inside `commands.handle_command()`) → the matching feature module →
`speech_output.speak()`.

---

## Installation

### 1. Clone / download the project
```bash
git clone <your-repo-url>
cd Python-Task1-VoiceAssistant
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **Note on PyAudio:** on some systems you may need system-level audio
> libraries first, e.g. on Debian/Ubuntu: `sudo apt-get install portaudio19-dev`,
> then `pip install pyaudio`.

### 4. Configure environment variables
```bash
cp .env.example .env
```
Then edit `.env` and fill in your own values (see below).

---

## OpenWeatherMap API setup

1. Create a free account at https://openweathermap.org/api
2. Generate an API key
3. Put it in `.env` as `OPENWEATHER_API_KEY=...`
4. Weather features are automatically disabled (with a clear spoken
   message) if this key is missing.

## Email configuration

1. Use a **test/dummy email account** during development — do not use a
   primary personal account.
2. For Gmail, generate an **app password** (do not use your real login
   password): https://support.google.com/accounts/answer/185833
3. Set `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `SMTP_SERVER`, `SMTP_PORT` in `.env`.
4. Email features are automatically disabled (with a clear spoken message)
   if credentials are missing.

---

## How to run

```bash
python main.py
```

The assistant will greet you and start listening. If no working
microphone is detected, or speech keeps failing, it automatically
switches to typed input after a few attempts so you can keep testing.

---

## Example voice commands

```
Hello
What time is it?
What's the date today?
What's the weather like in Bangalore?
Search the internet for Python tutorials
Look up machine learning
Open YouTube
Open GitHub
Send an email
Remind me after 10 minutes
Who is the capital of France        (also works as "what is the capital of France")
Exit
```

### Sample session
```text
==================================================
          PYTHON VOICE ASSISTANT
==================================================

Assistant: Hello! How can I help you?

You: What's the weather in Bangalore?
Assistant: Fetching weather...
Assistant: The weather in Bangalore is scattered clouds with a
temperature of 28°C, feeling like 29°C. Humidity is 65% and wind
speed is 3.1 meters per second.

You: Search Python machine learning tutorials
Assistant: Searching the web for python machine learning tutorials.

You: Exit
Assistant: Goodbye! Have a great day.
```

---

## Screenshots

Add screenshots of the running assistant to the `screenshots/` folder,
for example:
- `terminal_greeting.png`
- `weather_lookup.png`
- `email_flow.png`
- `reminder_scheduled.png`

---

## Error handling

The assistant is designed to never crash. It handles, with clear
messages and graceful recovery:

- Microphone unavailable → falls back to typed input after repeated failures
- Speech not recognized → asks the user to repeat
- Speech recognition service unavailable → clear spoken/text error
- Internet unavailable → clear error for any network-dependent feature
- Invalid OpenWeatherMap API key → clear message, feature disabled
- Invalid city name → clear "city not found" message
- Invalid/malformed user input → asked to rephrase
- Email send failure (auth, connection, SMTP errors) → clear message, no crash
- Invalid reminder duration → asked to rephrase
- Missing `custom_commands.json` → treated as no custom commands, app continues
- Missing environment variables → affected feature is disabled with a clear message, rest of the app works normally

---

## Privacy considerations

- **Microphone data:** audio is only captured when actively listening for
  a command (`voice_input.listen()`); it is not recorded or stored to disk.
- **Speech recognition:** by default, this project uses `SpeechRecognition`'s
  Google Web Speech API backend, which means captured audio is sent to
  Google's servers for transcription. No audio is stored locally.
- **External API calls:** weather queries send only the requested city
  name to OpenWeatherMap; knowledge queries send only the question text
  to the DuckDuckGo Instant Answer API. No personal data is attached.
- **Credentials:** the OpenWeatherMap API key and email credentials are
  read only from environment variables (`.env`), never hard-coded, and
  never logged or transmitted anywhere except to their respective services
  (OpenWeatherMap / your configured SMTP server).
- **Email credentials must never be committed to GitHub.** The `.env`
  file is excluded via `.gitignore`; only `.env.example` (with placeholder
  values) is committed.
- **Removing your credentials:** simply delete or clear the values in your
  local `.env` file. Nothing is stored anywhere else by this application.

---

## Security considerations

- No hard-coded passwords or API keys anywhere in source code
- `.env` is excluded from version control via `.gitignore`
- `.env.example` provided with placeholder values only
- All external API responses are validated before use (status codes,
  expected JSON keys) rather than assumed to be well-formed
- No use of `eval()` or arbitrary code execution — custom commands only
  ever open a pre-configured URL
- Email passwords are never stored in `custom_commands.json` or any
  other JSON/config file — only in `.env`

---

## Testing checklist

- [ ] Greeting ("Hello") gets a spoken response
- [ ] "What time is it?" returns the correct current time
- [ ] "What's the date today?" returns the correct current date
- [ ] "Search for Python tutorials" opens a browser search
- [ ] "Open YouTube" / "Open GitHub" open the correct site
- [ ] "What's the weather in <valid city>" returns full weather details
- [ ] Weather lookup with an invalid city gives a clear error
- [ ] Weather lookup with an invalid API key gives a clear error
- [ ] "Send an email" completes the recipient/subject/message/confirm flow
- [ ] Email flow with missing `.env` credentials gives a clear disabled message
- [ ] "Remind me after 10 seconds" fires an audible reminder after the delay
- [ ] A phrase from `custom_commands.json` opens the correct URL
- [ ] An unrecognized command gets a helpful fallback response
- [ ] Speaking unclear/silent audio doesn't crash the app
- [ ] Running with no microphone attached falls back to typed input
- [ ] "Exit" ends the session with a goodbye message

---

## Future improvements

- Add a GUI (e.g. Tkinter or a simple web front-end) alongside the terminal interface
- Support wake-word activation ("Hey Assistant") instead of a fixed loop
- Add persistent reminder storage so reminders survive a restart
- Expand the local knowledge base and/or integrate a richer QA API
- Add multi-language speech recognition and TTS support

---

## Author

Built by Adithya, as part of the **Oasis Infobyte Python Programming
Internship (OIBSIP)** — Task 1: Voice Assistant.
