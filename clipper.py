#!/usr/bin/env python3
"""
Free auto clipper. Runs on YOUR computer.
Video (file or YouTube link) -> transcript -> best moments -> vertical 9:16 mp4 clips.

Setup (one time):
    pip install yt-dlp faster-whisper
    install ffmpeg (https://ffmpeg.org/download.html)

Use:
    python clipper.py myvideo.mp4
    python clipper.py "https://youtube.com/watch?v=XXXX" --count 8 --min 30 --max 60
    python clipper.py myvideo.mp4 --times "12:30-13:20,45:00-45:50"   (your own times)

Only use videos you own or have permission to use.
"""
import argparse, csv, os, re, subprocess

HOOK = re.compile(
    r"\b(secret|mistake|never|always|biggest|worst|best|why|how|truth|stop|actually|"
    r"nobody|everyone|free|money|story|learned|warning|crazy|real|problem|lesson)\b", re.I)


def run(cmd):
    subprocess.run(cmd, check=True)


def download(url):
    run(["yt-dlp", "-f", "bv*[height<=1080]+ba/b", "--merge-output-format", "mp4",
         "-o", "input.%(ext)s", url])
    return "input.mp4"


def transcribe(path):
    from faster_whisper import WhisperModel
    model = WhisperModel("small", compute_type="int8")
    segs, _ = model.transcribe(path, vad_filter=True)
    return [(s.start, s.end, s.text.strip()) for s in segs]


def ends_sentence(text):
    return text.endswith((".", "?", "!"))


def pick_clips(segs, count, lo, hi):
    cands = []
    for i in range(len(segs)):
        if i > 0 and not ends_sentence(segs[i - 1][2]):
            continue  # start only at the start of a sentence
        start = segs[i][0]
        for j in range(i, len(segs)):
            end = segs[j][1]
            dur = end - start
            if dur > hi:
                break
            if dur >= lo and ends_sentence(segs[j][2]):
                text = " ".join(s[2] for s in segs[i:j + 1])
                first = segs[i][2]
                score = (
                    2.0 * len(HOOK.findall(text))
                    + 1.5 * text.count("?")
                    + 0.5 * len(re.findall(r"\d+", text))
                    + 3.0 * bool(HOOK.search(first) or "?" in first)  # strong opening
                    + 4.0 * len(text.split()) / dur                    # fast, dense speech
                )
                cands.append((score, start, end, text))
    cands.sort(reverse=True)
    chosen = []
    for c in cands:
        if all(c[2] <= o[1] or c[1] >= o[2] for o in chosen):  # no overlap
            chosen.append(c)
        if len(chosen) == count:
            break
    return sorted(chosen, key=lambda c: c[1])


def parse_time(t):
    parts = [float(p) for p in t.strip().split(":")]
    sec = 0
    for p in parts:
        sec = sec * 60 + p
    return sec


def cut(path, start, end, out):
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-i", path,
         "-t", str(end - start),
         "-vf", "crop=ih*9/16:ih,scale=1080:1920",  # centre crop to vertical
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-c:a", "aac", "-b:a", "160k", out])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="video file or YouTube link")
    ap.add_argument("--count", type=int, default=6)
    ap.add_argument("--min", type=int, default=30, dest="lo")
    ap.add_argument("--max", type=int, default=60, dest="hi")
    ap.add_argument("--times", help='your own clips, like "12:30-13:20,45:00-45:50"')
    ap.add_argument("--out", default="clips")
    a = ap.parse_args()

    path = download(a.source) if a.source.startswith("http") else a.source
    os.makedirs(a.out, exist_ok=True)

    rows = []
    if a.times:
        for n, rng in enumerate(a.times.split(","), 1):
            s, e = rng.split("-")
            rows.append((n, parse_time(s), parse_time(e), ""))
    else:
        print("Transcribing (first run downloads a model, be patient)...")
        segs = transcribe(path)
        with open(os.path.join(a.out, "transcript.txt"), "w", encoding="utf-8") as f:
            for s, e, t in segs:
                f.write(f"[{s:7.1f}-{e:7.1f}] {t}\n")
        for n, (score, s, e, text) in enumerate(pick_clips(segs, a.count, a.lo, a.hi), 1):
            rows.append((n, s, e, text))

    with open(os.path.join(a.out, "clips.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["clip", "start_sec", "end_sec", "text"])
        for n, s, e, text in rows:
            out = os.path.join(a.out, f"clip_{n:02d}.mp4")
            print(f"Cutting clip {n}: {s:.0f}s to {e:.0f}s")
            cut(path, s, e, out)
            w.writerow([n, round(s, 1), round(e, 1), text])
    print(f"Done. Clips are in the '{a.out}' folder.")


if __name__ == "__main__":
    main()
