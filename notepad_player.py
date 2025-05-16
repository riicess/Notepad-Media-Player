import cv2
import numpy as np
import win32gui
import win32con
import time
import os
import traceback

CHAR_STYLES = {
    "classic_text": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "[::-1],
    "simple_text": "@%#*+=-:. "[::-1],
    "block_bw": "█▓▒░ "[::-1],
    "grade_text": "Ñ@#W$9876543210?!abc;:+=-,._ "[::-1],
    "minimal_text": "#=-. "[::-1]
}
DEFAULT_CHAR_STYLE_NAME = "block_bw"

PROFILES = {
    "standard_block_bw": {"width": 100, "art_style": "block_bw", "delay": 0.08, "char_aspect": 0.50, "center_canvas_width": 160},
    "detailed_block_bw": {"width": 180, "art_style": "block_bw", "delay": 0.05, "char_aspect": 0.48, "center_canvas_width": 280},
    "extreme_detail_block_bw": {"width": 245, "art_style": "block_bw", "delay": 0.01, "char_aspect": 0.42, "center_canvas_width": 1100},
    "max_fidelity_text_art": {"width": 160, "art_style": "classic_text", "delay": 0.04, "char_aspect": 0.45, "center_canvas_width": 250},
    "balanced_text_art": {"width": 100, "art_style": "classic_text", "delay": 0.07, "char_aspect": 0.50, "center_canvas_width": 160}
}

DEFAULT_ART_WIDTH = 100
DEFAULT_VIDEO_DELAY_S = 0.08
DEFAULT_CHAR_ASPECT_RATIO = 0.50
DEFAULT_NOTEPAD_TITLE = "Untitled - Notepad"
DEFAULT_CANVAS_WIDTH = 160

def get_notepad_handle(title):
    try:
        hwnd = win32gui.FindWindow(None, title)
        if hwnd == 0: print(f"Notepad '{title}' not found."); return None
        edit_hwnd = win32gui.FindWindowEx(hwnd, None, "Edit", None)
        if edit_hwnd == 0: print(f"Edit control not found in '{title}'."); return None
        return edit_hwnd
    except Exception as e: print(f"Find Notepad Error: {e}"); return None

def convert_image_to_art(image_frame, art_width, char_style_name, char_aspect, canvas_width=0):
    if image_frame is None: print("convert_image_to_art: null image_frame."); return ""
    char_set = CHAR_STYLES.get(char_style_name, CHAR_STYLES[DEFAULT_CHAR_STYLE_NAME])
    num_chars = len(char_set)
    original_height, original_width = image_frame.shape[:2]
    if original_width == 0 or original_height == 0 or art_width <= 0: return ""
    image_aspect = original_height / original_width
    new_height = int(art_width * image_aspect * char_aspect)
    if new_height <= 0: return ""
    try: resized_img = cv2.resize(image_frame, (art_width, new_height))
    except cv2.error as e: print(f"Resize Error: {e}"); return ""
    gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    raw_art_lines = []
    for i in range(new_height):
        line_chars = [' '] * art_width
        for j in range(art_width):
            intensity = gray_img[i, j]
            char_idx = min(int((intensity / 255) * num_chars), num_chars - 1)
            try: line_chars[j] = char_set[char_idx]
            except IndexError: line_chars[j] = '?'
        raw_art_lines.append("".join(line_chars))
    min_ink_col = art_width; max_ink_col = -1
    for line in raw_art_lines:
        stripped_line = line.lstrip()
        if stripped_line:
            current_left_ink = len(line) - len(stripped_line); min_ink_col = min(min_ink_col, current_left_ink)
            current_right_ink = len(line.rstrip()) - 1; max_ink_col = max(max_ink_col, current_right_ink)
    effective_content_lines = []; content_actual_width = 0
    if max_ink_col >= min_ink_col:
        content_actual_width = max_ink_col - min_ink_col + 1
        for line in raw_art_lines: effective_content_lines.append(line[min_ink_col : max_ink_col + 1])
    else: content_actual_width = art_width; effective_content_lines = raw_art_lines[:]
    if canvas_width > 0 and canvas_width > content_actual_width:
        padding = (canvas_width - content_actual_width) // 2
        padded_lines = [" " * padding + line for line in effective_content_lines]
        return "\n".join(padded_lines)
    else: return "\n".join(effective_content_lines)

