import sys
import random
import subprocess
import urllib.parse
import urllib.request
import json
import os


SEASON_2_EPISODE = {1: 33, 2: 26, 3: 26, 4: 20, 5: 24, 6: 23, 7: 24, 8: 27, 9: 24, 10: 22}

SES_NAMES = {
    1: "პირველ",
    2: "მეორე",
    3: "მესამე",
    4: "მეოთხე",
    5: "მეხუთე",
    6: "მეექვსე",
    7: "მეშვიდე",
    8: "მერვე",
    9: "მეცხრე",
    10: "მეათე"
}

API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
USERNAME = "@TVIMEDI"
SEARCH_BASE = "https://www.googleapis.com/youtube/v3/search"
CHANNELS_BASE = "https://www.googleapis.com/youtube/v3/channels"


def err(msg):
    print(msg)
    sys.exit(1)


def parse_args():
    s = None
    e = None
    args = sys.argv[1:]
    for i, a in enumerate(args):
        if a in ("-s", "--season") and i + 1 < len(args):
            try:
                s = int(args[i + 1])
            except:
                pass
        if a in ("-e", "--episode") and i + 1 < len(args):
            try:
                e = int(args[i + 1])
            except:
                pass
    return s, e


def pick_random(season, episode):
    if season is None:
        season = random.randint(1, 10)
    if season not in SEASON_2_EPISODE:
        return season, episode
    if episode is None:
        episode = random.randint(1, SEASON_2_EPISODE[season])
    return season, episode


def validate_ranges(s, e):
    if s is None or not (1 <= s <= 10):
        err("მხოლოდ პირველიდან მეათე სეზონის ჩათვლით დევს კონსისტენტურად იუთუბზე")
    maxe = SEASON_2_EPISODE[s]
    if not (1 <= e <= maxe):
        ses = SES_NAMES[s]
        err(f"{ses} სეზონში {e} სერია არაა, მხოლოდ {maxe} სერიაა")


def get_channel_id_by_username(username):
    if not API_KEY:
        return None
    params = {"part": "id", "forUsername": username.lstrip("@"), "key": API_KEY}
    url = CHANNELS_BASE + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.load(r)
            items = data.get("items", [])
            if items:
                return items[0]["id"]
    except:
        print("რაღაც პრობლემაა urllib.request-თან")
    return None


def youtube_search_video(title, channel_id=None):
    params = {
        "part": "snippet",
        "q": title,
        "type": "video",
        "maxResults": 1
    }
    if API_KEY:
        params["key"] = API_KEY
    if channel_id:
        params["channelId"] = channel_id
    url = SEARCH_BASE + "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.load(r)
            items = data.get("items", [])
            if items:
                return items[0]["id"]["videoId"]
    except:
        pass
    return None


def stream_in_terminal(video_id):
    play_url = f"https://www.youtube.com/watch?v={video_id}"
    player = os.environ.get("TERMPROG", "mpv")
    try:
        subprocess.run([player, play_url])
    except:
        try:
            subprocess.run(["mpv", play_url])
        except:
            err("MPV ვერ ჩაირთო")


def main():
    s, e = parse_args()
    s, e = pick_random(s, e)
    validate_ranges(s, e)
    title = f"შუა ქალაქში - სეზონი {s}, სერია {e}"
    print("იტვირთება", title, "⏳")
    channel_id = get_channel_id_by_username(USERNAME)
    video_id = youtube_search_video(title, channel_id)
    if not video_id:
        query = f"{title} TVIMEDI"
        video_id = youtube_search_video(query)
    if not video_id:
        err("ვერ მოიძებნა ვიდეო იუთუბზე")
    stream_in_terminal(video_id)


if __name__ == "__main__":
    main()
