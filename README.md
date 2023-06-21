# BXEngine Point-and-Click Adventure Engine

BXEngine is a Point-and-Click Adventure Engine with the goal of being able to make Myst-like adventure games. The name comes from the originally planned showcase game, Backrooms Explorer. BXEngine uses images and simple JSON formats to describe a game world, and also supports music, sound effects, and powerful event scripting.

## Gameplay and Structure

A game world is made of rooms filled with views, that are linked together by exits. Navigation indicators will appear when mousing over the sides or middle of the screen, if exits exist in those directions. Areas on the screen in a particular view may also produce look or use indicatiors, or a navigation indicator of their own. Gameplay consists of exploring and interacting with features of each room. To make things more interesting, some exits may only appear once in a while, or only on certain playthroughs. Some interactions may also result in scripted events.

## Requirements

BXEngine has the following requirements to run on your system:

  - Python 3 (https://www.python.org/)
  - PyGame (https://www.pygame.org/)
  - PyGame GUI (https://pygame-gui.readthedocs.io/)
  - JSON Schema (https://pypi.org/project/jsonschema/)
  - UBJSON (https://ubjson.org/)

## Features List

BXEngine currently supports the following features:

  - Simple human-readable-writable JSON file formats for the game world and its rooms and views.
  - UBJSON save file format for storing any custom variables.
  - Powerful event scripting API that gives access to all of the engine's internal features.
  - Support for sound effects and music.
  - Image overlays for objects that can appear, disappear, or move within a view.
  - Verbose and customizable engine logging that tells you exactly what is happening and gives helpful errors and warnings.
  - Resource caching to remove unused resources from memory after a configurable period of time.
  - Text boxes that can pop up on screen when prompted.
  - Exits between areas that can appear based on random chance or a funvalue generated at the start of each game world playthrough.
  - JSON schemas that validate your game files at runtime and point out mistakes.
  - In-game debugging mode that can drop you into a debug console at any time with a keypress, where you can see all of the engine's variables and call internal functions.
  - Extensively commented source code.

## Planned Features

The following features are planned for future releases:

  - Video overlays that allow you to trigger a video to play on an area of the screen, much like Myst.
  - Inventory and item system to allow you to place items in the world that can be picked up, and may have scripted effects when interacted with.
  - Encounter and combat system for battling enemies or monsters that may appear.
  - Player health tracking to go with the encounter and combat system.
  - Navigable menus and other user interface components besides text boxes.
  - Simple multiplayer chat system that allows you to see which other users are exploring the same room as you and chat with them.
  - Comprehensive game development manual that isn't just source code comments.

## FAQ

  - Why are the game saves stored in UBJSON format when the rest of the engine uses regular JSON?
    - This is a cheap security-by-obscurity ploy to make it slightly more tedious for players to cheat by modifying their save files.
  - Why does the demo suck?
    - I downloaded random images from Google Images just for testing and haven't replaced those with actual game areas yet.
