import os
import re
import time
import ctypes
import threading
import base64
import math
import traceback
import json
import zlib
import struct
import datetime
import urllib.request
import urllib.error
from ctypes import wintypes
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

LIMIT = 10                  # sirf itne Chrome kholne hain
DEFAULT_GAP = 0.1           # ek Chrome ka window dikhne ke baad agla kholne se pehle (second)
OPEN_TIMEOUT = 25           # ek Chrome ka window dikhne ka max intezaar (second)
ICON_SEARCH_TIME = 2.5      # extension icon screen par dhundhne ka max intezaar (second)
ICON_MATCH_MAX = 30         # isse zyada fark ho to icon nahi maana jayega (0 = bilkul same)
POPUP_TIMEOUT = 2.0         # icon dabane ke baad popup ka max intezaar (second)
POPUP_SETTLE = 0.08         # popup dikhne ke baad aage badhne se pehle ka intezaar (UI se badal sakte ho)
DIALOG_SETTLE = 0.12        # file dialog saamne aane ke baad likhna shuru karne se pehle ka intezaar
PRESS_START_AFTER_FILE = True    # Message mein file chunne ke baad hara Start bhi dabega (band karna ho to False)
EXT_FOLDER_NAME = "group-automation"   # Documents ke andar extension ka folder (Load unpacked mein yahi chuna jata hai)
AUTO_INSTALL_EXTENSION = True   # extension na mile to chrome://extensions se khud load karna (band karna ho to False)
DEV_TOGGLE_DX, DEV_TOGGLE_DY = -25, 149    # (ab use nahi hota, screen se khud dhundta hai) extensions page: "Developer mode" toggle (window ke daayein kinare / upar se)
TOGGLE_CENTER_DY = 148                      # patti ke bina Developer mode toggle ka beech (window ke upar se)
LOAD_BTN_DX, LOAD_BTN_DY = 85, 205         # extensions page: "Load unpacked" button (window ke baayein kinare / upar se)
ICON_TRIES = 3              # icon / tab dabane ki max koshish
# ---- Add Members auto-cycle: Start ke baad dekhna ki "Poora hua" aaya, phir Chrome band, phir agle 10 ----
MONITOR_POLL = 2.0          # har round ke beech ruknay ka samay (second)
MONITOR_TIMEOUT = 40 * 60   # ek batch ke liye max intezaar (second); isse zyada ho to wo Chrome khula chhodkar aage badhega
DONE_CONFIRM = 2            # "Poora hua" itni baar lagatar dikhe tabhi maanenge
MIN_RUN_SECONDS = 20        # Start ke itne second tak "Poora hua" nahi maanenge (galat pehchaan se bachne ke liye)
DONE_GREEN = (0, 130, 67)   # popup ke "Poora hua" hare label ka rang
CLOSE_X_DX, CLOSE_X_DY = 23, 23     # Chrome ke X button ki jagah (window ke daayein-upar kone se)
SELECT_FOLDER_DX, SELECT_FOLDER_DY = 174, 25   # folder dialog ka 'Select Folder' button (dialog ke daayein-neeche kone se)
THEME_FILE = os.path.join(os.path.expanduser("~"), ".chrome_opener_theme.txt")
SAVE_FILE = os.path.join(os.path.expanduser("~"), ".chrome_opener_folder.txt")
WORD_SAVE_FILE = os.path.join(os.path.expanduser("~"), ".chrome_opener_word_folder.txt")

# ---- Self-heal (Night mode mein khud theek karna) ----
LOG_FILE = os.path.join(os.path.expanduser("~"), "ChromeOpener_log.txt")     # subah yahan dekhna raat mein kya hua
AI_KEY_FILE = os.path.join(os.path.expanduser("~"), ".chrome_opener_ai_key.txt")   # Gemini (free) API key yahan save hoti hai
AI_MODELS = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-2.5-flash"]   # pehla na chale to agla try hoga (naam badle to yahin badlo)
AI_MAX_CALLS = 120           # ek run mein AI ko max itni baar poochhna (free limit bachane ke liye)
AI_MIN_GAP = 6.0            # do AI calls ke beech kam se kam itne second
RETRY_MAX = 2               # jis Chrome mein Start nahi dab paya, usse band karke itni baar dobara kholna
HEALTH_AI_EVERY = 15 * 60   # har chalte Chrome ko itni der mein ek baar AI se bhi dikhwana (chal rahi ho tab bhi)
STUCK_SECONDS = 8 * 60      # popup itni der tak bilkul na badle to 'atka hua' ki jaanch (AI se poochhna)
VISIT_EVERY = 25            # ek Chrome ke popup ko dobara kholkar dekhne ke beech kam se kam itne second
BLANK_WHITE = 0.985         # page ka itna hissa bilkul safed ho to 'white screen' maano
AUTO_PRESS_START = True     # popup mein Start hara dikhe (kaam chalta nahi) to khud dabana (band karna ho to False)
STUCK_RETRY = 2             # atke hue Chrome ko itni baar band karke dobara chalana
SHOTS_DIR = os.path.join(os.path.expanduser("~"), "ChromeOpener_shots")   # dikkat ke waqt ki tasveerein yahan
SAVE_EXCEL_ON_DONE = True   # 'Poora hua' ke baad 'Excel file mein save karein' dabake phir Chrome band karna (band karna ho to False)
SAVE_TRIES = 3              # save button dabane ki max koshish
SAVE_WAIT = 3.0             # save dabane ke baad itna ruko (second)
SAVE_REQUIRED = False       # True = save na ho paye to Chrome band nahi hoga (khula rahega); False = log mein likhkar band kar dega
MAX_BATCH_ERRORS = 3        # lagatar itne batch mein unexpected error aaye tabhi poora run rukega

# ---- Page ki patti / error se halat pehchaanna (extension par baar-baar click kiye bina) ----
LIGHT_EVERY = 20            # har ID par jaakar extension kholkar dekhne ke beech kam se kam itne second
NOT_RUNNING_RECOVER = 25    # patti bilkul na dikhe to itne second baad ek baar Start/Resume/Restart ki koshish
NOT_RUNNING_SECONDS = 60    # patti itne second tak bilkul na dikhe to wo ID band (kaam chal hi nahi raha)
DAILY_LIMIT_CLOSE = True    # "exceeded your daily limit" wala error aaye to ID poori maanke save + band karna
BANNER_GREEN = (0, 129, 62)      # page ki patti: "Kaam poora ho gaya"
BANNER_GRAY = (94, 99, 104)      # page ki patti: "Pause kiya gaya. Resume dabayein."
ERR_ICON_RED = (193, 0, 24)      # "An error occurred" dibbe ka laal gola
RESUME_DX = -259                 # popup mein Restart ke beech se Resume button kitna baayein (pixel)
PAUSE_FADED = (245, 156, 159)    # Pause button jab dabne layak nahi (kaam ruka hua)

# ---- Popup ki jagahein (icon ke centre se kitne pixel, 100% screen scaling par naapi gayi) ----
# Popup mein 3 tab hain: Message | Reminder (Word) | Add Members.
# Add Members wale view mein scrollbar ki wajah se popup 15 pixel chaura ho jata hai (tab khisak jate hain),
# isliye click wahan hota hai jahan tab dono view mein hota hai.
TAB_DY = 100                # tab ke beech ki ooncha-ai (click ke liye)
TAB_SAMPLE_DY = 88.5        # tab ka rang dekhne ki ooncha-ai (likhai ke upar, taaki akshar beech mein na aayein)
TAB_CLICK_DX = {"message": -324.5, "reminder": -195.5, "members": -67.0}
TAB_LABEL = {"message": "Message", "reminder": "Reminder (Word)", "members": "Add Members"}
BTN_DX, BTN_DY = -362.5, 163.5   # "Choose File" button ke andar ka hissa (kinara chhodkar), upar-baayein kona
BTN_W, BTN_H = 79, 13
LBL_OFF_X, LBL_OFF_Y = 86, -1    # "No file chosen" likhai us kone se
LBL_W, LBL_H = 87, 14
START_DX = -260             # Start button par x ("Start" likhe akshar se door)
START_SCAN_FROM, START_SCAN_TO = 120, 480
START_LOADED_DY = 350       # file load hone ke baad Start icon se kitna neeche hota hai
EXCEL_DX, EXCEL_DY = -203, 241   # Add Members: "Excel file chuniye / badliye" bade button ka beech (icon se)
MEM_START_DX = -372         # Add Members: Start button ka x - button ke baayein hisse mein (likhai se door), isi column mein dhundhte hain
MEM_SHOT_DX, MEM_SHOT_W = -420, 440
MEM_SCROLL_X, MEM_SCROLL_Y = -5, 300   # scroll ke liye mouse yahan (popup ke kinare ki khali patti par)
SHOT_DX, SHOT_W = -400, 430
SHOT_DY, SHOT_H = 60, 440

BLUE = (0, 117, 227)        # chuna hua tab
BANNER_RED = (233, 35, 43)     # page par extension ka laal sandesh ('Starred group nahi mila' jaisa)
ORANGE_BTN = (255, 150, 41)    # popup ka Restart button
STAR_BLUE = (0, 117, 227)      # star laga hua group
BOX_GRAY = (241, 243, 244)    # popup ke 'File / Abhi baaki' aur 'Poora hua / Add hue' dibbe ka dhoosar rang
GRAY_TAB = (231, 234, 237)  # na chuna hua tab
GREEN = (0, 157, 81)        # Start button
FADED_GREEN = (140, 198, 168)   # dhundhla (band) Start button

ICON_TEMPLATE_B64 = "//f//vf///f///f/xPX/Xsf5HobLBGOyBFmzHmXMXo/21tP+//f///f///b///f//vf///f/9/f/atL9BGmhAClUACBDABIwAAsqABI4AB9bHzCknIr7/PL///f///b//PX+9/f/QbbsAEJzAwklAzFVAc3tAKDJABg7AR49AxMuAQ8kGyF2jGfw/vL//fT+//f/acX5ADZpBiBCAK/kAFOAAKf3AH3BAGuUAJbMAAsuABY7Bg4hHxFxtoH5//f/yOz+AVueBwMcAEFsAIbLAFSIAJ3qAIHBAF6OAIvJAB0+AA0xACpDA19AVSmi8sr+W6/0AClZAwkpAHGfM5u9ALT2ALb7ALj7AHm5AH+tADZwAF1YAMmSA7RyGw9WuXP1G3XHABQ3AQ4xurjCstX7n8j1ocv6vb/Ok5WkkZqqYW+FADZEAJuBAWljAQIvfz3LA1asAA4tABQ2x9XiYbP6S6H5lcv8rrS/THiXADpml6W0AGBkADlIABI4ABItYySuA1CtABAuAAgsiJeuvuP9lb3r2ubunai7b4efeJ+0ZnOMABg3ABY4ARM3ABIuZSSvG2TJABU4CBw9ABg7Wml/Dh47ARg5BR5AFSlJKDdWAAgsAAkuAAsuAQwvABI3hDrLW5HyATFoi5CZb3GFYGd9cXWJeHqNUllxmpyqen2QcXGGc3mNg4WZe4mSLSZpuXDzyNr+ATumICg4AE90HkBdMFx2KVFrCDdTDjhUGkdiBl11IUReRGR9J0JNXCOo9cz+//f/aZP7AB92BmKKAGagAGWZAHCbAH6bAHuXAH+kAIedAI2VBn1wJR59xH76//f//PX++vL/SHT3ASaAARkwAxo3ARxAABc8ABo+AR0/Axw0AR0tMyWErGL2//H//fT+/vb///f/+/H/g4/7Gy+nBxpcABI3ABEtABAsABE3GhddUyWowYL7/vH///f///b///f//vb///f///f/1tH+hIP4TkrROy+1RS21a0PRrnz47s3+//f///f///b///f/"   # extension icon ki 16x16 tasveer
BTN_TEMPLATE_B64 = "7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v2NjYHBwcAAAAAAAAHBwc2NjY7+/v7+/vp6enHBwc2NjY7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vv7+/CQkJAAAAAAAAAAAAAAAACQkJv7+/p6enHBwc2NjYp6enHBwc2NjY7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vv7+/CQkJf39/7+/v7+/vf39/HBwc2NjY7+/vp6enHBwc2NjY7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjYp6enHBwc2NjY7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vWFhYWFhY7+/v7+/v7+/v5OTkOzs7f39/7+/vp6enHBwc2NjY7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjY7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v2NjYHBwcp6en7+/v7+/v7+/v7+/v7+/v7+/v7+/vp6enHBwcZWVlAAAAAAAAf39/7+/v7+/v2NjYHBwcAAAAAAAAp6en7+/v7+/v7+/vf39/AAAAAAAAOzs75OTk7+/v5OTkOzs7AAAAAAAAWFhY7+/v7+/v7+/vf39/AAAAAAAAOzs75OTk7+/v7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjYp6enHBwc2NjY7+/vv7+/CQkJAAAACQkJv7+/7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/v7+/v7+/vp6enAAAAf39/7+/vp6enCQkJv7+/5OTkOzs7f39/7+/vp6enCQkJv7+/7+/vp6enHBwc2NjY5OTkOzs7WFhY7+/vf39/WFhY7+/v5OTkOzs7p6en7+/vp6enHBwc2NjY7+/vWFhYWFhY7+/v7+/v7+/v7+/v7+/vv7+/CQkJAAAAAAAAAAAAAAAAp6en7+/vp6enHBwc2NjYp6enHBwc2NjY2NjYHBwcp6en7+/vp6enHBwc2NjY7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjY7+/vv7+/Gxsbv7+/v7+/Gxsbv7+/7+/v5OTkOzs7f39/7+/vWFhYWFhY7+/v7+/vp6enHBwc2NjYf39/CQkJv7+/7+/v7+/v7+/v7+/vWFhYf39/7+/v7+/vv7+/LCws2NjY7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjYp6enHBwc2NjYp6enOzs75OTk7+/v5OTkOzs7p6en7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v2NjYHBwcp6en7+/v7+/v7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjY7+/vv7+/Gxsbv7+/p6enHBwc2NjY7+/v5OTkOzs7f39/5OTkOzs7f39/7+/v7+/vp6enHBwc2NjY7+/vf39/AAAAAAAACQkJv7+/5OTkOzs7AAAAAAAAAAAAAAAACQkJv7+/7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjYp6enHBwc2NjYf39/AAAAAAAAAAAAAAAAAAAAf39/7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vWFhYWFhY7+/v7+/v7+/v7+/vWFhYWFhY7+/vp6enHBwc2NjY7+/vv7+/Gxsbv7+/v7+/Gxsbv7+/7+/v5OTkOzs7f39/7+/vWFhYWFhY7+/v7+/vp6enHBwc2NjY7+/v7+/v7+/v7+/vWFhYOzs75OTkWFhYf39/7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjYp6enHBwc2NjYp6enOzs75OTk7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/vv7+/CQkJf39/7+/v7+/vp6enCQkJv7+/7+/vp6enHBwc2NjY7+/vv7+/Gxsbv7+/5OTkOzs7f39/7+/vp6enCQkJv7+/7+/vp6enHBwc2NjY5OTkOzs7WFhY7+/vWFhYWFhY7+/v7+/vf39/WFhY7+/vp6enHBwc2NjY7+/vf39/HBwc2NjY7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjYp6enHBwc2NjY2NjYHBwcp6en7+/vv7+/CQkJp6en7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v2NjYHBwcAAAAAAAAHBwc2NjY7+/v7+/vp6enHBwc2NjY7+/vv7+/Gxsbv7+/7+/v2NjYHBwcAAAAAAAAp6en7+/v7+/v7+/vf39/AAAAAAAAOzs75OTk7+/v5OTkOzs7AAAAAAAAHBwc2NjY7+/v7+/vf39/AAAAAAAACQkJv7+/7+/v7+/v7+/v7+/v7+/vv7+/Gxsbv7+/7+/v7+/v7+/v7+/v7+/vp6enHBwc2NjYp6enHBwc2NjY7+/vv7+/CQkJAAAAAAAAf39/7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v7+/v"     # "Choose File" button ki tasveer
LBL_TEMPLATE_B64 = "/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////v///v///v////////////////////////////////////////////7///7///7//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////v/////////////////////////////////////////+///+//////7///7///7/////////c3R2Pz9C6enp////////////mJiac3R2////////////////////////////////////////////////////vLy9ICEkLzAzYmRmc3R2////c3R2c3R2////////////////////////////////////////////////////////////////////////9PT1WlpdmJia//////////////////////////////////////////////////////////////////////////////7///7///7//////////v/+/v///v///v///v/+///+///+/v///v///f///f//////////c3R2ICEkmJia////////////mJiac3R2////////////////////////////////////////////////9PT1WlpdmJia////c3R2c3R2////c3R2c3R2////////////////////////////////////////////////////////////////////////9PT1WlpdmJia/////////////////////////////////////////////v///v///v///v///v///v///v///v///v7+//7+//////7///7+/v7+/v7+/v7+/f39/fz8/fv7+/n6+vn5+Pj4+Pj49/f3////////c3R2Pj9BPj9B0tPT////////mJiac3R2////////////////////////////////////////////////9PT1WlpdvLy9////////////////c3R2c3R2////////////////////////////////////////////////////////////////////////9PT1WlpdmJia//////////////////////////////////////7//v///v///v///f/+/f/+/f/+/f/+/f/+/f/+/f7+/P79/fz8+/v7+vn59vX19PLy8fDw7+3t7uvr7unp6+Xm6ePk6ePj6ePj6ePj////////c3R2c3R2c3R2Wlpd9PT1////mJiac3R2////////0tPTLzAzICEkLzAz0tPT////////////////9PT1WlpdICEkICEkc3R2c3R2c3R2////c3R2c3R2////////mJiaICEkICEkWlpd9PT1////////////////////////0tPTLzAzICEkLzAz0tPT9PT1Wlpdf4CCPz9CICEkPz9C6enp///////+0tPSLzAzICEkLzAz0dPT/v7+/v7+c3R2ICEkICEkWVlc7/Dx+Pn58/X0xsfHLi8yICEkLi4xwLu76ODg3tbXVVJVYV1hLi4xICEkPTs+3s/R9OPl9OLl////////c3R2c3R26enpPz9CvLy9////mJiac3R2////6enpPz9CvLy9////mJiaPz9C6enp////////////////9PT1WlpdmJia////c3R2c3R2////c3R2c3R2////vLy9Pz9C6enp////c3R2c3R2////////////////////6enpPz9CvLy9////vLy9Pz9C39/gWlpdPz9C6enp9PT1Wlpdc3R2//7+6ejoPz9Cu7y8/v/+l5eZPz9C6Ojou7u8WVlc8O7w9fLzbW5vjIuN5eLi0s3NPDs+r6ep8eLjtKipPjs+4tDR7djbWFJWPjs+5M7R8NfcWVJWcmhs/d/l/d/l////////c3R2c3R2////vLy9Pz9C6enpmJiac3R2////vLy9Pz9C6enp////6enpPz9CvLy9////////////////9PT1WlpdmJia////c3R2c3R2////c3R2c3R2////c3R2mJia////////0tPTTU1Q6enp////////////////vLy9Pz9C6enp////////////9PT1WlpdmJia////////c3R2c3R2/v/+u7y8Pz9C6Ono/v7+5ujnPj5Bt7a3sq+xICEkq6ip59/g6uDg7eHh8eLjtqmrWFNX8djd/eDl8tbbWVJWu6aq89bbWlFWmIaL/97k/97kc2hsc2hs/97k/97k////////c3R2c3R2////9PT1Wlpdc3R2mJiac3R2////mJiaWlpd9PT1////6enpPz9CvLy9////////////////9PT1WlpdmJia////c3R2c3R2////c3R2c3R29PT1WlpdICEkICEkICEkICEkLzAz0tPT////////////////mJiaWlpd9PT1////////////9PT1WlpdmJia//7///7+c3R2c3R2/f/+lpiZWVpd7/Hy9PX12NnZPDs/rKao69/hsaapICEkICEkICEkuair/ODll4eMICEkICEkICEkICEkICEkmIaM9NXcWlJWl4eL/eDk/eDkcmhsc2hs/d/k/d/k////////c3R2c3R2////////0tPTPj9BZ2dqc3R2////vLy9Pz9C6enp////6enpPz9CvLy9////////////////9PT1WlpdmJia////c3R2c3R2////c3R2c3R2////c3R2mJia////////////////////////////////////vLy9Pz9C6enp////////////9PT1Wlpdl5ia/v7//v7+c3R2c3R2/Pz8tra3PT1A0tLR5eHh1M3NPTs+tais+eLm++Hl/ODj/d7jl4aLPzo+6cvSu6WrWlJW89bb/d/k/ODk+uHl+eHl7dfbWFJWk4iL9OHi9OHibmlrbWhr7+Di7+Dh////////c3R2c3R2////////////mJiaICEkc3R2////6enpPz9CvLy9////mJiaPz9C6enp////////////////9PT1WlpdmJia////c3R2c3R2////c3R2c3R2////vLy9Pz9C6enp////mJiaPz9C6enp////////////////6enpPz9CvLy9////0tPTPj9ByMrLWlpdl5ea/v7//P7+cnN1b25w7ejo1s/PPDs+sqip9OPjlImLPjs+5s3Rl4eLWlFW9NXa/97jvKWrWlFW8tbc5M7SPjs+taiq8uLkxru9Li4xr6ao39bXVFJVjIeJ597e5t7faWhqaGhq4d7e4d7e////////c3R2c3R2////////////6enpPz9Cc3R2////////0tPTLzAzICEkLzAz0tPT////////////////////9PT1WlpdmJia////c3R2c3R2////c3R2c3R2////////mJiaICEkICEkLzAz0tPT////////////////////////0tPTLzAzICEkICEku7y88vP0Wlpdl5aZ9/b38fDwa2tta2lr7uDh9ODizbu9Ly4xICEkLy4x0rm9/t7j/d7jcmhsICEkICEkLy4xy7q98+Dj79/hwrm6LS4xICEkICEkiYaJ4t7e19XWUlFUh4aI4N7e4N7eZ2hqZ2hq39/f39/f/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////v///v///v///v///v/+/v/+/f79/P38+ff37+zt6eTl6ODh7uHi9OLk+eLl/N/k/t7k/97k/97k/97l/t7l++Dl+OHk9eHk8eHj7d/h6N/g5t7f5N7e497e4t7e4N7e4N7f4N7f4N7g4N/g4N/g4N/g39/g39/f4N/f4N/g4N/g4N/f4N7f/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////v///v///v///f7+/f79/P38+Pf28e3t6OHh6t/h8eHj9+Ll+uLl/ODl/d/l/t7k/t7l/t/l+9/l+t/l9+Dl8eDj69/h5t7f497e4N7e3+Df3uDe3t/e39/f39/f39/f3+Dg3+Dg4OHi4ODh4ODh4ODh4ODh4eHh4eHh4eHh4uLi4uLi4uLi"     # "No file chosen" likhai ki tasveer

