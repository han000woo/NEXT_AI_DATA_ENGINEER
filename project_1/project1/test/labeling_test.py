from youtube_transcript_api import YouTubeTranscriptApi
 
video_id="rg_XO_6fKws"
yttp = YouTubeTranscriptApi()
srt = yttp.fetch(video_id, languages=['ko'])
 
with open("script.txt", "w", encoding="utf-8") as f:
    for i in srt:
        f.write("{}\n".format(i["text"]))