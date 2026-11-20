# auto-video-clipper

Turn long videos into short vertical clips (Shorts / Reels / TikTok) for free.

Two parts:

1. **`clipper.py`** – a script that runs on your own computer. Give it a video file or a YouTube link. It writes a transcript, picks the best moments, and cuts vertical 9:16 clips.
2. **A skill for Claude** – Claude picks smarter moments from a transcript, and cuts clips for you when you attach the video file.

## Use the script

One-time setup:

```
pip install yt-dlp faster-whisper
```

Also install [ffmpeg](https://ffmpeg.org/download.html) (Windows: `winget install ffmpeg`).

Run:

```
python clipper.py "https://www.youtube.com/watch?v=VIDEO_ID"
python clipper.py myvideo.mp4 --count 8 --min 30 --max 60
python clipper.py myvideo.mp4 --times "12:30-13:20,45:00-45:50"
```

Clips are saved in the `clips` folder, with `transcript.txt` and `clips.csv`.

Only use videos you own or have permission to use.

## Add the skill to Claude

Install as a plugin:

```
/plugin marketplace add YOUR_GITHUB_NAME/auto-video-clipper
/plugin install auto-video-clipper@auto-video-clipper
```

Or add it by hand: zip the `skills/auto-video-clipper` folder and upload it in Claude under Settings, Capabilities, Skills.

## Limits

- Automatic picking uses simple rules (strong words, questions, fast speech). For better picks, give Claude the transcript.
- Clips are cropped from the center.
