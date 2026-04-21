import os
import re
import json
from datetime import datetime
from flask import Flask, jsonify, request, render_template, abort, Response, make_response
from flask_cors import CORS
from sqlalchemy import or_

from models import db, Beverage, Cocktail
from recommendations import get_recommendations, get_pairings, compare_beverages

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alcohol.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD", "spiritus2026")
app.config["BASE_URL"] = os.environ.get("BASE_URL", "https://spiritus.onrender.com")

db.init_app(app)


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


# ── Frontend ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Health (keeps Render free tier awake via cron-job.org ping) ─────────────

@app.route("/googlef5f4d09995984f1f.html")
def google_verify():
    return "google-site-verification: googlef5f4d09995984f1f.html"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


# ── SEO: Individual spirit pages ─────────────────────────────────────────────

@app.route("/spirits/<slug>")
def spirit_detail(slug):
    bevs = Beverage.query.all()
    bev = next((b for b in bevs if slugify(b.name) == slug), None)
    if not bev:
        abort(404)
    pairings = get_pairings(bev.id)
    schema = _spirit_jsonld(bev)
    return render_template("spirit_detail.html", bev=bev, pairings=pairings,
                           schema=json.dumps(schema), base_url=app.config["BASE_URL"])


# ── SEO: Individual cocktail pages ───────────────────────────────────────────

@app.route("/cocktails/<slug>")
def cocktail_detail(slug):
    cocktails = Cocktail.query.all()
    cocktail = next((c for c in cocktails if slugify(c.name) == slug), None)
    if not cocktail:
        abort(404)
    schema = _cocktail_jsonld(cocktail)
    return render_template("cocktail_detail.html", cocktail=cocktail,
                           schema=json.dumps(schema), base_url=app.config["BASE_URL"])


# ── SEO: Category pages ───────────────────────────────────────────────────────

@app.route("/category/<bev_type>")
def category_page(bev_type):
    bevs = Beverage.query.filter(Beverage.type == bev_type.lower()).order_by(Beverage.name).all()
    if not bevs:
        abort(404)
    return render_template("category.html", bev_type=bev_type, bevs=bevs,
                           base_url=app.config["BASE_URL"], slugify=slugify)


# ── SEO: Sitemap ─────────────────────────────────────────────────────────────

@app.route("/sitemap.xml")
def sitemap():
    base = app.config["BASE_URL"]
    bevs = Beverage.query.all()
    cocktails = Cocktail.query.all()
    types = list({b.type for b in bevs})

    urls = [base + "/", base + "/spirits", base + "/cocktails"]
    for b in bevs:
        urls.append(f"{base}/spirits/{slugify(b.name)}")
    for c in cocktails:
        urls.append(f"{base}/cocktails/{slugify(c.name)}")
    for t in types:
        urls.append(f"{base}/category/{t}")

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for url in urls:
        xml += f"  <url><loc>{url}</loc></url>\n"
    xml += "</urlset>"
    return Response(xml, mimetype="application/xml")


# ── SEO: Robots ───────────────────────────────────────────────────────────────

@app.route("/robots.txt")
def robots():
    base = app.config["BASE_URL"]
    content = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


# ── Admin panel ───────────────────────────────────────────────────────────────

@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    if data.get("password") == app.config["ADMIN_PASSWORD"]:
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Incorrect password."}), 401


@app.route("/api/admin/spirits", methods=["GET"])
def admin_list_spirits():
    _require_admin()
    bevs = Beverage.query.order_by(Beverage.name).all()
    return jsonify([b.to_dict() for b in bevs])


@app.route("/api/admin/spirits/<int:bev_id>", methods=["PUT"])
def admin_update_spirit(bev_id):
    _require_admin()
    bev = db.session.get(Beverage, bev_id)
    if not bev:
        abort(404)
    data = request.get_json(silent=True) or {}
    editable = ["name", "brand", "description", "tasting_notes", "price_min", "price_max",
                "quality_tier", "abv", "country", "region", "subtype", "color",
                "flavor_sweet", "flavor_bitter", "flavor_smoky", "flavor_fruity",
                "flavor_spicy", "flavor_floral", "flavor_earthy", "flavor_crisp",
                "flavor_woody", "flavor_creamy"]
    for field in editable:
        if field in data:
            setattr(bev, field, data[field])
    db.session.commit()
    return jsonify(bev.to_dict())


