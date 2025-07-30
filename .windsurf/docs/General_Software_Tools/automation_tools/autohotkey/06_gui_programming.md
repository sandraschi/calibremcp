# 6. GUI Programming: Giving Your Scripts a Face

While hotkeys are great for background tasks, sometimes you need a way to interact with your script more directly. AutoHotkey allows you to create your own custom Graphical User Interfaces (GUIs) with windows, buttons, text boxes, and other controls. This opens up a whole neworld of possibilities for creating user-friendly, interactive tools.

## Creating Your First GUI

Creating a GUInvolves a few simple steps:
1.  Create a GUI object.
2.  Add controls (like text and buttons) to it.
3.  Define what happens when a user interacts with a control (e.g., clicks a button).
4.  Show the GUI window.

Here is a very basic example:

```autohotkey
; 1. Create a new GUI object.
MyGui := Gui("My First GUI", "+AlwaysOnTop")

; 2. Add some texto the GUI.
MyGui.Add("Text",, "Hello, world! This my first GUI.")

; 3. Add a button. We'll make it do something later.
MyGui.Add("Button", "Default", "OK")

; 4. Show the GUI window.
MyGui.Show()
```

Let's break it down:
-   `MyGui := Gui(...)`: This creates a new GUI window object and stores it in the `MyGui` variable. The first parameter is the window title. The second, `"+AlwaysOnTop"`, is an option to make the window stay on top of others.
-   `MyGui.Add("Text", ...)`: This adds a text control to the GUI.
-   `MyGui.Add("Button", ...)`: This adds a button control. The `"Default"` option means this button will be "clicked" if the user presses Enter.
-   `MyGui.Show()`: This makes the GUI window visible on the screen.

When you run thiscript, a small windowill appear with your text and an OK button. The button doesn't do anything yet, and closing the windowon't exithe script. Let's fix that.

## Handling User Interaction: Events

To make a GUI useful, you need to respond when the user doesomething, like clicking a button or closing the window. These actions are called **events**.

You can link a function to an event. This function is often called an **event handler**.

```autohotkey
; Create the GUI window.
MyGui := Gui("Interactive GUI")
MyGui.SetFont("s12") ; Set a larger font for all controls

; Add a text control.
MyGui.Add("Text",, "Enter your name below:")

; Add an edit control for text input.
; We store the control object in a variable (MyEdit) to access it later.
MyEdit := MyGui.Add("Edit", "w300")

; Add a button and link its click evento a function.
MyButton := MyGui.Add("Button", "Default w100", "Greet Me")
MyButton.OnEvent("Click", GreetUser)

; Handle the window's closevent.
MyGui.OnEvent("Close", GuiClose)

; Show the window.
MyGui.Show()


; --- Event Handler Functions ---

; This function is called when the button is clicked.
GreetUser(*)
{
    ; Retrieve the text from thedit control using its .Value property.
    UserName := MyEdit.Value
    MsgBox("Hello, " UserName "! Welcome to your first interactive script.")
}

; This function is called when the GUI's close button (the X) is pressed.
GuiClose(*)
{
    ExitApp() ; This command exits thentire script.
}
```

### What's New Here?

-   `MyEdit := MyGui.Add("Edit", ...)`: We are now storing the control object itself in a variable. This crucial for getting its value later.
-   `MyButton.OnEvent("Click", GreetUser)`: This thevent handling line. Itells the script: "When `MyButton` receives a `Click` event, call the `GreetUser` function."
-   `MyGui.OnEvent("Close", GuiClose)`: This handles thevent of the user clicking the 'X' button the window's title bar. It calls the `GuiClose` function.
-   `GreetUser(*)`: This our event handler function. The `*` in the parameters means it can accept any number of parameters, which istandard practice for event handlers.
-   `MyEdit.Value`: We access the content of thedit control using its `.Value` property.
-   `ExitApp()`: This a built-in command thaterminates the script. It's essential for providing a clean way to close your GUI application.

This example demonstrates the fundamental pattern of all GUI applications: create controls, link their events to functions, and write the functions to perform the desired actions. Withese building blocks, you can create powerful, custom tools for any task. Next, we will explore some of the most powerful features of the language in [Advanced Topics](/automation_tools/autohotkey/./07_advanced_topics.md).

