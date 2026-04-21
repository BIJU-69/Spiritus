from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


class Beverage(db.Model):
    __tablename__ = "beverages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(50), nullable=False)       # whiskey, vodka, rum, wine, beer, gin, tequila, brandy, liqueur, champagne
    subtype = db.Column(db.String(80))                    # single malt, bourbon, lager, etc.
    abv = db.Column(db.Float, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100))
    price_min = db.Column(db.Float)
    price_max = db.Column(db.Float)
    quality_tier = db.Column(db.String(25))               # budget, mid-range, premium, ultra-premium
    description = db.Column(db.Text)
    tasting_notes = db.Column(db.Text)
    color = db.Column(db.String(60))

    # Flavor intensity scores 0–10
    flavor_sweet = db.Column(db.Integer, default=0)
    flavor_bitter = db.Column(db.Integer, default=0)
    flavor_smoky = db.Column(db.Integer, default=0)
    flavor_fruity = db.Column(db.Integer, default=0)
    flavor_spicy = db.Column(db.Integer, default=0)
    flavor_floral = db.Column(db.Integer, default=0)
    flavor_earthy = db.Column(db.Integer, default=0)
    flavor_crisp = db.Column(db.Integer, default=0)
    flavor_woody = db.Column(db.Integer, default=0)
    flavor_creamy = db.Column(db.Integer, default=0)

    def flavors_dict(self):
        return {
            "sweet": self.flavor_sweet,
            "bitter": self.flavor_bitter,
            "smoky": self.flavor_smoky,
            "fruity": self.flavor_fruity,
            "spicy": self.flavor_spicy,
            "floral": self.flavor_floral,
            "earthy": self.flavor_earthy,
            "crisp": self.flavor_crisp,
            "woody": self.flavor_woody,
            "creamy": self.flavor_creamy,
        }

    def top_flavors(self, n=3):
        ranked = sorted(self.flavors_dict().items(), key=lambda x: x[1], reverse=True)
        return [f for f, v in ranked if v > 0][:n]

    def price_label(self):
        if self.price_min and self.price_max:
            return f"${self.price_min:.0f}–${self.price_max:.0f}"
        elif self.price_min:
            return f"From ${self.price_min:.0f}"
        return "Price varies"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "type": self.type,
            "subtype": self.subtype,
            "abv": self.abv,
            "country": self.country,
            "region": self.region,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "price_label": self.price_label(),
            "quality_tier": self.quality_tier,
            "description": self.description,
            "tasting_notes": self.tasting_notes,
            "color": self.color,
            "flavors": self.flavors_dict(),
            "top_flavors": self.top_flavors(),
        }


class Cocktail(db.Model):
    __tablename__ = "cocktails"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_spirit = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)   # JSON array of {"item": str, "amount": str}
    instructions = db.Column(db.Text)
    garnish = db.Column(db.String(200))
    glass_type = db.Column(db.String(60))
    mood_tags = db.Column(db.String(200))              # comma-separated
    flavor_profile = db.Column(db.String(200))         # comma-separated flavor keywords
    difficulty = db.Column(db.String(20))              # easy, medium, hard
    description = db.Column(db.Text)
    abv_estimate = db.Column(db.Float)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "base_spirit": self.base_spirit,
            "ingredients": json.loads(self.ingredients) if self.ingredients else [],
            "instructions": self.instructions,
            "garnish": self.garnish,
            "glass_type": self.glass_type,
            "mood_tags": [t.strip() for t in self.mood_tags.split(",")] if self.mood_tags else [],
            "flavor_profile": [f.strip() for f in self.flavor_profile.split(",")] if self.flavor_profile else [],
            "difficulty": self.difficulty,
            "description": self.description,
            "abv_estimate": self.abv_estimate,
        }
