<div id="top"></div>

<p>
   <a href="https://pypi.org/project/ChessToTheDeath/" alt="Downloads">
      <img src="https://static.pepy.tech/personalized-badge/chesstothedeath?period=total&units=international_system&left_color=grey&right_color=orange&left_text=Downloads" align="right">
   </a>
   <a href="https://pypi.org/project/ChessToTheDeath/" alt="Visitors">
      <img src="https://visitor-badge.laobi.icu/badge?page_id=SilenZcience.ChessToTheDeath" align="right">
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
         <li><a href="#examples">Examples</a></li>
         </ul>
      </li>
      <li><a href="#license">License</a></li>
      <li><a href="#contact">Contact</a></li>
   </ol>
</details>

## About The Project

This project simply contains a custom chess variant in which every chess piece has it's own
health and damage values. Therefor simply taking an enemy piece is not an option. Instead
you have to fight it multiple times. The game ends when one of the Kings has no healthpoints
left.

### Made With
[![Python][MadeWith-Python]](https://www.python.org/)
[![Numpy][MadeWith-Numpy]](https://numpy.org/)

<p align="right">(<a href="#top">back to top</a>)</p>

## Getting Started

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

## Usage

```console
python -m chess_to_the_death [-h] [-v] [-fps FPS] [-nohighlight] [-noflip]
```

| Argument               | Description                                         |
|------------------------|-----------------------------------------------------|
| -h, --help             | show help message and exit                          |
| -v, --version          | show program's version number and exit              |
| -fps FPS, --fps FPS    | set max fps (a lower value will improve performance)|
| -nohighlight           | disable cell-highlighting on mouse hover            |
| -noflip                | disable board flipping                              |

### Examples

![Example1](https://raw.githubusercontent.com/SilenZcience/ChessToTheDeath/main/img/example1.png "example1")

![Example2](https://raw.githubusercontent.com/SilenZcience/ChessToTheDeath/main/img/example2.png "example2")

![Example3](https://raw.githubusercontent.com/SilenZcience/ChessToTheDeath/main/img/example3.png "example3")

<p align="right">(<a href="#top">back to top</a>)</p>

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/SilenZcience/ChessToTheDeath/blob/main/LICENSE) file for details

## Contact

> **SilenZcience** <br/>
[![GitHub-SilenZcience][GitHub-SilenZcience]](https://github.com/SilenZcience)

[OS-Windows]: https://svgshare.com/i/ZhY.svg
[OS-Linux]: https://svgshare.com/i/Zhy.svg
[OS-MacOS]: https://svgshare.com/i/ZjP.svg

[MadeWith-Python]: https://img.shields.io/badge/Made%20with-Python-brightgreen
[MadeWith-Numpy]: https://img.shields.io/badge/Made%20with-Numpy-brightgreen

[GitHub-SilenZcience]: https://img.shields.io/badge/GitHub-SilenZcience-orange