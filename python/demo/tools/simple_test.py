import os, re, shutil, pathlib

SRC = "/source_videos"
DEST = "/videos"

for f in pathlib.Path(SRC).glob("*.*"):
    name = f.name
    # 电视剧检测
    if re.search(r"S\d{2}E\d{2}", name, re.I):
        show = re.split(r"[-_]", name)[0]
        dest = pathlib.Path(DEST) / "TV" / show.strip()
    # 电影检测
    elif re.search(r"(19|20)\d{2}", name):
        dest = pathlib.Path(DEST) / "Movies"
    # 短视频
    else:
        dest = pathlib.Path(DEST) / "Clips"

    # dest.mkdir(parents=True, exist_ok=True)
    # shutil.move(str(f), str(dest / f.name))