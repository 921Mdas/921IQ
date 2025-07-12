# DRCongo
from NewsScrapers.DRCongo.RFIcd import RFICdScrap
from NewsScrapers.DRCongo.Actucd import ActuCdScrap
from NewsScrapers.DRCongo.Okapi import RadioOkapiScrap
from NewsScrapers.DRCongo.Seven import Sur7CDScrap
from NewsScrapers.DRCongo.Mediacd import MediaCdScrap


# Gabon
from NewsScrapers.Gabon.GabonNews import LUnionScrap
from NewsScrapers.Gabon.GabonNews import GabonActuScrap
from NewsScrapers.Gabon.GabonNews import Info241Scrap
from NewsScrapers.Gabon.GabonNews import GabonMediaTimeScrap
from NewsScrapers.Gabon.GabonNews import GabonReviewScrap

#DRCongoNewsSources
DRC_scrapers = [
    # RFICdScrap,
    ActuCdScrap,
    # RadioOkapiScrap,
    # Sur7CDScrap,
    # MediaCdScrap
]


# GabonNewsSources
Gabon_scrapers = [
    # GabonReviewScrap,
    # LUnionScrap,
    # GabonActuScrap,
    # Info241Scrap,
    # GabonMediaTimeScrap
]