def get_choice(prompt, options, allow_empty_default=None, default_val_key=None):
    print(prompt)
    keys = list(options.keys()) if isinstance(options, dict) else options
    display_names = [options[k] for k in keys] if isinstance(options, dict) else options
    for i, name in enumerate(display_names): print(f"  {i+1}. {name}")
    while True:
        inp_str = input(f"Choice (1-{len(keys)}){' or Enter for default' if allow_empty_default and default_val_key else ''}: ")
        if allow_empty_default and not inp_str and default_val_key: return default_val_key
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
                print(f"Value out of range ({min_val if min_val is not None else '-inf'} to {max_val if max_val is not None else 'inf'}).")
                continue
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
                print(f"Value out of range ({min_val if min_val is not None else '-inf'} to {max_val if max_val is not None else 'inf'}).")
                continue
            return val
        except ValueError: print("Invalid float.")

def get_config(media_type="video"):
    print(f"\n--- New {media_type.capitalize()} Setup ---")
    while True:
        f_path = input(f"Enter {media_type} file path: ")
        if f_path and os.path.exists(f_path): break
        elif not f_path: print("Path cannot be empty.")
        else: print(f"File not found: {f_path}")
    notepad_title = input(f"Notepad window title (default: '{DEFAULT_NOTEPAD_TITLE}'): ") or DEFAULT_NOTEPAD_TITLE
    cfg = {"media_type": media_type, "file_path": f_path,
           "width": DEFAULT_ART_WIDTH, "art_style": DEFAULT_CHAR_STYLE_NAME,
           "char_aspect": DEFAULT_CHAR_ASPECT_RATIO, "notepad_title": notepad_title,
           "center_canvas_width": DEFAULT_CANVAS_WIDTH}
    if media_type == "video": cfg["delay"] = DEFAULT_VIDEO_DELAY_S
    print("\n--- Art Style Profile ---")
    profile_disp = {k: f"{k} (Style:{'B&W Blocks' if 'block_bw' in k else 'Text Art'},W:{v['width']},Canvas:{v.get('center_canvas_width',0)})" for k,v in PROFILES.items()}
    profile_disp["custom"] = "custom"
    profile_disp["none"] = "none (defaults, then customize)"
    profile_key = get_choice("Select profile:", profile_disp)
    if profile_key in PROFILES:
        cfg.update(PROFILES[profile_key].copy())
        print(f"Applied profile: '{profile_key}'")
        # Remove suggested_zoom_percent if it was in profile, as we are not using it directly for user display
        cfg.pop('suggested_zoom_percent', None) 
        if media_type != "video" and "delay" in cfg: del cfg["delay"]
        elif media_type == "video" and "delay" not in cfg : cfg["delay"] = DEFAULT_VIDEO_DELAY_S
    elif profile_key == "custom":
        print("\n--- Custom Settings ---")
        cfg["width"] = get_int("Art width (chars)", cfg["width"], 10)
        style_disp = {k: f"{k} ({'B&W Blocks' if k=='block_shades_bw' else 'Text Art'}, {len(v)} chars)" for k,v in CHAR_STYLES.items()}
        cfg["art_style"] = get_choice("Art style/character set", style_disp, True, cfg["art_style"])
        if media_type == "video": cfg["delay"] = get_float("Video delay (s)", cfg.get("delay", DEFAULT_VIDEO_DELAY_S), 0.01)
        cfg["char_aspect"] = get_float("Char aspect (height factor)", cfg["char_aspect"], 0.1, 1.0)
        cfg["center_canvas_width"] = get_int("Center canvas width (0=none)", cfg["center_canvas_width"], 0)
    else: # "none"
        cfg["width"] = get_int(f"Art width (default: {cfg['width']})", cfg["width"], 10)
        cfg["center_canvas_width"] = get_int(f"Center canvas (0=none, default: {cfg['center_canvas_width']})", cfg["center_canvas_width"], 0)
        if media_type == "video": cfg["delay"] = get_float(f"Video delay (s, default: {cfg.get('delay', DEFAULT_VIDEO_DELAY_S)})", cfg.get("delay", DEFAULT_VIDEO_DELAY_S), 0.01)
    return cfg

