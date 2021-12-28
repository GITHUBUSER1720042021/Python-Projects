from dearpygui.dearpygui import *
import os
import requests as rq
from time import sleep, monotonic

create_context()
create_viewport(width=700, height=500, title="Download Manager")
setup_dearpygui()

def update():
    URL = str(get_value("update"))
    req = rq.get(get_value("update"), stream=True, allow_redirects=True)
    filename = str(req.url[URL.rfind("/") + 1:])
    file_size = int(req.headers['content-length'])
    print(get_value("update_save") + "\\" + get_value("update_file"))

    start = last_print = monotonic()
    downloaded = 0

    with open(get_value("update_save") + "\\" + get_value("update_file"), "wb") as f:
        set_value("update_text", "Downloading...")
        for data in req.iter_content(chunk_size=8192):
            downloaded += f.write(data)
            now = monotonic()

            if now - last_print > 1:
                pct_done = round(downloaded / file_size * 100)
                speed = round(downloaded / (now - start) / 1024)
                set_value("update_speed", f"Download {pct_done}% done, Average speed {speed} kbps")
                last_print = now
        
    set_value("update_text", "Download finished successfully!")
    set_value("update", "")
    set_value("update_file", "")
    set_value("update_save", "")
    set_value("update_speed", "")
    sleep(1)
    set_value("update_text", "")
    sleep(2)
    quit()

def default_path():
    path = os.path.join(os.environ['USERPROFILE'], "Downloads")
    set_value("update_save", path)

with window(label="Window", tag="window", no_background=True):
    add_input_text(label="URL", hint="URL (required)", callback=update, tag="update", on_enter=True)
    add_input_text(label="Path", hint="Save Path (required)", callback=update, tag="update_save", on_enter=True)
    add_input_text(label="File Name", hint="Overwrite original file name (required)", callback=update, tag="update_file", on_enter=True)
    add_button(label="Download", callback=update)
    add_same_line()
    add_button(label="Default Download Path", callback=default_path)
    add_same_line()
    add_text("", tag="update_text")
    add_text("", tag="update_speed")

set_primary_window("window", True)

show_viewport()
start_dearpygui()
destroy_context()