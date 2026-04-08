# darkdump

## About 
Darkdump is a OSINT interface for carrying out deep web investgations written in python in which it allows users to enter a search query in which darkdump provides the ability to scrape .onion sites relating to that query to try to extract emails, metadata, keywords, images, social media etc. Darkdump retrieves sites via Ahmia.fi and scrapes those .onion addresses when connected via the tor network. 

## Installation
1) ``git clone https://github.com/LuckyDavidYang/darkdump.git``<br/>
2) ``cd darkdump``<br/>
3) ``python3.12 -m pip install -r requirements.txt``<br/>
4) ``python3.12 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"``
5) ``sh "/Applications/Python 3.12/Install Certificates.command"``
6) ``python3.12 -m pip install -U certifi nltk``
7) ``python3.12 -c "import nltk; nltk.download('stopwords'); nltk.download('punkt_tab')"``
8) ``python3.12 darkdump.py --help``<br/>

### Python Version
Darkdump is expected to run with `Python 3.12`.<br/>

### Tor Configuration 
To use Darkdump effectively, you need to configure Tor to allow your script to control it via the Tor control port. Here's how to set up your `torrc` file and verify that Tor is running: <br/>

#### Step 1: Install Tor
If Tor is not already installed on your system, you need to install it. Here's how you can install Tor on various operating systems:

Debian/Kali/Ubuntu: `sudo apt install tor`<br/>
MacOS: `brew install tor`<br/>

#### Step 2: Configure the Tor torrc File<br/>
Locate your torrc file. This file is usually found at `/etc/tor/torrc`on Linux and sometimes Mac. 

Add the following lines to your torrc to enable the control port and set a control port password:
```
ControlPort 9051
HashedControlPassword [YourHashedPasswordHere]
```
Replace `[YourHashedPasswordHere]` with a hashed password which can be generated using the `tor --hash-password` command: `tor --hash-password "my_password"`

#### Step 3: Start Tor Service
Linux: `sudo systemctl start tor.service`<br/>
MacOS: `brew services start tor`<br/>

### Example Queries: 
`python3.12 darkdump.py -q "hacking" -a 10 --scrape --proxy` - search for 10 links and scrape each site <br/>
`python3.12 darkdump.py -q "free movies" -a 25` - don't scrape, just return 25 links for that query (does not require tor) <br/>
`python3.12 darkdump.py -q "marketplaces" -a 15 --scrape --proxy -i` - search for 10 links and scrape each site as well as find and store images.

### Python API
If you want to collect data programmatically instead of using CLI output:

```python
from darkdump_collector import (
    batch_collect_dark_net,
    collect_dark_net,
    save_batch_collect_dark_net_to_excel,
)

data = collect_dark_net("marketplaces", 5)
print(data["returned_count"])
print(data["tor_ip"])
print(data["results"][0]["onion_link"])

batch_result = batch_collect_dark_net(["marketplaces", "forums"], 5)
excel_path = save_batch_collect_dark_net_to_excel(batch_result, "darkdump_results.xlsx")
print(excel_path)
```

`collect_dark_net` follows the same collection path as:
`python3.12 darkdump.py -q "marketplaces" -a 5 --scrape --proxy`

It returns structured data instead of printing the banner and per-site CLI output.
When Tor is connected, the returned payload also includes `tor_ip`, for example:
`Current IP Address via Tor: 185.220.101.1`

`batch_collect_dark_net` processes a list of keywords with the same `amount`.
`save_batch_collect_dark_net_to_excel` writes one Excel row per `collect_dark_net(... )["results"]` item and keeps the worksheet name as `results`.

## Menu
```

     _            _       _                            __
  __| | __ _ _ __| | ____| |_   _ _ __ ___  _ __      / /
 / _` |/ _` | '__| |/ / _` | | | | '_ ` _ \| '_ \    / / 
| (_| | (_| | |  |   < (_| | |_| | | | | | | |_) |  / /  
 \__,_|\__,_|_|  |_|\_\__,_|\__,_|_| |_| |_| .__/  /_/  v3 
                                           |_|           

usage: darkdump.py [-h] [-v] [-q QUERY] [-a AMOUNT] [-p] [-i] [-s]

Darkdump is an interface for scraping the deepweb through Ahmia. Made by yours truly.

options:
  -h, --help            show this help message and exit
  -v, --version         returns darkdump's version
  -q QUERY, --query QUERY
                        the keyword or string you want to search on the deepweb
  -a AMOUNT, --amount AMOUNT
                        the amount of results you want to retrieve
  -p, --proxy           use tor proxy for scraping
  -i, --images          scrape images and visual content from the site
  -s, --scrape          scrape the actual site for content and look for keywords

```
## Visual
<p align="center">
  <img src="imgs/darkdump_example.png">
</p>

## Ethical Notice
The developer of this program, is not resposible for misuse of this data gathering tool. Do not use darkdump to navigate websites that take part in any activity that is identified as illegal under the laws and regulations of your government. May God bless you all. 

## License 
MIT License<br/>
Copyright (c) 