# ---------- Windows ke functions ----------
try:
    ctypes.windll.user32.SetProcessDPIAware()   # screen scaling se coordinates na bigdein
except Exception:
    pass

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
dwmapi = ctypes.windll.dwmapi

user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetDC.restype = wintypes.HDC
user32.GetDC.argtypes = [wintypes.HWND]
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.IsIconic.argtypes = [wintypes.HWND]
user32.IsZoomed.argtypes = [wintypes.HWND]
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
dwmapi.DwmGetWindowAttribute.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleDC.restype = wintypes.HDC
gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.BitBlt.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                         wintypes.HDC, ctypes.c_int, ctypes.c_int, wintypes.DWORD]
gdi32.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT,
                            ctypes.c_void_p, ctypes.c_void_p, wintypes.UINT]
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.DeleteDC.argtypes = [wintypes.HDC]

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


# ---- keyboard (file dialog mein path likhne ke liye) ----
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]


def _key_input(vk=0, scan=0, flags=0):
    i = INPUT()
    i.type = 1      # INPUT_KEYBOARD
    i.u.ki = KEYBDINPUT(vk, scan, flags, 0, 0)
    return i


def send_inputs(items):
    for k in range(0, len(items), 64):
        chunk = items[k:k + 64]
        arr = (INPUT * len(chunk))(*chunk)
        user32.SendInput(len(chunk), arr, ctypes.sizeof(INPUT))
        time.sleep(0.01)


def type_text(text):
    data = text.encode("utf-16-le")
    items = []
    for i in range(0, len(data), 2):
        unit = data[i] | (data[i + 1] << 8)
        items.append(_key_input(0, unit, 0x0004))             # KEYEVENTF_UNICODE
        items.append(_key_input(0, unit, 0x0004 | 0x0002))    # + KEYUP
    send_inputs(items)


def press_keys(*vks):
    """vks ek saath dabate hain (jaise Ctrl + A), phir ulte kram mein chhodte hain."""
    items = [_key_input(vk, 0, 0) for vk in vks] + [_key_input(vk, 0, 0x0002) for vk in reversed(vks)]
    send_inputs(items)


VK_CONTROL, VK_A, VK_RETURN, VK_ESCAPE = 0x11, 0x41, 0x0D, 0x1B


def window_class(hwnd):
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def window_rect(hwnd):
    rect = wintypes.RECT()
    # DWMWA_EXTENDED_FRAME_BOUNDS = 9 (window ka asli dikhne wala hissa)
    ok = dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(rect), ctypes.sizeof(rect)) == 0
    if not ok:
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
    return rect


def rect_tuple(hwnd):
    r = window_rect(hwnd)
    return (r.left, r.top, r.right, r.bottom)


def dpi_scale():
    try:
        return user32.GetDpiForSystem() / 96.0
    except Exception:
        return 1.0


def windows_of_class(cls, titled_only=False):
    found = []

    def cb(hwnd, lparam):
        if user32.IsWindowVisible(hwnd) and window_class(hwnd) == cls:
            if not titled_only or user32.GetWindowTextLengthW(hwnd) > 0:
                found.append(hwnd)
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return found


def chrome_windows(titled_only=False):
    """Saari dikhti Chrome windows (popup bhi)."""
    return windows_of_class("Chrome_WidgetWin_1", titled_only)


def dialog_windows():
    """Windows ke dialog (jaise file chunne wala 'Open' dialog)."""
    return windows_of_class("#32770")


def click_at(x, y):
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.02)
    user32.mouse_event(0x0002, 0, 0, 0, 0)   # left down
    time.sleep(0.02)
    user32.mouse_event(0x0004, 0, 0, 0, 0)   # left up


user32.mouse_event.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]


def wheel_at(x, y, notches=1):
    """Mouse (x, y) par rakh kar wheel neeche ghumao (notches baar)."""
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.03)
    for _ in range(notches):
        user32.mouse_event(0x0800, 0, 0, (-120) & 0xFFFFFFFF, 0)    # MOUSEEVENTF_WHEEL, neeche
        time.sleep(0.06)


def force_foreground(hwnd):
    user32.keybd_event(0x12, 0, 0, 0)       # ALT dabao-chhodo: foreground ki ijazat ke liye
    user32.keybd_event(0x12, 0, 2, 0)
    user32.SetForegroundWindow(hwnd)


def bring_front_maximized(hwnd):
    """Window ko saamne laata hai aur maximize karta hai. Sahi hua to True."""
    for _ in range(3):
        if not user32.IsWindow(hwnd):
            return False
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, 9)          # SW_RESTORE
        if not user32.IsZoomed(hwnd):
            user32.ShowWindow(hwnd, 3)          # SW_MAXIMIZE
        force_foreground(hwnd)
        t = time.time()
        while time.time() - t < 0.7:
            if user32.GetForegroundWindow() == hwnd and user32.IsZoomed(hwnd):
                return True
            time.sleep(0.02)
    return False


def wait_rect_stable(hwnd, limit=1.2):
    """Maximize ka animation khatam hone tak ruko (jaise hi size tham jaye, aage badho)."""
    last = None
    t = time.time()
    while time.time() - t < limit:
        cur = rect_tuple(hwnd)
        if cur == last:
            return
        last = cur
        time.sleep(0.03)


def wait_popup(before, main_hwnd, ix, iy):
    """Icon dabane ke baad naya popup window dhundo. Mila to uska hwnd, warna None."""
    t = time.time()
    while time.time() - t < POPUP_TIMEOUT:
        for h in chrome_windows():
            if h in before or h == main_hwnd:
                continue
            l, tp, r, b = rect_tuple(h)
            if (r - l) <= 1200 and l - 40 <= ix <= r + 40 and tp >= iy - 40:
                return h
        time.sleep(0.02)
    return None


def popup_alive(popup):
    return bool(user32.IsWindow(popup)) and bool(user32.IsWindowVisible(popup))


def wheel_up_at(x, y, notches=1):
    """Mouse (x, y) par rakh kar wheel UPAR ghumao (notches baar)."""
    user32.SetCursorPos(int(x), int(y))
    time.sleep(0.03)
    for _ in range(notches):
        user32.mouse_event(0x0800, 0, 0, 120, 0)
        time.sleep(0.06)


def inside_popup(popup, x, y):
    if not popup_alive(popup):
        return False
    l, tp, r, b = rect_tuple(popup)
    return l <= x <= r and tp <= y <= b


# ---------- Screen ki tasveer aur pehchaan (bina numpy/pillow ke) ----------
_T0 = base64.b64decode(ICON_TEMPLATE_B64)      # 16x16 RGB
_BTN = base64.b64decode(BTN_TEMPLATE_B64)      # BTN_W x BTN_H RGB
_LBL = base64.b64decode(LBL_TEMPLATE_B64)      # LBL_W x LBL_H RGB


def _prep(tmpl, tw, th):
    """Template ke kaale (likhai) aur safed (khali) pixel alag karo."""
    dark, light = [], []
    for y in range(th):
        for x in range(tw):
            o = (y * tw + x) * 3
            lum = (tmpl[o] + tmpl[o + 1] + tmpl[o + 2]) / 3.0
            if lum < 140:
                dark.append((y, x))
            elif lum > 200:
                light.append((y, x))
    return tw, th, dark, light


_BTN_P = _prep(_BTN, BTN_W, BTN_H)
_LBL_P = _prep(_LBL, LBL_W, LBL_H)


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD), ("biWidth", ctypes.c_long), ("biHeight", ctypes.c_long),
                ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", ctypes.c_long),
                ("biYPelsPerMeter", ctypes.c_long), ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD)]


def grab_region(x, y, w, h):
    """Screen ke ek hisse ki tasveer (BGRA bytes) lo."""
    hdc = user32.GetDC(None)
    mem = gdi32.CreateCompatibleDC(hdc)
    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    old = gdi32.SelectObject(mem, bmp)
    try:
        # SRCCOPY | CAPTUREBLT
        if not gdi32.BitBlt(mem, 0, 0, w, h, hdc, int(x), int(y), 0x00CC0020 | 0x40000000):
            return None
        bi = BITMAPINFOHEADER()
        bi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bi.biWidth = w
        bi.biHeight = -h            # upar se neeche
        bi.biPlanes = 1
        bi.biBitCount = 32
        buf = ctypes.create_string_buffer(w * h * 4)
        if gdi32.GetDIBits(mem, bmp, 0, h, buf, ctypes.byref(bi), 0) == 0:
            return None
        return buf.raw
    finally:
        gdi32.SelectObject(mem, old)
        gdi32.DeleteObject(bmp)
        gdi32.DeleteDC(mem)
        user32.ReleaseDC(None, hdc)


class Shot:
    """Screen ke ek hisse ki tasveer. Coordinates poori screen ke hisaab se (x, y)."""

    def __init__(self, buf, x0, y0, w, h):
        self.buf, self.x0, self.y0, self.w, self.h = buf, int(x0), int(y0), int(w), int(h)

    def rgb(self, x, y):
        x, y = int(round(x)) - self.x0, int(round(y)) - self.y0
        if x < 0 or y < 0 or x >= self.w or y >= self.h:
            return None
        o = (y * self.w + x) * 4
        b = self.buf
        return b[o + 2], b[o + 1], b[o]


def take_shot(x0, y0, w, h):
    buf = grab_region(x0, y0, w, h)
    return Shot(buf, x0, y0, w, h) if buf else None


def is_green(c):
    """Chalu Start button ka hara rang (gehra (0,129,62) se halka (0,157,81) tak sab). Dhundhla/neela/safed nahi."""
    return c is not None and c[0] <= 40 and 105 <= c[1] <= 180 and 40 <= c[2] <= 105 and c[1] - c[2] >= 35


def near(c, ref, tol):
    return c is not None and abs(c[0] - ref[0]) <= tol and abs(c[1] - ref[1]) <= tol and abs(c[2] - ref[2]) <= tol


def find_load_unpacked_in(buf, w, h, s):
    """chrome://extensions par 'Load unpacked' button ko tasveer (BGRA buf, w x h) mein dhundho.
    Is page par ek hi line mein 3 neele-text button hote hain: Load unpacked | Pack extension | Update.
    Position (upar-neeche / bookmarks bar / debugging patti / window size / scaling) se farak nahi padta.
    Mila to (x, y) tasveer ke andar ka, warna None."""
    rows = []
    for y in range(h):
        base = y * w * 4
        xs = []
        for x in range(w):
            o = base + x * 4
            bl, g, r = buf[o], buf[o + 1], buf[o + 2]
            if bl >= 190 and r <= 50 and 75 <= g <= 130 and bl - g >= 90:      # button ke text ka gehra neela (icon/logo ke halke neele nahi)
                xs.append(x)
        rows.append(xs)
    gap_y = max(2, int(2 * s))
    gap_x = 16 * s
    y = 0
    while y < h:
        if not rows[y]:
            y += 1
            continue
        y0 = y
        last = y
        xs_all = set(rows[y])
        y += 1
        while y < h and y - last <= gap_y:
            if rows[y]:
                last = y
                xs_all.update(rows[y])
            y += 1
        y1 = last
        if not (6 * s <= (y1 - y0 + 1) <= 28 * s):
            continue
        xs = sorted(xs_all)
        segs = []
        a = p = xs[0]
        for x in xs[1:]:
            if x - p > gap_x:
                segs.append((a, p))
                a = x
            p = x
        segs.append((a, p))
        segs = [sg for sg in segs if sg[1] - sg[0] >= 18 * s]
        if len(segs) >= 3 and (segs[0][1] - segs[0][0]) >= 40 * s and (segs[1][1] - segs[1][0]) >= 40 * s \
                and (segs[0][1] - segs[0][0]) <= 220 * s:
            return (segs[0][0] + segs[0][1]) / 2.0, (y0 + y1) / 2.0
    return None



def make_template(scale):
    """Icon ki tasveer (gol hissa) scale ke hisaab se: (size, [(dy, dx, r, g, b), ...])"""
    n = max(8, int(round(16 * scale)))
    c = (n - 1) / 2.0
    rad2 = (6.0 * n / 16.0) ** 2
    px = []
    for y in range(n):
        for x in range(n):
            if (y - c) ** 2 + (x - c) ** 2 > rad2:
                continue
            sx = x * 15.0 / (n - 1)
            sy = y * 15.0 / (n - 1)
            x0, y0 = int(sx), int(sy)
            x1, y1 = min(15, x0 + 1), min(15, y0 + 1)
            fx, fy = sx - x0, sy - y0
            rgb = []
            for k in range(3):
                rgb.append(_T0[(y0 * 16 + x0) * 3 + k] * (1 - fx) * (1 - fy)
                           + _T0[(y0 * 16 + x1) * 3 + k] * fx * (1 - fy)
                           + _T0[(y1 * 16 + x0) * 3 + k] * (1 - fx) * fy
                           + _T0[(y1 * 16 + x1) * 3 + k] * fx * fy)
            px.append((y, x, rgb[0], rgb[1], rgb[2]))
    return n, px


