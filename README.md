<p align="center">
  <img src="https://www.tibiawiki.com.br/images/9/93/Dark_Monk.gif" alt="Tibia character animation" width="250">
</p>

<h1 align="center">🧙‍♂️ Exeta Infir</h1>
<p align="center">
  <em>A sprite extractor tool for Tibia characters.</em>
</p>

---

## 📜 About the Project

**Exeta Infir** is a tool for extracting and generating spritesheets of Tibia characters directly from the official assets ⚔️

You can use this project to generate spritesheets from characters exported via [`Assets-Editor`](https://github.com/Arch-Mina/Assets-Editor), organizing all animation directions and phases into one image – ready for game engines like **Godot**, **Unity**, or even your own engine.

---

## 🧰 Requirements

- Python 3.8+
- [`Pillow`](https://pillow.readthedocs.io/en/stable/) → `pip install pillow`
- [`colorama`](https://pypi.org/project/colorama/) → `pip install colorama`

---

## 📦 How it works

1. Use [`Assets-Editor`](https://github.com/Arch-Mina/Assets-Editor) to export the character(s) you want.
2. Copy the exported JSON data into a file called:

> This file should be an array of objects – one for each character you want to extract.

3. Organize your `spritesheets/` folder with all `.bmp` files extracted from the Tibia client.  
   The files must follow the naming format:

- The first **20 files** contain **144 sprites each**, sized **32x32**.
- The rest contain sprites sized **64x64**.
- The sprites are extracted from the Tibia `.dat` files using external tools.

4. Each character includes **two animation states**:

   - `idle`
   - `moving`

   And **four directions**:

   - `up`, `right`, `down`, `left`

   The output spritesheet organizes these directions **horizontally**, and each animation **vertically**.

---

## 🧪 Included examples

This repository contains:

- Sample `spritesheets/` with `.bmp` files
- A working `assets-editor-data.json` file with two characters (for testing)

You can run everything out of the box to see how it works 💫

---

## 🧙‍♂️ Running the Spell

Once everything is ready, simply cast the rune:

```bash
python main.py
```
