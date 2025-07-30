# 1. Introduction to AutoHotkey

## The Origins of a Power Tool

AutoHotkey was created in 2003 by Chris Mallett. It began as a fork of another scripting program called AutoIt v2, withe initial goal of adding better support for keyboard shortcuts, or "hotkeys." Over time, it evolved far beyond its origins, transforming into a full-fledged, Turing-complete scripting language specifically designed for task automation Microsoft Windows.

Its development has always been driven by its community. Users would request features, and the language would grow to accommodate them, leading to a rich, eclectic, and incredibly practical set of commands for interacting withe Windows OS at a deep level.

## The Core Philosophy: Simplicity and Power

Thenduring philosophy of AutoHotkey is to make powerful automation accessible to everyone, not just professional programmers. This reflected in its design:

-   **Declarative Syntax for Simple Tasks**: For common tasks like creating a hotkey, the syntax isimple andeclarative. You state *what* you wanto happen, and AHK handles the *how*.
-   **Shallow Learning Curve**: A beginner can write a useful script in minutes without needing to understand complex programming concepts. You can get a lot done with just a few basicommands.
-   **Deep Capabilities for Experts**: Beneathe simple surface lies a powerfulanguage. For those who wish to go deeper, AHK offers arrays, objects, functions, GUI creation, and even the ability to make direct calls to the Windows API, providing nearly limitless automation potential.

## The Most Importanthing to Know: v1 vs. v2

As a new user, the most critical concepto understand is thexistence of two major versions of AutoHotkey: **v1.1** and **v2.0**.

For manyears, v1.1 was the standard. However, as the language grew organically, it accumulated some syntactic inconsistencies and confusing behaviors. AutoHotkey v2.0 was developed to address these issues, introducing a more logical, consistent, and robust syntax that is better suited for building large and complex scripts.

**As of 2025, AutoHotkey v2.0 is the official, recommended version for all new users and new projects.** While there is a vast amount of legacy code and tutorials for v1 online, starting with v2 will save you from confusion and lead to better scripting habits.

### Key Differences at a Glance

| Feature | AutoHotkey v1.1 (Legacy) | AutoHotkey v2.0 (Modern) |
| :--- | :--- | :--- |
| **Syntax** | Often ambiguous. Commands and functions hadifferent syntax. | Consistent expression-based syntax. Everything is a function call or an expression. |
| **Variables** | Variables were often treated as plain text. Required `%` signs to dereference. | Variables are always treated as variables. No `%` signs needed in expressions. |
| **Commands** | Used a comma-separated syntax (e.g., `MsgBox, Hello, World!`). | All commands are now functions (e.g., `MsgBox("Hello, World!")`). |
| **Error Handling** | Error detection was often weak or silent. | Much stricterror checking. Scripts will fail with a clear message instead of behaving unpredictably. |

**This guide will focus exclusively on AutoHotkey v2.0.** When searching for help online, it is crucial to look for v2-specific examples and tutorials to avoid confusion.

Now that younderstand the background, let's move on to [Getting Started](/automation_tools/autohotkey/./02_getting_started.md) with installing AutoHotkey and writing your first script.