@app.route("/api/admin/spirits", methods=["POST"])
def admin_add_spirit():
    _require_admin()
    data = request.get_json(silent=True) or {}
    required = ["name", "brand", "type", "abv", "country"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Field '{field}' is required."}), 400
    bev = Beverage(**{k: v for k, v in data.items() if hasattr(Beverage, k)})
    db.session.add(bev)
    db.session.commit()
    return jsonify(bev.to_dict()), 201


@app.route("/api/admin/spirits/<int:bev_id>", methods=["DELETE"])
def admin_delete_spirit(bev_id):
    _require_admin()
    bev = db.session.get(Beverage, bev_id)
    if not bev:
        abort(404)
    db.session.delete(bev)
    db.session.commit()
    return jsonify({"deleted": True})


@app.route("/api/admin/stats", methods=["GET"])
def admin_stats():
    _require_admin()
    total_spirits = Beverage.query.count()
    total_cocktails = Cocktail.query.count()
    by_type = {}
    for t, in db.session.query(Beverage.type).distinct():
        by_type[t] = Beverage.query.filter(Beverage.type == t).count()
    return jsonify({
        "total_spirits": total_spirits,
        "total_cocktails": total_cocktails,
        "by_type": by_type,
    })


def _require_admin():
    auth = request.headers.get("X-Admin-Password", "")
    if auth != app.config["ADMIN_PASSWORD"]:
        abort(401, description="Unauthorised.")


# ── JSON-LD helpers ───────────────────────────────────────────────────────────

def _spirit_jsonld(bev):
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": bev.name,
        "brand": {"@type": "Brand", "name": bev.brand},
        "description": bev.description or "",
        "category": bev.type.capitalize(),
        "countryOfOrigin": bev.country,
        "offers": {
            "@type": "Offer",
            "priceCurrency": "USD",
            "price": str(bev.price_min or ""),
            "availability": "https://schema.org/InStock",
        } if bev.price_min else {},
    }


def _cocktail_jsonld(cocktail):
    import json as _json
    try:
        ingredients = _json.loads(cocktail.ingredients or "[]")
    except Exception:
        ingredients = []
    return {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": cocktail.name,
        "description": cocktail.description or "",
        "recipeCategory": "Cocktail",
        "recipeIngredient": [f"{i.get('amount','')} {i.get('item','')}".strip() for i in ingredients],
        "recipeInstructions": cocktail.instructions or "",
    }


# ── Beverages ───────────────────────────────────────────────────────────────

@app.route("/api/beverages", methods=["GET"])
def list_beverages():
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

    resp = make_response(jsonify({
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": [b.to_dict() for b in items],
    }))
    resp.headers["Cache-Control"] = "public, max-age=86400"
    return resp


@app.route("/api/beverages/<int:bev_id>", methods=["GET"])
def get_beverage(bev_id):
    bev = db.session.get(Beverage, bev_id)
    if not bev:
        abort(404, description="Beverage not found.")
    return jsonify(bev.to_dict())


@app.route("/api/search", methods=["GET"])
def search():
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
    if request.path.startswith("/api/"):
        return jsonify({"error": str(e)}), 404
    return render_template("404.html"), 404


@app.errorhandler(401)
def unauthorized(e):
    return jsonify({"error": str(e)}), 401


@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": str(e)}), 400


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error."}), 500


# ── Entry point ──────────────────────────────────────────────────────────────

def _auto_seed():
    db.create_all()
    if Beverage.query.count() == 0:
        from seed_data import BEVERAGES, COCKTAILS
        for data in BEVERAGES:
            db.session.add(Beverage(**data))
        for data in COCKTAILS:
            db.session.add(Cocktail(**data))
        db.session.commit()

with app.app_context():
    _auto_seed()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