def find_icon_in(buf, w, h, scale):
    """buf = BGRA tasveer. Icon ka centre (x, y) dega, na mile ya pakka na ho to None."""
    n, px = make_template(scale)
    if w < n or h < n:
        return None
    step = max(1, len(px) // 8)
    anchors = px[::step][:8]
    stride = w * 4
    cands = []
    for y in range(h - n + 1):
        for x in range(w - n + 1):
            ok = True
            for dy, dx, r, g, b in anchors:
                o = (y + dy) * stride + (x + dx) * 4
                if abs(buf[o + 2] - r) + abs(buf[o + 1] - g) + abs(buf[o] - b) > 90:
                    ok = False
                    break
            if ok:
                cands.append((y, x))
    limit = ICON_MATCH_MAX * len(px) * 3
    scored = []
    for y, x in cands:
        tot = 0.0
        for dy, dx, r, g, b in px:
            o = (y + dy) * stride + (x + dx) * 4
            tot += abs(buf[o + 2] - r) + abs(buf[o + 1] - g) + abs(buf[o] - b)
            if tot > limit:
                break
        else:
            scored.append((tot / (len(px) * 3.0), y, x))
    if not scored:
        return None
    scored.sort()
    best, by, bx = scored[0]
    for sc, y, x in scored[1:]:
        if (abs(y - by) >= n or abs(x - bx) >= n) and best > 0.5 * sc:
            return None         # koi doosri jagah bhi lagbhag utni hi milti hai: pakka nahi
    return bx + (n - 1) / 2.0, by + (n - 1) / 2.0


def find_extension_icon(hwnd, scale, hint=None):
    """Chrome window ki upar wali patti (toolbar) mein extension icon dhundo. (x, y) screen pixel ya None.
    hint = pichhle Chrome mein icon jahan mila tha: pehle wahin aas-paas dekhta hai (tez), na mile to poori patti."""
    if hint and user32.IsWindow(hwnd):
        r = int(26 * scale)
        hx, hy = int(hint[0]) - r, int(hint[1]) - r
        buf = grab_region(hx, hy, 2 * r, 2 * r)
        if buf:
            res = find_icon_in(buf, 2 * r, 2 * r, scale)
            if res:
                return hx + res[0], hy + res[1]
    t0 = time.time()
    while time.time() - t0 < ICON_SEARCH_TIME:
        if not user32.IsWindow(hwnd):
            return None
        l, tp, r, b = rect_tuple(hwnd)
        x0 = l + int((r - l) * 0.35)
        y0 = tp + int(20 * scale)
        w = r - x0
        h = int(95 * scale)
        buf = grab_region(x0, y0, w, h)
        if buf:
            res = find_icon_in(buf, w, h, scale)
            if res:
                return x0 + res[0], y0 + res[1]
        time.sleep(0.05)
    return None


def match_binary(shot, prep, ex, ey, rx, ry, min_dark=0.8, min_light=0.97):
    """Template ki likhai (kaale pixel) aur khali jagah (safed pixel) screen se milao.
    Button ka halka-gehra rang badalne se fark nahi padta. Mila to (x, y), warna None."""
    tw, th, dark, light = prep
    ex, ey = int(round(ex)), int(round(ey))
    b = shot.buf
    best = None
    for oy in range(-ry, ry + 1):
        for ox in range(-rx, rx + 1):
            x, y = ex + ox, ey + oy
            if x - shot.x0 < 0 or y - shot.y0 < 0 or x + tw - shot.x0 > shot.w or y + th - shot.y0 > shot.h:
                continue
            base = ((y - shot.y0) * shot.w + (x - shot.x0)) * 4
            d = 0
            for dy, dx in dark:
                o = base + (dy * shot.w + dx) * 4
                if (b[o] + b[o + 1] + b[o + 2]) < 510:        # kaala / gehra
                    d += 1
            if d < min_dark * len(dark):
                continue
            l = 0
            for dy, dx in light:
                o = base + (dy * shot.w + dx) * 4
                if (b[o] + b[o + 1] + b[o + 2]) >= 600:       # safed / halka
                    l += 1
            if l < min_light * len(light):
                continue
            score = d / len(dark) + l / len(light)
            if best is None or score > best[0]:
                best = (score, x, y)
    return (best[1], best[2]) if best else None


def tab_state(shot, ix, iy, s):
    """Popup mein kaun sa tab chuna hua hai: 'message', 'reminder', 'members' ya None (abhi samajh nahi aaya)."""
    y = iy + TAB_SAMPLE_DY * s
    cols = {k: shot.rgb(ix + dx * s, y) for k, dx in TAB_CLICK_DX.items()}
    blue = [k for k, c in cols.items() if near(c, BLUE, 25)]
    gray = [k for k, c in cols.items() if near(c, GRAY_TAB, 24)]
    if len(blue) == 1 and len(gray) == 2:
        return blue[0]
    return None


def find_choose_button(shot, ix, iy, s):
    """'Choose File' button dhundo. (x, y) = uske andar ke hisse ka upar-baayein kona, ya None."""
    if s != 1.0:
        return None         # button ki tasveer 100% scaling ki hai
    return match_binary(shot, _BTN_P, ix + BTN_DX, iy + BTN_DY, 6, 9, 0.8, 0.97)


def label_state(shot, bx, by):
    """Button ke saamne ki likhai: 'nofile' ("No file chosen"), 'file' (koi file ka naam), ya None (khali / abhi nahi dikha)."""
    if match_binary(shot, _LBL_P, bx + LBL_OFF_X, by + LBL_OFF_Y, 2, 2, 0.8, 0.97):
        return "nofile"
    # kuch likha hua dikhe to wo file ka naam hai
    dark = 0
    for yy in range(int(by - 1), int(by + 12)):
        for xx in range(int(bx + 86), int(bx + 86 + 150)):
            c = shot.rgb(xx, yy)
            if c is not None and (c[0] + c[1] + c[2]) < 450:
                dark += 1
    return "file" if dark >= 25 else None


def find_start(shot, ix, iy, s):
    """Start button: ('green', centre_y) chalu, ('faded', centre_y) dhundhla, ya None (dikha hi nahi)."""
    x = ix + START_DX * s
    for kind, ref, tol in (("green", None, 0), ("faded", FADED_GREEN, 14)):
        best = None
        run_start = None
        y0, y1 = int(iy + START_SCAN_FROM * s), int(iy + START_SCAN_TO * s)
        for y in range(y0, y1 + 2):
            c = shot.rgb(x, y) if y <= y1 else None
            hit = (is_green(c) if ref is None else near(c, ref, tol))
            if hit and run_start is None:
                run_start = y
            elif not hit and run_start is not None:
                if y - run_start >= 14 * s and (best is None or y - run_start > best[1]):
                    best = (run_start, y - run_start)
                run_start = None
        if best:
            return kind, best[0] + best[1] / 2.0 - 0.5
    return None


def _green_runs(shot, x, y0, y1, ref, tol, min_h):
    out, rs = [], None
    for y in range(y0, y1 + 2):
        c = shot.rgb(x, y) if y <= y1 else None
        hit = (is_green(c) if ref is None else near(c, ref, tol))
        if hit and rs is None:
            rs = y
        elif not hit and rs is not None:
            if y - rs >= min_h:
                out.append((rs, y - rs))
            rs = None
    return out


def find_members_start(shot, ix, iy, s):
    """Add Members ka Start button: sabse upar wala hara/dhundhla button us column mein.
    ('green' ya 'faded', centre_y, ooncha-ai) ya None (poora dikha nahi)."""
    x = ix + MEM_START_DX * s
    y0 = int(iy + 100 * s)
    y1 = min(shot.y0 + shot.h - 1, int(iy + 620 * s))
    found = []
    for kind, ref, tol in (("green", None, 0), ("faded", FADED_GREEN, 14)):
        for st, h in _green_runs(shot, x, y0, y1, ref, tol, int(14 * s)):
            found.append((st, h, kind))
    if not found:
        return None
    found.sort()
    st, h, kind = found[0]               # sabse upar wala = "Start" ("Sab ID Start" uske neeche hai)
    if h < 30 * s:                       # abhi adha hi dikha (popup ke kinare par kata hua)
        return None
    return kind, st + h / 2.0 - 0.5, h


def find_save_button(shot, ix, iy, s):
    """'Excel file mein save karein' bada neela button: (x, y) beech ya None.
    Pehchaan: chaura neela button (likhai se bachne ke liye baayein kinare ke column mein dekhte hain) jiske theek neeche hara 'Sab ID Start' ho."""
    x = int(ix + (EXCEL_DX - 140) * s)
    y0 = int(iy + 100 * s)
    y1 = min(shot.y0 + shot.h - 1, int(iy + 620 * s))
    runs = _green_runs(shot, x, y0, y1, BLUE, 30, int(26 * s))
    for st, h in reversed(runs):                 # sabse neeche wala neela button
        cy = st + h / 2.0
        if h > 60 * s:
            continue
        # chaura ho (tab nahi): daayein taraf bhi neela
        if not near(shot.rgb(x + 250 * s, cy), BLUE, 30):
            continue
        # neeche 5-60 pixel ke andar hara 'Sab ID Start' ho
        green_below = any(is_green(shot.rgb(x, yy)) or near(shot.rgb(x, yy), FADED_GREEN, 18)
                          for yy in range(int(st + h + 4 * s), int(st + h + 60 * s)))      # 'Sab ID Start' hara ya dhundhla dono
        if green_below:
            return (ix + EXCEL_DX * s, cy)
    return None


# ---------- Folder ke items ----------
def natural_key(name):
    # Chrome 2 ko Chrome 10 se pehle rakhta hai
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def get_items(folder):
    files = [
        f for f in os.listdir(folder)
        if os.path.isfile(os.path.join(folder, f))
        and not f.startswith(".")
        and f.lower() != "desktop.ini"
    ]
    chrome_files = [f for f in files if "chrome" in f.lower()]
    chosen = chrome_files if chrome_files else files
    chosen.sort(key=natural_key)
    return chosen


def get_word_files(folder):
    """Word folder se {number: poora path}. '1st file', '2nd fie', '10th file' ... naam ke shuru ka number.
    'reminders' jaisi bina number wali file kabhi nahi chuni jati."""
    found = {}
    for f in sorted(os.listdir(folder), key=natural_key):
        full = os.path.join(folder, f)
        if not os.path.isfile(full) or f.startswith("~$") or not f.lower().endswith(".docx"):
            continue
        if "reminder" in f.lower():
            continue
        m = re.match(r"\s*(\d+)", f)
        if m and int(m.group(1)) not in found:
            found[int(m.group(1))] = os.path.abspath(full)
    return found


def get_reminder_files(folder):
    """Word folder se {number: poora path} Reminder ki files: re1.docx, re2.docx ... re10.docx."""
    found = {}
    for f in sorted(os.listdir(folder), key=natural_key):
        full = os.path.join(folder, f)
        if not os.path.isfile(full) or f.startswith("~$"):
            continue
        m = re.match(r"^\s*re[\s_-]*(\d+)\.docx$", f, re.I)
        if m and int(m.group(1)) not in found:
            found[int(m.group(1))] = os.path.abspath(full)
    return found


def get_excel_files(folder):
    """Word folder se {number: poora path} Excel files: Id 1, Id 2 ... Id 10 (.xlsx / .xls / .csv)."""
    rank = {"xlsx": 0, "xlsm": 1, "xls": 2, "csv": 3}
    found = {}
    for f in sorted(os.listdir(folder), key=natural_key):
        full = os.path.join(folder, f)
        if not os.path.isfile(full) or f.startswith("~$"):
            continue
        m = re.match(r"^\s*id[\s_-]*(\d+)\.(xlsx|xlsm|xls|csv)$", f, re.I)
        if not m:
            continue
        n, r = int(m.group(1)), rank[m.group(2).lower()]
        if n not in found or r < found[n][0]:
            found[n] = (r, os.path.abspath(full))
    return {n: v[1] for n, v in found.items()}


def default_word_folder():
    home = os.path.expanduser("~")
    for base in (os.path.join(home, "Documents"), os.path.join(home, "OneDrive", "Documents")):
        for name in ("automation file", "tool"):
            p = os.path.join(base, name)
            if os.path.isdir(p):
                return p
    return ""


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


# ---------- design ke widgets: gol kinare + gradient wale button ----------
_IMG_CACHE = {}


def _hex(c):
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def _mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rgb(t):
    return "#%02x%02x%02x" % t


def lighter(c, t=0.14):
    return _rgb(_mix(_hex(c), (255, 255, 255), t))


def round_image(w, h, r, c1, c2, outline, bg):
    key = (w, h, r, c1, c2, outline, bg)
    img = _IMG_CACHE.get(key)
    if img is not None:
        return img
    A, B, G = _hex(c1), _hex(c2 or c1), _hex(bg)
    O = _hex(outline) if outline else None
    img = tk.PhotoImage(width=w, height=h)
    hw, hh = w / 2.0, h / 2.0
    rows = []
    for y in range(h):
        row = []
        for x in range(w):
            px, py = x + 0.5 - hw, y + 0.5 - hh
            qx, qy = abs(px) - (hw - r), abs(py) - (hh - r)
            sd = math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r
            a_out = min(1.0, max(0.0, 0.5 - sd))
            col = _mix(A, B, x / max(1, w - 1))
            if O:
                col = _mix(O, col, min(1.0, max(0.0, 0.5 - (sd + 1))))
            row.append(_rgb(_mix(G, col, a_out)))
        rows.append("{" + " ".join(row) + "}")
    img.put(" ".join(rows))
    _IMG_CACHE[key] = img
    return img


class RoundBtn(tk.Canvas):
    """Gol kinare wala button (gradient bhi ho sakta hai). style = dict(c1, c2, h1, h2, fg, outline)."""

    def __init__(self, parent, text, command, w, h, style, bg, radius=10, font=("Segoe UI", 10, "bold")):
        super().__init__(parent, width=w, height=h, bg=bg, highlightthickness=0, bd=0, cursor="hand2")
        self.w, self.h, self.r, self.pbg = w, h, radius, bg
        self.text, self.command, self.font, self.style = text, command, font, style
        self.enabled, self.hover = True, False
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.paint()

    def _click(self, e):
        if self.enabled and self.command:
            self.command()

    def _set_hover(self, v):
        self.hover = v
        self.paint()

    def paint(self):
        st = self.style
        if not self.enabled:
            c1 = c2 = P["disabled"]
            fg, outline = P["muted"], None
        elif self.hover:
            c1, c2 = st.get("h1", st["c1"]), st.get("h2", st.get("c2", st["c1"]))
            fg, outline = st["fg"], st.get("outline")
        else:
            c1, c2 = st["c1"], st.get("c2", st["c1"])
            fg, outline = st["fg"], st.get("outline")
        self.delete("all")
        self._img = round_image(self.w, self.h, self.r, c1, c2, outline, self.pbg)
        self.create_image(0, 0, anchor="nw", image=self._img)
        self.create_text(self.w / 2, self.h / 2, text=self.text, fill=fg, font=self.font)
        self.config(cursor="hand2" if self.enabled else "arrow")

    def set_style(self, style):
        self.style = style
        self.paint()

    def set_enabled(self, v):
        self.enabled = bool(v)
        self.paint()


def _styles():
    return {
        "tab_on": dict(c1=P["grad1"], c2=P["grad2"], h1=lighter(P["grad1"]), h2=lighter(P["grad2"]), fg="#ffffff"),
        "tab_off": dict(c1=P["card"], c2=P["card"], h1=P["card_hi"], h2=P["card_hi"], fg=P["text"], outline=P["border"]),
        "file": dict(c1=P["grad1"], c2=P["grad2"], h1=lighter(P["grad1"]), h2=lighter(P["grad2"]), fg="#ffffff"),
        "start": dict(c1=P["green"], c2=P["green_hi"], h1=lighter(P["green"]), h2=lighter(P["green_hi"]), fg="#ffffff"),
        "stop": dict(c1=P["red"], c2=P["red_hi"], h1=lighter(P["red"]), h2=lighter(P["red_hi"]), fg="#ffffff"),
    }


MODES = [("message", "Message"), ("reminder", "Reminder (Word)"), ("members", "Add Members")]
MODE_ICON = {"message": "\U0001F4AC", "reminder": "\U0001F4C4", "members": "\U0001F465"}

# ---- rang (design): THEME = "dark" ya "light" ----
THEME = "light"
THEMES = {
    "dark": dict(bg="#13151b", card="#1c1f28", card_hi="#262a36", border="#2b3040", input="#12141a",
                 text="#e8eaf0", muted="#8b90a0", accent="#5b6cff", accent_hi="#7482ff",
                 grad1="#7a3df0", grad2="#4a7df7", dash="#4a5170", disabled="#2b3040",
                 green="#16a36a", green_hi="#1fbd7c", red="#d65a70", red_hi="#e56c82",
                 ok="#3ddc97", warn="#ffa04d", list="#151820"),
    "light": dict(bg="#ffffff", card="#ffffff", card_hi="#eef1fb", border="#dde2ef", input="#f6f8fd",
                  text="#1f2430", muted="#6b7280", accent="#5b5bf0", accent_hi="#7373ff",
                  grad1="#7a3df0", grad2="#4a7df7", dash="#9fb3e8", disabled="#dde2ef",
                  green="#12a06a", green_hi="#19b87b", red="#f0788c", red_hi="#f58a9c",
                  ok="#0a8f5f", warn="#c2410c", list="#f6f8fd"),
}
try:
    with open(THEME_FILE, encoding="utf-8") as _f:
        if _f.read().strip() in THEMES:
            _f.seek(0)
            THEME = _f.read().strip()
except OSError:
    pass
P = THEMES[THEME]

MODE_HINT = {
    "message": "Extension icon  ›  Message tab  ›  Choose File  ›  Chrome ke number ki Word file "
               "(Shuru no. wala pehla Chrome = 1st file ... das-vaan = 10th file). 'reminders' file nahi chuni jayegi.",
    "reminder": "Extension icon  ›  Reminder (Word) tab  ›  Choose File  ›  Chrome ke number ki re file "
                "(pehla Chrome = re1 ... das-vaan = re10)  ›  Open  ›  Start.",
    "members": "Extension icon  ›  Add Members tab  ›  Excel file chuniye  ›  Chrome ke number ki Id file "
               "(pehla Chrome = Id 1 ... das-vaan = Id 10)  ›  Open  ›  halka scroll  ›  Start.",
}


def progress_signature(shot, x0, y0, w, h, s):
    """Popup ke dhoosar dibbon ('Abhi baaki', 'Add hue') ka nishan. Kaam aage badhe to ye badalta hai.
    Neeche ki 'Pulse ok' wali line shaamil nahi (wo kaam atka ho tab bhi badalti rehti hai)."""
    probe_x = int(x0 + w - 40 * s)
    rows = [y for y in range(int(y0), int(y0 + h)) if near(shot.rgb(probe_x, y), BOX_GRAY, 3)]
    if len(rows) < 20:
        return None
    xa, xb = int(x0 + 12 * s), int(x0 + w - 36 * s)
    acc = 0
    for y in rows:
        o = ((y - shot.y0) * shot.w + (xa - shot.x0)) * 4
        acc = zlib.crc32(shot.buf[o:o + (xb - xa) * 4], acc)
    return acc


def find_red_banner(shot, x0, y0, w, h, s):
    """Page ke upar beech mein laal sandesh wali patti dikhe to True (baayein-beech ke hisse mein dhundhta hai)."""
    xs = list(range(int(x0), int(x0 + w), 8))
    rows = 0
    for y in range(int(y0), int(y0 + h)):
        hits = sum(1 for x in xs if near(shot.rgb(x, y), BANNER_RED, 20))
        if xs and hits * 10 >= len(xs) * 4:
            rows += 1
    return rows >= int(14 * s)


def find_page_banner(shot, x0, y0, w, h, s):
    """Page ke upar beech mein extension ki patti ("Auto Groups [ID n]: ..."): 'green' (poora hua) / 'gray' (pause) /
    'red' (extension ka laal sandesh) / 'other' (koi aur gehre rang ki patti, jaise chal raha ho) / None (patti nahi)."""
    best = {}
    step = 2
    for y in range(int(y0), int(y0 + h), 2):
        run = {}
        for x in range(int(x0), int(x0 + w), step):
            c = shot.rgb(x, y)
            if c is None:
                continue
            if near(c, BANNER_GREEN, 14):
                k = "green"
            elif near(c, BANNER_GRAY, 14):
                k = "gray"
            elif near(c, BANNER_RED, 20):
                k = "red"
            elif near(c, ORANGE_BTN, 28) or (max(c) < 150 and (max(c) - min(c) >= 25 or max(c) < 110)) \
                    or (c[2] >= 170 and c[0] <= 60 and 50 <= c[1] <= 150):
                k = "other"         # narangi (captcha / chal raha hai), neeli ya gehri patti
            else:
                k = None
            if k:
                run[k] = run.get(k, 0) + 1
        for k, n in run.items():
            if n * step >= 90 * s:
                best[k] = best.get(k, 0) + 1
    # patti kam se kam ~14 pixel ooncha-ai (2-2 pixel ke qadam par 7 qatar)
    for k in ("green", "gray", "red", "other"):
        if best.get(k, 0) >= 7:
            return k
    return None


def find_error_dialog(shot, x0, y0, w, h, s):
    """Page ke neeche-baayein kone mein "An error occurred" dibba (laal gola + likhai): True/False.
    Laal gola (193,0,24) ek chhote 24x24 hisse mein ~30+ pixel."""
    pts = []
    for y in range(int(y0), int(y0 + h)):
        for x in range(int(x0), int(x0 + w)):
            c = shot.rgb(x, y)
            if c is not None and 170 <= c[0] <= 215 and c[1] <= 45 and c[2] <= 60:
                pts.append((x, y))
    if len(pts) < int(20 * s):
        return False
    xs = [a for a, _ in pts]
    ys = [b for _, b in pts]
    return (max(xs) - min(xs)) <= 30 * s and (max(ys) - min(ys)) <= 30 * s


def find_stars(shot, left, right, top, bottom, s):
    """Groups list ke star ke nishan: [(beech_y, laga_hua_hai)] upar se neeche. Star 'right' se ~48 pixel andar hota hai."""
    xa, xb = int(right - 62 * s), int(right - 34 * s)
    rows = []
    for y in range(int(top), int(bottom)):
        gray = blue = False
        for x in range(xa, xb, 2):
            c = shot.rgb(x, y)
            if c is None:
                continue
            if near(c, STAR_BLUE, 30):
                blue = True
            elif min(c) < 205 and max(c) - min(c) < 40:
                gray = True
        rows.append((y, gray, blue))
    out, cur = [], []
    for y, gray, blue in rows + [(None, False, False)]:
        if y is not None and (gray or blue):
            cur.append((y, blue))
            continue
        if cur and len(cur) >= 6:
            out.append(((cur[0][0] + cur[-1][0]) // 2, any(b for _, b in cur)))
        cur = []
    # upar ki patti ke aaikon (settings, apps) hatao: group ke star ek-doosre se ~42 pixel par hote hain
    start = None
    for i in range(len(out) - 1):
        if 36 * s <= out[i + 1][0] - out[i][0] <= 52 * s:
            start = i
            break
    if start is None and out:
        start = len(out) - 1             # sirf ek group ho to sabse neeche wala
    return out[start:] if start is not None else []


def find_orange_button(shot, x0, y0, w, h, s):
    """Popup ka narangi Restart button: (x, y) beech ya None."""
    cols = []
    for y in range(int(y0), int(y0 + h)):
        xs = [x for x in range(int(x0), int(x0 + w), 2) if near(shot.rgb(x, y), ORANGE_BTN, 12)]
        if len(xs) * 2 >= 60 * s:
            cols.append((y, xs[0], xs[-1]))
    if len(cols) < int(20 * s):
        return None
    return (sum((a + b) / 2 for _, a, b in cols) / len(cols), (cols[0][0] + cols[-1][0]) / 2)


def find_done_pill(shot, x0, y0, w, h, s):
    """Popup mein chhota hara label (jaise 'Poora hua') dhundho. Bada hara Start button / page ka bada hara patta nahi maana jata."""
    rows = []
    for y in range(int(y0), int(y0 + h)):
        first = last = None
        cnt = 0
        for x in range(int(x0), int(x0 + w), 2):
            if near(shot.rgb(x, y), DONE_GREEN, 14):
                if first is None:
                    first = x
                last = x
                cnt += 1
        span = (last - first) if first is not None else 0
        ok = first is not None and 40 * s <= span <= 115 * s and cnt * 2 >= span * 0.15
        rows.append((first, last) if ok else None)
    run = []
    for r in rows + [None]:
        if r and (not run or abs(r[0] - run[-1][0]) <= 8 * s):
            run.append(r)
            continue
        if run and 9 * s <= len(run) <= 26 * s:
            return True
        run = [r] if r else []
    return False



# ---------- Log + AI (Gemini free API) ----------
_log_lock = threading.Lock()


def write_log(text):
    try:
        with _log_lock, open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "  " + str(text) + "\n")
    except Exception:
        pass


def bgra_to_png(buf, w, h, step=2):
    """BGRA bytes -> PNG bytes (bina kisi extra library ke). step=2 se tasveer aadhi chhoti (tez upload)."""
    rows = []
    for y in range(0, h, step):
        base = y * w * 4
        end = base + w * 4
        r = buf[base + 2:end:4 * step]
        g = buf[base + 1:end:4 * step]
        b = buf[base:end:4 * step]
        row = bytearray(len(r) * 3)
        row[0::3], row[1::3], row[2::3] = r, g, b
        rows.append(b"\x00" + bytes(row))
    ow, oh = len(r), len(rows)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", ow, oh, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(b"".join(rows), 6)) + chunk(b"IEND", b""))


def save_debug_shot(name, shot):
    """Dikkat ke waqt popup ki tasveer ~/ChromeOpener_shots mein rakho (subah dekhne ke liye)."""
    try:
        if not shot:
            return
        os.makedirs(SHOTS_DIR, exist_ok=True)
        png = bgra_to_png(shot.buf, shot.w, shot.h, 1)
        fn = datetime.datetime.now().strftime("%H%M%S") + "_" + name + ".png"
        with open(os.path.join(SHOTS_DIR, fn), "wb") as f:
            f.write(png)
    except Exception:
        pass


def load_ai_key():
    k = os.environ.get("GEMINI_API_KEY", "").strip()
    if k:
        return k
    try:
        with open(AI_KEY_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def ask_ai(png, prompt, key):
    """Gemini se screenshot ke baare mein poochho. JSON dict lautata hai, ya {'error': ...}."""
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt},
                                {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(png).decode()}}]}],
        "generationConfig": {"temperature": 0, "responseMimeType": "application/json"},
    }).encode("utf-8")
    last = "koi model nahi chala"
    for model in AI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        req = urllib.request.Request(url, data=body, method="POST",
                                     headers={"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                data = json.loads(r.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
            return json.loads(text)
        except urllib.error.HTTPError as e:
            last = f"{model}: HTTP {e.code}"
            if e.code in (400, 404):         # model ka naam purana/galat - agla model try karo
                continue
            return {"error": last}           # 429 (limit) / 401 (key galat) - dobara mat thokna
        except Exception as e:
            last = f"{model}: {e}"
    return {"error": last}


class App:
    def __init__(self, root, keep=None):
        self.root = root
        root.title("Chrome Opener")
        root.resizable(False, False)
        root.configure(bg=P["bg"])
        for k, v in {"*Background": P["card"], "*Foreground": P["text"], "*Font": "{Segoe UI} 10",
                     "*Button.disabledForeground": P["muted"],
                     "*Entry.Background": P["input"], "*Entry.Foreground": P["text"],
                     "*Entry.insertBackground": P["text"],
                     "*Spinbox.Background": P["input"], "*Spinbox.Foreground": P["text"],
                     "*Spinbox.insertBackground": P["text"], "*Spinbox.buttonBackground": P["card_hi"],
                     "*Listbox.Background": P["list"], "*Listbox.Foreground": P["text"],
                     "*Listbox.selectBackground": P["accent"], "*Listbox.selectForeground": "#ffffff",
                     "*Listbox.highlightThickness": 0}.items():
            root.option_add(k, v)

        self.folder = ""
        self.word_folder = ""
        self.items = []
        self.running = False
        self.thread = None
        self.cur_mode = "message"
        self.word_files = {}
        self.reminder_files = {}
        self.excel_files = {}
        self.icon_hint = None
        self.cur_start = 1
        self.reset_state()

        W = 480
        self.ST = _styles()
        tk.Frame(root, width=W, height=1, bg=P["bg"]).pack()

        # ----- upar: Night mode (ek baar Start, pura folder khud: Chrome khud khule, khud band, agle 10...) -----
        self.auto_var = tk.BooleanVar(value=True if not keep else keep.get("auto", True))
        head = tk.Frame(root, bg=P["bg"])
        head.pack(fill="x", padx=14, pady=(8, 0))
        self.night_hint = tk.Label(head, text="", bg=P["bg"], fg=P["muted"], font=("Segoe UI", 8),
                                   anchor="w", justify="left", wraplength=215)
        self.night_hint.pack(side="left", padx=3)
        self.night_btn = RoundBtn(head, "", self.toggle_night, 150, 30, self.ST["start"], P["bg"], radius=10)
        self.night_btn.pack(side="right", padx=3)
        self.ai_btn = RoundBtn(head, "\U0001F916  AI key", self.set_ai_key, 95, 30, self.ST["tab_off"], P["bg"], radius=10)
        self.ai_btn.pack(side="right", padx=3)
        self.paint_night()

        # ----- upar teen tab: Message / Reminder (Word) / Add Members -----
        self.mode = tk.StringVar(value="message")
        tabs = tk.Frame(root, bg=P["bg"])
        tabs.pack(fill="x", padx=14, pady=(10, 4))
        self.tab_buttons = {}
        for i, (val, text) in enumerate(MODES):
            b = RoundBtn(tabs, f"{MODE_ICON[val]}  {text}", lambda v=val: self.select_mode(v),
                         144, 42, self.ST["tab_off"], P["bg"], radius=12)
            b.grid(row=0, column=i, padx=3)
            self.tab_buttons[val] = b

        # ----- card: folders (dashed upload box jaisa) -----
        c = self.card("Folders", "\U0001F4C1")
        zrow = tk.Frame(c, bg=P["card"])
        zrow.pack(fill="x")
        zc, self.chrome_btn, self.folder_label = self.zone(
            zrow, "Chrome folder (Day 1 / Day 2)", "Choose Folder", self.choose_folder)
        zc.grid(row=0, column=0, padx=(0, 8))
        zw, self.word_btn, self.word_label = self.zone(
            zrow, "Word files folder (.docx)", "Choose Folder", self.choose_word_folder)
        zw.grid(row=0, column=1)
        self.folder_label.config(text="No folder chosen")
        self.word_label.config(text="No folder chosen")

        # ----- card: file information (kaun si Chrome -> kaun si file) -----
        c = self.card("File Information", "\U0001F4CB")
        lrow = tk.Frame(c, bg=P["card"])
        lrow.pack(fill="x")
        sb = tk.Scrollbar(lrow, orient="vertical")
        sb.pack(side="right", fill="y")
        self.listbox = tk.Listbox(lrow, height=4, width=56, bd=0, highlightthickness=0, activestyle="none",
                                  font=("Segoe UI", 10), yscrollcommand=sb.set)
        self.listbox.pack(side="left", fill="x", expand=True)
        sb.config(command=self.listbox.yview)

        # ----- card: automation ready + settings -----
        c = self.card("Automation Ready", "\U0001F6E1")
        top = tk.Frame(c, bg=P["card"])
        top.pack(fill="x")
        ring = tk.Canvas(top, width=58, height=58, bg=P["card"], highlightthickness=0)
        ring.pack(side="left", padx=(0, 12))
        ring.create_oval(5, 5, 53, 53, outline=P["card_hi"], width=6)
        ring.create_arc(5, 5, 53, 53, start=60, extent=250, style="arc", outline=P["grad2"], width=6)
        ring.create_text(29, 29, text="\u26A1", fill=P["grad1"], font=("Segoe UI", 11))
        checks = tk.Frame(top, bg=P["card"])
        checks.pack(side="left", fill="x", expand=True)
        self.chk_chrome = tk.Label(checks, text="", anchor="w", justify="left", bg=P["card"])
        self.chk_chrome.pack(fill="x", pady=1)
        self.chk_word = tk.Label(checks, text="", anchor="w", justify="left", bg=P["card"])
        self.chk_word.pack(fill="x", pady=1)
        self.hint = tk.Label(c, text="", wraplength=410, justify="left", anchor="w", fg=P["muted"],
                             bg=P["card"], font=("Segoe UI", 8))
        self.hint.pack(fill="x", pady=(4, 4))

        def spin(parent, text, **kw):
            tk.Label(parent, text=text, fg=P["muted"], bg=P["card"]).pack(side="left")
            w = tk.Spinbox(parent, relief="flat", highlightthickness=1, highlightbackground=P["border"],
                           highlightcolor=P["accent"], **kw)
            w.pack(side="left", padx=(4, 12))
            return w

        row = tk.Frame(c, bg=P["card"])
        row.pack(fill="x")
        self.delay = spin(row, "Gap (s)", from_=0, to=10, increment=0.5, width=3)
        self.delay.delete(0, "end")
        self.delay.insert(0, str(DEFAULT_GAP))
        self.settle_box = spin(row, "Popup (s)", from_=0, to=3, increment=0.05, width=4)
        self.settle_box.delete(0, "end")
        self.settle_box.insert(0, str(POPUP_SETTLE))
        self.start_box = spin(row, "Shuru no.", from_=1, to=999, increment=1, width=4,
                              command=self.on_start_no)
        self.start_box.delete(0, "end")
        self.start_box.insert(0, "1")
        self.start_box.bind("<KeyRelease>", lambda e: self.on_start_no())
        tk.Label(row, text="Sirf no. (3,7)", fg=P["muted"], bg=P["card"]).pack(side="left")
        self.only = tk.Entry(row, width=6, relief="flat", highlightthickness=1,
                             highlightbackground=P["border"], highlightcolor=P["accent"])
        self.only.pack(side="left", padx=6)


        # ----- Start / Stop -----
        brow = tk.Frame(root, bg=P["bg"])
        brow.pack(fill="x", padx=14, pady=(6, 2))
        RoundBtn(brow, "\u25B6   Start", self.start, 218, 42, self.ST["start"], P["bg"], radius=12,
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=(3, 6))
        RoundBtn(brow, "\u25A0   Stop", self.pause, 218, 42, self.ST["stop"], P["bg"], radius=12,
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=1, padx=(6, 3))

        # ----- footer: status -----
        foot = tk.Frame(root, bg=P["bg"])
        foot.pack(fill="x", padx=18, pady=(2, 8))
        foot.columnconfigure(1, weight=1)
        self.dot = tk.Label(foot, text="\u25CF", bg=P["bg"], fg=P["ok"])
        self.dot.grid(row=0, column=0, sticky="nw")
        self.status = tk.Label(foot, text="Ready", bg=P["bg"], fg=P["ok"], wraplength=300,
                               justify="left", anchor="w")
        self.status.grid(row=0, column=1, sticky="nw", padx=(4, 0))
        tk.Label(foot, text="\u26A1 Automate \u2022 Save Time \u2022 Get Results", bg=P["bg"], fg=P["accent"],
                 font=("Segoe UI", 8)).grid(row=0, column=2, sticky="ne")

        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, encoding="utf-8") as f:
                    saved = f.read().strip()
                if saved and os.path.isdir(saved):
                    self.set_folder(saved)
            except OSError:
                pass
        saved_word = ""
        if os.path.exists(WORD_SAVE_FILE):
            try:
                with open(WORD_SAVE_FILE, encoding="utf-8") as f:
                    saved_word = f.read().strip()
            except OSError:
                pass
        if not (saved_word and os.path.isdir(saved_word)):
            saved_word = default_word_folder()
        if saved_word:
            self.set_word_folder(saved_word)
        if keep:
            self.start_box.delete(0, "end")
            self.start_box.insert(0, keep.get("start", "1"))
            self.mode.set(keep.get("mode", "message"))
        self.on_mode()
        self.fit_to_screen()

    def paint_night(self):
        on = bool(self.auto_var.get())
        self.night_btn.text = "\U0001F319  Night mode: ON" if on else "\U0001F319  Night mode: OFF"
        self.night_btn.set_style(self.ST["start"] if on else self.ST["tab_off"])
        self.night_hint.config(
            text=("Add Members mein ek baar Start: ID khud khulengi, 'Poora hua' par khud band, phir agli 10, "
                  "folder khatam hone par khud ruk jayega." if on else
                  "Band: sirf 10 Chrome khulenge aur Start dabega."))

    def toggle_night(self):
        if self.running or (self.thread and self.thread.is_alive()):
            self.say("Night mode badalne se pehle Stop dabao.", "#ffb347")
            return
        self.auto_var.set(not self.auto_var.get())
        self.paint_night()

    def fit_to_screen(self):
        """Window screen se lambi na ho: zarurat pade to list chhoti, aur window upar se shuru."""
        r = self.root
        r.update_idletasks()
        avail = r.winfo_screenheight() - 90          # taskbar + title bar ki jagah
        rows = int(self.listbox.cget("height"))
        while r.winfo_reqheight() > avail and rows > 2:
            rows -= 1
            self.listbox.config(height=rows)
            r.update_idletasks()
        x = max(0, (r.winfo_screenwidth() - r.winfo_reqwidth()) // 2)
        r.geometry(f"+{x}+4")

    # ----- design ke chhote hisse -----
    def card(self, title, icon):
        outer = tk.Frame(self.root, bg=P["border"], padx=1, pady=1)
        outer.pack(fill="x", padx=17, pady=3)
        inner = tk.Frame(outer, bg=P["card"], padx=12, pady=6)
        inner.pack(fill="both", expand=True)
        head = tk.Frame(inner, bg=P["card"])
        head.pack(fill="x", pady=(0, 4))
        tk.Label(head, text=icon, fg=P["grad2"], bg=P["card"], font=("Segoe UI", 11)).pack(side="left")
        tk.Label(head, text=title, font=("Segoe UI", 10, "bold"), anchor="w", bg=P["card"],
                 fg=P["text"]).pack(side="left", padx=(6, 0))
        return inner

    def zone(self, parent, title, btn_text, command, w=205, h=98):
        """Dashed upload box: title, gradient 'Choose' button, neeche chuna hua naam."""
        cv = tk.Canvas(parent, width=w, height=h, bg=P["card"], highlightthickness=0)
        cv.create_rectangle(2, 2, w - 2, h - 2, outline=P["dash"], dash=(5, 4))
        cv.create_text(w / 2, 15, text=title, fill=P["text"], font=("Segoe UI", 9, "bold"))
        btn = RoundBtn(cv, "\U0001F4C4  " + btn_text, command, 158, 32, self.ST["file"], P["card"], radius=10)
        cv.create_window(w / 2, 47, window=btn)
        lbl = tk.Label(cv, text="", bg=P["card"], fg=P["muted"], font=("Segoe UI", 8),
                       wraplength=w - 24, justify="center")
        cv.create_window(w / 2, 81, window=lbl)
        return cv, btn, lbl

    def select_mode(self, val):
        self.mode.set(val)
        self.on_mode()

    def on_mode(self):
        m = self.mode.get()
        self.hint.config(text=MODE_HINT[m])
        for val, b in self.tab_buttons.items():
            b.set_style(self.ST["tab_on"] if val == m else self.ST["tab_off"])
        use_word = True
        self.word_btn.set_enabled(use_word)
        self.word_label.config(fg=P["muted"] if use_word else P["border"])
        self.refresh_list()

    def refresh_checks(self):
        win = self.window()
        n = len(win)
        if n:
            self.chk_chrome.config(text=f"\u2713  {len(self.items)} Chrome mile, Chrome {win[0][0]} se {win[-1][0]} tak",
                                   fg=P["ok"])
        else:
            self.chk_chrome.config(text="\u2717  Chrome folder chuno", fg=P["warn"])
        m = self.mode.get()
        if not self.word_folder:
            self.chk_word.config(text="\u2717  Word files ka folder chuno", fg=P["warn"])
        else:
            files = self.files_for(m)
            have = sum(1 for i, _ in win if self.fno(i) in files)
            good = n > 0 and have == n
            kind = {"reminder": "Reminder files (re1...)", "members": "Excel files (Id 1...)"}.get(m, "Word files")
            self.chk_word.config(text=f"{chr(0x2713) if good else chr(0x2717)}  {kind}: {have}/{n} mili",
                                 fg=P["ok"] if good else P["warn"])

    def refresh_list(self):
        self.listbox.delete(0, "end")
        m = self.mode.get()
        use_word = True
        files = self.files_for(m)
        if not self.items:
            self.listbox.insert("end", "  Abhi koi Chrome folder nahi chuna")
        elif not self.window():
            self.listbox.insert("end", f"  Shuru no. {self.start_no()} se koi Chrome nahi (folder mein {len(self.items)} hain)")
        for i, name in self.window():
            line = f"{i}. {name}"
            if use_word:
                wf = files.get(self.fno(i))
                line += "     \u2192     " + (os.path.basename(wf) if wf else f"{self.file_label(self.fno(i), m)} NAHI MILI")
            self.listbox.insert("end", line)
        self.refresh_checks()

    def start_no(self):
        try:
            return max(1, int(float(self.start_box.get())))
        except (ValueError, tk.TclError):
            return 1

    def window(self):
        """[(number, naam)]: folder mein 'Shuru no.' se LIMIT (10) Chrome. Number folder ke kram wala hi rehta hai."""
        a = self.start_no()
        return [(i, n) for i, n in enumerate(self.items, 1) if a <= i < a + LIMIT]

    def fno(self, num, a=None):
        """Chrome number -> file number (hamesha 1 se shuru): Shuru no. 11 ho to Chrome 11 = file 1, Chrome 12 = file 2 ..."""
        if a is None:
            a = self.start_no()
        return num - a + 1

    def rfno(self, num):
        """Chalte run mein file number (run shuru hone par jo Shuru no. tha, usi se)."""
        return self.fno(num, self.cur_start)

    def on_start_no(self):
        if self.running or (self.thread and self.thread.is_alive()):
            return
        self.reset_state()
        self.refresh_list()

    def files_for(self, mode):
        if mode == "reminder":
            return self.reminder_files
        if mode == "members":
            return self.excel_files
        return self.word_files

    def file_label(self, num, mode):
        if mode == "reminder":
            return f"re{num}"
        if mode == "members":
            return f"Id {num}"
        return f"{ordinal(num)} file"

    # ----- state -----
    def reset_state(self):
        self.phase = 1          # 1 = sab Chrome kholna, 2 = extension ka kaam
        self.pos = 0            # abhi queue mein kaun sa number
        self.queue = []         # [(number, naam)]
        self.hwnds = {}         # number -> window handle
        self.problems = []      # [(number, wajah)]
        self.notes = []         # Start ke baad badlav dikha ya nahi
        self.popups = {}        # number -> popup window (Add Members: Start ke baad "Poora hua" dekhne ke liye)
        self.start_times = {}   # number -> Start dabne ka samay
        self.finished = set()   # jin Chrome ka kaam poora ho ke band ho chuka
        self.closed_count = 0
        self.batches = 0
        self.auto_run = False

    def ui(self, fn, *a):
        self.root.after(0, fn, *a)

    def say(self, text, color="#3ddc97"):
        self.ui(lambda: (self.status.config(text=text, fg=color), self.dot.config(fg=color)))

    def highlight(self, num):
        def f():
            self.listbox.selection_clear(0, "end")
            nums = [i for i, _ in self.window()]
            if num in nums:
                self.listbox.selection_set(nums.index(num))
                self.listbox.see(nums.index(num))
        self.ui(f)

    def set_folder(self, folder):
        self.folder = folder
        self.folder_label.config(text=os.path.basename(folder.rstrip("/\\")) or folder)
        self.items = get_items(folder)
        self.reset_state()
        self.refresh_list()
        self.status.config(text=f"{len(self.items)} Chrome mile")

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Day 1 ya Day 2 folder chuno")
        if folder:
            self.running = False
            self.set_folder(folder)
            try:
                with open(SAVE_FILE, "w", encoding="utf-8") as f:
                    f.write(folder)
            except OSError:
                pass

    def set_word_folder(self, folder):
        self.word_folder = folder
        try:
            self.word_files = get_word_files(folder)
            self.reminder_files = get_reminder_files(folder)
            self.excel_files = get_excel_files(folder)
        except OSError:
            self.word_files, self.reminder_files, self.excel_files = {}, {}, {}
        self.word_label.config(
            text=f"{os.path.basename(folder.rstrip(chr(47) + chr(92))) or folder}\n"
                 f"{len(self.word_files)} Word, {len(self.reminder_files)} re, {len(self.excel_files)} Id files mili")
        self.refresh_list()

    def choose_word_folder(self):
        folder = filedialog.askdirectory(title="Word files ka folder chuno (jaise Documents\\automation file)")
        if folder:
            self.set_word_folder(folder)
            try:
                with open(WORD_SAVE_FILE, "w", encoding="utf-8") as f:
                    f.write(folder)
            except OSError:
                pass

    def gap(self):
        try:
            return max(0.0, float(self.delay.get()))
        except ValueError:
            return DEFAULT_GAP

    def settle(self):
        try:
            return min(3.0, max(0.0, float(self.settle_box.get())))
        except ValueError:
            return POPUP_SETTLE

    def parse_only(self):
        txt = self.only.get().strip()
        if not txt:
            return None
        return {int(t) for t in re.findall(r"\d+", txt)}

    def start(self):
        if not self.folder:
            messagebox.showwarning("Folder", "Pehle Chrome folder chuno.")
            return
        if self.running or (self.thread and self.thread.is_alive()):
            return
        if self.phase == 1 and self.pos == 0:      # bilkul naya run
            self.items = get_items(self.folder)
            if not self.items:
                messagebox.showinfo("Khali", "Is folder mein koi item nahi mila.")
                return
            only = self.parse_only()
            queue = [(i, n) for i, n in self.window() if only is None or i in only]
            if not queue:
                messagebox.showinfo("Khali", "Shuru no. se koi Chrome nahi mila (ya Sirf no. list mein nahi hain).")
                return
            self.cur_mode = self.mode.get()
            self.cur_start = self.start_no()
            if True:
                if not self.word_folder or not os.path.isdir(self.word_folder):
                    messagebox.showwarning("Word folder", "Pehle 'Word files ka folder chuno' dabao.")
                    return
                self.word_files = get_word_files(self.word_folder)
                self.reminder_files = get_reminder_files(self.word_folder)
                self.excel_files = get_excel_files(self.word_folder)
                files = self.files_for(self.cur_mode)
                missing = [n for n, _ in queue if self.rfno(n) not in files]
                if missing:
                    hint = {"reminder": "File ka naam re1.docx, re2.docx ... hona chahiye.",
                            "members": "File ka naam Id 1.xlsx, Id 2.xlsx ... hona chahiye."}.get(
                        self.cur_mode, "File ka naam number se shuru hona chahiye (jaise 1st file, 2nd file...).")
                    messagebox.showwarning(
                        "Word file nahi mili",
                        "In Chrome ki file folder mein nahi mili: "
                        + ", ".join(f"{n} ({self.file_label(self.rfno(n), self.cur_mode)})" for n in missing)
                        + "\n\n" + hint)
                    return
            self.queue = queue
            self.hwnds, self.problems, self.notes = {}, [], []
            self.popups, self.start_times, self.finished = {}, {}, set()
            self.closed_count, self.batches = 0, 1
            self.run_start = self.cur_start
            self.auto_run = (self.cur_mode == "members" and bool(self.auto_var.get()))
            self.ai_calls = 0
        self.running = True
        self.thread = threading.Thread(target=self.worker, daemon=True)
        self.thread.start()

    def pause(self):
        if self.running:
            self.running = False
            self.say("Stop - abhi wala kaam poora hone ke baad rukega. Start dabane par wahin se aage badhega.", "#ffb347")

    # ----- worker -----
    def worker(self):
        fails = 0
        write_log(f"=== Run shuru (mode={self.cur_mode}, night={self.auto_run}, shuru no.={self.cur_start}) ===")
        while True:
            try:
                if self.phase == 1:
                    self.phase1()
                    if not self.running:
                        return
                    self.phase = 2
                    self.pos = 0
                    self.say("Sab Chrome khul gaye. Ab extension ka kaam...")
                if self.phase == 2:
                    self.phase2()
                    if not self.running:
                        return
                    if self.auto_run:
                        self.heal_failed()          # jin mein Start nahi dabaa, unhe band karke dobara koshish
                        self.phase = 3
                if self.phase == 3:
                    self.monitor()
                    if not self.running:
                        return
                fails = 0
                if self.auto_run and self.next_batch():
                    continue
                break
            except Exception as e:
                err = traceback.format_exc()
                print(err)
                write_log("BATCH ERROR: " + err)
                fails += 1
                if not self.auto_run or fails >= MAX_BATCH_ERRORS:
                    self.running = False
                    self.say(f"Error: {e}", "#ff6b6b")
                    return
                self.say(f"Gadbad ({e}) - is batch ko band karke agle par ja raha hoon", "#ffb347")
                for n, _ in self.queue:
                    try:
                        self.close_chrome_hard(n)
                    except Exception:
                        pass
                if not self.next_batch():
                    break
        try:
            self.finish()
        except Exception as e:
            self.running = False
            self.say(f"Error: {e}", "#ff6b6b")
            print(traceback.format_exc())

    # ----- Self-heal: fail hue Chrome ko band karke dobara kholna -----
    def heal_failed(self):
        names = dict(self.queue)
        for attempt in range(1, RETRY_MAX + 1):
            bad = [n for n, _ in self.queue if n not in self.popups]
            if not bad or not self.running:
                break
            self.say(f"Dobara koshish {attempt}/{RETRY_MAX}: Chrome " + ", ".join(map(str, bad)), "#ffb347")
            for num in bad:
                if not self.running:
                    return
                why = "; ".join(w for n, w in self.problems if n == num) or "pata nahi"
                write_log(f"Chrome {num} fail ({why}) - retry {attempt}")
                self.close_chrome_hard(num)
                self.hwnds.pop(num, None)
                self.problems = [(n, w) for n, w in self.problems if n != num]
                hwnd = self.open_one(names[num])
                if not hwnd:
                    self.problems.append((num, "retry mein bhi Chrome ka window nahi dikha"))
                    continue
                self.hwnds[num] = hwnd
                try:
                    problem = self.do_one(num, hwnd)
                except Exception as e:
                    print(traceback.format_exc())
                    problem = f"koi gadbad: {e}"
                if problem:
                    self.problems.append((num, problem))
                    self.ai_fix(num, problem)      # AI screen dekhke dialog/popup hata de
                else:
                    write_log(f"Chrome {num}: retry mein theek ho gaya")
        # ab bhi jo fail hain: band karo taaki agle batch ke saath dher na lage
        for num in [n for n, _ in self.queue if n not in self.popups]:
            why = "; ".join(w for n, w in self.problems if n == num)
            write_log(f"Chrome {num} SKIP kiya (dobara chalana): {why}")
            self.close_chrome_hard(num)
            self.finished.add(num)

    def close_chrome_hard(self, num):
        """Chrome band karo; na ho to AI se screen dekhwakar ek baar aur."""
        err = self.close_chrome(num)
        if err:
            self.ai_fix(num, err)
            err = self.close_chrome(num)
        return err

    def ai_fix(self, num, why):
        """Poori screen ki tasveer Gemini ko bhejo; wo sirf Enter / Esc / Alt+F4 / wait / none bata sakta hai."""
        key = load_ai_key()
        if not key:
            return None
        now = time.time()
        if getattr(self, "ai_calls", 0) >= AI_MAX_CALLS or now - getattr(self, "ai_last", 0) < AI_MIN_GAP:
            return None
        self.ai_calls = getattr(self, "ai_calls", 0) + 1
        self.ai_last = now
        try:
            hwnd = self.hwnds.get(num)
            sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
            buf = grab_region(0, 0, sw, sh)
            if not buf:
                return None
            png = bgra_to_png(buf, sw, sh, 2)
            prompt = (
                "Yeh ek Windows PC ki screenshot hai jahan ek automation tool kai Chrome windows chala raha hai. "
                f"Tool ko yeh dikkat aayi: '{why}'. Batao screen par kya rukawat hai (jaise 'Leave site?' dialog, "
                "file dialog atka hua, Chrome crash/error page, 'Restore pages' popup, ya kuch nahi). "
                "Sirf JSON do: {\"state\": \"chhota description\", "
                "\"action\": \"none|enter|escape|alt_f4|wait\", \"why\": \"Hindi mein ek line\"}. "
                "enter sirf tab jab dialog ko aage badhane ka safe tareeka ho (jaise 'Leave'); "
                "escape unwanted popup/file dialog band karne ko; alt_f4 atki hui Chrome/error window band karne ko; "
                "wait agar page bas load ho raha hai; none agar kuch galat nahi.")
            self.say(f"Chrome {num}: AI se screen poochh raha hoon...", "#ffb347")
            reply = ask_ai(png, prompt, key)
            write_log(f"AI (Chrome {num}, dikkat: {why}) -> {reply}")
            action = str(reply.get("action", "none")).lower() if isinstance(reply, dict) else "none"
            if action in ("enter", "escape", "alt_f4"):
                dl = dialog_windows()
                target = dl[-1] if dl else hwnd
                if target and user32.IsWindow(target):
                    force_foreground(target)
                    time.sleep(0.3)
                if action == "enter":
                    press_keys(VK_RETURN)
                elif action == "escape":
                    press_keys(VK_ESCAPE)
                else:
                    press_keys(0x12, 0x73)       # Alt + F4
                time.sleep(1.0)
            elif action == "wait":
                time.sleep(5.0)
            return action
        except Exception:
            write_log("AI fix error: " + traceback.format_exc())
            return None

    def ai_judge_popup(self, num):
        """Popup ki tasveer AI ko dikhao: 'working' / 'done' / 'error' / 'stuck'. AI na mile to None."""
        key = load_ai_key()
        popup = self.popups.get(num)
        now = time.time()
        if not key or not popup_alive(popup):
            return None
        if getattr(self, "ai_calls", 0) >= AI_MAX_CALLS or now - getattr(self, "ai_last", 0) < AI_MIN_GAP:
            return None
        self.ai_calls = getattr(self, "ai_calls", 0) + 1
        self.ai_last = now
        try:
            l, tp, r, b = rect_tuple(popup)
            buf = grab_region(l, tp, r - l, b - tp)
            if not buf:
                return None
            png = bgra_to_png(buf, r - l, b - tp, 1)
            prompt = ("Yeh ek Chrome extension ke popup ki tasveer hai jo groups mein members add karta hai. "
                      "Batao kya woh kaam kar raha hai, poora ho chuka hai, error dikha raha hai, ya atka hua hai "
                      "(kuch aage nahi badh raha). Sirf JSON do: "
                      "{\"status\": \"working|done|error|stuck\", \"why\": \"Hindi mein ek line\"}")
            reply = ask_ai(png, prompt, key)
            write_log(f"AI popup jaanch (Chrome {num}) -> {reply}")
            if isinstance(reply, dict) and reply.get("status") in ("working", "done", "error", "stuck"):
                return reply["status"]
        except Exception:
            write_log("AI judge error: " + traceback.format_exc())
        return None

    def check_stuck(self, num):
        """(1) Popup ke dibbe STUCK_SECONDS se nahi badle = kaam aage nahi badh raha, (2) HEALTH_AI_EVERY se AI ne nahi dekha.
        Dono mein AI se poochho; 'done' ho to chhodo, nahi to (atka / error) Chrome band karke dobara chalao."""
        now = time.time()
        sig = self.shot_sig.get(num)
        idle = (now - sig[1]) if sig else 0
        idle_long = idle >= STUCK_SECONDS
        last = self.ai_checked.get(num, self.start_times.get(num, now))
        periodic = now - last >= HEALTH_AI_EVERY
        if not (idle_long or periodic):
            return
        self.ai_checked[num] = now
        status = self.ai_judge_popup(num)
        if status == "done":
            return
        if not idle_long and status not in ("error", "stuck"):
            return
        popup = self.popups.get(num)
        if popup_alive(popup):
            l, tp, r, b = rect_tuple(popup)
            save_debug_shot(f"chrome{num}_stuck", take_shot(l, tp, r - l, b - tp))
        why = f"{int(idle // 60)} min se kaam aage nahi badha" if idle_long else f"AI ne '{status}' bataya"
        self.try_redo(num, why)

    def confirm_done(self, num):
        """Is Chrome par 'visit': safed screen, band popup, Start na laga ho - sab dekho aur theek karo.
        'Poora hua' do baar lagatar dikhe tabhi True."""
        now = time.time()
        if now - self.start_times.get(num, 0) < MIN_RUN_SECONDS:
            return False
        hwnd = self.hwnds.get(num)
        if not hwnd or not user32.IsWindow(hwnd):
            return False
        if not popup_alive(self.popups.get(num)):
            if now - self.reopen_at.get(num, 0) < VISIT_EVERY:
                return False
            self.reopen_at[num] = now
            if not bring_front_maximized(hwnd):
                return False
            if self.red_banner(hwnd):                        # laal sandesh (jaise 'Starred group nahi mila')
                self.fix_red_banner(num, hwnd)
                return False
            if self.page_is_blank(hwnd):                     # safed (white) screen
                self.blank_hits[num] = self.blank_hits.get(num, 0) + 1
                write_log(f"Chrome {num}: page bilkul safed dikha ({self.blank_hits[num]}/2)")
                if self.blank_hits[num] >= 2:
                    self.blank_hits[num] = 0
                    l, tp, r, b = rect_tuple(hwnd)
                    save_debug_shot(f"chrome{num}_white", take_shot(l, tp, r - l, b - tp))
                    self.try_redo(num, "page safed (white screen) hai")
                    return False
            else:
                self.blank_hits[num] = 0
            if not self.reopen_popup(num):
                return False
        if self.popup_done(num):
            time.sleep(0.6)
            return bool(self.popup_done(num))
        return self.check_idle(num) == "done"

    def red_banner(self, hwnd):
        s = dpi_scale()
        l, t, r, b = rect_tuple(hwnd)
        cx = (l + r) // 2
        x0, y0, w, h = int(cx - 150 * s), int(t + 100 * s), int(100 * s), int(200 * s)
        shot = take_shot(x0, y0, w, h)
        return bool(shot) and find_red_banner(shot, x0, y0, w, h, s)

    def fix_red_banner(self, num, hwnd):
        """Laal sandesh: pehle group par star lagao (na laga ho to), phir extension ke popup mein Restart dabao."""
        self.star_fixes[num] = self.star_fixes.get(num, 0) + 1
        write_log(f"Chrome {num}: laal sandesh dikha (koshish {self.star_fixes[num]})")
        l, t, r, b = rect_tuple(hwnd)
        save_debug_shot(f"chrome{num}_redbanner", take_shot(l, t, r - l, b - t))
        if self.star_fixes[num] > 3:
            self.try_redo(num, "laal sandesh baar baar aa raha hai")
            return
        s = dpi_scale()
        # 1) star
        shot = take_shot(l, t + int(150 * s), r - l, b - t - int(150 * s))
        stars = find_stars(shot, l, r, t + 150 * s, b - 20 * s, s) if shot else []
        if not stars:
            write_log(f"Chrome {num}: My groups list ke star nahi dikhe (page galat ho sakta hai)")
            self.try_redo(num, "star wali list nahi mili")
            return
        if not any(on for _, on in stars):
            cy = stars[0][0]
            click_at(r - 48 * s, cy)
            write_log(f"Chrome {num}: pehle group par star lagaya")
            time.sleep(1.5)
            shot = take_shot(l, t + int(150 * s), r - l, b - t - int(150 * s))
            stars = find_stars(shot, l, r, t + 150 * s, b - 20 * s, s) if shot else []
            if not any(on for _, on in stars):
                write_log(f"Chrome {num}: star lagane ke baad bhi star nahi dikha")
                self.try_redo(num, "group par star nahi lag paya")
                return
        else:
            write_log(f"Chrome {num}: star pehle se laga hai")
        # 2) extension popup ka Restart
        if not popup_alive(self.popups.get(num)):
            if not self.reopen_popup(num):
                self.try_redo(num, "star ke baad popup nahi khul paya")
                return
        popup = self.popups[num]
        pl, pt, pr, pb = rect_tuple(popup)
        pshot = take_shot(pl, pt, pr - pl, pb - pt)
        pos = find_orange_button(pshot, pl, pt, pr - pl, pb - pt, s) if pshot else None
        if not pos or not inside_popup(popup, pos[0], pos[1]):
            write_log(f"Chrome {num}: popup mein Restart button nahi dikha")
            save_debug_shot(f"chrome{num}_norestart", pshot)
            self.try_redo(num, "Restart button nahi mila")
            return
        click_at(pos[0], pos[1])
        write_log(f"Chrome {num}: Restart dabaya")
        self.start_times[num] = time.time()
        self.shot_sig.pop(num, None)
        self.idle_hits[num] = 0
        time.sleep(2.0)

    def page_is_blank(self, hwnd):
        """Chrome ke page ka baayein hissa lagbhag poora safed (255,255,255) ho to True."""
        s = dpi_scale()
        l, t, r, b = rect_tuple(hwnd)
        x0, y0 = int(l + 10 * s), int(t + 190 * s)
        w, h = int((r - l) * 0.4), int(b - y0 - 70 * s)
        if w < 100 or h < 100:
            return False
        shot = take_shot(x0, y0, w, h)
        if not shot:
            return False
        buf, white, total = shot.buf, 0, 0
        for y in range(0, h, 6):
            base = y * w * 4
            for x in range(0, w, 6):
                o = base + x * 4
                total += 1
                if buf[o] >= 250 and buf[o + 1] >= 250 and buf[o + 2] >= 250:
                    white += 1
        return total > 0 and white / total >= BLANK_WHITE

    def check_idle(self, num):
        """Popup khula hai par 'Poora hua' nahi: agar Start hara (dabne layak) hai to kaam chal nahi raha - Start dabao."""
        popup, pos = self.popups.get(num), self.__dict__.get("icons", {}).get(num)
        if not AUTO_PRESS_START or not popup_alive(popup) or not pos:
            return None
        ix, iy = pos
        s = dpi_scale()
        shot = self.members_shot(ix, iy, s)
        r = find_members_start(shot, ix, iy, s) if shot else None
        if not (r and r[0] == "green"):
            self.idle_hits[num] = 0
            return None
        self.idle_hits[num] = self.idle_hits.get(num, 0) + 1
        write_log(f"Chrome {num}: Start hara hai, kaam chalta nahi dikha ({self.idle_hits[num]}/2)")
        if self.idle_hits[num] < 2:                         # 2 visit lagatar - beech ke pal ko galat na maanein
            return None
        self.idle_hits[num] = 0
        if self.ai_judge_popup(num) == "done":               # Start dabane se pehle AI se: kaheen kaam poora to nahi hua?
            write_log(f"Chrome {num}: AI ne kaha kaam poora ho chuka hai")
            return "done"
        self.start_retry[num] = self.start_retry.get(num, 0) + 1
        if self.start_retry[num] > 3:
            self.try_redo(num, "Start baar baar nahi laga")
            return None
        save_debug_shot(f"chrome{num}_idle", shot)
        err = self.press_start_members(num, popup, ix, iy, s)
        write_log(f"Chrome {num}: Start dobara dabaya" + (f" - dikkat: {err}" if err else ""))
        if err:
            self.try_redo(num, err)
        return None

    def try_redo(self, num, why):
        """Chrome band karke dobara chalao (limit STUCK_RETRY); limit poori ho to usse chhodkar aage badho."""
        if self.redo_count.get(num, 0) >= STUCK_RETRY:
            write_log(f"Chrome {num}: {why} - dobara koshish ki limit poori, chhod diya")
            self.problems.append((num, f"{why} (dobara chalane par bhi theek nahi hua)"))
            self.close_chrome_hard(num)
            self.finished.add(num)
            return False
        self.redo_count[num] = self.redo_count.get(num, 0) + 1
        return self.redo_chrome(num, why)

    def reopen_popup(self, num):
        """Chrome saamne hai: extension icon dabao, Add Members tab chuno, neeche scroll karo. Taiyar ho to True."""
        hwnd = self.hwnds.get(num)
        if not hwnd or not user32.IsWindow(hwnd):
            return False
        s = dpi_scale()
        pos = find_extension_icon(hwnd, s, self.icon_hint)
        if not pos:
            write_log(f"Chrome {num}: popup band hai aur extension icon nahi dikha")
            return False
        self.icon_hint = pos
        ix, iy = pos
        self.__dict__.setdefault("icons", {})[num] = pos
        before = set(chrome_windows())
        click_at(ix, iy)
        popup = wait_popup(before, hwnd, ix, iy)
        if not popup:
            write_log(f"Chrome {num}: popup dobara nahi khul paya")
            return False
        self.popups[num] = popup
        time.sleep(self.settle())
        err = self.ensure_tab(popup, ix, iy, s, "members")
        if err:
            write_log(f"Chrome {num}: dobara khole popup mein {err}")
            return False
        wx, wy = ix + MEM_SCROLL_X * s, iy + MEM_SCROLL_Y * s
        if inside_popup(popup, wx, wy):
            wheel_at(wx, wy, 3)              # neeche ka 'Poora hua' / Start wala hissa dikhe
            time.sleep(0.3)
        return True

    def redo_chrome(self, num, why):
        """Chrome band karo, wahi file dobara kholo aur extension ka poora kaam phir se karo."""
        name = dict(self.queue)[num]
        self.say(f"Chrome {num}: {why} - dobara chala raha hoon", "#ffb347")
        write_log(f"Chrome {num}: {why} - band karke dobara")
        self.close_chrome_hard(num)
        for d in (self.hwnds, self.popups, self.start_times, self.shot_sig):
            d.pop(num, None)
        hwnd = self.open_one(name)
        problem = None
        if not hwnd:
            problem = "dobara kholne par Chrome ka window nahi dikha"
        else:
            self.hwnds[num] = hwnd
            try:
                problem = self.do_one(num, hwnd)
            except Exception as e:
                print(traceback.format_exc())
                problem = f"koi gadbad: {e}"
        if problem or num not in self.popups:
            problem = problem or "Start nahi dab paya"
            write_log(f"Chrome {num}: dobara chalana fail: {problem}")
            self.problems.append((num, problem))
            self.close_chrome_hard(num)
            self.finished.add(num)
            return False
        return True

    def set_ai_key(self):
        cur = load_ai_key()
        k = simpledialog.askstring(
            "AI key (Gemini, free)",
            "Google AI Studio (aistudio.google.com) se free API key banao aur yahan paste karo.\n"
            "Khali chhodkar OK = AI band (tab bhi retry/band karna chalega).",
            initialvalue=cur, parent=self.root)
        if k is None:
            return
        try:
            with open(AI_KEY_FILE, "w", encoding="utf-8") as f:
                f.write(k.strip())
            self.say("AI key save ho gayi." if k.strip() else "AI key hata di gayi.")
        except OSError as e:
            self.say(f"AI key save nahi hui: {e}", "#ff6b6b")

    # ----- Add Members auto-cycle -----
    def next_batch(self):
        """Agle 10 Chrome (Shuru no. + LIMIT) ki taiyari. Folder khatam ho to False."""
        nxt = self.cur_start + LIMIT
        if nxt > len(self.items):
            return False
        self.cur_start = nxt
        self.queue = [(i, n) for i, n in enumerate(self.items, 1) if nxt <= i < nxt + LIMIT]
        self.hwnds, self.popups, self.start_times, self.finished = {}, {}, {}, set()
        self.phase, self.pos = 1, 0
        self.batches += 1

        def show():
            self.start_box.delete(0, "end")
            self.start_box.insert(0, str(nxt))
            self.refresh_list()
        self.ui(show)
        self.say(f"Agle 10 Chrome: {self.queue[0][0]} se {self.queue[-1][0]} tak")
        write_log(f"Agla batch: {self.queue[0][0]} se {self.queue[-1][0]} tak")
        time.sleep(1.0)
        return True

    def monitor(self):
        """Start dabe hue Chrome ko dekho. Ab har ID par extension kholkar progress nahi dekhte: sirf page ki patti / error.
        Poora hua ya daily limit -> Excel save + ID band. Pause -> Resume (na chale to Restart). Kuch na chale -> 1 minute mein band."""
        self.shot_sig, self.redo_count, self.stuck_hits = {}, {}, {}
        self.ai_checked, self.reopen_at = {}, {}
        self.blank_hits, self.idle_hits, self.start_retry, self.star_fixes = {}, {}, {}, {}
        self.light_at, self.done_hits, self.paused_hits, self.no_banner_since = {}, {}, {}, {}
        self.recovered = set()
        self.no_banner_n = {}
        self.probe_fail, self.not_running_since = {}, {}
        nums = [n for n, _ in self.queue if n in self.popups]
        t0 = time.time()
        while self.running:
            pending = [n for n in nums if n not in self.finished]
            if not pending:
                return
            for num in pending:
                if not self.running:
                    return
                hwnd = self.hwnds.get(num)
                if not hwnd or not user32.IsWindow(hwnd):
                    write_log(f"Chrome {num}: window 'Poora hua' se pehle band ho gayi (crash ya kisi ne band kiya)")
                    if self.running and self.redo_count.get(num, 0) < STUCK_RETRY:
                        self.redo_count[num] = self.redo_count.get(num, 0) + 1
                        self.redo_chrome(num, "window band ho gayi")
                    else:
                        self.problems.append((num, "window baar baar band hui, chhod diya"))
                        self.finished.add(num)
                    continue
                result = self.visit(num)
                if result in ("done", "limit"):
                    self.finish_member(num, result)
                elif result == "dead":
                    self.problems.append((num, "1 minute mein bhi kaam chalu nahi hua (Start/Resume/Restart ke baad bhi), ID band - dobara chalana"))
                    err = self.close_chrome_hard(num)
                    self.finished.add(num)
            left = [n for n in nums if n not in self.finished]
            if left:
                self.say(f"Batch {self.batches}: {len(nums) - len(left)}/{len(nums)} poore. Intezaar: "
                         + ", ".join(map(str, left)))
            if left and time.time() - t0 > MONITOR_TIMEOUT:
                for n in left:
                    write_log(f"Chrome {n}: {MONITOR_TIMEOUT // 60} min mein 'Poora hua' nahi dikha")
                    self.ai_fix(n, "Poora hua bahut der se nahi dikha, shayad atka hua hai")
                    if self.auto_run:
                        self.problems.append((n, "Poora hua nahi dikha (time khatam), Chrome band kiya - dobara chalana"))
                        self.close_chrome_hard(n)
                    else:
                        self.problems.append((n, "Poora hua nahi dikha (time khatam), Chrome khula chhoda"))
                    self.finished.add(n)
                return
            time.sleep(MONITOR_POLL)

    # ----- Page par hi dekho (extension par click kiye bina): patti / error -----
    def page_state(self, num):
        """Chrome ko saamne lao aur sirf page dekho. Lautata hai (patti, error_dibba):
        patti = 'green'/'gray'/'red'/'other'/None, error_dibba = True/False. Window na mile to (None, False)."""
        hwnd = self.hwnds.get(num)
        if not hwnd or not user32.IsWindow(hwnd):
            return None, False
        for _ in range(2):
            if bring_front_maximized(hwnd):
                break
        wait_rect_stable(hwnd, 0.6)
        time.sleep(0.25)
        if user32.GetForegroundWindow() != hwnd:       # galat window ki tasveer na lein (galat ID band na ho)
            return "unknown", False
        s = dpi_scale()
        l, tp, r, b = rect_tuple(hwnd)
        cx = (l + r) // 2
        # patti: page ke upar beech (bookmarks bar / 'started debugging' patti ho ya na ho, sab mein)
        bx, by, bw, bh = int(cx - 260 * s), int(tp + 88 * s), int(520 * s), int(230 * s)
        bshot = take_shot(bx, by, bw, bh)
        banner = find_page_banner(bshot, bx, by, bw, bh, s) if bshot else None
        # error dibba: page ke neeche-baayein kone mein
        ex, ey, ew, eh = int(l + 10 * s), int(b - 330 * s), int(340 * s), int(300 * s)
        eshot = take_shot(ex, ey, ew, eh) if eh > 50 else None
        err = bool(eshot) and find_error_dialog(eshot, ex, ey, ew, eh, s)
        return banner, err

    def popup_buttons(self, num):
        """Popup khol kar Resume / Pause / Restart wali line dhundo (scroll neeche). Lautata hai
        (popup, resume_xy, restart_xy, resume_hara_hai) ya None."""
        if not popup_alive(self.popups.get(num)):
            bring_front_maximized(self.hwnds.get(num))
            if not self.reopen_popup(num):
                return None
        popup = self.popups.get(num)
        pos = self.__dict__.get("icons", {}).get(num)
        if not pos or not popup_alive(popup):
            return None
        s = dpi_scale()
        ix, iy = pos
        pl, pt, pr, pb = rect_tuple(popup)
        shot = take_shot(pl, pt, pr - pl, pb - pt)
        if not shot:
            return None
        o = find_orange_button(shot, pl, pt, pr - pl, pb - pt, s)       # Restart (narangi bada button)
        if not o:
            return None
        rx, ry = o
        # "Pause" chhota narangi label (Pause kiya gaya...) bhi narangi hai: Restart wo hai jo sabse neeche ho
        res_x, res_y = rx + RESUME_DX * s, ry
        green = is_green(shot.rgb(res_x - 40 * s, res_y))      # button ke baayein hisse ka rang (likhai se door)
        return popup, (res_x, res_y), (rx, ry), bool(green)

    def recover_member(self, num, why):
        """ID chal nahi rahi / ruki hai: popup mein Resume (hara dikhe to), na ho ya na chale to Restart.
        True = kuch dabaya."""
        ready = self.popup_buttons(num)
        if not ready:
            write_log(f"Chrome {num}: {why} - popup mein Resume/Restart nahi mile")
            return False
        popup, res, rst, green = ready
        for name, (x, y) in ((("Resume", res), ("Restart", rst)) if green else (("Restart", rst),)):
            if not inside_popup(popup, x, y):
                continue
            click_at(x, y)
            write_log(f"Chrome {num}: {why} - '{name}' dabaya")
            self.start_times[num] = time.time()
            self.shot_sig.pop(num, None)
            time.sleep(2.0)
            if name == "Resume":
                # 5 second dekho: patti 'gray' se badli? nahi badli to Restart bhi dabana padega
                t = time.time()
                while time.time() - t < 5.0:
                    time.sleep(1.0)
                st, _ = self.page_state(num)
                if st != "gray":
                    return True
                again = self.popup_buttons(num)
                if not again:
                    return True
                popup, res, rst, green = again
                click_at(rst[0], rst[1])
                write_log(f"Chrome {num}: Resume se chalu nahi hua - 'Restart' dabaya")
                time.sleep(2.0)
            return True
        return False

    def light_check(self, num):
        """Ek ID ki halat sirf page ki patti / error se dekho. Poora/error ho to 'done', warna None."""
        now = time.time()
        if now - self.light_at.get(num, 0) < LIGHT_EVERY:
            return None
        self.light_at[num] = now
        banner, err = self.page_state(num)
        if banner == "unknown":                    # window saamne nahi aayi: kuch bhi tay na karo
            write_log(f"Chrome {num}: window saamne nahi aayi, is baar chhod diya")
            self.light_at[num] = now - LIGHT_EVERY + 5
            return None
        age = now - self.start_times.get(num, now)
        write_log(f"Chrome {num}: page dekha - patti={banner}, error_dibba={err}, chalte {int(age)}s")
        if err and DAILY_LIMIT_CLOSE and age >= MIN_RUN_SECONDS:
            self.done_hits[num] = self.done_hits.get(num, 0) + 1
            if self.done_hits[num] >= 2 or banner == "green":
                write_log(f"Chrome {num}: 'daily limit' error aaya - ID poori maani")
                return "limit"
            return None
        if banner == "green" and age >= MIN_RUN_SECONDS:
            self.done_hits[num] = self.done_hits.get(num, 0) + 1
            return "done" if self.done_hits[num] >= 2 else None
        self.done_hits[num] = 0
        if banner == "red":
            hwnd = self.hwnds.get(num)
            self.fix_red_banner(num, hwnd)
            self.no_banner_since.pop(num, None)
            return None
        if banner == "gray":                       # Pause kiya gaya: Resume, na chale to Restart
            self.no_banner_since.pop(num, None)
            self.no_banner_n.pop(num, None)
            self.paused_hits[num] = self.paused_hits.get(num, 0) + 1
            if self.paused_hits[num] >= 2:
                self.paused_hits[num] = 0
                self.recover_member(num, "Pause kiya hua dikha")
            return None
        self.paused_hits[num] = 0
        if banner == "other":                      # kaam chal raha hai (koi aur patti dikh rahi)
            self.no_banner_since.pop(num, None)
            self.no_banner_n.pop(num, None)
            self.recovered.discard(num)
            return None
        # patti bilkul nahi: kaam shuru hi nahi hua / extension band
        first = self.no_banner_since.setdefault(num, now)
        self.no_banner_n[num] = self.no_banner_n.get(num, 0) + 1
        gone = now - first
        if age < 15:
            self.no_banner_since.pop(num, None)    # abhi Start dabe kuch hi der hui
            return None
        if gone >= NOT_RUNNING_SECONDS and self.no_banner_n.get(num, 0) >= 3:
            write_log(f"Chrome {num}: {int(gone)}s se patti nahi - kaam chal hi nahi raha, ID band")
            return "dead"
        if gone >= NOT_RUNNING_RECOVER and num not in self.recovered:
            self.recovered.add(num)
            self.recover_member(num, "patti nahi dikhi, kaam chalta nahi")
        return None

    # ----- Har ID par jao, extension kholo, popup dekho (chal raha / ruka / poora) -----
    def popup_probe(self, num):
        """ID ke Chrome mein extension khol kar popup padho. Lautata hai dict ya None:
        done (Poora hua dikha), running (Pause laal = chal raha), left_green (Start/Resume dabne layak),
        restart, left (Start/Resume ka xy), popup."""
        if not popup_alive(self.popups.get(num)):
            if not self.reopen_popup(num):
                return None
        popup = self.popups.get(num)
        pos = self.__dict__.get("icons", {}).get(num)
        if not pos or not popup_alive(popup):
            return None
        s = dpi_scale()
        ix, iy = pos
        force_foreground(popup)
        time.sleep(0.15)
        info = None
        for attempt in range(2):
            pl, pt, pr, pb = rect_tuple(popup)
            w, h = pr - pl, pb - pt
            shot = take_shot(pl, pt, w, h)
            if not shot:
                return None
            done = bool(find_done_pill(shot, pl, pt, w, h, s))
            o = find_orange_button(shot, pl, pt, w, h, s)
            if o or done:
                info = {"popup": popup, "done": done, "restart": o, "shot": shot, "left": None,
                        "left_green": False, "running": False, "w": w, "h": h, "pl": pl, "pt": pt}
                if o:
                    rx, ry = o
                    lx, ly = rx + RESUME_DX * s, ry
                    px = rx - 125 * s
                    info["left"] = (lx, ly)
                    info["left_green"] = is_green(shot.rgb(lx - 40 * s, ly))
                    info["running"] = near(shot.rgb(px - 40 * s, ry), BANNER_RED, 40)
                break
            if attempt == 0:                      # buttons nahi dikhe: thoda aur neeche scroll
                wx, wy = ix + MEM_SCROLL_X * s, iy + MEM_SCROLL_Y * s
                if inside_popup(popup, wx, wy):
                    wheel_at(wx, wy, 3)
                    time.sleep(0.3)
        if info is None:
            return None
        # progress ka nishan (kaam aage badh raha hai ya nahi)
        h2 = progress_signature(info["shot"], info["pl"], info["pt"], info["w"], info["h"], s)
        if h2 is None:
            h2 = zlib.crc32(info["shot"].buf)
        prev = self.shot_sig.get(num)
        if prev is None or prev[0] != h2:
            self.shot_sig[num] = (h2, time.time())
        return info

    def visit(self, num):
        """Ek ID par jao: page (error / laal sandesh) dekho, extension kholo, popup padho.
        'done' = Poora hua, 'limit' = daily limit error, 'dead' = 1 minute mein bhi nahi chala, warna None."""
        now = time.time()
        if now - self.light_at.get(num, 0) < LIGHT_EVERY:
            return None
        self.light_at[num] = now
        banner, err = self.page_state(num)
        if banner == "unknown":
            write_log(f"Chrome {num}: window saamne nahi aayi, is baar chhod diya")
            self.light_at[num] = now - LIGHT_EVERY + 5
            return None
        age = now - self.start_times.get(num, now)
        # 1) "exceeded your daily limit / Failed to add members" error = ID poori
        if err and DAILY_LIMIT_CLOSE and age >= MIN_RUN_SECONDS:
            time.sleep(1.0)
            b2, e2 = self.page_state(num)
            if e2:
                write_log(f"Chrome {num}: 'daily limit' error aaya - ID poori maani")
                return "limit"
        # 2) extension ka laal sandesh (jaise 'Starred group nahi mila')
        if banner == "red":
            self.fix_red_banner(num, self.hwnds.get(num))
            return None
        # 3) extension kholo aur popup padho
        info = self.popup_probe(num)
        if not info:
            self.probe_fail[num] = self.probe_fail.get(num, 0) + 1
            write_log(f"Chrome {num}: page patti={banner}; popup nahi padh paya ({self.probe_fail[num]}/3)")
            if banner == "green" and age >= MIN_RUN_SECONDS:
                return "done"                     # popup nahi khula par patti keh rahi hai poora hua
            if self.probe_fail[num] >= 3:
                self.probe_fail[num] = 0
                self.try_redo(num, "extension/popup nahi khul raha")
            return None
        self.probe_fail[num] = 0
        write_log(f"Chrome {num}: page patti={banner}, popup: poora={info['done']}, chal raha={info['running']}, "
                  f"start/resume hara={info['left_green']}, chalte {int(age)}s")
        if info["done"] and age >= MIN_RUN_SECONDS:
            time.sleep(0.6)
            again = self.popup_probe(num)
            if again and again["done"]:
                return "done"
            return None
        if info["running"]:
            self.not_running_since.pop(num, None)
            self.idle_hits[num] = 0
            self.check_stuck(num)
            return None
        # chal nahi raha: Pause kiya hua ya Start nahi dabaa
        first = self.not_running_since.setdefault(num, now)
        gone = now - first
        tries = self.idle_hits.get(num, 0)
        if gone >= NOT_RUNNING_SECONDS and tries >= 2:
            write_log(f"Chrome {num}: {int(gone)}s se chal nahi raha, Start/Resume/Restart ke baad bhi - ID band")
            return "dead"
        popup = info["popup"]
        save_debug_shot(f"chrome{num}_notrunning", info["shot"])
        if tries == 0 and info["left_green"] and info["left"]:
            x, y = info["left"]
            name = "Start/Resume"
        elif info["restart"]:
            x, y = info["restart"]
            name = "Restart"
        else:
            return None
        if inside_popup(popup, x, y):
            click_at(x, y)
            write_log(f"Chrome {num}: chal nahi raha - '{name}' dabaya (koshish {tries + 1})")
            self.idle_hits[num] = tries + 1
            self.start_times[num] = time.time()
            self.shot_sig.pop(num, None)
            time.sleep(1.5)
        return None

    def finish_member(self, num, kind):
        """'Poora hua' / daily limit: extension khol kar Excel mein save, phir ID (Chrome) band."""
        label = "daily limit ka error" if kind == "limit" else "Poora hua"
        self.say(f"Chrome {num}: {label}, Excel mein save kar raha hoon")
        try:
            save_err = self.save_to_excel(num)
        except Exception:
            write_log("SAVE ERROR: " + traceback.format_exc())
            save_err = "save mein gadbad"
        if save_err:
            write_log(f"Chrome {num}: Excel save nahi hua - {save_err}")
            self.problems.append((num, "Excel save nahi hua: " + save_err))
        if save_err and SAVE_REQUIRED:
            self.finished.add(num)
            return
        self.say(f"Chrome {num}: band kar raha hoon")
        write_log(f"Chrome {num}: {label}, band kiya")
        err = self.close_chrome_hard(num)
        if err:
            self.problems.append((num, err))
        else:
            self.closed_count += 1
        self.finished.add(num)

    def save_fallback(self, popup, s):
        """find_save_button na mile to: Restart (narangi) button dhundho, 'Excel file mein save karein' uske ~46 pixel neeche,
        Pause ke theek neeche (Restart se 125 pixel baayein) hota hai. Neela rang mile tabhi (x, y) lautao."""
        if not popup_alive(popup):
            return None
        pl, pt, pr, pb = rect_tuple(popup)
        shot = take_shot(pl, pt, pr - pl, pb - pt)
        if not shot:
            return None
        o = find_orange_button(shot, pl, pt, pr - pl, pb - pt, s)
        if not o:
            return None
        x, y = o[0] - 125 * s, o[1] + 46 * s
        if near(shot.rgb(x - 120 * s, y), BLUE, 30) and near(shot.rgb(x + 120 * s, y), BLUE, 30):
            write_log("Excel save button Restart ke neeche se mila (fallback)")
            return (x, y)
        return None

    def save_to_excel(self, num):
        """'Poora hua' ke baad: extension kholo, halka scroll karke 'Excel file mein save karein' dabao. Theek to None, warna dikkat ka text."""
        if not SAVE_EXCEL_ON_DONE:
            return None
        hwnd = self.hwnds.get(num)
        if not hwnd or not user32.IsWindow(hwnd):
            return "window nahi mili"
        s = dpi_scale()
        if not popup_alive(self.popups.get(num)):
            bring_front_maximized(hwnd)
            if not self.reopen_popup(num):
                return "save ke liye popup nahi khul paya"
        popup = self.popups.get(num)
        pos = self.__dict__.get("icons", {}).get(num)
        if not pos or not popup_alive(popup):
            return "popup/icon ki jagah nahi mili"
        ix, iy = pos
        force_foreground(popup)
        time.sleep(0.2)
        wx, wy = ix + MEM_SCROLL_X * s, iy + MEM_SCROLL_Y * s
        if not inside_popup(popup, wx, wy):
            return "scroll ki jagah popup ke bahar hai"
        # pehle jaisa hai waise dekho, phir halka upar, phir neeche
        steps = [("none", 0), ("up", 1), ("up", 1), ("down", 2), ("down", 2), ("down", 2)]
        for attempt in range(1, SAVE_TRIES + 1):
            found = None
            for how, n in steps:
                if not popup_alive(popup):
                    return "popup beech mein band ho gaya"
                if how == "up":
                    wheel_up_at(wx, wy, n)
                    time.sleep(0.35)
                elif how == "down":
                    wheel_at(wx, wy, n)
                    time.sleep(0.35)
                last = None
                for _ in range(4):                  # scroll tham jaye tab tak
                    shot = self.members_shot(ix, iy, s)
                    r = find_save_button(shot, ix, iy, s) if shot else None
                    if r and last and abs(r[1] - last[1]) <= 1:
                        found = r
                        break
                    last = r
                    time.sleep(0.12)
                if found:
                    break
            if not found:
                found = self.save_fallback(popup, s)         # Restart button ke neeche wala bada neela button
            if not found:
                save_debug_shot(f"chrome{num}_nosave", self.members_shot(ix, iy, s))
                return "'Excel file mein save karein' button nahi dikha"
            x, y = found
            if not inside_popup(popup, x, y):
                return "save button popup ke bahar hai"
            click_at(x, y)
            write_log(f"Chrome {num}: 'Excel file mein save karein' dabaya (koshish {attempt})")
            time.sleep(SAVE_WAIT)
            # save ke baad koi dialog aaye (jaise 'Save as' / permission) to use sambhalo
            if dialog_windows():
                save_debug_shot(f"chrome{num}_savedialog", self.members_shot(ix, iy, s))
                act = self.ai_fix(num, "Excel save dabane ke baad dialog aaya")
                if act is None and dialog_windows():
                    force_foreground(dialog_windows()[-1])
                    time.sleep(0.2)
                    press_keys(VK_RETURN)
                    time.sleep(1.5)
                write_log(f"Chrome {num}: save ke baad dialog sambhala")
            return None
        return "save button dabane ki koshish poori"

    def popup_done(self, num):
        popup = self.popups.get(num)
        if not popup_alive(popup):
            return False
        if time.time() - self.start_times.get(num, 0) < MIN_RUN_SECONDS:
            return False
        s = dpi_scale()
        force_foreground(popup)
        time.sleep(0.15)
        l, tp, r, b = rect_tuple(popup)
        shot = take_shot(l, tp, r - l, b - tp)
        if shot:
            h = progress_signature(shot, l, tp, r - l, b - tp, s)
            if h is None:
                h = zlib.crc32(shot.buf)
            prev = self.shot_sig.get(num)
            if prev is None or prev[0] != h:
                self.shot_sig[num] = (h, time.time())
        return bool(shot) and find_done_pill(shot, l, tp, r - l, b - tp, s)

    def close_chrome(self, num):
        """Chrome window band karo (pehle seedha band karne ka sandesh, na ho to X button par click). Theek to None."""
        hwnd = self.hwnds.get(num)
        popup = self.popups.get(num)
        if not hwnd or not user32.IsWindow(hwnd):
            return None
        user32.PostMessageW(hwnd, 0x0010, 0, 0)         # WM_CLOSE
        t = time.time()
        while time.time() - t < 4.0 and user32.IsWindow(hwnd):
            time.sleep(0.1)
        if user32.IsWindow(hwnd):
            if bring_front_maximized(hwnd):
                l, tp, r, b = rect_tuple(hwnd)
                s = dpi_scale()
                click_at(r - CLOSE_X_DX * s, tp + CLOSE_X_DY * s)
            t = time.time()
            while time.time() - t < 4.0 and user32.IsWindow(hwnd):
                time.sleep(0.1)
        if popup and user32.IsWindow(popup):
            user32.PostMessageW(popup, 0x0010, 0, 0)
            time.sleep(0.3)
        for _ in range(2):                              # 'Leave site?' jaisa popup: Enter = Leave
            if not user32.IsWindow(hwnd):
                break
            write_log(f"Chrome {num}: band nahi hui, 'Leave site?' maan kar Enter dabaya")
            force_foreground(hwnd)
            time.sleep(0.4)
            press_keys(VK_RETURN)
            t = time.time()
            while time.time() - t < 3.0 and user32.IsWindow(hwnd):
                time.sleep(0.1)
            if user32.IsWindow(hwnd):
                user32.PostMessageW(hwnd, 0x0010, 0, 0)
                time.sleep(1.0)
        if user32.IsWindow(hwnd):
            return "Chrome band nahi hui (shayad 'Leave site?' jaisa popup aaya)"
        return None

    # Phase 1: saare Chrome ek ke baad ek tezi se kholo
    def phase1(self):
        while self.pos < len(self.queue):
            if not self.running:
                self.say(f"Pause (agla Chrome: {self.queue[self.pos][0]})", "#ffb347")
                return
            num, name = self.queue[self.pos]
            self.highlight(num)
            self.say(f"Chrome khul raha hai: {name}")
            hwnd = self.open_one(name)
            if hwnd:
                self.hwnds[num] = hwnd
            elif self.running:
                self.problems.append((num, "Chrome ka window nahi dikha"))
            self.pos += 1
            time.sleep(self.gap())

    def open_one(self, name):
        before = set(chrome_windows(titled_only=True))
        taken = set(self.hwnds.values())
        try:
            os.startfile(os.path.join(self.folder, name))
        except OSError as e:
            print(e)
            return None
        t = time.time()
        while time.time() - t < OPEN_TIMEOUT:
            if not self.running:
                return None
            for h in chrome_windows(titled_only=True):
                if h not in before and h not in taken:
                    return h
            time.sleep(0.03)
        return None

    # Phase 2: har Chrome mein extension icon dabao aur mode ka kaam karo
    def phase2(self):
        while self.pos < len(self.queue):
            if not self.running:
                self.say(f"Pause (agla Chrome: {self.queue[self.pos][0]})", "#ffb347")
                return
            num, name = self.queue[self.pos]
            self.highlight(num)
            hwnd = self.hwnds.get(num)
            if not hwnd:
                self.pos += 1          # window mili hi nahi thi, pehle hi dikkat mein likha hai
                continue
            self.say(f"Extension: {name}")
            try:
                problem = self.do_one(num, hwnd)
            except Exception as e:
                print(traceback.format_exc())
                problem = f"koi gadbad: {e}"
            if problem:
                self.problems.append((num, problem))
                write_log(f"Chrome {num} dikkat: {problem}")
            self.pos += 1

    def shot(self, ix, iy, s):
        return take_shot(int(ix + SHOT_DX * s), int(iy + SHOT_DY * s), int(SHOT_W * s), int(SHOT_H * s))

    def do_one(self, num, hwnd):
        if not bring_front_maximized(hwnd):
            return "window saamne nahi aayi"
        wait_rect_stable(hwnd)
        s = dpi_scale()

        popup = None
        ix = iy = None
        installed = False
        for _ in range(ICON_TRIES):
            if user32.GetForegroundWindow() != hwnd and not bring_front_maximized(hwnd):
                return "window saamne nahi rahi, click nahi kiya"
            pos = find_extension_icon(hwnd, s, self.icon_hint)       # jahan icon dikhe, wahin click
            if not pos and AUTO_INSTALL_EXTENSION and not installed:
                installed = True
                self.say(f"Chrome {num}: extension nahi mili, chrome://extensions se load kar raha hoon")
                err = self.install_extension(num, hwnd, s)
                if err:
                    self.say(f"Chrome {num}: install dobara koshish ({err})", "#ffb347")
                    time.sleep(0.5)
                    err = self.install_extension(num, hwnd, s)
                if err:
                    self.icon_hint = None
                    return "extension install nahi hui: " + err
                if user32.GetForegroundWindow() != hwnd:
                    bring_front_maximized(hwnd)
                time.sleep(0.5)
                pos = find_extension_icon(hwnd, s, None)
                if not pos:
                    return "extension load ho gayi par toolbar mein icon nahi dikha (puzzle icon se pin karo)"
            if not pos:
                self.icon_hint = None
                return "extension icon screen par nahi dikha, click nahi kiya"
            ix, iy = pos
            before = set(chrome_windows())
            click_at(ix, iy)
            popup = wait_popup(before, hwnd, ix, iy)
            if popup:
                self.icon_hint = pos            # agle Chrome mein pehle yahin dekhenge (tez)
                break
            self.icon_hint = None
        if not popup:
            return "icon dabane par popup nahi khula, aage ka kaam nahi kiya"

        time.sleep(self.settle())
        if self.cur_mode == "message":
            return self.work_message(num, popup, ix, iy, s)
        if self.cur_mode == "reminder":
            return self.work_reminder(num, popup, ix, iy, s)
        return self.work_members(num, popup, ix, iy, s)

    # ----- extension nahi hai to: chrome://extensions > Developer mode > Load unpacked > group-automation folder -----
    def extension_folder(self):
        home = os.path.expanduser("~")
        for base in (os.path.join(home, "Documents"), os.path.join(home, "OneDrive", "Documents")):
            p = os.path.join(base, EXT_FOLDER_NAME)
            if os.path.isdir(p):
                return os.path.abspath(p)
        return None

    def dev_toggle(self, hwnd, s):
        """Extensions page ka Developer mode toggle (kahin bhi ho: bookmarks bar / debugging patti ho ya na ho): (state, cx, cy).
        state = 'on' (neela) / 'off' (dhoosar kinara) / None (page abhi nahi dikha)."""
        l, tp, r, b = rect_tuple(hwnd)
        x0, y0 = int(r - 150 * s), int(tp + 92 * s)
        w, h = int(148 * s), int(300 * s)       # upar se 300 pixel tak: patti/bookmarks bar aane par toggle neeche khisakta hai
        h = min(h, user32.GetSystemMetrics(1) - y0)
        shot = take_shot(x0, y0, w, h) if h > 40 else None
        if not shot:
            return None, 0, 0
        best_blue = best_gray = best_fill = None            # (lambai, shuru x, y)
        min_b, min_g, min_f = 10 * s, 18 * s, 16 * s
        for y in range(y0, y0 + h):
            rb = rg = rf = 0
            sb = sg = sf = 0
            for x in range(x0, x0 + w + 1):
                c = shot.rgb(x, y) if x < x0 + w else None
                isf = c is not None and near(c, (225, 227, 225), 4)
                isb = c is not None and c[2] >= 170 and c[0] <= 60 and 50 <= c[1] <= 130
                isg = c is not None and near(c, (116, 119, 117), 30)
                if isb:
                    if rb == 0:
                        sb = x
                    rb += 1
                else:
                    if rb >= min_b and (best_blue is None or rb > best_blue[0]):
                        best_blue = (rb, sb, y)
                    rb = 0
                if isg:
                    if rg == 0:
                        sg = x
                    rg += 1
                else:
                    if rg >= min_g and (best_gray is None or rg > best_gray[0]):
                        best_gray = (rg, sg, y)
                    rg = 0
                if isf:
                    if rf == 0:
                        sf = x
                    rf += 1
                else:
                    if rf >= min_f and (best_fill is None or rf > best_fill[0]):
                        best_fill = (rf, sf, y)
                    rf = 0
        if best_blue:
            n, sx, y = best_blue
            return "on", sx + 16 * s, y
        if best_fill:
            n, sx, y = best_fill                # naya Chrome: dhoosar bhara hua track; uske upar ka hissa, beech 5 pixel neeche
            return "off", sx + n / 2.0, y + 5 * s
        if best_gray:
            n, sx, y = best_gray                # purana Chrome: toggle ke upar ki lakeer; beech uske 10 pixel neeche
            return "off", sx + n / 2.0, y + 10 * s
        return None, 0, 0

    def find_load_unpacked(self, hwnd, s):
        """Poori screen par (Chrome window ke andar) 'Load unpacked' button dhundo. Mila to (x, y) screen ka, warna None."""
        l, tp, r, b = rect_tuple(hwnd)
        sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        x0, y0 = max(0, int(l)), max(0, int(tp + 90 * s))
        w = int(min(640 * s, r - x0, sw - x0))
        h = int(min(460 * s, b - y0, sh - y0))
        if w < 150 or h < 60:
            return None
        buf = grab_region(x0, y0, w, h)
        if not buf:
            return None
        pos = find_load_unpacked_in(buf, w, h, s)
        if not pos:
            return None
        return x0 + pos[0], y0 + pos[1]

    def install_extension(self, num, hwnd, s):
        """Naye tab mein chrome://extensions kholo. Developer mode off ho to on karo, phir 'Load unpacked' button screen par
        jahan bhi dikhe wahin dabao aur group-automation folder chuno. Theek to None, warna dikkat ka text."""
        folder = self.extension_folder()
        if not folder:
            return f"Documents mein '{EXT_FOLDER_NAME}' folder nahi mila"
        if not bring_front_maximized(hwnd):
            return "window saamne nahi aayi"
        wait_rect_stable(hwnd)
        if user32.GetForegroundWindow() != hwnd:
            return "window saamne nahi rahi, keys nahi bheje"
        press_keys(VK_CONTROL, 0x54)            # Ctrl+T: naya tab (purana tab jaisa hai waisa rahe)
        time.sleep(0.4)
        press_keys(VK_CONTROL, 0x4C)            # Ctrl+L: address bar
        time.sleep(0.1)
        type_text("chrome://extensions/")
        time.sleep(0.05)
        press_keys(VK_RETURN)

        err = "chrome://extensions page ya Developer mode toggle / Load unpacked button nahi dikha"
        for attempt in range(3):
            # 1. Load unpacked dikh raha ho (Developer mode pehle se on) to seedha wahi dabao;
            #    nahi dikha to Developer mode dekho: off ho to on karo, on ho to button aane ka intezaar
            pos = None
            toggle_clicks = 0
            last_click = 0.0
            t = time.time()
            while time.time() - t < 12.0:
                if not user32.IsWindow(hwnd):
                    return "window beech mein band ho gayi"
                pos = self.find_load_unpacked(hwnd, s)
                if pos:
                    time.sleep(0.15)
                    pos2 = self.find_load_unpacked(hwnd, s)     # tham gaya? (page abhi khisak raha ho to dobara dekho)
                    if pos2 and abs(pos2[0] - pos[0]) <= 3 * s and abs(pos2[1] - pos[1]) <= 3 * s:
                        pos = pos2
                        break
                    pos = None
                    continue
                state, tx, ty = self.dev_toggle(hwnd, s)
                if state == "off" and time.time() - last_click > 2.0:      # pehle se on ho to us par click nahi karna
                    if toggle_clicks >= 3:
                        return "Developer mode on nahi ho raha (shayad organization ne roka hai)"
                    click_at(tx, ty)
                    toggle_clicks += 1
                    last_click = time.time()
                time.sleep(0.25)
            if not pos:
                err = "Load unpacked button screen par nahi dikha"
                continue
            err = self.choose_via_dialog(hwnd, pos[0], pos[1], folder, enter_twice=True)
            if not err:
                break
            time.sleep(0.5)
        if err:
            return "Load unpacked: " + err
        time.sleep(1.5)                         # extension load hone do
        if user32.IsWindow(hwnd):
            force_foreground(hwnd)
            time.sleep(0.15)
            press_keys(VK_CONTROL, 0x57)        # Ctrl+W: extensions wala tab band, pehle wale tab par wapas
            time.sleep(0.4)
        return None

    # ----- Message: tab -> Choose File -> us Chrome number ki Word file -----
    def work_message(self, num, popup, ix, iy, s):
        err = self.ensure_tab(popup, ix, iy, s, "message")
        if err:
            return err
        err, chose = self.ensure_file(num, popup, ix, iy, s)
        if err:
            return err
        if PRESS_START_AFTER_FILE:
            return self.press_start(num, popup, ix, iy, s, chose)
        return None

    # ----- Reminder (Word): tab -> Choose File -> us Chrome number ki re file -> Start -----
    def work_reminder(self, num, popup, ix, iy, s):
        err = self.ensure_tab(popup, ix, iy, s, "reminder")
        if err:
            return err
        err, chose = self.ensure_file(num, popup, ix, iy, s)
        if err:
            return err
        return self.press_start(num, popup, ix, iy, s, chose)

    # ----- Add Members: tab -> Excel file chuniye -> us Chrome number ki Id file -> halka scroll -> Start -----
    def work_members(self, num, popup, ix, iy, s):
        err = self.ensure_tab(popup, ix, iy, s, "members")
        if err:
            return err
        err = self.pick_excel(num, popup, ix, iy, s)
        if err:
            return err
        return self.press_start_members(num, popup, ix, iy, s)

    def members_shot(self, ix, iy, s):
        x0, y0 = int(ix + MEM_SHOT_DX * s), int(iy + 20 * s)
        h = min(int(620 * s), user32.GetSystemMetrics(1) - y0)
        return take_shot(x0, y0, int(MEM_SHOT_W * s), h) if h > 100 else None

    def pick_excel(self, num, popup, ix, iy, s):
        path = self.excel_files.get(self.rfno(num))
        if not path or not os.path.isfile(path):
            return f"{num} number ({self.file_label(self.rfno(num), 'members')}) ki Excel file nahi mili"
        x, y = ix + EXCEL_DX * s, iy + EXCEL_DY * s
        # bada neela "Excel file chuniye / badliye" button dikhne tak ruko (likhai se bachkar 3 jagah dekhte hain)
        seen = False
        t = time.time()
        while time.time() - t < 3.0:
            if not popup_alive(popup):
                return "popup beech mein band ho gaya"
            shot = self.shot(ix, iy, s)
            if shot and all(near(shot.rgb(x + dx * s, y - 12 * s), BLUE, 30) for dx in (-120, 0, 120)):
                seen = True
                break
            time.sleep(0.05)
        if not seen:
            return "Excel file wala neela button nahi dikha, file nahi chuni"
        self.say(f"Chrome {num}: {os.path.basename(path)} chun raha hoon")
        err = None
        for _ in range(2):
            if not inside_popup(popup, x, y):
                return "Excel button popup ke bahar hai, click nahi kiya"
            err = self.choose_via_dialog(popup, x, y, path)
            if not err:
                time.sleep(0.4)          # file padhi jane do
                return None
            if not popup_alive(popup):
                break
        return err

    def press_start_members(self, num, popup, ix, iy, s):
        wx, wy = ix + MEM_SCROLL_X * s, iy + MEM_SCROLL_Y * s
        if not inside_popup(popup, wx, wy):
            return "scroll ki jagah popup ke bahar hai, Start nahi dabaya"
        wheel_at(wx, wy, 2)              # halka sa scroll
        time.sleep(0.35)
        extra, last, stable, faded_since = 0, None, 0, None
        deadline = time.time() + 14
        while time.time() < deadline:
            if not popup_alive(popup):
                return "popup beech mein band ho gaya"
            shot = self.members_shot(ix, iy, s)
            r = find_members_start(shot, ix, iy, s) if shot else None
            if r is None:                # Start abhi poora nahi dikha: ek aur halka scroll
                last, stable = None, 0
                if extra < 6:
                    wheel_at(wx, wy, 1)
                    extra += 1
                    time.sleep(0.35)
                else:
                    time.sleep(0.1)
                continue
            kind, y, h = r
            stable = stable + 1 if (last is not None and abs(y - last) <= 1) else 0
            last = y
            if stable < 2:               # scroll tham jaye tab dabayenge
                time.sleep(0.08)
                continue
            if kind == "faded":          # file load hone par Start hara hona chahiye
                faded_since = faded_since or time.time()
                if time.time() - faded_since > 4.0:
                    return "Start dhundhla hai (file load nahi hui ya pehle se chal raha hai), click nahi kiya"
                time.sleep(0.15)
                continue
            x = ix + MEM_START_DX * s
            if not inside_popup(popup, x, y):
                return "Start ki jagah popup ke bahar hai, click nahi kiya"
            shot = None
            self.__dict__.setdefault("icons", {})[num] = (ix, iy)
            for attempt in (1, 2):
                click_at(x, y)
                self.popups[num] = popup
                self.start_times[num] = time.time()
                t = time.time()
                while time.time() - t < 1.5:
                    if not popup_alive(popup):
                        write_log(f"Chrome {num}: Start ke baad popup band ho gaya (kaam shuru maana)")
                        return None
                    shot = self.members_shot(ix, iy, s)
                    r2 = find_members_start(shot, ix, iy, s) if shot else None
                    if r2 is None or r2[0] == "faded":
                        write_log(f"Chrome {num}: Start dab gaya (koshish {attempt})")
                        return None
                    time.sleep(0.1)
                write_log(f"Chrome {num}: Start dabane ke baad bhi hara hi dikha (koshish {attempt})")
                save_debug_shot(f"chrome{num}_start_try{attempt}", shot)
            self.popups.pop(num, None)
            self.start_times.pop(num, None)
            return "Start 2 baar dabaya par button nahi badla"
        return "Start button hara nahi dikha, click nahi kiya"

    def ensure_tab(self, popup, ix, iy, s, want):
        """Chahiye wala tab (message / reminder / members) chuna hua ho. Theek to None, warna dikkat ka text."""
        label = TAB_LABEL[want]
        clicks = 0
        t = time.time()
        while time.time() - t < 6:
            if not popup_alive(popup):
                return "popup beech mein band ho gaya"
            shot = self.shot(ix, iy, s)
            st = tab_state(shot, ix, iy, s) if shot else None
            if st == want:
                return None
            if st is None:                      # popup abhi poora nahi dikha
                time.sleep(0.04)
                continue
            if clicks >= ICON_TRIES:
                break
            x = ix + TAB_CLICK_DX[want] * s
            y = iy + TAB_DY * s
            if not inside_popup(popup, x, y):
                return f"{label} tab ki jagah popup ke bahar hai, click nahi kiya"
            click_at(x, y)
            clicks += 1
            time.sleep(0.12)
        return f"{label} tab nahi khul paya"

    def ensure_file(self, num, popup, ix, iy, s):
        """Is Chrome number ki Word file attach ho. Return (dikkat ya None, file abhi chuni gayi ya nahi)."""
        if abs(s - 1.0) > 0.01:
            return "Windows scaling 100% nahi hai (Display settings mein 100% karo), file nahi chuni", False

        # 1. Choose File button dhundo (popup poora banne tak thoda intezaar)
        btn = None
        shot = None
        t = time.time()
        while time.time() - t < 2.5:
            if not popup_alive(popup):
                return "popup beech mein band ho gaya", False
            shot = self.shot(ix, iy, s)
            btn = find_choose_button(shot, ix, iy, s) if shot else None
            if btn:
                break
            time.sleep(0.04)
        if not btn:
            return "Choose File button nahi dikha, file nahi chuni", False
        bx, by = btn

        # 2. file pehle se attach hai? (likhai poori dikhne tak ruko)
        state = label_state(shot, bx, by)
        t = time.time()
        while state is None and time.time() - t < 1.5:
            time.sleep(0.04)
            shot = self.shot(ix, iy, s)
            b2 = find_choose_button(shot, ix, iy, s) if shot else None
            if b2:
                bx, by = b2
                state = label_state(shot, bx, by)
        if state is None:
            return "button ke saamne ki likhai samajh nahi aayi, file nahi chuni", False
        if state == "file" and self.cur_mode != "reminder":
            return None, False      # Reminder mein hamesha apni re-file dobara chunte hain (galat file na rahe)

        # 3. attach nahi hai: us Chrome number ki Word file chuno (poora path seedha likh dete hain)
        path = self.files_for(self.cur_mode).get(self.rfno(num))
        if not path or not os.path.isfile(path):
            return f"{num} number ({self.file_label(self.rfno(num), self.cur_mode)}) ki Word file nahi mili", False
        self.say(f"Chrome {num}: {os.path.basename(path)} chun raha hoon")
        err = None
        for _ in range(2):
            err = self.pick_file(popup, bx, by, path)
            if not err:
                err = self.wait_file_loaded(popup, ix, iy, s)
                if not err:
                    return None, True
            if not popup_alive(popup):
                break
        return err, False

    def pick_file(self, popup, bx, by, path):
        """Choose File dabao, dialog mein file ka poora path likho aur Enter. Dikkat ho to text, warna None."""
        return self.choose_via_dialog(popup, bx + BTN_W / 2, by + BTN_H / 2, path)

    def choose_via_dialog(self, popup, cx, cy, path, enter_twice=False):
        """(cx, cy) par click karo, file dialog mein poora path likho aur Enter. Dikkat ho to text, warna None."""
        dlg = None
        for _ in range(2):
            if not inside_popup(popup, cx, cy):
                return "Choose File button popup ke bahar hai, click nahi kiya"
            before = set(dialog_windows())
            click_at(cx, cy)
            t = time.time()
            while time.time() - t < 3.0 and not dlg:
                for h in dialog_windows():
                    if h not in before:
                        dlg = h
                        break
                time.sleep(0.02)
            if dlg:
                break
        if not dlg:
            return "file chunne wala dialog nahi khula"
        force_foreground(dlg)
        t = time.time()
        while time.time() - t < 1.0 and user32.GetForegroundWindow() != dlg:
            time.sleep(0.02)
        time.sleep(DIALOG_SETTLE)
        press_keys(VK_CONTROL, VK_A)
        type_text(path)
        time.sleep(0.06)
        press_keys(VK_RETURN)
        if enter_twice:
            time.sleep(1.0)
            if user32.IsWindow(dlg) and user32.IsWindowVisible(dlg):
                press_keys(VK_RETURN)       # folder mein ghus gaya ho to ab "Select Folder" ki tarah dabega
            time.sleep(1.0)
            if user32.IsWindow(dlg) and user32.IsWindowVisible(dlg):
                # Enter se bhi band nahi hua: "Select Folder" button par seedha click (dialog ke neeche-daayein kone mein)
                force_foreground(dlg)
                time.sleep(0.15)
                dl, dt, dr, db = rect_tuple(dlg)
                sc = dpi_scale()
                click_at(dr - SELECT_FOLDER_DX * sc, db - SELECT_FOLDER_DY * sc)
        t = time.time()
        while time.time() - t < 5.0 and user32.IsWindow(dlg) and user32.IsWindowVisible(dlg):
            time.sleep(0.03)
        if user32.IsWindow(dlg) and user32.IsWindowVisible(dlg):
            press_keys(VK_ESCAPE)         # atka hua dialog band karo
            return "file dialog band nahi hua (file nahi chuni gayi)"
        return None

    def wait_file_loaded(self, popup, ix, iy, s):
        """File chunne ke baad popup mein 'No file chosen' nahi dikhna chahiye."""
        t = time.time()
        while time.time() - t < 2.5:
            if not popup_alive(popup):
                return "file chunne ke baad popup band ho gaya"
            shot = self.shot(ix, iy, s)
            b2 = find_choose_button(shot, ix, iy, s) if shot else None
            if b2 and label_state(shot, b2[0], b2[1]) == "file":
                return None
            time.sleep(0.05)
        return "file chunne ke baad bhi popup mein 'No file chosen' dikha"

    def press_start(self, num, popup, ix, iy, s, chose):
        """Hara Start button dhundo aur ek baar dabao."""
        last = None
        stable = 0
        cy = None
        t = time.time()
        while time.time() - t < 4.0:
            if not popup_alive(popup):
                return "popup beech mein band ho gaya"
            shot = self.shot(ix, iy, s)
            r = find_start(shot, ix, iy, s) if shot else None
            if r is None:
                time.sleep(0.1)
                continue
            kind, y = r
            if kind == "faded":
                return "Start button dhundhla hai (shayad pehle se chal raha hai), click nahi kiya"
            # Start tab dabayein jab uski jagah 3 baar lagatar wahi dikhe (popup ka size tham gaya)
            stable = stable + 1 if (last is not None and abs(y - last) <= 1) else 0
            last = y
            if stable >= 2:
                cy = y
                break
            time.sleep(0.05)
        if cy is None:
            return "Start button hara nahi dikha, click nahi kiya"

        x = ix + START_DX * s
        if not inside_popup(popup, x, cy):
            return "Start ki jagah popup ke bahar hai, click nahi kiya"
        click_at(x, cy)               # Start sirf EK baar dabta hai
        # jaanch: Start ka rang badalna chahiye (ya popup band ho jaye)
        t = time.time()
        while time.time() - t < 1.0:
            if not popup_alive(popup):
                return None
            shot = self.shot(ix, iy, s)
            r = find_start(shot, ix, iy, s) if shot else None
            if r is None or r[0] == "faded":
                return None
            time.sleep(0.1)
        self.notes.append(num)
        return None

    def finish(self):
        self.running = False
        done = len(self.queue) - len(self.problems)
        total = len(self.queue)
        if self.auto_run:
            text = (f"Ho gaya. Folder poora: {self.batches} batch, {self.closed_count} Chrome 'Poora hua' ke baad band hue.")
            done, total = 0, 0

            def back():
                self.start_box.delete(0, "end")
                self.start_box.insert(0, str(self.run_start))
                self.refresh_list()
            self.ui(back)
        elif self.cur_mode == "members":
            text = f"Ho gaya. {done}/{total} Chrome mein Add Members ki Id file chuni aur Start dab gaya."
        elif self.cur_mode == "reminder":
            text = f"Ho gaya. {done}/{total} Chrome mein Reminder (Word) ki re file chuni aur Start dab gaya."
        elif PRESS_START_AFTER_FILE:
            text = f"Ho gaya. {done}/{total} Chrome mein Start dab gaya."
        else:
            text = f"Ho gaya. {done}/{total} Chrome mein Message tab khula aur Word file chun li gayi."
        color = "#3ddc97"
        if self.problems:
            nums = ", ".join(str(n) for n, _ in self.problems)
            why = "; ".join(f"{n}: {w}" for n, w in self.problems)
            text += f"\nDikkat wale (dobara chalana): {nums}\n{why}"
            color = "#ffa04d"
        if self.notes:
            text += "\nStart ke baad Start ka rang nahi badla, ek baar dekh lena: " + ", ".join(map(str, self.notes))
        write_log(text)
        self.say(text, color)
        self.reset_state()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        App(root)
        root.mainloop()
    except Exception:
        err = traceback.format_exc()
        try:
            with open(os.path.join(os.path.expanduser("~"), "ChromeOpener_error.txt"), "w", encoding="utf-8") as f:
                f.write(err)
            messagebox.showerror("Chrome Opener", "App chalu nahi hui. Error yahan likha hai:\n"
                                 + os.path.join(os.path.expanduser("~"), "ChromeOpener_error.txt"))
        except Exception:
            pass
