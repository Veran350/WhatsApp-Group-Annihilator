#!/bin/bash  
termux-setup-storage  
pkg update -y  
pkg install python git tor root-repo -y  
pip install requests bs4 stem fake-useragent  
git clone https://github.com/yourusername/WhatsApp-Group-Annihilator  
cd WhatsApp-Group-Annihilator  
chmod +x scripts/*  
service tor start  
