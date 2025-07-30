# 3. Hotkeys and Hotstrings: The Core of AHK

Hotkeys and Hotstrings are the bread and butter of AutoHotkey. They are the simplest features to learn and provide the most immediate payoff in terms of productivity. Mastering them is the first major step to taking control of your workflow.

## Hotkeys: Your Custom Keyboard Shortcuts

A hotkey is a key or a combination of keys that, when pressed, executes a specific action. You've already created a simple one in the previous chapter (`^j`).

The syntax is `Modifiers & Key:: { Action }`.

### Modifier Symbols

AutoHotkey usespecial symbols to representhe modifier keys (Ctrl, Alt, Shift, Win). This makes defining hotkeys quick and readable.

| Symbol | Represents | Example | Description |
| :--- | :--- | :--- | :--- |
| `^` | Ctrl | `^j::` | Pressing Ctrl and J |
| `!` | Alt | `!n::` | Pressing Alt and N |
| `+` | Shift | `+F1::` | Pressing Shift and F1 |
| `#` | Win | `#e::` | Pressing the Windows key and E |

**Combining Modifiers:** You can combine these symbols to create more complex hotkeys.

```autohotkey
; Press Ctrl+Alt+To run this hotkey
^!t::
{
    ; The Run function launches a program or opens a file/website.
    Run("notepad.exe")
}

; Press Ctrl+Shift+Escape topen the Task Manager
^+Esc::
{
    Run("taskmgr")
}
```

### Context-Sensitive Hotkeys

One of AutoHotkey's most powerful features is the ability to make hotkeys that only work in specific windows. This prevents your custom shortcuts from interfering with other programs.

The `#HotIf` directive is used for this. You specify a condition, and all hotkeys defined below it will only fire if that condition is true.

```autohotkey
; This hotkey will ONLY work whenotepad is the active window.
#HotIf WinActive("ahk_class Notepad")

^s::
{
    ; This will send a different string instead of the normal Ctrl+Save command.
    Send("This hotkey only works inotepad!")
}

; It's good practice to resethe context when you're done.
#HotIf

; This hotkey works everywhere.
!s::
{
    MsgBox("This hotkey works in any window.")
}
```

-   `WinActive("ahk_class Notepad")` is a function that checks if the currently active window has the class name "Notepad". You can find a window's information using the "Window Spy" tool that comes with AutoHotkey.

--- 

## Hotstrings: Automated Text Expansion

A hotstring is a short piece of texthat, when typed, is automatically replaced by a longer piece of text. This incredibly useful for things you type frequently, like your email address, code snippets, or standard replies.

The syntax is `::trigger::replacement`.

### Basic Hotstrings

This the simplest form. You type the trigger text, and asoon as you type an ending character (like a space, period, or enter), it gets replaced.

```autohotkey
; Type "eml" and presspace to replace it with your email address.
::eml::my.email@example.com

; Useful for standard replies
::thx::Thank you for your inquiry. We will get back to you shortly.

; Can even be used for code snippets
::htmlskel::<!DOCTYPE html><html><head><title></title></head><body></body></html>
```

### Hotstring Options

You can customize a hotstring's behavior using options placed between the firstwo colons.

-   `*`: Thending character is not required. The replacement happens asoon as you type the trigger. `:*o:btw::by the way`
-   `?`: The hotstring will trigger even if it's inside another word. `:?o:alot::a lot`
-   `C`: Case-sensitive. The trigger must be typed with hexact case. `:Co:CEO::Chief Executive Officer`

```autohotkey
; No ending character needed. Type "btw" and it instantly becomes "by the way"
:*o:btw::by the way

; This will correct "alot" to "a lot" even if you type "alotofthings"
:?o:alot::a lot
```

Hotkeys and hotstrings are the foundation upon which most AutoHotkey scripts are built. In the next chapter, we will explore how to make your scripts more dynamic with [Variables and Expressions](/automation_tools/autohotkey/./04_variables_expressions.md).

