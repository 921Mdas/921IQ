# DRCongo
from NewsScrapers.DRCongo.RFIcd import RFICdScrap
from NewsScrapers.DRCongo.Actucd import ActuCdScrap
from NewsScrapers.DRCongo.Okapi import RadioOkapiScrap
from NewsScrapers.DRCongo.Seven import Sur7CDScrap


#DRCongoNewsSources
DRC_scrapers = [
    RFICdScrap,
    ActuCdScrap,
    RadioOkapiScrap,
    Sur7CDScrap,
]
