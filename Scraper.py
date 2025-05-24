import requests # type: ignore
import json
import os
from bs4 import BeautifulSoup
from flask import Flask




def scraper(url):
    try:
        #header
        headers = {"User-Agent": "Mozilla/5.0"} 
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        return soup

    except Exception as e:
        print('something went wrong', e)

    
    