def display_art_in_notepad_static(config, art_string):
    print("\n  DISPLAYING STATIC ART:")
    print("    ADVICE: Zoom Notepad In/Out (Ctrl+MouseWheel) until the art looks clear and fits well.")
    if config.get('center_canvas_width', 0) > 0 : print(f"    Art is designed for a canvas of {config.get('center_canvas_width',0)} chars; centering applied if wider than content.")
    else: print("    No centering padding applied.")
    if config.get('width',0) > 250: print("  WARNING: Art Width > 250 is extremely slow for Notepad!")
    edit_hwnd = get_notepad_handle(config["notepad_title"])
    if not edit_hwnd: print("  Notepad window not found."); return False
    try:
        win32gui.SetForegroundWindow(win32gui.GetParent(edit_hwnd)); time.sleep(0.2)
        win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, art_string)
        print("  Art sent to Notepad.")
        return True
    except Exception as e_send:
        if not win32gui.IsWindow(edit_hwnd): print("\n  Notepad closed.")
        else: print(f"\n  Error sending art: {e_send}")
        return False

def display_image(config):
    print(f"\n--- Processing Image: {config['file_path']} ---")
    try:
        img = cv2.imread(config["file_path"])
        if img is None: print(f"  Error reading image: '{config['file_path']}'."); return False
    except Exception as e: print(f"  Image read ERROR: {e}"); traceback.print_exc(); return False
    art_str = convert_image_to_art(img, config["width"], config["art_style"], config["char_aspect"], config["center_canvas_width"])
    if not art_str: print("  Error converting image to art."); return False
    return display_art_in_notepad_static(config, art_str)

