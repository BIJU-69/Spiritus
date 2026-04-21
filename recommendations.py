"""
Recommendation engine using a weighted multi-criteria scoring system.

Scoring breakdown (max 100):
  - Mood match   : 0–40 pts  (type affinity per mood)
  - Strength     : 0–30 pts  (ABV proximity to desired range)
  - Flavor match : 0–30 pts  (overlap between user prefs and beverage flavors)

Each recommendation also carries a human-readable explanation assembled from
template fragments so the UI can show *why* each drink was suggested.
"""

from models import Beverage, Cocktail


# How well each beverage type matches each mood (0–10 scale, scaled to 40 pts)
MOOD_TYPE_AFFINITY = {
    "relaxed": {
        "whiskey": 9, "wine": 10, "beer": 8, "brandy": 9, "gin": 6,
        "vodka": 4,  "rum": 5,   "tequila": 3, "liqueur": 7, "champagne": 6, "mezcal": 5,
    },
    "party": {
        "vodka": 10, "tequila": 9, "rum": 9,  "beer": 8,  "gin": 7,
        "whiskey": 4, "wine": 4,  "champagne": 8, "liqueur": 5, "brandy": 2, "mezcal": 7,
    },
    "romantic": {
        "champagne": 10, "wine": 10, "gin": 6, "brandy": 8, "whiskey": 6,
        "vodka": 4,  "rum": 4,    "tequila": 2, "liqueur": 8, "beer": 1, "mezcal": 2,
    },
    "stressed": {
        "whiskey": 10, "brandy": 9, "wine": 8, "rum": 6,  "gin": 6,
        "vodka": 5,  "beer": 7,    "tequila": 3, "liqueur": 7, "champagne": 1, "mezcal": 4,
    },
    "celebratory": {
        "champagne": 10, "wine": 8, "vodka": 8, "tequila": 8, "rum": 6,
        "whiskey": 6,  "gin": 7,  "beer": 5,  "liqueur": 5,  "brandy": 5, "mezcal": 5,
    },
    "adventurous": {
        "tequila": 9, "mezcal": 10, "gin": 9,  "rum": 7,  "vodka": 6,
        "whiskey": 7, "beer": 6,   "wine": 4,  "brandy": 4, "champagne": 3, "liqueur": 5,
    },
    "cozy": {
        "whiskey": 10, "brandy": 10, "wine": 9, "beer": 8, "rum": 7,
        "liqueur": 8,  "gin": 5,    "vodka": 3, "tequila": 2, "champagne": 4, "mezcal": 3,
    },
}

# ABV boundaries for each strength label (inclusive lower, exclusive upper)
STRENGTH_RANGES = {
    "light":    (0.0,  8.0),
    "moderate": (8.0, 25.0),
    "strong":   (25.0, 100.0),
}

# Explanation fragments assembled per recommendation
MOOD_PHRASES = {
    "relaxed":     "Its smooth character makes it perfect for unwinding.",
    "party":       "A crowd-favourite that keeps any gathering energised.",
    "romantic":    "The sophistication here sets an effortlessly intimate mood.",
    "stressed":    "Its depth and warmth offer the perfect antidote to a long day.",
    "celebratory": "Built for moments worth remembering.",
    "adventurous": "A bold, characterful pour for the curious palate.",
    "cozy":        "Rich and warming — ideal for slow, comfortable evenings.",
}

STRENGTH_PHRASES = {
    "light":    "At {abv}% ABV it's easy to enjoy without feeling overwhelmed.",
    "moderate": "With {abv}% ABV it strikes a perfect balance of presence and accessibility.",
    "strong":   "At {abv}% ABV it delivers a full-strength, unapologetic experience.",
}

QUALITY_PHRASES = {
    "budget":        "Great value that punches above its price point.",
    "mid-range":     "Dependable quality without breaking the bank.",
    "premium":       "A premium choice that rewards every sip.",
    "ultra-premium": "An exceptional, collector-grade expression.",
}


