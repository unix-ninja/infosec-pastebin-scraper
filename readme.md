# Infosec Pastebin Scraper

This utility is intended to aid threat intelligence requirements for your information security program. Pastebin is an easy and valuable source of intelligence to pull from, and should be included in any long term strategy.

## Requirements

This utility is currently tested with Python 2.7. It should run on any system which supports Python.

## Usage and recommendations

Two scripts are provided in this repo.
  * scraper.py - the legacy script which scraps HTML directly from the website. This is deprecated, and should no longer be used.
  * scraper.api.py - polls Pastebin's API for new data. This is the recommended approach, though you will need to have a PRO account to make use of the API.

Once you have setup your PRO account and whitelisted your IP, you can simply run `scraper.api.py` to begin scraping data. Data will be saved in the following hierarchy: `/pastes/YYYY/MM/DD/PASTEID.txt`

It is recommended that you mount /pastes on its own high speed storage volume for increased performance. I'd also like to recommend search through the data using ripgrep. It's incredibly fast, which is what you are going to want for this method of storage.

Other considerations: For long term execution, you may want to create a scheduling job in something like systemd or daemontools to manager process execution continuity. At the very least, if you aren't doing that, just run it in screen or tmux.

Have fun!
