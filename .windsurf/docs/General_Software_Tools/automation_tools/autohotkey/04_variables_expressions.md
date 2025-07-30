# 4. Variables and Expressions

Now that you've mastered the basics of hotkeys and hotstrings, it's time to make your scripts dynamic. To do this, you need to be able to store and manipulate information. This where variables and expressions come in. This chapter introduces the fundamental programming concepts in AutoHotkey v2.

## What is a Variable?

A variable isimply a named container in memory that holds a value. You can put information into it, and you can retrieve that information later by using the variable's name. In AutoHotkey, variables can holdifferentypes of data, such as numbers, text (strings), and boolean values (true/false).

### Assignment: Storing a Value

In AutoHotkey v2, you assign a value to a variable using the `:=` operator. This known as the "expression assignment" operator.

```autohotkey
; Assign the string "Sandra" to a variable named MyName := "Sandra"

; Assign the number 42 to a variable named UserCount := 42

; You can also store the result of a calculation
TotalCost := 19.99 * 3
```

**Important Note for v2:** Always use `:=` for assigning values. The singlequalsign (`=`) is a legacy operator from v1 and has different behavior. Sticking to `:=` will prevent confusion and errors.

### Using Variables

Once a value istored in a variable, you can use it in your script. For example, you can display its contents in a message box. To include a variable within a string of text, you simply write its name.

```autohotkey
MyName := "Sandra"
UserAge := 30

; Display the contents of the MyName variable
MsgBox("Hello, " MyName)

; You can combine text and variables
MsgBox(MyName " is " UserAge " years old.")
```

Notice thathere are no `%` signs around the variables. In v2, when a variable is used in an expression (like inside the parentheses of a function), it is automatically evaluated to its contents. The parts of the string are concatenated (joined together) with a space.

## Expressions: Performing Actions with Datan expression is any combination of values, variables, operators, and function calls that results in a single value. You've already been using them with `MsgBox()`.

### Mathematical Expressions

You can perform standard mathematicalculations.

```autohotkey
Price := 100
TaxRate := 0.07
TaxAmount := Price * TaxRate
FinalPrice := Price + TaxAmount

MsgBox("The final price is: " FinalPrice)
```

### String Concatenation

Combining strings is a fundamental operation. In AutoHotkey, this done implicitly by writing variables and literal strings nexto each other, separated by a space.

```autohotkey
FirstName := "John"
LastName := "Doe"

; The space between the variables acts as the concatenation operator.
FullName := FirstName " " LastName

MsgBox(FullName) ; Displays "John Doe"
```

## Data Types

AutoHotkey handles data types mostly automatically, but it's good to be aware of them:

-   **String**: A sequence of characters, enclosed in double quotes (`"`). Example: `"Hello, World!"`
-   **Number**: Can be an integer (like `42`) or a floating-point number (like `3.14`).
-   **Boolean**: Represents a value of either `true` or `false`. These are crucial for making decisions in your scripts.

```autohotkey
IsLoggedIn := true
HasAdminRights := false
```

Understanding how to store and manipulate data is the key to unlocking the full power of AutoHotkey. Withis knowledge, you canow create scripts that are not justatic, but can react and adapto different situations. In the next chapter, we willearn how to use this to control the flow of our scripts with [Control Flow: If, Else, and Loops](/automation_tools/autohotkey/./05_control_flow.md).

