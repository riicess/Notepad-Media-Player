# rat!!!!

import cv2
import numpy as np
import win32gui
import win32con
import time
import os
import traceback
import requests
from io import BytesIO

CHAR_STYLES = {
    "classic_text": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "[::-1],
    "simple_text": "@%#*+=-:. "[::-1],
    "block_shades_bw": "███▓▓▒▒░░  "[::-1],
    "dithered_block_bw": "█▓▒░ ", 
    "grade_text": "Ñ@#W$9876543210?!abc;:+=-,._ "[::-1],
    "minimal_text": "#=-. "[::-1]
}
DEFAULT_CHAR_STYLE_NAME = "block_shades_bw"

PROFILES = {
    "standard_block_bw": {"width": 100, "art_style": "block_shades_bw", "char_aspect": 0.50, "center_canvas_width": 160},
    "dithered_standard_bw": {"width": 100, "art_style": "dithered_block_bw", "char_aspect": 0.50, "center_canvas_width": 160},
    "detailed_block_bw": {"width": 180, "art_style": "block_shades_bw", "char_aspect": 0.48, "center_canvas_width": 280},
    "dithered_detailed_bw": {"width": 180, "art_style": "dithered_block_bw", "char_aspect": 0.48, "center_canvas_width": 280},
    "extreme_detail_block_bw": {"width": 245, "art_style": "block_shades_bw", "char_aspect": 0.42, "center_canvas_width": 1100},
    "dithered_extreme_bw": {"width": 245, "art_style": "dithered_block_bw", "char_aspect": 0.42, "center_canvas_width": 1100},
    "max_fidelity_text_art": {"width": 160, "art_style": "classic_text", "char_aspect": 0.45, "center_canvas_width": 250},
    "balanced_text_art": {"width": 100, "art_style": "classic_text", "char_aspect": 0.50, "center_canvas_width": 160}
}

DEFAULT_ART_WIDTH = 100
DEFAULT_VIDEO_DELAY_S = 0.08
DEFAULT_CHAR_ASPECT_RATIO = 0.50
DEFAULT_NOTEPAD_TITLE = "Untitled - Notepad"
DEFAULT_CANVAS_WIDTH = 160
DEFAULT_GIF_FRAME_SKIP = 1

def get_notepad_handle(title):
    try:
        hwnd = win32gui.FindWindow(None, title)
        if hwnd == 0: print(f"Notepad '{title}' not found."); return None
        edit_hwnd = win32gui.FindWindowEx(hwnd, None, "Edit", None)
        if edit_hwnd == 0: print(f"Edit control not found in '{title}'."); return None
        return edit_hwnd
    except Exception as e: print(f"Find Notepad Error: {e}"); return None

def floyd_steinberg_dither(image_gray):
    dither_palette_chars = ['█', '▓', '▒', '░', ' '] 
    dither_palette_values = np.linspace(0, 255, len(dither_palette_chars), dtype=np.float32)
    img_dithered = image_gray.astype(np.float32)
    h, w = img_dithered.shape
    output_art_lines = []
    for y in range(h):
        line_chars = [' '] * w 
        for x in range(w):
            old_pixel = img_dithered[y, x]
            diffs = np.abs(dither_palette_values - old_pixel)
            closest_palette_idx = np.argmin(diffs)
            chosen_char_value = dither_palette_values[closest_palette_idx]
            line_chars[x] = dither_palette_chars[closest_palette_idx]
            quant_error = old_pixel - chosen_char_value
            if x + 1 < w: img_dithered[y, x + 1] += quant_error * 7 / 16
            if y + 1 < h:
                if x - 1 >= 0: img_dithered[y + 1, x - 1] += quant_error * 3 / 16
                img_dithered[y + 1, x] += quant_error * 5 / 16
                if x + 1 < w: img_dithered[y + 1, x + 1] += quant_error * 1 / 16
        output_art_lines.append("".join(line_chars))
    return output_art_lines