def _strength_score(abv: float, strength_pref: str) -> float:
    """Return 0–30 based on how well a beverage's ABV fits the desired strength band."""
    lo, hi = STRENGTH_RANGES.get(strength_pref, (0, 100))
    if lo <= abv < hi:
        # Perfect match – score by how centred the ABV is within the range
        mid = (lo + hi) / 2
        spread = (hi - lo) / 2 or 1
        centrality = 1 - abs(abv - mid) / spread
        return 20 + 10 * centrality
    # Outside range – penalise proportionally to how far outside
    distance = max(lo - abv, abv - hi)
    band_width = hi - lo or 10
    penalty = min(distance / band_width, 1.0)
    return max(0.0, 10 - 10 * penalty)


def _flavor_score(beverage: Beverage, desired_flavors: list[str]) -> float:
    """Return 0–30 based on overlap between desired flavors and beverage flavor profile."""
    if not desired_flavors:
        return 15  # Neutral score when user has no preference

    flavors = beverage.flavors_dict()
    total = 0.0
    for flavor in desired_flavors:
        intensity = flavors.get(flavor, 0)
        total += intensity / 10.0  # Normalise to 0–1

    match_ratio = total / len(desired_flavors)
    return round(match_ratio * 30, 2)


def _mood_score(beverage: Beverage, mood: str) -> float:
    """Return 0–40 based on type affinity for the given mood."""
    affinity_map = MOOD_TYPE_AFFINITY.get(mood, {})
    raw = affinity_map.get(beverage.type, 3)  # Default 3/10 for unmapped types
    return (raw / 10.0) * 40


def _build_explanation(bev: Beverage, mood: str, strength: str, flavors: list[str]) -> str:
    parts = []

    mood_phrase = MOOD_PHRASES.get(mood, "A versatile choice for any occasion.")
    parts.append(mood_phrase)

    strength_tmpl = STRENGTH_PHRASES.get(strength, "")
    if strength_tmpl:
        parts.append(strength_tmpl.format(abv=bev.abv))

    top = bev.top_flavors(2)
    if top:
        parts.append(f"Expect notes of {' and '.join(top)}.")

    matched = [f for f in flavors if (bev.flavors_dict().get(f, 0) or 0) >= 5]
    if matched:
        parts.append(f"Matches your preference for {', '.join(matched)} flavours.")

    quality_phrase = QUALITY_PHRASES.get(bev.quality_tier, "")
    if quality_phrase:
        parts.append(quality_phrase)

    return " ".join(parts)


