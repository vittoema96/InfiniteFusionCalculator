# InfiniteFusionCalculator by vittoema96

## Table of Contents
1. [Introduction](#introduction)
2. [What does it do](#explanation)
    - [Example](#example)
    - [Stats and types](#stats)
    - [Modes](#modes)
      - [Single](#single) 
      - [Batch](#batch)
      - [Type](#type)
3. [Installation](#install)
   - [App .exe](#exe)
     - [Rebuild .exe](#rebuild_exe)
   - [Python Project](#python)
4. [What was used](#info)


# 1. Introduction <a id="introduction"></a>
This project is intended as an improvement on the functionalities 
of [Pokemon Infinite Fusion Calculator](https://aegide.github.io/).


# 2. What does it do <a id="explanation"></a>

It shows full evolution lines of fusions between Pokemon.  

## Example <a id="example"></a>
### Fearow + Ekans
![Fearow + Ekans](ifc/resources/images/example_fearow_ekans.jpg)  
### Fearow evolution line   
- Spearow [1-19] 
- Fearow [20-100]  
### Ekans evolution line  
- Ekans [1-21] 
- Arbok [22-100] 
### Fusions:  
- Ekans + Spearow [1-19] 
- Ekans + Fearow [20-21] 
- Arbok + Fearow [22-100]

## Stats and types <a id="stats"></a>
The typing of a Fusion is simply deductible from the colors of the box at the right of the Fusion Sprite.  

If that's not enough, hovering a fusion with the mouse allows a Tooltip to appear.  

This tooltip will display:
- The type (or types) of the Fusion
- The stats of the Fusion  

![Fearow + Ekans](ifc/resources/images/example_info.jpg)  


## Modes <a id="modes"></a>

This application has 3 modes:
### Single <a id="single"></a>
Performs fusion between two Pokemon as described in the [Example](#example) .

### Batch <a id="batch"></a>
Given a list ok pokemon, calculates all the possible pairs and performs fusion between them.

![Fearow + Ekans](ifc/resources/images/example_batch.jpg)  

### Type <a id="type"></a>
Given two types and, optionally, a base pokemon, it will show all possible fusions with that typing (and base pokemon).
Here you can also order the evolutions by stat. The ordering is done by taking the maximum stat for each fusion evoline.
Only fusion pokemon matching the required types are taken into account for this calculation.
![Fearow + Ekans](ifc/resources/images/example_type.jpg)  


# 3. Installation <a id="install"></a>
If you just want to run the program read [App .exe](#exe).  

If you want to open the project in an IDE read [Python project](#python).   

If you edited the program and want to rebuild the .exe read  [Rebuild .exe](#rebuild_exe).  

# App .exe <a id="exe"></a>
If your only goal is to run the app, what you really need is to download 
the [dist/IFC.zip](dist/IFC.zip) folder.  
### *Click [here](https://github.com/vittoema96/InfiniteFusionCalculator/raw/main/dist/IFC.zip) to download the zip.*  
Once downloaded, run the `IFC.exe` file that you'll find inside.

### Rebuild .exe <a id="rebuild_exe"></a>
If you are editing the app and want to recompile the `IFC.exe`,
run  
`python build_exe.py`  
and the program will be recompiled to an exe (and its zip version) inside the [dist/](/dist/) 
folder using `auto-py-to-exe`.


## Python Project <a id="python"></a>

To run the python project, first create a `venv` with Python 3.8  
Activate it and run the command  
`pip install -r requirements.txt`.  
This will install the required libraries.  
Then run  
`python main.py`

# What was used <a id="info"></a>

### PokeAPI  
 
[PokeAPI](https://pokeapi.co/) was used to gather data about pokemon, such as 
minimum and maximum levels, typings, evolution lines and stats.  

#### Stats and Types

Stats are calculated as stated here:  https://infinitefusion.fandom.com/wiki/Pok%C3%A9mon_Fusion#Stats  
Typing takes into account this: https://infinitefusion.fandom.com/wiki/Pok%C3%A9mon_Fusion#Typing

## Vanilla sprites
Pokemon sprites are dynamically downloaded from here:   
`https://img.pokemondb.net/sprites/black-white/normal/<pokemon_name>.png`  
### Bulbasaur Example:  
https://img.pokemondb.net/sprites/black-white/normal/bulbasaur.png  
![Bulbasaur](https://img.pokemondb.net/sprites/black-white/normal/bulbasaur.png )  

## Fusion sprites
Fusion sprites are dynamically downloaded from here:  
` https://raw.githubusercontent.com/Aegide/custom-fusion-sprites/main/CustomBattlers/<head_pokedex_id>.<body_pokedex_id>.png`   
### Charizard + Blastoise Example:  

https://raw.githubusercontent.com/Aegide/custom-fusion-sprites/main/CustomBattlers/9.6.png  
![Bulbasaur](https://raw.githubusercontent.com/Aegide/custom-fusion-sprites/main/CustomBattlers/9.6.png   )
(If the app can't find the sprite, it will try look under `master/Battlers`, `master/Battlers/<head_dex_id>` and 
`autogen-fusion-sprites/master/Battlers/<head_dex_id>`)

### auto-py-to-exe
The application is compiled to an .exe using [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/)