def convert_image_to_art(original_image_frame, target_art_width, char_style_name, 
                         char_aspect_ratio_for_font, canvas_width_for_centering=0, 
                         crop_to_content=True):
    if original_image_frame is None: print("convert_image_to_art: null image_frame."); return ""
    image_to_process = original_image_frame
    if crop_to_content:
        gray_original = cv2.cvtColor(original_image_frame, cv2.COLOR_BGR2GRAY)
        _ , thresh_original = cv2.threshold(gray_original, 220, 255, cv2.THRESH_BINARY_INV) 
        contours, _ = cv2.findContours(thresh_original, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            all_points = np.concatenate(contours)
            x, y, w, h = cv2.boundingRect(all_points)
            if w > 5 and h > 5: image_to_process = original_image_frame[y : y + h, x : x + w]
    content_h, content_w = image_to_process.shape[:2]
    if content_w == 0 or content_h == 0 or target_art_width <= 0: return ""
    content_aspect_ratio = content_h / content_w
    art_height = int(target_art_width * content_aspect_ratio * char_aspect_ratio_for_font)
    if art_height <= 0: art_height = 1
    try: scaled_content_img = cv2.resize(image_to_process, (target_art_width, art_height))
    except cv2.error as e: print(f"Resize Error (scaled content): {e}"); return ""
    gray_scaled_content = cv2.cvtColor(scaled_content_img, cv2.COLOR_BGR2GRAY)
    art_lines = []
    if char_style_name == "dithered_block_bw":
        art_lines = floyd_steinberg_dither(gray_scaled_content)
    else:
        char_set = CHAR_STYLES.get(char_style_name, CHAR_STYLES[DEFAULT_CHAR_STYLE_NAME])
        num_chars_in_set = len(char_set)
        for i in range(art_height):
            line_chars = [' '] * target_art_width
            for j in range(target_art_width):
                intensity = gray_scaled_content[i, j]
                char_idx = min(int((intensity / 255) * num_chars_in_set), num_chars_in_set - 1)
                try: line_chars[j] = char_set[char_idx]
                except IndexError: line_chars[j] = '?'
            art_lines.append("".join(line_chars))
    if canvas_width_for_centering > 0 and canvas_width_for_centering > target_art_width:
        padding = (canvas_width_for_centering - target_art_width) // 2
        padded_lines = [" " * padding + line for line in art_lines]
        return "\n".join(padded_lines)
    else: return "\n".join(art_lines)

def get_choice(prompt, options, allow_empty_default=None, default_val_key=None):
    print(prompt)
    keys = list(options.keys()) if isinstance(options, dict) else options
    display_names = [options[k] for k in keys] if isinstance(options, dict) else options
    for i, name in enumerate(display_names): print(f"  {i+1}. {name}")
    while True:
        inp_str = input(f"Choice (1-{len(keys)}){' or Enter for default' if allow_empty_default and default_val_key else ''}: ")
        if allow_empty_default and not inp_str and default_val_key:
            if isinstance(options, dict): return next((k for k,v_disp in options.items() if v_disp == default_val_key or k == default_val_key), default_val_key)
            return default_val_key
        try:
            num = int(inp_str)
            if 1 <= num <= len(keys): return keys[num-1]
            else: print("Invalid selection number.")
        except ValueError: print("Invalid input. Number expected.")

def get_int(prompt, default, min_val=None, max_val=None):
    while True:
        inp = input(f"{prompt} (default: {default}): ")
        if not inp: return default
        try:
            val = int(inp)
            if (min_val is not None and val < min_val) or \
               (max_val is not None and val > max_val):
                print(f"Value out of range ({min_val or '-inf'} to {max_val or 'inf'})."); continue
            return val
        except ValueError: print("Invalid integer.")

def get_float(prompt, default, min_val=None, max_val=None):
    while True:
        inp = input(f"{prompt} (default: {default}): ")
        if not inp: return default
        try:
            val = float(inp)
            if (min_val is not None and val < min_val) or \
               (max_val is not None and val > max_val):
                print(f"Value out of range ({min_val or '-inf'} to {max_val or 'inf'})."); continue
            return val
        except ValueError: print("Invalid float.")

def get_bool_input(prompt_text, default_val_bool):
    default_display = "yes" if default_val_bool else "no"
    while True:
        val_str = input(f"{prompt_text} (yes/no, default: {default_display}): ").lower()
        if not val_str: return default_val_bool
        if val_str in ["yes", "y"]: return True
        if val_str in ["no", "n"]: return False
        print("Invalid input. Please enter 'yes' or 'no'.")

def get_config(media_type="video", source_type="file", pre_filled_path_or_url=None):
    print(f"\n--- New {media_type.capitalize()} from {source_type.capitalize()} Setup ---")
    path_or_url = pre_filled_path_or_url
    if path_or_url is None:
        prompt_suffix = "(videos, images, gifs)" if media_type == "video" else "(images)"
        if source_type == "file":
            while True:
                path_or_url = input(f"Enter {media_type} file path {prompt_suffix}: ")
                if path_or_url and os.path.exists(path_or_url): break
                elif not path_or_url: print("Path cannot be empty.")
                else: print(f"File not found: {path_or_url}")
        elif source_type == "url":
            while True:
                path_or_url = input(f"Enter direct URL to {media_type} {prompt_suffix}: ")
                if path_or_url.lower().startswith(("http://", "https://")): break
                else: print("Invalid URL format.")
    else: print(f"  Processing item: {path_or_url}")
    notepad_title = input(f"Notepad window title (default: '{DEFAULT_NOTEPAD_TITLE}'): ") or DEFAULT_NOTEPAD_TITLE
    cfg = {"media_type": media_type, "source_type": source_type, "file_path": path_or_url,
           "width": DEFAULT_ART_WIDTH, "art_style": DEFAULT_CHAR_STYLE_NAME,
           "char_aspect": DEFAULT_CHAR_ASPECT_RATIO, "notepad_title": notepad_title,
           "center_canvas_width": DEFAULT_CANVAS_WIDTH, "loop_gif": False, 
           "gif_frame_skip": DEFAULT_GIF_FRAME_SKIP}
    if media_type == "video": cfg["delay"] = DEFAULT_VIDEO_DELAY_S
    print("\n--- Art Style Profile ---")
    profile_disp = {k: f"{k} (Style:{'Dithered B&W' if k.startswith('dithered') else ('B&W Blocks' if 'block_bw' in k else 'Text Art')},W:{v['width']},Canvas:{v.get('center_canvas_width',0)})" for k,v in PROFILES.items()}
    profile_disp["custom"] = "custom"; profile_disp["none"] = "none (defaults, then customize)"
    profile_key = get_choice("Select profile:", profile_disp)
    if profile_key in PROFILES:
        profile_settings = PROFILES[profile_key].copy()
        profile_settings.pop('delay', None) 
        cfg.update(profile_settings)
        print(f"Applied profile: '{profile_key}'")
    elif profile_key == "custom":
        print("\n--- Custom Art Settings ---")
        cfg["width"] = get_int("Art width (chars)", cfg["width"], 10)
        style_disp = {k: f"{k} ({'Dithered B&W' if k=='dithered_block_bw' else ('B&W Blocks' if k=='block_shades_bw' else 'Text Art')}, {len(v)} chars)" for k,v in CHAR_STYLES.items()}
        cfg["art_style"] = get_choice("Art style/character set", style_disp, True, cfg["art_style"])
        cfg["char_aspect"] = get_float("Char aspect (height factor)", cfg["char_aspect"], 0.1, 1.0)
        cfg["center_canvas_width"] = get_int("Center canvas width (0=none)", cfg["center_canvas_width"], 0)
    else: # "none"
        cfg["width"] = get_int(f"Art width (default: {cfg['width']})", cfg["width"], 10)
        style_disp = {k: f"{k} ({'Dithered B&W' if k=='dithered_block_bw' else ('B&W Blocks' if k=='block_shades_bw' else 'Text Art')}, {len(v)} chars)" for k,v in CHAR_STYLES.items()}
        cfg["art_style"] = get_choice("Art style/character set", style_disp, True, cfg["art_style"])
        cfg["char_aspect"] = get_float(f"Char aspect (default: {cfg['char_aspect']})", cfg["char_aspect"], 0.1, 1.0)
        cfg["center_canvas_width"] = get_int(f"Center canvas (0=none, default: {cfg['center_canvas_width']})", cfg["center_canvas_width"], 0)
    if media_type == "video":
        cfg["delay"] = get_float(f"Video/GIF delay (s) (default: {cfg.get('delay', DEFAULT_VIDEO_DELAY_S)})", cfg.get("delay", DEFAULT_VIDEO_DELAY_S), 0.01)
        if path_or_url.lower().endswith(".gif"):
            print("\n--- GIF Playback Options ---")
            cfg["loop_gif"] = get_bool_input("Loop GIF playback?", True)
            cfg["gif_frame_skip"] = get_int("Process every Nth frame for this GIF? (1=all)", DEFAULT_GIF_FRAME_SKIP, min_val=1)
    print("\n--- Content Scaling ---")
    crop_options = {"yes_crop": "Yes - Crop to main content, then scale (makes sparse content larger).",
                    "no_crop":  "No  - Scale the entire original frame (preserves full composition)."}
    suggest_crop_default = "yes_crop"
    crop_choice = get_choice("Attempt to crop to main content before scaling to Art Width?", crop_options, True, suggest_crop_default)
    cfg["crop_to_content"] = True if crop_choice == "yes_crop" else False
    return cfg

def display_art_in_notepad_static(config, art_string):
    print("\n  DISPLAYING STATIC ART:")
    print("    ADVICE: Zoom Notepad In/Out (Ctrl+MouseWheel) until art looks clear and fits well.")
    if config.get('center_canvas_width', 0) > 0 : print(f"    Art content centered in canvas of {config.get('center_canvas_width',0)} chars if wider.")
    else: print("    No centering padding applied.")
    if config.get('width',0) > 250: print("  WARNING: Art Width > 250 is slow for Notepad!")
    edit_hwnd = get_notepad_handle(config["notepad_title"])
    if not edit_hwnd: print("  Notepad window not found."); return False
    try:
        win32gui.SetForegroundWindow(win32gui.GetParent(edit_hwnd)); time.sleep(0.2)
        win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, art_string)
        print("  Art sent to Notepad.")
        return True
    except Exception as e:
        if not win32gui.IsWindow(edit_hwnd): print("\n  Notepad closed.")
        else: print(f"\n  Error sending art: {e}")
        return False

