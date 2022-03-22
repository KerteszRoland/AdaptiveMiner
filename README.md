# <img src=https://github.com/Orangeman69/AdaptiveMiner/blob/master/icons/pickaxe.ico width=80> AdaptiveMiner
## A script which helps you to mine your crypto carefree. It will stop mining if your specified program is running.
### ONLY WINDOWS (10 tested)

## Features:
- Automatic miner start/stop, when you quit/launch an exe
- Run at Windows startup
- Automatic [MSI Afterburner](https://www.msi.com/Landing/afterburner/graphics-cards) profile change with shortcuts
- Resume/Pause miner 
- View Miner dashboard
- Track mined time and current mining session

## Showcase

https://user-images.githubusercontent.com/64317447/159583847-6ac43cd0-5548-49e9-92fb-b756d634815b.mp4


## Setup:
-	### Download:
	-	[Zip](https://github.com/Orangeman69/AdaptiveMiner/archive/refs/heads/master.zip) 
	-	Clone: 
		```
		git clone https://github.com/Orangeman69/AdaptiveMiner
		```
-	### Install dependencies with pip (pip install -r requirements.txt)
-	### Fill out the .env file with your config:
	MINER_PATH: A path to your miner bat file's shortcut  
	EXES: Your programs exe's that you want to check seperated by semicolons  
	DASHBOARD_URL: If your miner provides a local dashboard you can put the url here  
	CHECK_FREQ: Running program check frequency in seconds
	AFTERBURNER_MINER_SHORTCUT: Keyboard shortcut to change Afterburner profile to miner profile (ctrl+shift+alt+k)  
	AFTERBURNER_IDLE_SHORTCUT: Keyboard shortcut to change Afterburner profile to idle profile (ctrl+shift+alt+l)  
-	### Open main.pyw script by double click (You should see the AdaptiveMiner icon in your tray)

## Usage:
-	You can hover over the tray icon to show miner's status, uptime if mining
-	Right click to:
	-	Resume/Pause miner
	-	Visit your miner's dashboard (if you specified it in .env)
	-	Run at Startup (will make a windows shortcut in your user startup folder)
	-	Quit from the application
