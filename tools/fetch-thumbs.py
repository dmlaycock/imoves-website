#!/usr/bin/env python3
"""Version C: fetch each video's designed thumbnail from Wistia (while it still exists) and save it as
video/thumbs/<wistia id>.jpg and .webp at 1280x720. Runs in GitHub Actions because the authoring
environment cannot reach embed-ssl.wistia.com. Idempotent: existing files are skipped."""
import json, os, requests
from PIL import Image
from io import BytesIO
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
urls = json.load(open(os.path.join(ROOT, 'tools', 'video-thumb-urls.json')))
out = os.path.join(ROOT, 'video', 'thumbs'); os.makedirs(out, exist_ok=True)
done = 0
for wid, h in urls.items():
    jpg = os.path.join(out, wid + '.jpg')
    if os.path.exists(jpg): continue
    r = requests.get(f'https://embed-ssl.wistia.com/deliveries/{h}.jpg?image_crop_resized=1280x720', timeout=60)
    r.raise_for_status()
    im = Image.open(BytesIO(r.content)).convert('RGB')
    im.save(jpg, 'JPEG', quality=85, optimize=True)
    im.save(os.path.join(out, wid + '.webp'), 'WEBP', quality=82, method=6)
    done += 1
print('fetched', done, 'of', len(urls))