def fetch_image_from_url(url):
    print(f"  Fetching image from URL: {url}")
    try:
        response = requests.get(url, stream=True, timeout=15)
        response.raise_for_status()
        image_bytes = BytesIO(response.content)
        image_np = np.frombuffer(image_bytes.read(), np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        if image is None: print("  Error decoding image from URL."); return None
        print("  Image fetched and decoded."); return image
    except requests.exceptions.RequestException as e: print(f"  URL fetch Error: {e}"); return None
    except Exception as e: print(f"  Image URL processing Error: {e}"); return None

def display_single_media(config):
    print(f"\n--- Processing Single {config['media_type'].capitalize()}: {config['file_path']} ---")
    image_data = None
    if config["source_type"] == "file":
        try:
            image_data = cv2.imread(config["file_path"])
            if image_data is None: print(f"  Error reading image file: '{config['file_path']}'."); return False
        except Exception as e: print(f"  Image file read ERROR: {e}"); traceback.print_exc(); return False
    elif config["source_type"] == "url" and config["media_type"] == "image":
        image_data = fetch_image_from_url(config["file_path"])
        if image_data is None: return False
    else: print(f"  Unsupported source/media for single display: {config['source_type']}/{config['media_type']}"); return False
    art_str = convert_image_to_art(image_data, config["width"], config["art_style"], 
                                 config["char_aspect"], config["center_canvas_width"], 
                                 config["crop_to_content"])
    if not art_str: print("  Error converting to art."); return False
    return display_art_in_notepad_static(config, art_str)

def play_video(config):
    print("\n--- Video Playback ---")
    for k,v in config.items(): print(f"  {k.replace('_',' ').capitalize()}: {v}")
    print(f"  Art Style: '{config['art_style']}' ({len(CHAR_STYLES[config['art_style']])} chars)")
    print(f"\n  ADVICE: Zoom Notepad In/Out until video looks clear and fits well.")
    if config.get('width',0) > 180: print("  WARNING: Video Art Width > 180 is very slow!")

    edit_hwnd = get_notepad_handle(config["notepad_title"])
    if not edit_hwnd: print("Notepad window not found."); return False
    
    cap = None; video_source = config["file_path"]
    is_gif = video_source.lower().endswith(".gif")
    loop_this_gif = config.get("loop_gif", False) and is_gif
    frame_skip = config.get("gif_frame_skip", 1) if is_gif else 1
    if frame_skip < 1: frame_skip = 1

    if config["source_type"] == "url": print(f"  Attempting to stream video from URL: {video_source} (EXPERIMENTAL)")
    
    try:
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened(): print(f"  Error opening video/gif source: '{video_source}'."); cap and cap.release(); return False
    except Exception as e: print(f"  Video/gif open ERROR: {e}"); traceback.print_exc(); cap and cap.release(); return False
    
    try: win32gui.SetForegroundWindow(win32gui.GetParent(edit_hwnd)); time.sleep(0.2)
    except Exception: pass
    
    source_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"  Source FPS: {source_fps:.2f} (GIFs may report 0 or inaccurate FPS)")
    if is_gif:
        if loop_this_gif: print("  GIF Looping: ENABLED")
        if frame_skip > 1: print(f"  GIF Frame Skip: Processing 1 of every {frame_skip} frames")
    print("  Ctrl+C in console to stop.")
    
    gif_art_cache = [] # pmo
    processed_gif_once = False

    frame_num_processed = 0; frame_num_read = 0
    proc_start_time = time.time(); video_done = False; op_success = True
    
    try:
        while True: 
            if is_gif and loop_this_gif and processed_gif_once and gif_art_cache:
                # Loop from cache
                print("  Looping GIF from cache...")
                for art_str in gif_art_cache:
                    if not win32gui.IsWindow(edit_hwnd): print("\n  Notepad closed."); op_success = False; break
                    try: win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, art_str)
                    except Exception as e: print(f"\n  Error sending cached text: {e}"); op_success=False; break
                    time.sleep(config.get("delay", DEFAULT_VIDEO_DELAY_S))
                    frame_num_processed +=1
                    if frame_num_processed % (10 * (len(gif_art_cache) // 10 or 1) ) == 0:
                         print(f"  Cached Loop Frame: {frame_num_processed}")
                if not op_success: break
                time.sleep(0.1)
                continue 

            frame_num_read_this_pass = 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            if is_gif and loop_this_gif and not processed_gif_once: gif_art_cache = []

            while True:
                ret, frame = cap.read()
                frame_num_read += 1
                frame_num_read_this_pass +=1
                if not ret: 
                    if is_gif and loop_this_gif:
                        processed_gif_once = True
                        break
                    else: video_done = True; print("\n  End of video/gif."); break
                
                if frame_skip > 1 and ((frame_num_read_this_pass -1) % frame_skip != 0):
                    continue 

                current_frame_start_time = time.time()
                art_str = convert_image_to_art(frame, config["width"], config["art_style"], 
                                               config["char_aspect"], config["center_canvas_width"],
                                               config["crop_to_content"])
                if not art_str: time.sleep(config["delay"]); continue

                if is_gif and loop_this_gif and not processed_gif_once:
                    gif_art_cache.append(art_str)

                try: win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, art_str)
                except Exception as e:
                    if not win32gui.IsWindow(edit_hwnd): print("\n  Notepad closed.")
                    else: print(f"\n  Error sending text: {e}")
                    op_success = False; break 
                
                frame_num_processed += 1
                frame_proc_time = time.time() - current_frame_start_time
                sleep_for = config.get("delay", DEFAULT_VIDEO_DELAY_S) - frame_proc_time
                if sleep_for > 0: time.sleep(sleep_for)
                
                if frame_num_processed % 10 == 0:
                    elapsed_total=time.time()-proc_start_time; current_avg_fps=frame_num_processed/elapsed_total if elapsed_total > 0 else 0
                    lines=art_str.split('\n'); h=len(lines); w_sent=len(lines[0]) if h>0 else 0
                    print(f"  Frame:{frame_num_processed}(read:{frame_num_read}), Sent:{w_sent}x{h} (ContentW:{config['width']}), ProcT:{frame_proc_time:.3f}s, AvgFPS:{current_avg_fps:.1f}")
            
            if video_done or not op_success: 
            break 
    except KeyboardInterrupt: print("\n  Playback stopped."); op_success = False
    except Exception as e: print(f"\n  PLAYBACK ERROR: {e}"); traceback.print_exc(); op_success = False
    finally:
        if cap and cap.isOpened(): cap.release(); print("  Video/gif resources released.")
        if video_done and not loop_this_gif : print("  Playback finished normally.")
        elif loop_this_gif and op_success and processed_gif_once: print("  GIF Looping finished/interrupted.")
        elif not op_success and frame_num_processed > 0 : print("  Playback interrupted/errored.")
        elif not op_success : print("  Playback failed/errored early.")
        return op_success or video_done


def process_dropped_input_and_get_config(dropped_text, current_notepad_title=None):
    print(f"\n--- Processing Dropped Item: '{dropped_text[:100]}{'...' if len(dropped_text)>100 else ''}' ---")
    path_or_url = dropped_text.strip().strip('"')
    source_type = ""; media_type = ""
    if path_or_url.lower().startswith(("http://", "https://")):
        source_type = "url"
        if any(vid_ext in path_or_url.lower() for vid_ext in ['.mp4', '.mkv', '.avi', '.mov', '.gif']):
            media_type = "video"; print(f"  Detected URL, looks like video/gif (EXPERIMENTAL): {path_or_url}")
        else: media_type = "image"; print(f"  Detected URL (assuming image): {path_or_url}")
    elif os.path.exists(path_or_url):
        source_type = "file"; _, ext = os.path.splitext(path_or_url.lower())
        if ext in ['.jpg','.jpeg','.png','.bmp','.tiff','.webp']: media_type = "image"
        elif ext in ['.mp4','.avi','.mkv','.mov','.flv','.wmv', '.gif']: media_type = "video"
        else: print(f"  Unrecognized file extension '{ext}'. Assuming image."); media_type = "image"
        print(f"  Detected local file: {path_or_url} (Type: {media_type})")
    else: print(f"  Error: Dropped item not valid URL or file path: '{path_or_url}'"); return None
    return get_config(media_type=media_type, source_type=source_type, pre_filled_path_or_url=path_or_url)


def main():
    last_cfg = None; first_run = True
    current_notepad_title_for_drag_drop = DEFAULT_NOTEPAD_TITLE
    while True:
        next_op = None; current_cfg = None
        if first_run:
            print("\nNotepad Media Player"); print("====================")
            print("Renders media as monochrome art in Notepad.")
            print("ADVICE: ZOOM OUT in Notepad (Ctrl+MouseWheel) for detailed art.")
            print("        Match 'Center canvas width' to your zoomed Notepad view.\n")
            first_run = False; next_op = "initial_choice"
        else:
            print("\n--- Main Menu ---")
            menu_options = {"new_video_file": "Play video/gif (File)", "new_image_file": "Display image (File)",
                            "new_image_url": "Display image (URL)", "new_video_url": "Play video/gif (URL - Experimental)",
                            "drag_drop": "Process Dropped File/URL"}
            if last_cfg: menu_options["retry"] = f"Retry last ({last_cfg.get('media_type','?')} from {last_cfg.get('source_type','?')})"
            menu_options["close"] = "Close"
            next_op = get_choice("Choose action:", menu_options)
        if next_op == "initial_choice":
             initial_menu = {"new_video_file": "Play video/gif (File)", "new_image_file": "Display image (File)",
                             "new_image_url": "Display image (URL)", "new_video_url": "Play video/gif (URL - Exp.)",
                             "drag_drop": "Process Dropped File/URL", "close": "Close"}
             next_op = get_choice("Initial action:", initial_menu)
        if next_op == "retry":
            if last_cfg: print(f"\nRetrying last {last_cfg['media_type']} from {last_cfg['source_type']}..."); current_cfg = last_cfg
            else: print("\nNo previous action to retry."); continue
        elif next_op == "new_video_file": current_cfg = get_config(media_type="video", source_type="file")
        elif next_op == "new_image_file": current_cfg = get_config(media_type="image", source_type="file")
        elif next_op == "new_image_url": current_cfg = get_config(media_type="image", source_type="url")
        elif next_op == "new_video_url": current_cfg = get_config(media_type="video", source_type="url")
        elif next_op == "drag_drop":
            dropped_text = input("Drag a file/URL onto the console, then press Enter: ")
            if dropped_text:
                current_cfg = process_dropped_input_and_get_config(dropped_text, current_notepad_title_for_drag_drop)
                if current_cfg: current_notepad_title_for_drag_drop = current_cfg["notepad_title"]
            else: print("No input for drag and drop."); continue
        elif next_op == "close": print("Exiting."); break
        else: print("Invalid action."); continue
        if current_cfg:
            op_ok = False
            if current_cfg["media_type"] == "video": op_ok = play_video(current_cfg)
            elif current_cfg["media_type"] == "image": op_ok = display_single_media(current_cfg)
            if op_ok: last_cfg = current_cfg.copy()
            else: print(f"Previous {current_cfg.get('media_type','operation')} from {current_cfg.get('source_type','?')} not fully successful.")
        elif next_op == "drag_drop" and not current_cfg : pass
        else: print("Configuration failed or was skipped.")
    print("\nScript finished.")

if __name__ == "__main__":
    try: main()
    except Exception as e: print(f"\nCRITICAL SCRIPT ERROR: {type(e).__name__}: {e}"); traceback.print_exc()
    finally: print("\nExecution ended."); input("Press Enter to close console...")
