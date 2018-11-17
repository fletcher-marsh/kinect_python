# Kinect + Python

## Installation Instructions
NOTE: must have a machine capable of 
 - Windows 8+
 - PyKinect2

1. Download stuff!
    * [Visual Studio](https://visualstudio.microsoft.com/vs/) (community works!) NOTE: Select the 'Python development' checkbox when the installation prompts you!
    * [Anaconda 32-bit](https://repo.anaconda.com/archive/Anaconda3-5.3.0-Windows-x86.exe) NOTE: install for all users, and preferably put it on your C:\ drive for easy access
    * [Kinect V2 SDK](https://www.microsoft.com/en-us/download/details.aspx?id=44561)
2. In visual studio: View > Other Windows > Python Environments
3. Click on Python version installed by Anaconda (probably between 3.5 and 3.7, will definitely be 32-bit)
4. (Optional) click 'Make this the default environment for new projects'
5. Click on the 'Overview' dropdown > 'Packages'
6. In the search box below, install the following packages by searching for them:
    * PyKinect2
    * Pygame
    * If doesn't exist already, comtypes

## Debugging
 * Use the Kinect SDK (Body Basics) while the Kinect is connected to your machine to run diagnostics
 * `assert sizeof(tagSTATSTG) == 72, sizeof(tagSTATSTG)` or `AssertionError: 80`: You are running Anaconda 64-bit! Change to 32-bit [here](https://repo.anaconda.com/archive/Anaconda3-5.3.0-Windows-x86.exe).