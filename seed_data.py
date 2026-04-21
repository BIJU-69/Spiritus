"""
Populates the database with a curated set of 52 beverages and 22 cocktails.
Run once with: python seed_data.py
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import Beverage, Cocktail


BEVERAGES = [
    # ── WHISKEYS ───────────────────────────────────────────────────────────
    dict(name="Glenfiddich 12 Year", brand="Glenfiddich", type="whiskey", subtype="Single Malt Scotch",
         abv=40.0, country="Scotland", region="Speyside", price_min=45, price_max=55,
         quality_tier="premium", color="Pale gold",
         description="One of the world's best-selling single malts, Glenfiddich 12 brings an approachable fruitiness that has converted millions to Scotch whisky.",
         tasting_notes="Fresh pear, creamy toffee, subtle oak, a hint of vanilla on the long finish.",
         flavor_sweet=7, flavor_fruity=8, flavor_woody=5, flavor_crisp=4, flavor_floral=3),

    dict(name="The Macallan 12 Sherry Oak", brand="The Macallan", type="whiskey", subtype="Single Malt Scotch",
         abv=43.0, country="Scotland", region="Speyside", price_min=55, price_max=75,
         quality_tier="premium", color="Rich amber",
         description="Matured exclusively in hand-picked sherry-seasoned oak casks from Jerez, Spain. The benchmark for sherry-influenced Scotch.",
         tasting_notes="Dried fruits, vanilla, ginger, cinnamon, and a warming wood spice finish.",
         flavor_sweet=7, flavor_fruity=7, flavor_woody=7, flavor_spicy=6, flavor_earthy=4),

    dict(name="Johnnie Walker Black Label", brand="Johnnie Walker", type="whiskey", subtype="Blended Scotch",
         abv=40.0, country="Scotland", region="Blended", price_min=30, price_max=42,
         quality_tier="mid-range", color="Deep amber",
         description="Aged for a minimum of 12 years, Black Label is a smooth, complex blended Scotch known for its subtle smokiness.",
         tasting_notes="Sweet vanilla, dark fruit, smoky notes, long peppery finish.",
         flavor_sweet=5, flavor_smoky=5, flavor_fruity=4, flavor_woody=5, flavor_spicy=5),

    dict(name="Laphroaig 10 Year", brand="Laphroaig", type="whiskey", subtype="Single Malt Scotch",
         abv=43.0, country="Scotland", region="Islay", price_min=40, price_max=58,
         quality_tier="premium", color="Pale amber",
         description="One of the most distinctive whiskies in the world — intensely peaty and medicinal with a devoted global following.",
         tasting_notes="Heavy smoke, iodine, seaweed, vanilla, and a surprisingly sweet long finish.",
         flavor_smoky=10, flavor_earthy=8, flavor_sweet=4, flavor_bitter=5, flavor_crisp=3),

    dict(name="Jack Daniel's Old No.7", brand="Jack Daniel's", type="whiskey", subtype="Tennessee Whiskey",
         abv=40.0, country="USA", region="Tennessee", price_min=25, price_max=35,
         quality_tier="mid-range", color="Amber",
         description="America's best-selling whiskey, charcoal-mellowed through 10 feet of sugar maple charcoal before maturation.",
         tasting_notes="Vanilla, caramel, toasted oak, subtle banana, and a smooth charcoal-filtered finish.",
         flavor_sweet=7, flavor_woody=5, flavor_earthy=4, flavor_fruity=3, flavor_smoky=3),

    dict(name="Maker's Mark", brand="Maker's Mark", type="whiskey", subtype="Bourbon",
         abv=45.0, country="USA", region="Kentucky", price_min=25, price_max=36,
         quality_tier="mid-range", color="Deep amber",
         description="Handmade in small batches, Maker's Mark uses red winter wheat instead of rye for a distinctively smooth, sweeter bourbon.",
         tasting_notes="Caramel, vanilla, red berries, and a soft, lingering wheat-driven sweetness.",
         flavor_sweet=8, flavor_fruity=5, flavor_woody=4, flavor_creamy=4, flavor_spicy=2),

    dict(name="Woodford Reserve Distiller's Select", brand="Woodford Reserve", type="whiskey", subtype="Bourbon",
         abv=43.2, country="USA", region="Kentucky", price_min=35, price_max=48,
         quality_tier="mid-range", color="Rich amber",
         description="A rich, full-bodied Kentucky Straight Bourbon made at America's smallest and oldest distillery, triple-distilled in copper pot stills.",
         tasting_notes="Dried fruit, vanilla, toasted oak, spice, and a chocolate-orange finish.",
         flavor_sweet=6, flavor_fruity=6, flavor_woody=7, flavor_spicy=6, flavor_earthy=4),

    dict(name="Jameson Irish Whiskey", brand="Jameson", type="whiskey", subtype="Irish Blended",
         abv=40.0, country="Ireland", region="Cork", price_min=22, price_max=34,
         quality_tier="mid-range", color="Pale gold",
         description="Triple-distilled for exceptional smoothness. The world's best-selling Irish whiskey.",
         tasting_notes="Light floral notes, fresh fruit, toasted wood, vanilla, and a clean, crisp finish.",
         flavor_sweet=6, flavor_fruity=5, flavor_floral=5, flavor_crisp=6, flavor_woody=3),

    dict(name="Wild Turkey 101", brand="Wild Turkey", type="whiskey", subtype="Bourbon",
         abv=50.5, country="USA", region="Kentucky", price_min=22, price_max=32,
         quality_tier="budget", color="Amber",
         description="Boldly high-proof for a budget bourbon, aged in new charred American white oak barrels. A legendary American whiskey.",
         tasting_notes="Bold caramel, vanilla, honey, toasted grain, sharp pepper on the finish.",
         flavor_sweet=6, flavor_spicy=7, flavor_woody=6, flavor_earthy=4, flavor_bitter=3),

    dict(name="Blanton's Original Single Barrel", brand="Blanton's", type="whiskey", subtype="Bourbon",
         abv=46.5, country="USA", region="Kentucky", price_min=60, price_max=80,
         quality_tier="premium", color="Deep honey",
         description="The world's first commercially bottled single barrel bourbon, each bottle traceable to one specific barrel number.",
         tasting_notes="Honey, citrus, spice, dried fruit, creamy vanilla, and a long caramel finish.",
         flavor_sweet=7, flavor_fruity=6, flavor_spicy=5, flavor_woody=6, flavor_creamy=5),

    dict(name="Lagavulin 16 Year", brand="Lagavulin", type="whiskey", subtype="Single Malt Scotch",
         abv=43.0, country="Scotland", region="Islay", price_min=75, price_max=100,
         quality_tier="premium", color="Deep gold",
         description="Often cited as the pinnacle of Islay single malts — intensely smoky yet with remarkable depth and elegance.",
         tasting_notes="Intense peat smoke, seaweed, dried fruit, dark chocolate, and sea salt.",
         flavor_smoky=10, flavor_earthy=8, flavor_bitter=5, flavor_fruity=4, flavor_sweet=4),

    dict(name="Redbreast 12 Year", brand="Redbreast", type="whiskey", subtype="Irish Single Pot Still",
         abv=40.0, country="Ireland", region="Cork", price_min=55, price_max=70,
         quality_tier="premium", color="Golden amber",
         description="The flagship of the Single Pot Still style — Ireland's most characterful whiskey tradition, triple-distilled with malted and unmalted barley.",
         tasting_notes="Plump orchard fruit, spice, toasted grain, nuts, and a long sherry-influenced finish.",
         flavor_fruity=7, flavor_sweet=6, flavor_spicy=5, flavor_woody=5, flavor_earthy=4),

    # ── VODKAS ─────────────────────────────────────────────────────────────
    dict(name="Grey Goose", brand="Grey Goose", type="vodka", subtype="French Wheat Vodka",
         abv=40.0, country="France", region="Cognac", price_min=35, price_max=48,
         quality_tier="premium", color="Crystal clear",
         description="Distilled from single-origin Picardie wheat and filtered through Champagne limestone. The gold standard of ultra-premium vodka.",
         tasting_notes="Clean, smooth, light grain sweetness, subtle citrus, and a silky finish.",
         flavor_sweet=4, flavor_crisp=8, flavor_floral=3, flavor_fruity=2),

    dict(name="Belvedere", brand="Belvedere", type="vodka", subtype="Polish Rye Vodka",
         abv=40.0, country="Poland", region="Mazovia", price_min=35, price_max=50,
         quality_tier="premium", color="Crystal clear",
         description="Made from 100% Dankowskie Gold Rye using traditional Polish methods. The world's first luxury vodka.",
         tasting_notes="Creamy vanilla, white pepper, subtle rye spice, exceptionally clean finish.",
         flavor_crisp=8, flavor_sweet=3, flavor_spicy=3, flavor_creamy=5),

    dict(name="Absolut Original", brand="Absolut", type="vodka", subtype="Swedish Winter Wheat Vodka",
         abv=40.0, country="Sweden", region="Åhus", price_min=18, price_max=28,
         quality_tier="mid-range", color="Crystal clear",
         description="Continuously distilled from winter wheat with no additives. Produced in one place — Åhus, Sweden.",
         tasting_notes="Rich, full-bodied, subtle grain sweetness with hints of dried fruit and a lingering finish.",
         flavor_sweet=4, flavor_crisp=7, flavor_fruity=2),

    dict(name="Tito's Handmade Vodka", brand="Tito's", type="vodka", subtype="Corn Vodka",
         abv=40.0, country="USA", region="Texas", price_min=20, price_max=30,
         quality_tier="mid-range", color="Crystal clear",
         description="Made in old-fashioned pot stills from 100% corn, distilled six times. America's most popular craft vodka.",
         tasting_notes="Slightly sweet corn, neutral clean palate, smooth and easy finish.",
         flavor_sweet=5, flavor_crisp=7),

    dict(name="Smirnoff No. 21", brand="Smirnoff", type="vodka", subtype="Triple-Distilled Vodka",
         abv=37.5, country="USA", region="National", price_min=12, price_max=18,
         quality_tier="budget", color="Crystal clear",
         description="The world's best-selling vodka. Triple-distilled and ten-times filtered for a clean, approachable character.",
         tasting_notes="Neutral, clean, mildly grainy with a short, smooth finish.",
         flavor_crisp=7, flavor_sweet=2),

    # ── RUMS ───────────────────────────────────────────────────────────────
    dict(name="Diplomatico Reserva Exclusiva", brand="Diplomatico", type="rum", subtype="Aged Rum",
         abv=40.0, country="Venezuela", region="Andes", price_min=38, price_max=55,
         quality_tier="premium", color="Deep mahogany",
         description="Aged for up to 12 years in bourbon and sherry casks, this is widely considered one of the finest sipping rums in the world.",
         tasting_notes="Rich toffee, dark chocolate, dried apricot, vanilla, orange peel, and warming spice.",
         flavor_sweet=9, flavor_fruity=6, flavor_woody=6, flavor_spicy=5, flavor_creamy=5),

    dict(name="Mount Gay XO", brand="Mount Gay", type="rum", subtype="Extra Old Rum",
         abv=43.0, country="Barbados", region="Saint Lucy", price_min=55, price_max=70,
         quality_tier="premium", color="Deep amber",
         description="From the world's oldest rum distillery (est. 1703), XO is a blend of rums aged 8–15 years in charred bourbon and American oak casks.",
         tasting_notes="Banana, tropical fruit, almond, vanilla, toasted wood, and a long, warm finish.",
         flavor_fruity=7, flavor_sweet=6, flavor_woody=7, flavor_earthy=4, flavor_spicy=4),

    dict(name="Bacardi Superior", brand="Bacardi", type="rum", subtype="White Rum",
         abv=40.0, country="Cuba", region="Santiago de Cuba", price_min=12, price_max=18,
         quality_tier="budget", color="Clear",
         description="The iconic white rum, charcoal-filtered for exceptional clarity. The world's most-awarded spirit.",
         tasting_notes="Crisp citrus, light sweetness, subtle almond, clean and easy.",
         flavor_sweet=5, flavor_fruity=5, flavor_crisp=6),

    dict(name="Captain Morgan Original Spiced", brand="Captain Morgan", type="rum", subtype="Spiced Rum",
         abv=35.0, country="Jamaica", region="Kingston", price_min=15, price_max=23,
         quality_tier="budget", color="Amber",
         description="The ultimate party rum — Caribbean rum blended with natural spices and flavours.",
         tasting_notes="Vanilla, caramel, clove, cinnamon, and a smooth, easy sweetness.",
         flavor_sweet=8, flavor_spicy=7, flavor_fruity=3, flavor_creamy=4),

    dict(name="Havana Club 7 Años", brand="Havana Club", type="rum", subtype="Aged Rum",
         abv=40.0, country="Cuba", region="Havana", price_min=28, price_max=40,
         quality_tier="mid-range", color="Rich amber",
         description="The quintessential Cuban aged rum, crafted to be savoured neat or in a premium Cuba Libre.",
         tasting_notes="Tobacco, dark fruit, caramel, toasted wood, and a smooth, lingering finish.",
         flavor_sweet=6, flavor_earthy=6, flavor_fruity=5, flavor_woody=6, flavor_smoky=3),

    dict(name="Appleton Estate 12 Year", brand="Appleton Estate", type="rum", subtype="Aged Rum",
         abv=43.0, country="Jamaica", region="Nassau Valley", price_min=35, price_max=48,
         quality_tier="premium", color="Deep amber",
         description="Blended from pot and column still rums aged in American oak bourbon barrels in the tropical Jamaican climate.",
         tasting_notes="Spiced fruit cake, orange peel, molasses, walnut, gingerbread, and a warm, long finish.",
         flavor_fruity=7, flavor_spicy=6, flavor_sweet=6, flavor_earthy=4, flavor_woody=5),

    # ── TEQUILAS & MEZCAL ──────────────────────────────────────────────────
    dict(name="Patrón Silver", brand="Patrón", type="tequila", subtype="Blanco",
         abv=40.0, country="Mexico", region="Jalisco", price_min=38, price_max=52,
         quality_tier="premium", color="Crystal clear",
         description="Handcrafted in small batches at the Hacienda Patrón distillery, made from 100% Weber Blue Agave.",
         tasting_notes="Fresh agave, citrus blossom, light pepper, and a crisp, clean finish.",
         flavor_crisp=8, flavor_fruity=5, flavor_spicy=4, flavor_floral=5, flavor_earthy=4),

    dict(name="Don Julio 1942", brand="Don Julio", type="tequila", subtype="Añejo",
         abv=38.0, country="Mexico", region="Jalisco", price_min=135, price_max=175,
         quality_tier="ultra-premium", color="Deep gold",
         description="Aged for a minimum of two and a half years, 1942 is the benchmark for luxury añejo tequila.",
         tasting_notes="Rich caramel, vanilla, dried fruit, toasted agave, and a long, warm chocolate finish.",
         flavor_sweet=8, flavor_woody=7, flavor_fruity=5, flavor_creamy=6, flavor_earthy=5),

    dict(name="Casamigos Blanco", brand="Casamigos", type="tequila", subtype="Blanco",
         abv=40.0, country="Mexico", region="Jalisco", price_min=40, price_max=55,
         quality_tier="premium", color="Crystal clear",
         description="Co-founded by George Clooney, Casamigos is ultra-smooth with almost no burn, designed to be drunk at room temperature.",
         tasting_notes="Smooth agave, vanilla, citrus, light caramel, and a clean, easy finish.",
         flavor_sweet=6, flavor_fruity=5, flavor_crisp=7, flavor_floral=4),

    dict(name="Jose Cuervo Especial Gold", brand="Jose Cuervo", type="tequila", subtype="Joven",
         abv=38.0, country="Mexico", region="Jalisco", price_min=18, price_max=26,
         quality_tier="budget", color="Pale gold",
         description="The world's best-selling tequila — a mix of reposado and other aged tequilas for a smooth, golden colour.",
         tasting_notes="Agave, vanilla, light wood, and a mildly sweet, accessible finish.",
         flavor_sweet=6, flavor_earthy=4, flavor_woody=3, flavor_fruity=2),

    dict(name="Del Maguey Vida Mezcal", brand="Del Maguey", type="mezcal", subtype="Single Village",
         abv=42.0, country="Mexico", region="Oaxaca", price_min=40, price_max=58,
         quality_tier="premium", color="Pale straw",
         description="Produced by Zapotec villagers using generations-old traditions — wild agave roasted in earthen pits then fermented in open-air wooden vats.",
         tasting_notes="Rustic smoke, roasted earth, tropical fruit, citrus peel, mineral, and a long wild finish.",
         flavor_smoky=8, flavor_earthy=9, flavor_fruity=5, flavor_bitter=4, flavor_crisp=4),

    # ── WINES ──────────────────────────────────────────────────────────────
    dict(name="Opus One", brand="Opus One Winery", type="wine", subtype="Cabernet Sauvignon Blend",
         abv=14.5, country="USA", region="Napa Valley, California", price_min=380, price_max=450,
         quality_tier="ultra-premium", color="Deep ruby-black",
         description="The iconic Napa Bordeaux-style blend — a collaboration between Robert Mondavi and Baron Philippe de Rothschild, produced since 1979.",
         tasting_notes="Blackcurrant, dark cherry, cedar, graphite, violet, and a structured, long finish.",
         flavor_fruity=9, flavor_earthy=7, flavor_woody=7, flavor_bitter=4, flavor_floral=4),

    dict(name="Veuve Clicquot Yellow Label Brut", brand="Veuve Clicquot", type="champagne", subtype="Non-Vintage Brut",
         abv=12.0, country="France", region="Champagne, Reims", price_min=55, price_max=72,
         quality_tier="premium", color="Pale gold with fine bubbles",
         description="The most recognisable champagne in the world, defined by its yellow label and signature full-bodied, house style.",
         tasting_notes="White peach, citrus, brioche, toasted yeast, creamy mouthfeel, and a dry, persistent finish.",
         flavor_fruity=6, flavor_crisp=7, flavor_creamy=6, flavor_floral=5, flavor_bitter=3),

    dict(name="Kim Crawford Sauvignon Blanc", brand="Kim Crawford", type="wine", subtype="Sauvignon Blanc",
         abv=12.5, country="New Zealand", region="Marlborough", price_min=15, price_max=22,
         quality_tier="mid-range", color="Pale straw",
         description="A benchmark Marlborough Sauvignon Blanc — vibrant, zingy, and intensely fruity.",
         tasting_notes="Passionfruit, grapefruit, fresh-cut grass, and a crisp, zingy finish.",
         flavor_fruity=8, flavor_crisp=8, flavor_floral=4, flavor_bitter=3),

    dict(name="Santa Margherita Pinot Grigio", brand="Santa Margherita", type="wine", subtype="Pinot Grigio",
         abv=12.5, country="Italy", region="Alto Adige", price_min=22, price_max=30,
         quality_tier="mid-range", color="Pale golden",
         description="The wine that popularised Pinot Grigio worldwide — elegant, refreshing, and consistently excellent.",
         tasting_notes="Golden apple, citrus, white peach, almond, and a clean, refreshing finish.",
         flavor_fruity=7, flavor_crisp=7, flavor_floral=4, flavor_sweet=4),

    dict(name="Meiomi Pinot Noir", brand="Meiomi", type="wine", subtype="Pinot Noir",
         abv=13.5, country="USA", region="Sonoma, Monterey, Santa Barbara", price_min=18, price_max=26,
         quality_tier="mid-range", color="Medium ruby",
         description="A silky Californian Pinot Noir blended from three iconic coastal regions for complexity.",
         tasting_notes="Strawberry, blackberry, raspberry, mocha, and a smooth, velvety finish.",
         flavor_fruity=8, flavor_sweet=6, flavor_earthy=4, flavor_creamy=4),

    dict(name="Whispering Angel Rosé", brand="Chateau d'Esclans", type="wine", subtype="Rosé",
         abv=13.0, country="France", region="Provence", price_min=22, price_max=32,
         quality_tier="premium", color="Pale blush",
         description="The world's most iconic Provence rosé — elegant, refined, and the benchmark for the pale pink style.",
         tasting_notes="Strawberry blossom, peach, citrus, fresh cream, and a dry, mineral finish.",
         flavor_fruity=6, flavor_floral=7, flavor_crisp=6, flavor_creamy=4),

    # ── BEERS ──────────────────────────────────────────────────────────────
    dict(name="Guinness Draught", brand="Guinness", type="beer", subtype="Dry Irish Stout",
         abv=4.2, country="Ireland", region="Dublin", price_min=2, price_max=5,
         quality_tier="mid-range", color="Opaque black with cream head",
         description="The world's most famous stout — nitrogen-infused for a velvety pour and iconic cream head.",
         tasting_notes="Roasted barley, coffee, dark chocolate, a hint of caramel, and a dry, bitter finish.",
         flavor_bitter=8, flavor_earthy=7, flavor_sweet=3, flavor_creamy=7, flavor_smoky=3),

    dict(name="Heineken Lager Beer", brand="Heineken", type="beer", subtype="Euro Pale Lager",
         abv=5.0, country="Netherlands", region="Amsterdam", price_min=1, price_max=4,
         quality_tier="budget", color="Clear pale gold",
         description="One of the world's most recognised beer brands — crisp, refreshing, and consistently clean.",
         tasting_notes="Light malted barley, subtle hops, mild bitterness, clean and crisp finish.",
         flavor_crisp=8, flavor_bitter=4, flavor_sweet=2),

    dict(name="Corona Extra", brand="Corona", type="beer", subtype="Pale Lager",
         abv=4.6, country="Mexico", region="Coahuila", price_min=1, price_max=4,
         quality_tier="budget", color="Pale straw",
         description="Mexico's most famous beer export, best served ice-cold with a wedge of lime.",
         tasting_notes="Light, refreshing, mildly sweet grain, touch of citrus, clean and approachable.",
         flavor_crisp=7, flavor_sweet=3, flavor_fruity=3, flavor_bitter=2),

    dict(name="Blue Moon Belgian White", brand="Blue Moon", type="beer", subtype="Witbier",
         abv=5.4, country="USA", region="Denver, Colorado", price_min=2, price_max=5,
         quality_tier="mid-range", color="Hazy golden-orange",
         description="An unfiltered Belgian-style wheat ale brewed with Valencia orange peel and coriander.",
         tasting_notes="Orange citrus, coriander, wheat, creamy mouthfeel, and a smooth, refreshing finish.",
         flavor_fruity=7, flavor_sweet=5, flavor_floral=4, flavor_spicy=4, flavor_crisp=5),

    dict(name="Sierra Nevada Pale Ale", brand="Sierra Nevada", type="beer", subtype="American Pale Ale",
         abv=5.6, country="USA", region="Chico, California", price_min=2, price_max=5,
         quality_tier="mid-range", color="Deep golden",
         description="The beer that launched the American craft beer revolution in 1980. A benchmark for the style.",
         tasting_notes="Cascade hops, grapefruit, pine resin, caramel malt, and a clean, bitter finish.",
         flavor_bitter=7, flavor_fruity=6, flavor_crisp=6, flavor_earthy=4),

    dict(name="Hoegaarden Original", brand="Hoegaarden", type="beer", subtype="Belgian Witbier",
         abv=4.9, country="Belgium", region="Hoegaarden", price_min=2, price_max=4,
         quality_tier="mid-range", color="Hazy pale white",
         description="The original Belgian white beer — naturally cloudy and spiced with dried curaçao orange and coriander.",
         tasting_notes="Coriander, orange peel, clove, wheat, creamy texture, and a refreshing, slightly tart finish.",
         flavor_fruity=6, flavor_spicy=5, flavor_floral=5, flavor_sweet=4, flavor_crisp=5),

    # ── GINS ───────────────────────────────────────────────────────────────
    dict(name="Hendrick's", brand="Hendrick's", type="gin", subtype="Scottish Gin",
         abv=41.4, country="Scotland", region="Girvan", price_min=28, price_max=40,
         quality_tier="premium", color="Crystal clear",
         description="Distilled in Bennett and Carter stills, then infused with Bulgarian rose and cucumber — an eccentric classic.",
         tasting_notes="Cucumber, rose, juniper, angelica, light citrus, and a floral, refreshing finish.",
         flavor_floral=9, flavor_crisp=8, flavor_fruity=4, flavor_sweet=3, flavor_earthy=3),

    dict(name="Tanqueray London Dry", brand="Tanqueray", type="gin", subtype="London Dry",
         abv=47.3, country="England", region="London", price_min=22, price_max=32,
         quality_tier="mid-range", color="Crystal clear",
         description="The gold standard London Dry Gin, made with just four botanicals: juniper, coriander, angelica root, and liquorice.",
         tasting_notes="Bold juniper, fresh citrus, coriander spice, and a dry, clean finish.",
         flavor_crisp=8, flavor_spicy=5, flavor_bitter=5, flavor_floral=4, flavor_earthy=3),

    dict(name="Bombay Sapphire", brand="Bombay Sapphire", type="gin", subtype="London Dry",
         abv=47.0, country="England", region="Hampshire", price_min=20, price_max=30,
         quality_tier="mid-range", color="Crystal clear",
         description="Vapour-infused with 10 hand-selected botanicals in a unique Carterhead still for a lighter, more aromatic style.",
         tasting_notes="Juniper, lemon, coriander, grains of paradise, floral, and a smooth, delicate finish.",
         flavor_floral=7, flavor_crisp=7, flavor_spicy=5, flavor_fruity=4, flavor_bitter=3),

    dict(name="The Botanist Islay Dry Gin", brand="The Botanist", type="gin", subtype="Islay Dry",
         abv=46.0, country="Scotland", region="Islay", price_min=38, price_max=52,
         quality_tier="premium", color="Crystal clear",
         description="Distilled from 22 hand-foraged local botanicals on the Isle of Islay — one of the most complex gins in the world.",
         tasting_notes="Complex herbal and floral, wild thyme, chamomile, juniper, and a lingering botanical finish.",
         flavor_floral=9, flavor_earthy=7, flavor_spicy=5, flavor_crisp=7, flavor_bitter=4),

    # ── COGNAC / BRANDY ────────────────────────────────────────────────────
    dict(name="Hennessy VS", brand="Hennessy", type="brandy", subtype="Cognac VS",
         abv=40.0, country="France", region="Cognac", price_min=33, price_max=45,
         quality_tier="mid-range", color="Amber",
         description="A blend of over 40 eaux-de-vie aged in French oak — the world's most famous cognac.",
         tasting_notes="Fruity, woody, toasted oak, light vanilla, grapes, and a warm, short finish.",
         flavor_fruity=7, flavor_woody=6, flavor_sweet=5, flavor_spicy=4, flavor_earthy=3),

    dict(name="Rémy Martin VSOP", brand="Rémy Martin", type="brandy", subtype="Cognac VSOP",
         abv=40.0, country="France", region="Cognac (Fine Champagne)", price_min=48, price_max=68,
         quality_tier="premium", color="Deep amber",
         description="Made exclusively from Grande and Petite Champagne crus — the finest cognac growing areas.",
         tasting_notes="Rich fruit, floral notes, vanilla, spices, dried fruit, and a long, elegant finish.",
         flavor_fruity=8, flavor_floral=6, flavor_sweet=6, flavor_spicy=5, flavor_woody=5),

    dict(name="Armagnac Château de Laubade XO", brand="Château de Laubade", type="brandy", subtype="Armagnac XO",
         abv=40.0, country="France", region="Bas-Armagnac", price_min=55, price_max=78,
         quality_tier="premium", color="Deep mahogany",
         description="The rustic cousin of cognac — column-distilled once for more character, aged in Gascon black oak.",
         tasting_notes="Prunes, apricot, orange peel, walnuts, coffee, caramel, and a long, complex finish.",
         flavor_fruity=7, flavor_earthy=7, flavor_sweet=7, flavor_woody=7, flavor_spicy=4),

    # ── LIQUEURS ───────────────────────────────────────────────────────────
    dict(name="Baileys Original Irish Cream", brand="Baileys", type="liqueur", subtype="Irish Cream",
         abv=17.0, country="Ireland", region="Dublin", price_min=22, price_max=30,
         quality_tier="mid-range", color="Cream brown",
         description="A unique blend of fresh Irish cream, Irish whiskey, and a touch of cocoa — the world's best-selling liqueur.",
         tasting_notes="Cream, milk chocolate, coffee, vanilla, Irish whiskey warmth, and a silky smooth finish.",
         flavor_creamy=10, flavor_sweet=9, flavor_fruity=2, flavor_earthy=2),

    dict(name="Kahlúa Coffee Liqueur", brand="Kahlúa", type="liqueur", subtype="Coffee Liqueur",
         abv=20.0, country="Mexico", region="Veracruz", price_min=20, price_max=28,
         quality_tier="mid-range", color="Deep brown",
         description="Made with 100% Arabica coffee beans grown in Veracruz — the world's leading coffee liqueur.",
         tasting_notes="Strong roasted coffee, vanilla, caramel, chocolate, and a sweet, warm finish.",
         flavor_sweet=8, flavor_earthy=7, flavor_bitter=5, flavor_creamy=5),

    dict(name="Grand Marnier Cordon Rouge", brand="Grand Marnier", type="liqueur", subtype="Orange Liqueur",
         abv=40.0, country="France", region="Paris", price_min=35, price_max=48,
         quality_tier="premium", color="Rich amber",
         description="A blend of fine cognac and distilled wild tropical orange liqueur — a uniquely French luxury.",
         tasting_notes="Bitter orange, cognac warmth, vanilla, caramel, and a long, complex finish.",
         flavor_fruity=8, flavor_sweet=7, flavor_bitter=5, flavor_woody=4),

    dict(name="Cointreau", brand="Cointreau", type="liqueur", subtype="Triple Sec",
         abv=40.0, country="France", region="Saint-Barthélemy-d'Anjou", price_min=32, price_max=45,
         quality_tier="premium", color="Crystal clear",
         description="The original triple sec, made from sun-dried sweet and bitter orange peels. Essential in countless cocktails.",
         tasting_notes="Fresh orange zest, clean citrus, subtle sweetness, and a clean dry finish.",
         flavor_fruity=9, flavor_sweet=6, flavor_bitter=4, flavor_crisp=5),
]


COCKTAILS = [
    dict(name="Old Fashioned", base_spirit="whiskey",
         difficulty="easy", mood_tags="relaxed,cozy,stressed", abv_estimate=32.0,
         glass_type="Rocks glass", garnish="Orange peel, Maraschino cherry",
         flavor_profile="sweet,woody,bitter",
         description="The original cocktail — a simple, spirit-forward classic that lets the whiskey shine.",
         ingredients=json.dumps([
             {"item": "Bourbon or Rye Whiskey", "amount": "60ml"},
             {"item": "Simple syrup", "amount": "5ml"},
             {"item": "Angostura bitters", "amount": "2 dashes"},
             {"item": "Orange peel", "amount": "1 strip"},
         ]),
         instructions="Add sugar syrup and bitters to a chilled rocks glass. Add a large ice cube. Pour the whiskey over. Stir gently for 30 seconds. Express the orange peel over the glass to release its oils, then drop it in."),

    dict(name="Manhattan", base_spirit="whiskey",
         difficulty="easy", mood_tags="romantic,relaxed,cozy", abv_estimate=28.0,
         glass_type="Coupe glass", garnish="Maraschino cherry",
         flavor_profile="sweet,bitter,woody,fruity",
         description="A timeless, sophisticated cocktail that has defined elegance in a glass for over 150 years.",
         ingredients=json.dumps([
             {"item": "Rye or Bourbon Whiskey", "amount": "60ml"},
             {"item": "Sweet Vermouth", "amount": "30ml"},
             {"item": "Angostura Bitters", "amount": "2 dashes"},
         ]),
         instructions="Combine all ingredients in a mixing glass with ice. Stir for 30 seconds until cold and diluted. Strain into a chilled coupe glass. Garnish with a maraschino cherry."),

    dict(name="Negroni", base_spirit="gin",
         difficulty="easy", mood_tags="adventurous,relaxed,party", abv_estimate=24.0,
         glass_type="Rocks glass", garnish="Orange peel",
         flavor_profile="bitter,sweet,floral,earthy",
         description="The perfectly balanced cocktail — equal parts bittersweet, perfectly stirred.",
         ingredients=json.dumps([
             {"item": "London Dry Gin", "amount": "30ml"},
             {"item": "Campari", "amount": "30ml"},
             {"item": "Sweet Vermouth", "amount": "30ml"},
         ]),
         instructions="Combine all ingredients in a rocks glass over a large ice cube. Stir briefly. Garnish with a large orange peel."),

    dict(name="Classic Martini", base_spirit="gin",
         difficulty="medium", mood_tags="romantic,celebratory,relaxed", abv_estimate=30.0,
         glass_type="Martini glass", garnish="Lemon twist or olive",
         flavor_profile="crisp,floral,bitter",
         description="The ultimate expression of elegance — a cocktail that requires technique and rewards with perfection.",
         ingredients=json.dumps([
             {"item": "London Dry Gin", "amount": "60ml"},
             {"item": "Dry Vermouth", "amount": "10ml"},
         ]),
         instructions="Combine gin and vermouth in a mixing glass with ice. Stir for 45 seconds until very cold. Strain into a chilled Martini glass. Express a lemon twist over the surface and either drop in or garnish the rim."),

    dict(name="Margarita", base_spirit="tequila",
         difficulty="easy", mood_tags="party,celebratory,adventurous", abv_estimate=20.0,
         glass_type="Margarita or rocks glass", garnish="Salt rim, lime wheel",
         flavor_profile="crisp,fruity,bitter",
         description="Mexico's greatest cocktail export — a bright, tart, salty celebration in a glass.",
         ingredients=json.dumps([
             {"item": "Blanco Tequila", "amount": "50ml"},
             {"item": "Cointreau or Triple Sec", "amount": "25ml"},
             {"item": "Fresh lime juice", "amount": "25ml"},
         ]),
         instructions="Rim a rocks glass with salt. Combine tequila, Cointreau, and lime juice in a shaker with ice. Shake vigorously for 15 seconds. Strain into the prepared glass over ice. Garnish with a lime wheel."),

    dict(name="Mojito", base_spirit="rum",
         difficulty="easy", mood_tags="party,relaxed,adventurous", abv_estimate=12.0,
         glass_type="Highball glass", garnish="Fresh mint sprig, lime wheel",
         flavor_profile="crisp,fruity,sweet,floral",
         description="Cuba's most famous cocktail — fresh, minty, and impossibly refreshing.",
         ingredients=json.dumps([
             {"item": "White Rum", "amount": "50ml"},
             {"item": "Fresh lime juice", "amount": "25ml"},
             {"item": "Simple syrup", "amount": "15ml"},
             {"item": "Fresh mint leaves", "amount": "8–10 leaves"},
             {"item": "Club soda", "amount": "Top up"},
         ]),
         instructions="Gently muddle mint with lime juice and syrup in a highball glass. Add rum and stir. Fill with crushed ice. Top with club soda. Stir briefly and garnish with a mint sprig and lime wheel."),

    dict(name="Daiquiri", base_spirit="rum",
         difficulty="easy", mood_tags="party,relaxed,adventurous", abv_estimate=22.0,
         glass_type="Coupe glass", garnish="Lime wheel",
         flavor_profile="crisp,fruity,sweet",
         description="Hemingway's favourite and a masterclass in balance — perfectly showcasing the beauty of simplicity.",
         ingredients=json.dumps([
             {"item": "White Rum", "amount": "60ml"},
             {"item": "Fresh lime juice", "amount": "25ml"},
             {"item": "Simple syrup", "amount": "15ml"},
         ]),
         instructions="Combine all ingredients in a shaker with ice. Shake hard for 10–15 seconds. Double-strain into a chilled coupe glass. Garnish with a lime wheel on the rim."),

    dict(name="Piña Colada", base_spirit="rum",
         difficulty="easy", mood_tags="party,relaxed,cozy", abv_estimate=13.0,
         glass_type="Hurricane or large glass", garnish="Pineapple wedge, maraschino cherry",
         flavor_profile="sweet,fruity,creamy",
         description="The Puerto Rican national drink — tropical, creamy, and completely irresistible.",
         ingredients=json.dumps([
             {"item": "White Rum", "amount": "50ml"},
             {"item": "Coconut cream", "amount": "30ml"},
             {"item": "Fresh pineapple juice", "amount": "90ml"},
         ]),
         instructions="Blend all ingredients with a cup of crushed ice until smooth. Pour into a chilled hurricane glass. Garnish with a pineapple wedge and cherry."),

    dict(name="Moscow Mule", base_spirit="vodka",
         difficulty="easy", mood_tags="party,relaxed,adventurous", abv_estimate=10.0,
         glass_type="Copper mug", garnish="Lime wedge, mint sprig",
         flavor_profile="crisp,spicy,fruity",
         description="A crisp, refreshing vodka cocktail with a ginger kick — best served in its iconic copper mug.",
         ingredients=json.dumps([
             {"item": "Vodka", "amount": "50ml"},
             {"item": "Ginger Beer", "amount": "120ml"},
             {"item": "Fresh lime juice", "amount": "15ml"},
         ]),
         instructions="Fill a copper mug with ice. Pour in the vodka and lime juice. Top with ginger beer and stir briefly. Garnish with a lime wedge and mint."),

    dict(name="Cosmopolitan", base_spirit="vodka",
         difficulty="easy", mood_tags="party,romantic,celebratory", abv_estimate=20.0,
         glass_type="Martini glass", garnish="Flamed orange peel",
         flavor_profile="fruity,crisp,sweet",
         description="The cocktail that defined the late 90s — tart, pink, and endlessly glamorous.",
         ingredients=json.dumps([
             {"item": "Citrus Vodka", "amount": "40ml"},
             {"item": "Cointreau", "amount": "15ml"},
             {"item": "Cranberry juice", "amount": "30ml"},
             {"item": "Fresh lime juice", "amount": "15ml"},
         ]),
         instructions="Combine all ingredients in a shaker with ice. Shake well. Strain into a chilled martini glass. Flambé an orange peel and drop it in."),

    dict(name="Whiskey Sour", base_spirit="whiskey",
         difficulty="medium", mood_tags="relaxed,party,stressed", abv_estimate=18.0,
         glass_type="Rocks or sour glass", garnish="Cherry, orange slice, dehydrated lemon",
         flavor_profile="fruity,sweet,bitter",
         description="A perfectly balanced tart-sweet classic made more luxurious with a frothy egg white foam.",
         ingredients=json.dumps([
             {"item": "Bourbon", "amount": "60ml"},
             {"item": "Fresh lemon juice", "amount": "25ml"},
             {"item": "Simple syrup", "amount": "15ml"},
             {"item": "Egg white (optional)", "amount": "1"},
         ]),
         instructions="If using egg white, dry shake all ingredients without ice for 15 seconds. Add ice and shake again. Strain into a rocks glass over a large ice cube. Garnish with a cherry and dehydrated lemon slice."),

    dict(name="Espresso Martini", base_spirit="vodka",
         difficulty="medium", mood_tags="party,celebratory,adventurous", abv_estimate=18.0,
         glass_type="Martini glass", garnish="3 coffee beans",
         flavor_profile="earthy,sweet,bitter,creamy",
         description="Dick Bradsell's legendary creation — the perfect cocktail for those who want to be drunk AND awake.",
         ingredients=json.dumps([
             {"item": "Vodka", "amount": "50ml"},
             {"item": "Kahlúa", "amount": "25ml"},
             {"item": "Fresh espresso (cooled)", "amount": "30ml"},
             {"item": "Simple syrup", "amount": "5ml"},
         ]),
         instructions="Combine all ingredients in a shaker with ice. Shake extremely vigorously for 15 seconds — this creates the foam. Double-strain into a chilled martini glass. Garnish with 3 coffee beans."),

    dict(name="Tom Collins", base_spirit="gin",
         difficulty="easy", mood_tags="party,relaxed,adventurous", abv_estimate=11.0,
         glass_type="Collins glass", garnish="Lemon wheel, cherry",
         flavor_profile="crisp,fruity,floral",
         description="A long, refreshing, lemony gin drink perfect for warm evenings.",
         ingredients=json.dumps([
             {"item": "London Dry Gin", "amount": "50ml"},
             {"item": "Fresh lemon juice", "amount": "25ml"},
             {"item": "Simple syrup", "amount": "15ml"},
             {"item": "Club soda", "amount": "Top up (approx 60ml)"},
         ]),
         instructions="Combine gin, lemon juice, and syrup in a shaker with ice. Shake briefly. Strain into a Collins glass filled with ice. Top with club soda. Garnish with a lemon wheel and cherry."),

    dict(name="Dark & Stormy", base_spirit="rum",
         difficulty="easy", mood_tags="party,adventurous,cozy", abv_estimate=12.0,
         glass_type="Highball glass", garnish="Lime wedge",
         flavor_profile="spicy,sweet,fruity",
         description="Bermuda's national cocktail — dark rum's caramel meets fiery ginger for a perfect storm.",
         ingredients=json.dumps([
             {"item": "Dark Rum (preferably Gosling's)", "amount": "50ml"},
             {"item": "Ginger Beer", "amount": "120ml"},
             {"item": "Fresh lime juice", "amount": "15ml"},
         ]),
         instructions="Fill a highball glass with ice. Add lime juice. Pour in the ginger beer. Float the dark rum on top by pouring it slowly over the back of a spoon. Garnish with a lime wedge."),

    dict(name="Paloma", base_spirit="tequila",
         difficulty="easy", mood_tags="party,relaxed,adventurous", abv_estimate=10.0,
         glass_type="Highball or rocks glass", garnish="Grapefruit wedge, salt rim",
         flavor_profile="fruity,crisp,bitter",
         description="Mexico's most popular cocktail — bright grapefruit bitterness elevating blanco tequila.",
         ingredients=json.dumps([
             {"item": "Blanco Tequila", "amount": "50ml"},
             {"item": "Fresh grapefruit juice", "amount": "60ml"},
             {"item": "Lime juice", "amount": "15ml"},
             {"item": "Grapefruit soda (e.g., Jarritos)", "amount": "Top up"},
             {"item": "Salt rim", "amount": "Optional"},
         ]),
         instructions="Optional: rim a highball glass with salt. Fill with ice. Add tequila, grapefruit juice, and lime juice. Top with grapefruit soda and stir gently. Garnish with a grapefruit wedge."),

    dict(name="French 75", base_spirit="gin",
         difficulty="medium", mood_tags="celebratory,romantic,party", abv_estimate=15.0,
         glass_type="Champagne flute", garnish="Lemon twist",
         flavor_profile="crisp,fruity,floral",
         description="Named after the French 75mm field gun — this cocktail packs a punch disguised as elegance.",
         ingredients=json.dumps([
             {"item": "London Dry Gin", "amount": "30ml"},
             {"item": "Fresh lemon juice", "amount": "15ml"},
             {"item": "Simple syrup", "amount": "10ml"},
             {"item": "Champagne or Prosecco", "amount": "Top up"},
         ]),
         instructions="Combine gin, lemon juice, and syrup in a shaker with ice. Shake briefly. Strain into a chilled champagne flute. Top with chilled champagne. Garnish with a lemon twist."),

    dict(name="Sidecar", base_spirit="brandy",
         difficulty="medium", mood_tags="romantic,relaxed,cozy", abv_estimate=22.0,
         glass_type="Coupe glass", garnish="Sugar rim, orange peel",
         flavor_profile="fruity,sweet,bitter",
         description="A classic 1920s Parisian cocktail — cognac's sophistication elevated by orange and lemon.",
         ingredients=json.dumps([
             {"item": "Cognac", "amount": "50ml"},
             {"item": "Cointreau", "amount": "20ml"},
             {"item": "Fresh lemon juice", "amount": "20ml"},
         ]),
         instructions="Sugar-rim a chilled coupe glass. Combine all ingredients in a shaker with ice. Shake well. Strain into the prepared glass. Garnish with an orange peel."),

    dict(name="Penicillin", base_spirit="whiskey",
         difficulty="hard", mood_tags="adventurous,relaxed,stressed", abv_estimate=20.0,
         glass_type="Rocks glass", garnish="Candied ginger, lemon peel",
         flavor_profile="smoky,spicy,fruity,sweet",
         description="Sam Ross's modern classic — blended Scotch with honey-ginger, finished with a float of Islay malt.",
         ingredients=json.dumps([
             {"item": "Blended Scotch Whisky", "amount": "50ml"},
             {"item": "Fresh lemon juice", "amount": "22ml"},
             {"item": "Honey-ginger syrup", "amount": "22ml"},
             {"item": "Peaty Islay Single Malt (e.g., Laphroaig)", "amount": "7ml (float)"},
         ]),
         instructions="Combine blended scotch, lemon juice, and honey-ginger syrup in a shaker with ice. Shake vigorously. Strain into a rocks glass over a large ice cube. Float the Islay malt by pouring it slowly over the back of a spoon. Garnish with candied ginger."),

    dict(name="Aperol Spritz", base_spirit="wine",
         difficulty="easy", mood_tags="relaxed,party,celebratory", abv_estimate=8.0,
         glass_type="Large wine glass", garnish="Orange slice",
         flavor_profile="bitter,fruity,crisp",
         description="Italy's beloved aperitivo — bitter, bubbly, and impossibly easy to drink.",
         ingredients=json.dumps([
             {"item": "Aperol", "amount": "60ml"},
             {"item": "Prosecco", "amount": "90ml"},
             {"item": "Splash of soda water", "amount": "30ml"},
         ]),
         instructions="Fill a large wine glass with ice. Pour in Aperol, then Prosecco, then soda water. Stir very briefly. Garnish with a half-orange slice."),

    dict(name="Boulevardier", base_spirit="whiskey",
         difficulty="easy", mood_tags="cozy,relaxed,romantic", abv_estimate=26.0,
         glass_type="Rocks glass", garnish="Orange peel or cherry",
         flavor_profile="sweet,bitter,woody,fruity",
         description="The Negroni's sophisticated bourbon cousin — richer, fuller, and deeply satisfying.",
         ingredients=json.dumps([
             {"item": "Bourbon Whiskey", "amount": "45ml"},
             {"item": "Sweet Vermouth", "amount": "30ml"},
             {"item": "Campari", "amount": "30ml"},
         ]),
         instructions="Combine all ingredients in a mixing glass with ice. Stir for 30 seconds. Strain into a rocks glass over a large ice cube. Garnish with an orange peel."),

    dict(name="Oaxacan Old Fashioned", base_spirit="mezcal",
         difficulty="medium", mood_tags="adventurous,relaxed,cozy", abv_estimate=32.0,
         glass_type="Rocks glass", garnish="Flamed orange peel",
         flavor_profile="smoky,sweet,earthy,woody",
         description="Phil Ward's legendary cocktail — mezcal's smoke meets reposado's sweetness in a modern masterpiece.",
         ingredients=json.dumps([
             {"item": "Reposado Tequila", "amount": "45ml"},
             {"item": "Mezcal", "amount": "15ml"},
             {"item": "Agave nectar", "amount": "5ml"},
             {"item": "Mole bitters", "amount": "2 dashes"},
         ]),
         instructions="Combine all ingredients in a mixing glass with ice. Stir until cold and diluted (about 30 seconds). Strain into a rocks glass over a large ice cube. Flambé an orange peel over the drink and drop it in."),

    dict(name="Kir Royale", base_spirit="champagne",
         difficulty="easy", mood_tags="romantic,celebratory,relaxed", abv_estimate=11.0,
         glass_type="Champagne flute", garnish="Fresh raspberry",
         flavor_profile="fruity,sweet,crisp",
         description="A French classic — the simplest and most elegant champagne cocktail.",
         ingredients=json.dumps([
             {"item": "Crème de Cassis (blackcurrant liqueur)", "amount": "10ml"},
             {"item": "Champagne or Cremant", "amount": "Top up"},
         ]),
         instructions="Pour crème de cassis into a chilled champagne flute. Slowly top with chilled champagne — let the cassis rise naturally through the bubbles. Garnish with a single fresh raspberry."),
]


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        for data in BEVERAGES:
            bev = Beverage(**data)
            db.session.add(bev)

        for data in COCKTAILS:
            cocktail = Cocktail(**data)
            db.session.add(cocktail)

        db.session.commit()
        print(f"Seeded {len(BEVERAGES)} beverages and {len(COCKTAILS)} cocktails.")


if __name__ == "__main__":
    seed()
