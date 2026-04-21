from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from sqlalchemy import or_

from models import db, Beverage, Cocktail
from recommendations import get_recommendations, get_pairings, compare_beverages

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alcohol.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ── Frontend ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Beverages ───────────────────────────────────────────────────────────────

@app.route("/api/beverages", methods=["GET"])
def list_beverages():
    """
    Query params:
      type          – filter by type (e.g. whiskey)
      quality_tier  – budget | mid-range | premium | ultra-premium
      min_abv       – float
      max_abv       – float
      sort          – name | abv | price (ascending)
      limit         – int (default 100)
      offset        – int (default 0)
    """
    q = Beverage.query

    bev_type = request.args.get("type")
    if bev_type:
        q = q.filter(Beverage.type == bev_type.lower())

    quality = request.args.get("quality_tier")
    if quality:
        q = q.filter(Beverage.quality_tier == quality)

    min_abv = request.args.get("min_abv", type=float)
    max_abv = request.args.get("max_abv", type=float)
    if min_abv is not None:
        q = q.filter(Beverage.abv >= min_abv)
    if max_abv is not None:
        q = q.filter(Beverage.abv <= max_abv)

    sort = request.args.get("sort", "name")
    if sort == "abv":
        q = q.order_by(Beverage.abv)
    elif sort == "price":
        q = q.order_by(Beverage.price_min)
    else:
        q = q.order_by(Beverage.name)

    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)

    total = q.count()
    items = q.offset(offset).limit(limit).all()

    return jsonify({
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": [b.to_dict() for b in items],
    })


@app.route("/api/beverages/<int:bev_id>", methods=["GET"])
def get_beverage(bev_id):
    bev = db.session.get(Beverage, bev_id)
    if not bev:
        abort(404, description="Beverage not found.")
    return jsonify(bev.to_dict())


@app.route("/api/search", methods=["GET"])
def search():
    """
    Query param: q – search term (matches name, brand, type, subtype, country)
    """
    term = request.args.get("q", "").strip()
    if not term:
        return jsonify({"beverages": [], "cocktails": []})

    like = f"%{term}%"

    bevs = Beverage.query.filter(
        or_(
            Beverage.name.ilike(like),
            Beverage.brand.ilike(like),
            Beverage.type.ilike(like),
            Beverage.subtype.ilike(like),
            Beverage.country.ilike(like),
            Beverage.description.ilike(like),
        )
    ).limit(20).all()

    cocktails = Cocktail.query.filter(
        or_(
            Cocktail.name.ilike(like),
            Cocktail.base_spirit.ilike(like),
            Cocktail.description.ilike(like),
        )
    ).limit(10).all()

    return jsonify({
        "beverages": [b.to_dict() for b in bevs],
        "cocktails": [c.to_dict() for c in cocktails],
    })


# ── Recommendations ─────────────────────────────────────────────────────────

@app.route("/api/recommend", methods=["POST"])
def recommend():
    """
    Body (JSON):
      mood    – relaxed | party | romantic | stressed | celebratory | adventurous | cozy
      strength – light | moderate | strong
      flavors  – list of flavor strings (e.g. ["sweet", "fruity"])
      limit   – number of results (default 5)
    """
    data = request.get_json(silent=True) or {}

    mood     = data.get("mood", "relaxed")
    strength = data.get("strength", "moderate")
    flavors  = data.get("flavors", [])
    limit    = int(data.get("limit", 5))

    if not isinstance(flavors, list):
        flavors = []

    results = get_recommendations(mood, strength, flavors, limit=limit)
    return jsonify({"recommendations": results})


# ── Compare ─────────────────────────────────────────────────────────────────

@app.route("/api/compare", methods=["POST"])
def compare():
    """
    Body (JSON):
      ids – list of beverage IDs to compare (2–4)
    """
    data = request.get_json(silent=True) or {}
    ids  = data.get("ids", [])

    if not ids or len(ids) < 2:
        return jsonify({"error": "Provide at least 2 beverage IDs to compare."}), 400
    if len(ids) > 4:
        ids = ids[:4]

    result = compare_beverages(ids)
    return jsonify(result)


# ── Pairings ─────────────────────────────────────────────────────────────────

@app.route("/api/pairings/<int:bev_id>", methods=["GET"])
def pairings(bev_id):
    bev = db.session.get(Beverage, bev_id)
    if not bev:
        abort(404, description="Beverage not found.")
    result = get_pairings(bev_id)
    return jsonify(result)


# ── Cocktails ────────────────────────────────────────────────────────────────

@app.route("/api/cocktails", methods=["GET"])
def list_cocktails():
    """
    Query params:
      base_spirit – filter by spirit type
      mood        – filter by mood tag
      difficulty  – easy | medium | hard
    """
    q = Cocktail.query

    spirit = request.args.get("base_spirit")
    if spirit:
        q = q.filter(Cocktail.base_spirit == spirit.lower())

    mood = request.args.get("mood")
    if mood:
        q = q.filter(Cocktail.mood_tags.ilike(f"%{mood}%"))

    difficulty = request.args.get("difficulty")
    if difficulty:
        q = q.filter(Cocktail.difficulty == difficulty.lower())

    items = q.order_by(Cocktail.name).all()
    return jsonify({"cocktails": [c.to_dict() for c in items]})


@app.route("/api/cocktails/<int:cid>", methods=["GET"])
def get_cocktail(cid):
    cocktail = db.session.get(Cocktail, cid)
    if not cocktail:
        abort(404, description="Cocktail not found.")
    return jsonify(cocktail.to_dict())


# ── Meta / Filters ───────────────────────────────────────────────────────────

@app.route("/api/filters", methods=["GET"])
def filters():
    """Returns distinct values for each filterable dimension."""
    types   = [r[0] for r in db.session.query(Beverage.type).distinct().order_by(Beverage.type).all()]
    tiers   = [r[0] for r in db.session.query(Beverage.quality_tier).distinct().order_by(Beverage.quality_tier).all()]
    spirits = [r[0] for r in db.session.query(Cocktail.base_spirit).distinct().order_by(Cocktail.base_spirit).all()]

    return jsonify({
        "beverage_types": types,
        "quality_tiers":  tiers,
        "cocktail_spirits": spirits,
        "moods":    ["relaxed", "party", "romantic", "stressed", "celebratory", "adventurous", "cozy"],
        "strengths": ["light", "moderate", "strong"],
        "flavors":   ["sweet", "bitter", "smoky", "fruity", "spicy", "floral", "earthy", "crisp", "woody", "creamy"],
    })


# ── Error handlers ───────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": str(e)}), 404


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e)}), 400


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error."}), 500


# ── Entry point ──────────────────────────────────────────────────────────────

def _auto_seed():
    """Create tables and seed data if the database is empty."""
    db.create_all()
    if Beverage.query.count() == 0:
        from seed_data import BEVERAGES, COCKTAILS
        import json
        for data in BEVERAGES:
            db.session.add(Beverage(**data))
        for data in COCKTAILS:
            db.session.add(Cocktail(**data))
        db.session.commit()

with app.app_context():
    _auto_seed()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
