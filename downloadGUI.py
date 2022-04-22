import os
from pathlib import Path
from platform import system
from time import sleep, monotonic
from urllib.parse import urlparse

import pyttsx3 as pt
import requests as rq
from dearpygui.dearpygui import *
from eta import convert_seconds

create_context()
create_viewport(width=700, height=300, title="Free Download Manager", resizable=False)
setup_dearpygui()

if system() == "Windows":
    path = os.path.join(os.environ['USERPROFILE'], "\\Desktop\\resources\\")

else:
    path = str(Path.home() / "Desktop/resources/")

width, height, channels, data = load_image(path + "/images/add.png")
width1, height1, channels1, data1 = load_image(path + "/images/trash.png")


def say(message):
    engine = pt.init()
    engine.say(message)


sizes = ["B", "KB", "MB", "GB", "TB"]


def process_size(size):
    index = 0
    while size >= 1024 and index <= 3:
        size /= 1024
        index += 1
    if sizes[index] == "byte":
        return f"{round(size)} byte"
    return f"{round(size, 2)} {sizes[index]}"


def units(time):
    if 1000 <= time < 1000000:
        return " kB"
    elif 1000000 <= time < 1000000000:
        return " MB"
    elif 1000000000000 <= time:
        return " GB"


def size_format(b):
    if b < 1000:
        return '%i' % b + ' B'
    elif 1000 <= b < 1000000:
        return '%.1f' % float(b / 1000) + ' KB'
    elif 1000000 <= b < 1000000000:
        return '%.1f' % float(b / 1000000) + ' MB'
    elif 1000000000 <= b < 1000000000000:
        return '%.1f' % float(b / 1000000000) + ' GB'
    elif 1000000000000 <= b:
        return '%.1f' % float(b / 1000000000000) + ' TB'


def add_job():
    try:
        global urlJob
        urlJob = str(get_value("urlInput"))
        save_path = str(get_value("save"))
        parsedUrl = urlparse(urlJob)

        req = rq.get(urlJob, stream=True, allow_redirects=True, timeout=100)
        filename = os.path.basename(parsedUrl.path)
        file_size = int(req.headers['content-length'])

    except rq.ConnectionError as e:
        add_text(label=f"Error! {e}", parent="add_url_popup", tag="problem")
        sleep(1)
        delete_item("problem")

    start = last_print = monotonic()
    downloaded = 0

    hide_item("add_url_popup")

    with open(save_path + "/" + filename, "wb") as f:
        for chunk in req.iter_content(chunk_size=8192):
            if chunk:
                downloaded += f.write(chunk)
                now = monotonic()

                if now - last_print > 1:
                    pct_done = round(downloaded / file_size * 100)
                    speed = round(downloaded / (now - start) / 1024)
                    pct_prgs_done = pct_done / 100
                    show_item("progress")
                    missing = file_size - downloaded
                    ETA = (missing / 1024) / speed

                    if speed < 1000:
                        configure_item("progress",
                                       overlay=f"{filename}  {pct_done}% {speed} KB/s  {convert_seconds(round(ETA))}")
                    if speed >= 1000:
                        configure_item("progress",
                                       overlay=f"{filename}  {pct_done}% {f'{speed / 1000: .1f}'} MB/s  {convert_seconds(round(ETA))}")
                    if speed >= 1000000:
                        configure_item("progress",
                                       overlay=f"{filename}  {pct_done}% {f'{speed / 1000000: .1f}'} GB/s  {convert_seconds(round(ETA))}")

                    set_value("progress", pct_prgs_done)

        set_value("urlInput", "")
        set_value("save", "")
        set_value("progress", 0)
        hide_item("progress")
        configure_item("add_text_job", default_value="")
        configure_item("add_text_job", default_value="Download Completed!")
        say("Download completed!")
        sleep(1)
        configure_item("add_text_job", default_value="")


def delete_all_jobs():
    add_text("To be implemented soon...", tag="soon", parent="download_stage")
    sleep(1)
    delete_item("soon")


def default_save_path():
    default_path = str(Path.home() / "Downloads")
    set_value("save", default_path)


with texture_registry():
    add_static_texture(width, height, data, tag="add_texture")
    add_static_texture(width1, height1, data1, tag="delete_texture")

with window(label="Window", tag="window"):
    with group(horizontal=True):
        add_image_button("add_texture", callback=lambda: show_item("add_url_popup"), tag="add_url")
        add_image_button("delete_texture", callback=delete_all_jobs, tag="delete_url")

    add_child_window(tag="download_stage")

    with group(horizontal=True):
        add_text("", tag="add_text_job", parent="download_stage", before="progress", wrap=100)
        add_progress_bar(parent="download_stage", show=False, tag="progress", width=430, overlay="add_text_job")

with popup(parent="add_url", modal=True, tag="add_url_popup"):
    add_input_text(hint="Enter URL", tag="urlInput")
    add_input_text(hint="Enter Save Path", tag="save")

    with group(horizontal=True):
        add_button(label="Add Job", callback=add_job)
        add_button(label="Default Download Path", callback=default_save_path)

set_primary_window("window", True)

show_viewport()
start_dearpygui()
destroy_context()
