<div id="top"></div>

<p>
   <a href="https://pypi.org/project/ChessToTheDeath/" alt="Downloads">
      <img src="https://static.pepy.tech/personalized-badge/chesstothedeath?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads" align="right">
   </a>
   <a href="https://pypi.org/project/ChessToTheDeath/" alt="Visitors">
      <img src="https://hitscounter.dev/api/hit?url=https%3A%2F%2Fgithub.com%2FSilenZcience%2FChessToTheDeath&label=Visitors&icon=person-circle&color=%23479f76" align="right">
   </a>
</p>

[![OS-Windows]][OS-Windows]
[![OS-Linux]][OS-Linux]
[![OS-MacOS]][OS-MacOS]

<br/>
<div align="center">
<h2 align="center">ChessToTheDeath</h2>
   <p align="center">
      A simple chess variant where pieces have damage and health values.
      <br/>
      <a href="https://github.com/SilenZcience/ChessToTheDeath/blob/main/chess_to_the_death/util/gui.py">
         <strong>Explore the code »</strong>
      </a>
      <br/>
      <br/>
      <a href="https://github.com/SilenZcience/ChessToTheDeath/issues">Report Bug</a>
      ·
      <a href="https://github.com/SilenZcience/ChessToTheDeath/issues">Request Feature</a>
   </p>
</div>


<details>
   <summary>Table of Contents</summary>
   <ol>
      <li>
         <a href="#about-the-project">About The Project</a>
         <ul>
            <li><a href="#made-with">Made With</a></li>
         </ul>
      </li>
      <li>
         <a href="#getting-started">Getting Started</a>
         <ul>
            <li><a href="#installation">Installation</a></li>
         </ul>
      </li>
      <li><a href="#usage">Usage</a>
         <ul>
         <li><a href="#help">Help</a></li>
         <li><a href="#examples">Examples</a></li>
         </ul>
      </li>
      <li><a href="#license">License</a></li>
      <li><a href="#contact">Contact</a></li>
   </ol>
</details>

<div id="about-the-project"></div>

## About The Project

This project simply contains a custom chess variant in which every chess piece has it's own
health and damage values. Therefor simply taking an enemy piece is not an option. Instead
you have to fight it multiple times. The game ends when one of the Kings has no healthpoints
left.

<div id="made-with"></div>

### Made With
[![Python][MadeWith-Python]](https://www.python.org/)
[![Numpy][MadeWith-Numpy]](https://numpy.org/)

<p align="right">(<a href="#top">back to top</a>)</p>
<div id="getting-started"></div>

## Getting Started

<div id="installation"></div>

### Installation

Choose one of the options below:
```console
pip install ChessToTheDeath
```
```console
pip install git+https://github.com/SilenZcience/ChessToTheDeath.git
```
```console
git clone git@github.com:SilenZcience/ChessToTheDeath.git
cd ./ChessToTheDeath
```

<p align="right">(<a href="#top">back to top</a>)</p>
<div id="usage"></div>

## Usage

```console
python -m chess_to_the_death [-h] [-v] ...
```

| Argument               | Description                                          |
|------------------------|------------------------------------------------------|
| -h, --help             | show help message and exit                           |
| -v, --version          | show program's version number and exit               |
| -fps FPS, --fps FPS    | set max fps (a lower value will improve performance) |
| -nohighlight           | disable cell-highlighting on mouse hover             |
| -noflip                | disable board flipping                               |
| -random                | randomize the health and damage values of all pieces |
| -default               | play the default chess variant                       |
| -crazy                 | play the crazyhouse chess variant                    |
| -pos POSITION          | FEN starting position                                |

- ***leftclick*** a piece to select it
- ***leftclick*** a tile to move/attack with your selected piece
- ***rightclick*** a tile to mark it with a circle
- ***rightclick*** a circled tile to mark it with a square
- ***rightclick*** drag & drop across different tiles to draw an arrow
- ***middleclick*** an empty tile to crazyplace a piece (only with `-crazy` parameter enabled)

<div id="help"></div>

### Help

> **Q: Why am i seeing weird characters like `[31;1mr[0m `in the console?**

> A: This project uses `ANSI-Escape Codes` to display colors in the Terminal. If you see these weird characters, then your Terminal does not support these Codes.

> ⚠️If you are using the Command Prompt on Windows 10 you can most likely solve this issue by going in the Registry under `Computer\HKEY_CURRENT_USER\Console` and adding/editing the `DWORD` value `VirtualTerminalLevel` and setting it to `1`.

- - - -

> **Q: Is it possible to have a different board size/shape?**

> A: Yes, the `-pos POSITION` parameter supports different board widths and heights. Simply expand the notation with additional rows or columns.

<div id="examples"></div>

### Examples

```console
python -m chess_to_the_death
```
<p float="left">
   <img src="https://raw.githubusercontent.com/SilenZcience/ChessToTheDeath/main/img/example1.png" width="30%"/>
   <img src="https://raw.githubusercontent.com/SilenZcience/ChessToTheDeath/main/img/example2.png" width="30%"/>
   <img src="https://raw.githubusercontent.com/SilenZcience/ChessToTheDeath/main/img/example3.png" width="30%"/>
</p>

```console
python -m chess_to_the_death -default -pos "5Q/3k2/1p4/1Pp2p/2Pp1P/3P1K b" -noflip
```
<p float="left">
   <img src="https://raw.githubusercontent.com/SilenZcience/ChessToTheDeath/main/img/example4.png" width="30%"/>
   <img src="https://raw.githubusercontent.com/SilenZcience/ChessToTheDeath/main/img/example5.png" width="30%"/>
   <img src="https://raw.githubusercontent.com/SilenZcience/ChessToTheDeath/main/img/example6.png" width="30%"/>
</p>


<p align="right">(<a href="#top">back to top</a>)</p>
<div id="license"></div>

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/SilenZcience/ChessToTheDeath/blob/main/LICENSE) file for details

<div id="contact"></div>

## Contact

> **SilenZcience** <br/>
[![GitHub-SilenZcience][GitHub-SilenZcience]](https://github.com/SilenZcience)

[OS-Windows]: https://img.shields.io/badge/os-windows-green
[OS-Linux]: https://img.shields.io/badge/os-linux-green
[OS-MacOS]: https://img.shields.io/badge/os-macOS-green

[MadeWith-Python]: https://img.shields.io/badge/Made%20with-Python-brightgreen
[MadeWith-Numpy]: https://img.shields.io/badge/Made%20with-Numpy-brightgreen

[GitHub-SilenZcience]: https://img.shields.io/badge/GitHub-SilenZcience-orange