def play_video(config):
    print("\n--- Video Playback ---")
    for k,v in config.items(): print(f"  {k.replace('_',' ').capitalize()}: {v}")
    print(f"  Art Style: '{config['art_style']}' ({len(CHAR_STYLES[config['art_style']])} chars)")
    print("\n  ADVICE: Zoom Notepad In/Out (Ctrl+MouseWheel) until the video looks clear and fits well.")
    print("          For detailed art (wide width settings), significant zoom-out is usually needed.")
    if config.get('width',0) > 180: print("  WARNING: Video Art Width > 180 is very slow!")
    edit_hwnd = get_notepad_handle(config["notepad_title"])
    if not edit_hwnd: print("  Notepad window not found."); return False
    cap = None
    try:
        cap = cv2.VideoCapture(config["file_path"])
        if not cap.isOpened(): print(f"  Error opening video: '{config['file_path']}'."); cap and cap.release(); return False
    except Exception as e: print(f"  Video open ERROR: {e}"); traceback.print_exc(); cap and cap.release(); return False
    try: win32gui.SetForegroundWindow(win32gui.GetParent(edit_hwnd)); time.sleep(0.2)
    except Exception: pass
    print(f"  Video Source FPS: {cap.get(cv2.CAP_PROP_FPS):.2f}")
    print("  Ctrl+C in console to stop.")
    frame_num = 0; proc_start_time = time.time(); video_done = False; op_success = True
    try:
        while True:
            ret, frame = cap.read()
            if not ret: video_done = True; print("\n  End of video."); break
            current_frame_start_time = time.time()
            art_str = convert_image_to_art(frame, config["width"], config["art_style"], config["char_aspect"], config["center_canvas_width"])
            if not art_str: time.sleep(config["delay"]); continue
            try: win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, 0, art_str)
            except Exception as e:
                if not win32gui.IsWindow(edit_hwnd): print("\n  Notepad closed.")
                else: print(f"\n  Error sending text: {e}")
                op_success = False; break 
            frame_num += 1; frame_proc_time = time.time() - current_frame_start_time
            sleep_for = config.get("delay", DEFAULT_VIDEO_DELAY_S) - frame_proc_time
            if sleep_for > 0: time.sleep(sleep_for)
            if frame_num % 10 == 0:
                elapsed_total = time.time()-proc_start_time; current_avg_fps = frame_num/elapsed_total if elapsed_total > 0 else 0
                lines=art_str.split('\n'); h=len(lines); w_sent=len(lines[0]) if h>0 else 0
                print(f"  Frame:{frame_num}, Sent:{w_sent}x{h} (ContentW:{config['width']}), ProcT:{frame_proc_time:.3f}s, AvgFPS:{current_avg_fps:.1f}")
    except KeyboardInterrupt: print("\n  Playback stopped."); op_success = False
    except Exception as e: print(f"\n  PLAYBACK ERROR: {e}"); traceback.print_exc(); op_success = False
    finally:
        if cap and cap.isOpened(): cap.release(); print("  Video resources released.")
        if video_done: print("  Playback finished.")
        elif not op_success and frame_num > 0 : print("  Playback interrupted/errored.")
        elif not op_success : print("  Playback failed/errored early.")
        return op_success or video_done

def main():
    last_cfg = None; first_run = True
    while True:
        next_op = None; current_cfg = None
        if first_run:
            print("\nNotepad Media Player")
            print("====================")
            print("Renders media as monochrome art in Notepad.")
            print("Advice:")
            print("ZOOM OUT in Notepad (Ctrl+MouseWheel or View menu) for detailed art until it looks clear and fits your window.")
            print("Adjust 'Center canvas width' in custom to match your zoomed Notepad view.\n")
            first_run = False; next_op = "Select Format"
        else:
            print("\n--- Main Menu ---")
            menu_options = {"new_video": "Play video", "new_image": "Display image"}
            if last_cfg: menu_options["retry"] = f"Retry last ({last_cfg.get('media_type','?')})"
            menu_options["close"] = "Close"
            next_op = get_choice("Choose action:", menu_options)
        if next_op == "Select Format":
             initial_menu = {"new_video": "Play video", "new_image": "Display image", "close": "Close"}
             next_op = get_choice("Select Format:", initial_menu)
        if next_op == "retry":
            if last_cfg: print(f"\nRetrying last {last_cfg['media_type']}..."); current_cfg = last_cfg
            else: print("\nNo previous action to retry."); continue
        elif next_op == "new_video": current_cfg = get_config(media_type="video")
        elif next_op == "new_image": current_cfg = get_config(media_type="image")
        elif next_op == "close": print("Exiting."); break
        else: print("Invalid action."); continue
        if current_cfg:
            op_ok = False
            if current_cfg["media_type"] == "video": op_ok = play_video(current_cfg)
            elif current_cfg["media_type"] == "image": op_ok = display_image(current_cfg)
            if op_ok: last_cfg = current_cfg.copy()
            else: print(f"Previous {current_cfg.get('media_type','operation')} not fully successful.")
        else: print("Configuration step failed or was skipped.")
    print("\nScript finished.")

if __name__ == "__main__":
    try: main()
    except Exception as e: print(f"\nCRITICAL SCRIPT ERROR: {type(e).__name__}: {e}"); traceback.print_exc()
    finally: print("\nExecution ended."); input("Press Enter to close console...")