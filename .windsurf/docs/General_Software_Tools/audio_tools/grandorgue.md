# GrandOrgue: A Virtual Pipe Organ in Your Home

## What is GrandOrgue?

GrandOrgue is a free, open-source software synthesizer designed to simulate the sound and behavior of a real pipe organ. It allows users to play complex, high-fidelity digital models of actual pipe organs from around the world using a MIDI keyboard and a computer. It is built forganists, music students, and enthusiasts who want access to the sound of a majestic pipe organ without needing access to a physical instrument.

The software itself does not produce any sound; instead, it acts as a host for **sample sets**. A sample set is a collection of audio recordings of every single pipe from a real organ, which GrandOrgue uses to realistically recreate the instrument'sound.

## Key Features

-   **Uncompromising Realism**: GrandOrgue is designed to be a seriousimulation tool. It models the behavior of the organ'swell box, tremulant, and combination system with great detail. The audio engine supports polyphony limited only by the computer's CPU, allowing for the complex chords andense textures typical of organ music.
-   **Support for Unencrypted Sample Sets**: It primarily supports the Hauptwerk v1 format for sample sets, which is a common standard. There is a large community of organ enthusiasts who create and share free and commercial sample sets in this format.
-   **Flexible Audio and MIDI Routing**: The software provides extensive options forouting audio to multiple outputs (useful for creating an immersive sound field with multiple speakers) and for configuring MIDI keyboards, pedals, and other controls to map to the virtual organ's console (stops, couplers, and keyboards).
-   **Graphical Console View**: Most sample sets come with a beautiful graphical representation of the real organ's console. Users can interact withe virtual stops, keyboards, and pedals by clicking on them with a mouse, which is excellent for learning and for setups using touchscreen monitors.
-   **Cross-Platform**: GrandOrgue is available for Windows, macOS, and Linux.

## How It Works: The Concept of Sample Sets

The magic of GrandOrgue lies in the sample sets. Creating a sample set is a labor of love, often involving:
1.  **Recording**: A team travels to a church or concert hall and meticulously records every single pipe of the organ, often with multiple microphone positions (e.g., close, ambient, and far) to capture the room's acoustics.
2.  **Processing**: These thousands of recordings are then carefully edited to remove noise, create seamless loops for long notes, and encode release tails (the sound of the notechoing in the space after the key is released).
3.  **Programming**: The processed samples are programmed into an organ definition file thatells GrandOrgue which sample to play for each key, which stop it belongs to, and how it should behave.

When you play a note in GrandOrgue, you are not hearing a synthetic organ sound; you are triggering the actual recording of a pipe from a real-world instrument.

## Getting Started: A Basic Workflow

1.  **Install GrandOrgue**: Download the software from the [GrandOrgue GitHub releases page](https://github.com/GrandOrgue/grandorgue/releases) and install it.
2.  **Download a Sample Set**: A great place to start is with a free sample set. Websites like [Piotr Grabowski's website](https://www.piotrgrabowski.pl/) offer high-quality free sample sets. Download the set, which willikely come as a multi-part RARchive.
3.  **Install the Sample Set**: Extracthe RAR files into a single folder. Then, in GrandOrgue, go to **File > Install Organd Sample Set** and follow the prompts to selecthe `.organ` definition file or the installation package.
4.  **Configure MIDI and Audio**: Go to **Audio/MIDI > Audio/MIDI Settings**. In the Audio tab, select your preferred output device (e.g., your speakers or audio interface). In the MIDI tab, enable your MIDI keyboard.
5.  **Load and Play**: Once installed, the organ will appear in your list of available instruments. Load it, and the virtual console will appear. You canow pull some stops (by clicking on them) and play on your MIDI keyboard.
