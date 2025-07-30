# Example: DaVinci Resolve Python Script – Auto-tagging with External AI

This example demonstrates how to use DaVinci Resolve’s Python API to analyze imported video/audio, call an external AI service (e.g., for face recognition or speech-to-text), and write results into Resolve’s metadata.

```python
import DaVinciResolveScript as dvr
import requests

resolve = dvr.scriptapp('Resolve')
project = resolve.GetProjectManager().GetCurrentProject()
media_pool = project.GetMediaPool()
clips = media_pool.GetRootFolder().GetClips()

for clip_id, clip in clips.items():
    file_path = clip.GetClipProperty('File Path')
    # Call your AI tagging API (example: POST video file or audio to external service)
    ai_result = requests.post('http://localhost:5000/ai-tag', files={'file': open(file_path, 'rb')}).json()
    tags = ai_result.get('tags', [])
    # Write tags into Resolve metadata
    clip.SetMetadata('Keywords', ','.join(tags))
```
*You can adapthis to call any AI service (face, speech, etc.) and write any metadata field supported by Resolve.*
