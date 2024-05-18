import distyll
from pathlib import Path
from config import ETIENNE_COLLECTION, DSPY_COLLECTION
import os
import json

openai_api_key = os.getenv("OPENAI_APIKEY")
out_dir = Path("./dl_dir")

for videos in [
    ETIENNE_COLLECTION,
    # DSPY_COLLECTION
]:
    for yt_url in videos:
        transcript = distyll.transcripts.from_youtube(
            yt_url=yt_url,
            dl_dir=Path("./dl_dir/etienne"),
            openai_apikey=openai_api_key,
        )
        out_path = out_dir / f"{yt_url.split('/')[-1]}.json"
        out_path.write_text(json.dumps(transcript, indent=2))
        print(f"Saved transcript to {out_path}")
