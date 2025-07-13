scraper_engine takes the config json data in the African database > process it 
it's basically a beautiful soup code split in two: html and classes in the json file and the function processing it  in the scraper_engine


.
├── NewsScrapers/
│   ├── publication_ids.py  # Your existing file
│   ├── Scraper_engine.py
│   └── DRCongo/
│       └── Actucd.py      # Modified
└── Main.py                # Unchanged