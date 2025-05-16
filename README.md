# Notepad Player: See Videos & Images in Notepad!

Ever thought your trusty Windows Notepad could play videos or show pictures? Well, with this script, it kind of can! This program turns your videos and images into text-art and displays them right inside Notepad, creating a fun, retro, blocky effect.

Think of it as a quirky art project, not a replacement for your actual media player!

## What's Cool About It?

*   **Videos in Notepad:** Feed it a video file, and watch as Notepad tries its best to "play" it with text frames.
*   **Show Images in Notepad:** Open an image, and see it transformed into text or block art.
*   **Choose Your Style:**
    *   **Clean B&W Blocks:** This is the go-to for a clear, pixelated black and white look. Uses special block characters (`█▓▒░`).
    *   **Classic Text Art:** Uses a variety of regular text characters to create shades and shapes, like old-school ASCII art.
*   **Control the Look & Feel:**
    *   **Pre-set Profiles:** Jumpstart with settings for different looks:
        *   `standard_block_bw`: Good quality B&W blocks that are easy to view.
        *   `detailed_block_bw`: Finer B&W blocks. You'll want to zoom out in Notepad for this one!
        *   `extreme_detail_block_bw`: Super-duper detailed B&W blocks. You'll need to zoom WAAAY out in Notepad (like, a lot!) to see the whole picture.
        *   `max_fidelity_text_art`: For the most detailed art using regular text characters.
        *   `balanced_text_art`: A good all-around quality for text-based art.
    *   **Go Custom:** Want to fine-tune? You can set the art width (how many characters wide), pick the character style, and adjust how it's centered.
*   **Smart Centering:** The script does its best to center the main part of your image or video frame in Notepad.
*   **Easy to Use:** Just follow the on-screen prompts to get started.

## Super Important Tips!

*   **WINDOWS ONLY!** This script needs Windows to talk to Notepad.
*   **It's an Illusion, Not a Movie Player:** Expect slow, jerky "playback" for videos, especially if you choose high detail. This is for the cool, retro effect!
*   **ZOOM YOUR NOTEPAD!**
    *   For the detailed profiles (especially `detailed_block_bw` and `extreme_detail_block_bw`), you **MUST zoom out a lot** in Notepad. Use `Ctrl + Mouse Wheel Down` or go to Notepad's `View > Zoom` menu. Keep zooming out until the picture looks clear and fits your window.
    *   Experiment with zoom to find what looks best for any setting!

## Getting Started

**1. What You Need:**
    *   Python 3 (if you don't have it, get it from python.org)
    *   A Windows computer

**2. Install a Couple of Things:**
    *   Open your Command Prompt (search for "cmd" in your Start Menu).
    *   Type these commands one by one, and press Enter after each:
        ```bash
        pip install opencv-python
        pip install pywin32
        ```
    *   (If `pip` gives an error, you might need to check if Python was added to your system's PATH when you installed it. Sometimes `py -m pip install ...` works instead.)

**3. Get the Script:**
    *   Download the `notepad_player.py` file (or whatever you've named it) and save it to a folder on your computer (e.g., `C:\MyCoolScripts`).

**4. Let's Go!**
    *   **Open Notepad.** A fresh, blank one is perfect.
    *   **Go back to your Command Prompt.**
    *   Use the `cd` command to go to the folder where you saved the script. For example:
        ```bash
        cd C:\MyCoolScripts
        ```
    *   Now, run the script by typing:
        ```bash
        python notepad_player.py
        ```
    *   The script will start asking you questions. Just follow the prompts, pick your video or image, and choose your settings. Remember to adjust Notepad's zoom!

## Using the Script

1.  **First Choice:** Tell the script if you want to "play" a video or "show" an image.
2.  **Find Your File:** Give the script the full path to your video or image file (like `C:\Users\YourName\Pictures\cat.jpg`).
3.  **Notepad's Name:** Usually, "Untitled - Notepad" is fine. If your Notepad window has a different title (like "notes.txt - Notepad"), type that in.
4.  **Pick a Style (Profile):** Choose one of the cool pre-set art styles, or pick "custom" to tweak everything yourself.
5.  **Look at Notepad!** The magic (or, well, the text) will appear there.

After it's done, the script will ask if you want to:
*   **Retry:** Play/show the same thing again.
*   **New:** Pick a different file or change settings.
*   **Close:** Exit the script.

Have a blast making your Notepad do things it never thought it could!
