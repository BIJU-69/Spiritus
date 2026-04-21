# SPIRITUS - Intelligent Drinks Guide

An AI-powered alcohol intelligence web app for discovering, comparing, and getting personalised recommendations for the world's finest spirits, wines, and beers.

**Live demo:** https://spiritus.onrender.com

---

## Tech Stack

| Layer    | Technology |
|----------|-----------|
| Backend  | Python 3 / Flask / SQLAlchemy |
| Database | SQLite |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Hosting  | Render (free tier) |

---

## Features

- **Smart Recommendations** - mood, strength, and flavour-based scoring engine
- **Explore & Filter** - browse 50+ spirits by type, ABV, quality tier
- **Side-by-side Comparison** - compare up to 4 drinks with a full flavour breakdown
- **Cocktail Recipes** - 22 classic cocktails with full ingredients and instructions
- **Pairing Suggestions** - mixers, garnishes, and food pairings per spirit
- **Global Search** - instant search across spirits and cocktails

---

## Setup (5 steps)

```bash
# 1. Clone the repo
git clone https://github.com/BIJU-69/Spiritus.git
cd Spiritus

# 2. Install dependencies
pip install -r requirements.txt

# 3. Seed the database
python seed_data.py

# 4. Start the app
python app.py

# 5. Open in browser
# http://127.0.0.1:5000
```

---

## Adding New Spirits

Open `seed_data.py` and add a new entry to the `BEVERAGES` list:

```python
dict(
    name="Your Spirit Name",
    brand="Brand Name",
    type="whiskey",
    subtype="Single Malt",
    abv=43.0,
    country="Scotland",
    region="Speyside",
    price_min=45,
    price_max=60,
    quality_tier="premium",
    description="A short description.",
    tasting_notes="Tasting notes here.",
    color="Pale gold",
    flavor_sweet=6,
    flavor_bitter=2,
    flavor_smoky=3,
    flavor_fruity=7,
    flavor_spicy=4,
    flavor_floral=3,
    flavor_earthy=2,
    flavor_crisp=5,
    flavor_woody=4,
    flavor_creamy=0,
),
```

Then re-run `python seed_data.py` to refresh the database.

---

## Drink Responsibly

Spiritus is for educational and entertainment purposes. Always drink responsibly and in accordance with the laws of your country.
