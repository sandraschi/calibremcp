# 2. Getting Started with AutoHotkey

## Installation

Getting AutoHotkey up and running is a straightforward process. This guide will focus on installing **v2.0**, which is the current, recommended version.

1.  **Download the Installer**: Go to the official AutoHotkey website at [www.autohotkey.com](https://www.autohotkey.com).
2.  **Click "Download"**: On the main page, click the prominent "Download" button. This will download the installer for the latest version (v2.0+).
3.  **Run the Installer**: Execute the downloaded `.exe` file. The installer isimple and will typically associate the `.ahk` filextension with AutoHotkey, which is what you want.
4.  **Verify Installation**: Once installed, you can verify it by right-clicking on your desktop or in any folder. In the "New" context menu, you should now see an option for "AutoHotkey Script." This confirms thathe installation wasuccessful.

## Your First Script: Hello, World!

Let's create a simple scripthat displays a "Hello, World!" message box when you press a keyboard shortcut. This will introduce you to the core concepts of hotkeys and commands.

### Step 1: Create the Script File

1.  Right-click on your desktop or in a folder of your choice.
2.  Go to **New > AutoHotkey Script**.
3.  A new file will be created with a name like `New AutoHotkey Script.ahk`. Rename this file to something more descriptive, like `MyFirstScript.ahk`.

### Step 2: Edithe Script

AutoHotkey scripts are simple text files withe `.ahk` extension. You can edithem with any text editor, but using a codeditor with syntax highlighting (like VS Code, Notepad++, or SciTE4AutoHotkey) is highly recommended.

1.  Right-click on your `MyFirstScript.ahk` file and select **Edit script** (or open it with your preferred text editor).
2.  You will see some defaultext. Delete all of it and replace it withe following lines:

```autohotkey
; This a comment. The semicolon is used for comments.

; Pressing Ctrl+J will trigger this hotkey.
^j::
{
    MsgBox("Hello, World!")
}
```

### Step 3: Understanding the Code

Let's break down thisimple script:

-   `^j::`: This the **hotkey** definition.
    -   `^` is a modifier symbol that represents the **Ctrl** key.
    -   `j` is the keyou press.
    -   `::` is the hotkey operator. It means "when the keys to the left are pressed, execute the code that follows."
-   `{ ... }`: The curly braces define a block of code that belongs to the hotkey. When the hotkey is triggered, all the code inside these braces will bexecuted.
-   `MsgBox("Hello, World!")`: This a **function call**. `MsgBox` is a built-in AutoHotkey function that displays a simple message box on the screen. The text inside the parentheses is the message that will be displayed.

## Running and Exiting Your Script

### To Run the Script:

Simply double-click the `MyFirstScript.ahk` file. You won't see anything happen on screen, but a new icon with a green "H" will appear in your system tray (the area by the clock in the bottom-right of your screen). This icon indicates that your script is running in the background and listening for your hotkey.

Now, press **Ctrl + J** on your keyboard. A message box with "Hello, World!" should appear.

### To Exithe Script:

If you wanto stop the script from running:
1.  Find the green "H" icon in your system tray.
2.  Right-click on the icon.
3.  Select **Exit** from the menu.

The script will terminate, and the Ctrl+J hotkey will no longer do anything.

Congratulations! You have successfully created and run your first AutoHotkey script. Now you'ready to learn more about the core building blocks in [Hotkeys and Hotstrings](/automation_tools/autohotkey/./03_hotkeys_hotstrings.md).