def get_recommendations(mood: str, strength: str, flavors: list[str], limit: int = 5) -> list[dict]:
    """
    Core recommendation function.

    Returns up to `limit` beverages ranked by composite score,
    each decorated with a score breakdown and explanation string.
    """
    if mood not in MOOD_TYPE_AFFINITY:
        mood = "relaxed"
    if strength not in STRENGTH_RANGES:
        strength = "moderate"

    beverages = Beverage.query.all()

    scored = []
    for bev in beverages:
        mood_pts    = _mood_score(bev, mood)
        strength_pts = _strength_score(bev.abv, strength)
        flavor_pts  = _flavor_score(bev, flavors)
        total       = round(mood_pts + strength_pts + flavor_pts, 2)

        scored.append({
            "beverage": bev,
            "score": total,
            "score_breakdown": {
                "mood":     round(mood_pts, 1),
                "strength": round(strength_pts, 1),
                "flavor":   round(flavor_pts, 1),
            },
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:limit]

    results = []
    for item in top:
        bev = item["beverage"]
        results.append({
            **bev.to_dict(),
            "recommendation_score": item["score"],
            "score_breakdown": item["score_breakdown"],
            "explanation": _build_explanation(bev, mood, strength, flavors),
        })

    return results


def get_pairings(beverage_id: int) -> dict:
    """
    Return mixer, garnish, food, and cocktail suggestions for a specific beverage.
    Logic is derived from the beverage's type, subtype, and dominant flavor profile.
    """
    bev = Beverage.query.get_or_404(beverage_id)
    flavors = bev.flavors_dict()

    mixers = _suggest_mixers(bev, flavors)
    garnishes = _suggest_garnishes(bev, flavors)
    food = _suggest_food(bev, flavors)
    cocktails = _suggest_cocktails(bev)

    return {
        "beverage": bev.to_dict(),
        "mixers": mixers,
        "garnishes": garnishes,
        "food_pairings": food,
        "cocktail_suggestions": cocktails,
    }


def _suggest_mixers(bev: Beverage, flavors: dict) -> list[dict]:
    type_mixers = {
        "whiskey": [
            {"mixer": "Still water", "reason": "A few drops open the nose and soften the alcohol."},
            {"mixer": "Dry ginger ale", "reason": "Complements caramel and vanilla notes beautifully."},
            {"mixer": "Club soda", "reason": "Lightens the spirit while preserving its character."},
        ],
        "vodka": [
            {"mixer": "Tonic water", "reason": "Clean bitterness enhances the neutral spirit."},
            {"mixer": "Cranberry juice", "reason": "Adds colour and tartness for easy sipping."},
            {"mixer": "Fresh lime juice", "reason": "Citrus brightness lifts vodka's clean profile."},
        ],
        "rum": [
            {"mixer": "Cola", "reason": "A classic pairing that amplifies caramel and molasses notes."},
            {"mixer": "Coconut water", "reason": "Echoes tropical origins and balances sweetness."},
            {"mixer": "Pineapple juice", "reason": "Tropical acidity pairs perfectly with aged rum."},
        ],
        "gin": [
            {"mixer": "Indian tonic water", "reason": "The quinine bitterness is the gin's natural partner."},
            {"mixer": "Elderflower cordial", "reason": "Amplifies the floral, botanical character."},
            {"mixer": "Cucumber water", "reason": "Enhances the fresh, crisp botanical notes."},
        ],
        "tequila": [
            {"mixer": "Fresh lime juice", "reason": "Citrus acidity is the perfect counterpart to agave."},
            {"mixer": "Grapefruit soda", "reason": "The bitterness cuts through tequila's earthiness."},
            {"mixer": "Agave syrup & soda", "reason": "Echoes the base ingredient and lengthens the drink."},
        ],
        "wine": [
            {"mixer": "Sparkling water", "reason": "Creates a refreshing, lower-ABV spritzer."},
            {"mixer": "Fruit juice (matching profile)", "reason": "Sangria-style enrichment."},
        ],
        "beer": [
            {"mixer": "Lime wedge", "reason": "Classic citrus enhancement for lagers."},
            {"mixer": "Ginger (shandy)", "reason": "Ginger beer adds spice and reduces intensity."},
        ],
        "brandy": [
            {"mixer": "Warm apple juice", "reason": "Complements the fruity, oak-driven character."},
            {"mixer": "Ginger ale", "reason": "Light effervescence lifts brandy's richness."},
        ],
        "champagne": [
            {"mixer": "Orange juice", "reason": "Classic Mimosa combination — citrus brightens the bubbles."},
            {"mixer": "Peach purée", "reason": "The Bellini pairing is a timeless luxury match."},
        ],
        "liqueur": [
            {"mixer": "Fresh cream", "reason": "Creates a silky, indulgent dessert drink."},
            {"mixer": "Espresso (cold)", "reason": "Coffee-forward liqueurs shine with espresso."},
            {"mixer": "Milk", "reason": "Softens the sweetness for a nightcap sip."},
        ],
        "mezcal": [
            {"mixer": "Fresh grapefruit juice", "reason": "Citrus cuts through smoke and earthy agave."},
            {"mixer": "Coconut water", "reason": "Tropical sweetness balances mezcal's intensity."},
            {"mixer": "Ginger beer", "reason": "Spice-on-spice creates a complex, layered experience."},
        ],
    }
    return type_mixers.get(bev.type, [{"mixer": "Club soda", "reason": "A neutral lengthener for any spirit."}])


def _suggest_garnishes(bev: Beverage, flavors: dict) -> list[str]:
    base = {
        "whiskey":   ["Orange peel", "Maraschino cherry", "Cocktail cherry"],
        "vodka":     ["Lemon twist", "Lime wedge", "Cucumber ribbon", "Olive"],
        "rum":       ["Lime wedge", "Pineapple chunk", "Mint sprig", "Coconut flakes"],
        "gin":       ["Cucumber slice", "Lemon twist", "Rosemary sprig", "Pink peppercorn"],
        "tequila":   ["Lime wheel", "Salt rim", "Jalapeño slice", "Chilli powder rim"],
        "wine":      ["None required", "Citrus wheel for spritz"],
        "beer":      ["Lime wedge (lagers)", "Orange slice (wheat beers)"],
        "brandy":    ["Lemon twist", "Orange peel", "Cinnamon stick"],
        "champagne": ["Strawberry", "Raspberry", "Sugar cube with bitters"],
        "liqueur":   ["Grated chocolate", "Coffee beans", "Crushed nuts"],
        "mezcal":    ["Orange slice with chilli salt", "Fresh jalapeño", "Lime wheel"],
    }
    extra = []
    if flavors.get("fruity", 0) >= 6:
        extra.append("Fresh berry skewer")
    if flavors.get("floral", 0) >= 6:
        extra.append("Edible flower")
    if flavors.get("smoky", 0) >= 7:
        extra.append("Charred wood chip")

    result = base.get(bev.type, ["Citrus peel"])
    return list(dict.fromkeys(result + extra))  # Deduplicate while preserving order


def _suggest_food(bev: Beverage, flavors: dict) -> list[dict]:
    food_map = {
        "whiskey": [
            {"food": "Dark chocolate", "reason": "Amplifies vanilla and caramel notes."},
            {"food": "Smoked meats & charcuterie", "reason": "Complementary smokiness and umami."},
            {"food": "Sharp aged cheddar", "reason": "Salty richness balances the sweetness."},
        ],
        "vodka": [
            {"food": "Caviar & blinis", "reason": "Classic Eastern European pairing."},
            {"food": "Smoked salmon", "reason": "Neutral spirit doesn't overpower delicate fish."},
            {"food": "Pickles & cured foods", "reason": "Acidity resets the palate between sips."},
        ],
        "rum": [
            {"food": "Jerk chicken", "reason": "Caribbean origins make this a natural match."},
            {"food": "Coconut-based desserts", "reason": "Tropical flavours echo the spirit."},
            {"food": "Banana foster", "reason": "Sweet, caramelised fruit echoes rum's molasses."},
        ],
        "gin": [
            {"food": "Cucumber sandwiches", "reason": "Botanical, fresh pairing for the spirit's character."},
            {"food": "Light seafood & oysters", "reason": "Briny notes complement juniper botanicals."},
            {"food": "Citrus tarts", "reason": "Citrus echoes gin's natural brightness."},
        ],
        "tequila": [
            {"food": "Tacos & salsas", "reason": "Regional cuisine is always the best match."},
            {"food": "Guacamole", "reason": "Creamy avocado softens the agave spirit."},
            {"food": "Grilled corn", "reason": "Earthy sweetness complements blanco tequila."},
        ],
        "wine": [
            {"food": "Cheese board", "reason": "Wine's acidity cuts through dairy fat beautifully."},
            {"food": "Charcuterie", "reason": "Cured meats and tannins are a timeless pairing."},
            {"food": "Seasonal fresh fruit", "reason": "Mirrors the fruity notes in the wine."},
        ],
        "beer": [
            {"food": "Pizza & burgers", "reason": "Carbonation cuts through richness perfectly."},
            {"food": "Roasted nuts & pretzels", "reason": "Salt and malt are natural companions."},
            {"food": "Grilled sausages", "reason": "Smoky, fatty meats pair brilliantly with beer."},
        ],
        "brandy": [
            {"food": "Foie gras", "reason": "Rich, unctuous textures match brandy's depth."},
            {"food": "Pecan pie", "reason": "Nutty sweetness echoes the spirit's oak notes."},
            {"food": "Blue cheese", "reason": "Bold flavours stand up to aged brandy."},
        ],
        "champagne": [
            {"food": "Oysters", "reason": "The ultimate luxury pairing — minerality and bubbles."},
            {"food": "Strawberries & cream", "reason": "Fruit sweetness accentuates the fine bubbles."},
            {"food": "Sushi & sashimi", "reason": "Clean, delicate flavours match champagne's elegance."},
        ],
        "liqueur": [
            {"food": "Tiramisu", "reason": "Coffee liqueurs are the star ingredient here."},
            {"food": "Ice cream", "reason": "Pour over vanilla for an instant affogato."},
            {"food": "Almond biscotti", "reason": "The biscuit's sweetness echoes the liqueur."},
        ],
        "mezcal": [
            {"food": "Mole negro", "reason": "Complex, earthy sauces match mezcal's smokiness."},
            {"food": "Grasshopper tacos", "reason": "Traditional Oaxacan pairing for adventurous diners."},
            {"food": "Dark chocolate (70%+)", "reason": "Bitterness and smoke create a stunning contrast."},
        ],
    }
    return food_map.get(bev.type, [{"food": "Mixed nuts", "reason": "A safe, crowd-pleasing snack pairing."}])


def _suggest_cocktails(bev: Beverage) -> list[dict]:
    """Return cocktail suggestions relevant to this beverage type."""
    type_cocktails = {
        "whiskey":   ["Old Fashioned", "Manhattan", "Whiskey Sour", "Penicillin", "Boulevardier"],
        "vodka":     ["Moscow Mule", "Cosmopolitan", "Espresso Martini", "Martini", "Sex on the Beach"],
        "rum":       ["Mojito", "Daiquiri", "Piña Colada", "Dark & Stormy", "Mai Tai"],
        "gin":       ["Negroni", "Tom Collins", "Gimlet", "Clover Club", "French 75"],
        "tequila":   ["Margarita", "Paloma", "Tequila Sunrise", "Tommy's Margarita"],
        "brandy":    ["Sidecar", "Brandy Alexander", "Vieux Carré"],
        "champagne": ["Champagne Cocktail", "Kir Royale", "Aperol Spritz", "French 75"],
        "wine":      ["Sangria", "Aperol Spritz", "Kir Royale"],
        "liqueur":   ["Espresso Martini", "White Russian", "Baileys Hot Chocolate"],
        "beer":      ["Shandy", "Beer Margarita", "Michelada"],
        "mezcal":    ["Mezcal Negroni", "Naked and Famous", "Oaxacan Old Fashioned"],
    }
    suggestions = type_cocktails.get(bev.type, ["Classic Sour", "Simple Highball"])

    # Try to return matching Cocktail records from DB
    matching = []
    for name in suggestions:
        record = Cocktail.query.filter(Cocktail.name.ilike(f"%{name}%")).first()
        if record:
            matching.append({"id": record.id, "name": record.name, "base_spirit": record.base_spirit})
        else:
            matching.append({"id": None, "name": name, "base_spirit": bev.type})

    return matching[:4]


def compare_beverages(ids: list[int]) -> dict:
    """
    Side-by-side comparison of multiple beverages.
    Returns structured data the frontend renders as a comparison table.
    """
    beverages = Beverage.query.filter(Beverage.id.in_(ids)).all()
    if not beverages:
        return {"error": "No beverages found for the provided IDs."}

    # Sort by input order
    id_order = {v: i for i, v in enumerate(ids)}
    beverages.sort(key=lambda b: id_order.get(b.id, 999))

    all_flavors = ["sweet", "bitter", "smoky", "fruity", "spicy", "floral", "earthy", "crisp", "woody", "creamy"]

    return {
        "beverages": [b.to_dict() for b in beverages],
        "flavor_keys": all_flavors,
        "summary": {
            "highest_abv": max(beverages, key=lambda b: b.abv).name,
            "lowest_abv":  min(beverages, key=lambda b: b.abv).name,
            "best_value":  min(
                [b for b in beverages if b.price_min],
                key=lambda b: b.price_min,
                default=beverages[0]
            ).name if any(b.price_min for b in beverages) else None,
        },
    }
