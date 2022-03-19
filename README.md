# AdaptiveMiner

## Features:
- Automatic miner start/stop, when you quit/launch an exe
- Automatic miner shutdown, when you launch an exe
- Start with windows
- Automatic MSI Afterburner profile change with shortcut
- Enable/Disable miner 
- View Miner dashboard

## Setup:
-	### Install requirements with pip (pip install -r requirements.txt)
-	### Fill out the .env file with your details
	MINER_PATH: A path to your miner bat file's shortcut /
	EXES: Your programs exes that you want to check seperated by semicolons /
	DASHBOARD_URL: If your miner provides a local dashboard you can write it here /
	CHECK_FREQ: Check frequency in seconds /
-	### Start the main.pyw script
