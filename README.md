# Hand-tracking based air Hand Pan Instrument 

![Example Image](images/DALLE.png)

## Overview

The script is designed to create an interactive digital musical instrument (DMI) that responds to hand gestures. Using a webcam, the script captures real-time video and employs MediaPipe to detect and track hand movements. The screen is divided into segments, each corresponding to a specific musical note, inspired by the layout of a handpan. As the user moves their hand over these segments, the script detects the position and intensity of the movement, mapping it to an audio response. The volume of the sound played is determined by how forcefully the hand moves downward, simulating the dynamics of playing a physical instrument. Additionally, visual feedback is provided by having the circle around the activated segment flash black, confirming the user's interaction. Audio is managed using the Pygame mixer, which ensures that the sound is played in real-time with the appropriate volume and without delay.


## Getting Started

These instructions will guide you through setting up the project on your local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python  3.x

### Installation

Follow these steps to install the project and its dependencies:

1. Clone the repository: `git clone https://github.com/Aekp/MiniProject`
2. Change into the project directory: `cd yourrepository`
3. Install the required Python packages: `pip install -r requirements.txt`

## Usage

To use the system, follow these steps:

1. Run the main script: `python air_hand_pan_circles.py`
