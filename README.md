# Notepad Player: Videos & Images in Notepad!
This script is a bit of a experiment that turns your Windows Notepad into a makeshift screen for videos, images, and even GIFs It converts them into text-art (or block-art)

> [!Important]
> I know, I know, others have probably done similar things. But hey, I built this one myself with Python, and it's been a blast!

It's not gonna replace your VLC player, obviously.

## Screenshots

![image](https://github.com/user-attachments/assets/5c34c6bd-f209-40ff-a201-b8fb40a11725)

https://github.com/user-attachments/assets/620824ac-cdf8-48ae-99d1-3f3f6883df47







## Features

*   **Videos, Images, GIFs:** Chuck a local file at it – `.mp4`, `.jpg`, `.png`, `.gif` – and see what happens.
*   **Image URLs Too:** Got a direct link to a JPG or PNG? It can try and grab that too.
*   **Drag and Drop Detection** You can Drag and Drop urls and files.
*   **Different "Art" Looks (Profiles):**
    *   **B&W Blocks:** This is usually the best for a clear, pixelated black and white picture using special block characters (`█▓▒░`). Comes in standard, detailed, and *extreme* detail (prepare to zoom!).
    *   **Dithered B&W Blocks:** A variation of the B&W blocks that uses a dithering technique to try and show more shades. Can look pretty cool!
    *   **Classic Text Art:** Uses a mix of normal keyboard characters to make the image, like old-school ASCII art.
*   **Profiles:**
    *   **Quick Profiles:** Pick a pre-set style and go!
    *   **Go Custom:** If you're feeling adventurous, you can control:
        *   How wide the art is (in characters).
        *   The character set or block style used.
        *   How the art is centered.
        *   *Content Cropping:* Decide if you want to "zoom in" on the main subject of a sparse image or show the whole original frame scaled down.
*   **Smart Centering:** Tries to put the art in the middle of your Notepad window.
*   **Drag and Drop:** In the menu, choose the "Dropped File/URL" option, then drag a file from Explorer (or an image URL from your browser) onto the black console window, press Enter, and it'll try to process it! You still get to pick the style.
*   **Easy Menu:** It's all run from the command line with simple numbered choices.

## Heads Up! - Super Important Tips

*   **WINDOWS ONLY!** this uses Windows to control Notepad.
*   **ZOOM YOUR NOTEPAD!** This is the **BIG ONE**.
    *   For any of the "detailed" or "extreme" profiles, you **HAVE TO ZOOM OUT A LOT** in Notepad. Like, way out. Use `Ctrl + Mouse Wheel Down` or Notepad's `View > Zoom` menu. Keep going until the picture actually looks like something and fits.
    *   Play around with Notepad's zoom for *any* setting to get the best look. What the script *sends* and what Notepad *shows* at different zoom levels can be very different.
*   **Font Choice in Notepad:** The B&W block styles usually look best with standard monospaced fonts like `Consolas` or `Courier New` (check Notepad's `Format > Font...` menu).

## Setup

**1. Stuff You Need:**
    *   Python 3 (from python.org if you don't have it).
    *   A Windows computer.

**2. Install Some Python Dependencies**
    *   Open your Command Prompt (search "cmd" in your Start Menu).
    *   Type these commands one by one, and hit Enter after each:
      ```
        pip install opencv-python,
        pip install pywin32,
        pip install requests
      ```
    *   *(If `pip` isn't working, you might need to make sure Python was added to your system PATH during its installation, or sometimes `py -m pip install ...` does the trick).*

**3. Grab the Script:**
    *   Download the `notepad_player.py` file (or whatever it's called).
    *   Or you can download the exe and start it there, you still need to download dependency libraries.
    *   Stick it in a folder somewhere easy to find, like `C:\NotepadPlayer`.

**4. Let's Fire It Up!**
    *   **Open Notepad.**
    *   **Go back to your Command Prompt.**
    *   Use the `cd` command to go to the folder where you put the script. For example:
        ```
        cd C:\NotepadFun
        ```
    *   Run the script by typing:
        ```
        python notepad_player.py
        ```
     * Or just run the .exe
    *   The script will start talking to you with on-screen prompts. Just follow along. And don't forget to play with Notepad's zoom!

## Using the Player

1.  **Pick Your Format** Choose if you're playing a video, showing an image from a file, an image from a URL, or using the drag-and-drop option.
2.  **Point to Your File/URL:**
    *   If it's a file, give the full path (like `C:\MyStuff\Videos\epic_cat_video.mp4`).
    *   If drag-and-drop, drag it onto the console when prompted and hit Enter.
3.  **Tell it Your Notepad's Name:** "Untitled - Notepad" usually works. If yours is different (like "my_masterpiece.txt - Notepad"), type that in.
4.  **Choose the Art Style (Profile):** Pick a pre-made style or go "custom" to get into the nitty-gritty.
5.  **Content Scaling:** Decide if you want the script to try and "crop" to the main subject of your image/video before turning it into art (good for making small things bigger) or if you want to use the whole original frame.
6.  **Watch Notepad!** The texty, blocky art will show up there.

When it's done, it'll ask if you want to:
*   **Retry:** Run the same thing again.
*   **New:** Choose a different file or mess with the settings.
*   **Close:** Shut it down.

Have fun!
