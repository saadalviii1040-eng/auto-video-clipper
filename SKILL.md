---
name: auto-video-clipper
description: Use when the user wants to clip, cut, or turn a long video into Shorts/Reels/TikTok clips for free, or wants an automatic clipping script. Picks the best moments from a transcript and cuts finished vertical 9:16 clips.
---

# Auto Video Clipper

Goal: turn a long video into short vertical clips, for free, with no paid credits.

## Rules
- Use simple words. The user may not be a native English speaker.
- Do not use paid tools (vidIQ clip generator, Picsart) unless the user asks for them. They can use credits.
- Only use videos the user owns or has permission to use.
- Do not claim a step worked until it ran. Say plainly what was and was not tested.
- Claude cannot download from YouTube in chat. Downloading happens on the user's computer with `clipper.py`.

## Workflow

1. Ask what the user has: a video file, a YouTube link, or a transcript.

2. **User attached a video file (do the whole job in chat):**
   - Check the tools first: `which ffmpeg`. If ffmpeg is missing, tell the user and fall back to step 4.
   - If the user also gave a transcript, use it. If not, say that speech-to-text is not available in chat (installs may be blocked) and ask for a transcript, or offer `clipper.py` on their computer. Do not make up what is said in the video.
   - Pick the clips (see "Picking clips").
   - Cut each clip with `clipper.py` using `--times`, for example:
     `python /path/to/clipper.py video.mp4 --times "12:30-13:20,45:00-45:50" --out clips`
     This crops to vertical 9:16 from the center.
   - Send each finished clip back with SendUserFile. Large files may fail; say so if they do.

3. **User gave a transcript with timestamps:**
   - Pick the clips (see "Picking clips") and give them the list.
   - Then give the command: `python clipper.py myvideo.mp4 --times "START-END,START-END"`

4. **User gave only a YouTube link, or no file or transcript:**
   - Send `clipper.py` with SendUserFile and explain the setup in simple steps:
     1. Install Python and ffmpeg.
     2. Run `pip install yt-dlp faster-whisper`
     3. Run `python clipper.py "LINK"` and read the `clips` folder.
   - Offer the smarter option: the user pastes `clips/transcript.txt`, Claude picks the moments, and the user re-runs with `--times`.

## Picking clips
- 30-60 seconds each unless the user says otherwise. No overlap.
- Start at the beginning of a sentence. End at the end of a sentence.
- The first sentence must work as a hook: a question, a bold claim, a surprise, or a promise.
- One clear idea per clip that makes sense without the rest of the video.
- For each clip give: start, end, title, hook line, short caption. Keep them short.

## Limits to be honest about
- The script's own automatic picking uses simple rules. Claude's picks from a transcript are better.
- The crop is from the center, so a speaker who is not centered can be cut off.
- Speech-to-text needs `faster-whisper` on the user's computer.

## clipper.py
The script is in this skill's folder: `clipper.py`. Options: `--count`, `--min`, `--max`, `--times`, `--out`.
