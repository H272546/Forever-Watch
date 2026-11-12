"""Canonical ingredient vocabulary: maps a cookbook ingredient line to one id.

CANON[id] = (display name, kind, aisle)
  kind  'fresh'  -> things you look for in the fridge; a recipe needs these on hand
        'staple' -> dry goods, sauces, spices; assumed on hand unless told otherwise
"""
import re

CANON = {}
RULES = []


def _add(id_, name, kind, aisle, pattern):
    CANON[id_] = (name, kind, aisle)
    RULES.append((re.compile(pattern, re.I), id_))


# Order matters: first match wins.
# --- compound / specific first ---
_add("peanut-butter", "Peanut butter", "staple", "Pantry", r"peanut butter|\bpb2?\b")
_add("cream-cheese", "Cream cheese", "fresh", "Dairy", r"cream cheese|philadelphia|laughing cow|cheese (triangle|wedge)")
_add("cottage-cheese", "Cottage cheese", "fresh", "Dairy", r"cottage cheese")
_add("sour-cream", "Sour cream", "fresh", "Dairy", r"sour cream|cr[eè]me fra[iî]che")
_add("whipped-cream", "Whipped cream", "fresh", "Dairy", r"whipp(ed|ing) cream|squirty cream")
_add("ice-cream", "Ice cream", "fresh", "Frozen", r"ice cream")
_add("coconut-milk", "Coconut milk", "staple", "Pantry", r"coconut milk|coconut cream")
_add("almond-milk", "Almond milk", "fresh", "Dairy", r"almond milk|oat milk|soy milk")
_add("evaporated-milk", "Evaporated milk", "staple", "Pantry", r"evaporated milk|condensed milk")
_add("chicken-stock", "Stock / bouillon", "staple", "Pantry", r"stock|broth|bouillon")
_add("chicken-thigh", "Chicken thighs", "fresh", "Meat & fish", r"chicken thigh")
_add("chicken-wings", "Chicken wings", "fresh", "Meat & fish", r"chicken wing|wings\b|drumstick")
_add("whole-chicken", "Whole chicken", "fresh", "Meat & fish", r"whole chicken")
_add("chicken-mince", "Chicken mince", "fresh", "Meat & fish", r"chicken mince|ground chicken|minced chicken")
_add("chicken-breast", "Chicken breast", "fresh", "Meat & fish", r"chicken breast|chicken tender|chicken fillet|raw chicken|cooked chicken|shredded chicken|^chicken$|chicken,|chicken \(|diced chicken|chicken strips|chicken pieces?|fajita chicken|pieces of thigh")
_add("turkey", "Turkey (bacon / mince)", "fresh", "Meat & fish", r"turkey")
_add("bacon", "Bacon", "fresh", "Meat & fish", r"bacon|pepperoni|sausage|salami|\bham\b")
_add("ground-beef", "Lean ground beef", "fresh", "Meat & fish", r"ground beef|beef mince|minced beef|lean mince|\bmince\b|lean beef|burger patt|beef patt")
_add("steak", "Steak / sirloin beef", "fresh", "Meat & fish", r"steak|sirloin|topside|rump|flank|\bbeef\b")
_add("shrimp", "Shrimp / prawns", "fresh", "Meat & fish", r"shrimp|prawn")
_add("salmon", "Salmon", "fresh", "Meat & fish", r"salmon")
_add("tuna", "Tuna", "staple", "Pantry", r"tuna")
_add("egg-whites", "Egg whites", "fresh", "Dairy", r"egg white")
_add("eggs", "Eggs", "fresh", "Dairy", r"\beggs?\b")
# --- sauces & pastes (before produce, so 'tomato paste' doesn't hit tomato) ---
_add("tomato-paste", "Tomato paste / puree", "staple", "Pantry", r"tomato (paste|pur[eé]e)")
_add("passata", "Passata / chopped tomatoes", "staple", "Pantry", r"passata|chopped tomato|crushed tomato|canned tomato|tinned tomato|tomato sauce|marinara|pizza sauce|pasta sauce|diced tomato")
_add("salsa", "Salsa", "staple", "Pantry", r"salsa|pico de gallo")
_add("ketchup", "Ketchup (reduced sugar)", "staple", "Pantry", r"ketchup")
_add("bbq-sauce", "BBQ sauce", "staple", "Pantry", r"bbq|barbecue")
_add("buffalo-sauce", "Hot / buffalo sauce", "staple", "Pantry", r"buffalo|hot sauce|frank'?s|tabasco|peri peri sauce|peri-peri sauce|nando")
_add("sriracha", "Sriracha", "staple", "Pantry", r"sriracha|siracha")
_add("sweet-chilli", "Sweet chilli sauce", "staple", "Pantry", r"sweet chil+i")
_add("gochujang", "Gochujang", "staple", "Pantry", r"gochujang")
_add("chilli-garlic", "Chilli garlic / chilli paste", "staple", "Pantry", r"chil+i garlic|chil+i paste|chil+i crisp|chil+i oil|sambal|harissa")
_add("chipotle-paste", "Chipotle paste", "staple", "Pantry", r"chipotle (paste|in adobo|sauce)|adobo")
_add("soy-sauce", "Soy sauce", "staple", "Pantry", r"soya? sauce|\bsoy\b|tamari")
_add("oyster-sauce", "Oyster sauce", "staple", "Pantry", r"oyster sauce|hoisin|fish sauce")
_add("teriyaki", "Teriyaki sauce", "staple", "Pantry", r"teriyaki sauce")
_add("worcestershire", "Worcestershire sauce", "staple", "Pantry", r"worcester")
_add("tamarind", "Tamarind paste", "staple", "Pantry", r"tamarind")
_add("curry-paste", "Curry paste", "staple", "Pantry", r"curry paste|tikka paste|tandoori paste|masala paste")
_add("pesto", "Pesto", "staple", "Pantry", r"pesto")
_add("mayo", "Light mayo", "fresh", "Dairy", r"mayo")
_add("mustard", "Mustard", "staple", "Pantry", r"mustard")
_add("vinegar", "Vinegar", "staple", "Pantry", r"vinegar")
_add("honey", "Honey", "staple", "Pantry", r"honey")
_add("maple", "Maple syrup", "staple", "Pantry", r"maple|syrup|agave")
_add("garlic", "Garlic", "staple", "Produce", r"garlic(?! powder| granules| salt| & herb| and herb| naan| bread)")
_add("ginger", "Ginger", "staple", "Produce", r"ginger(?! powder)")
# --- dairy ---
_add("butter", "Butter (reduced fat)", "fresh", "Dairy", r"butter(?!nut|milk)")
_add("yogurt", "Yogurt (Greek / fat free)", "fresh", "Dairy", r"yog(h)?urt|skyr|quark")
_add("mozzarella", "Mozzarella", "fresh", "Dairy", r"mozzarella|pizza cheese")
_add("parmesan", "Parmesan", "fresh", "Dairy", r"parmesan|parmigiano|pecorino")
_add("feta", "Feta", "fresh", "Dairy", r"feta|halloumi|paneer")
_add("cheese-slices", "Cheese slices", "fresh", "Dairy", r"cheese slice|slices? .*cheese|american cheese|burger cheese")
_add("cheddar", "Cheddar / grated cheese", "fresh", "Dairy", r"cheddar|cheese")
_add("cream", "Cooking cream", "fresh", "Dairy", r"\bcream\b|half and half|half & half")
_add("milk", "Milk", "fresh", "Dairy", r"\bmilk\b")
# --- bread & wraps ---
_add("tortilla", "Tortilla wraps", "fresh", "Bakery", r"tortilla|wraps?\b|taco shell|lavash")
_add("naan", "Naan / pita", "fresh", "Bakery", r"naan|pita|pitta|flatbread")
_add("buns", "Burger buns", "fresh", "Bakery", r"\bbuns?\b|brioche|bagel|english muffin|sub roll|baguette|ciabatta")
_add("bread", "Bread", "fresh", "Bakery", r"bread(?!crumb)|toast\b|sourdough")
_add("lasagna-sheets", "Lasagne sheets", "staple", "Pasta, rice & noodles", r"lasagn")
# --- carbs ---
_add("noodles", "Noodles", "staple", "Pasta, rice & noodles", r"noodle")
_add("pasta", "Pasta", "staple", "Pasta, rice & noodles", r"pasta|macaroni|penne|spaghetti|linguine|fettuccine|rigatoni|fusilli|tagliatelle|orzo")
_add("rice", "Rice", "staple", "Pasta, rice & noodles", r"\brice\b(?! vinegar| noodle| paper| krisp| cake| flour)")
_add("rice-krispies", "Rice Krispies / cereal", "staple", "Pantry", r"krispies|cereal|cornflake|granola")
_add("sweet-potato", "Sweet potato", "fresh", "Produce", r"sweet potato")
_add("potato", "Potatoes", "fresh", "Produce", r"potato|frozen fries|\bfries\b")
_add("oats", "Oats / oat flour", "staple", "Pantry", r"\boats?\b|oat flour")
_add("tortilla-chips", "Tortilla chips", "staple", "Pantry", r"tortilla chips|nachos?\b|doritos|crisps")
# --- produce ---
_add("cherry-tomato", "Cherry tomatoes", "fresh", "Produce", r"cherry tomato")
_add("sundried-tomato", "Sun-dried tomatoes", "staple", "Pantry", r"sun.?dried")
_add("tomato", "Tomatoes", "fresh", "Produce", r"tomato")
_add("spring-onion", "Spring onion", "fresh", "Produce", r"green onion|spring onion|scallion|chives")
_add("red-onion", "Red onion", "fresh", "Produce", r"red onion|shallot")
_add("onion", "Onion", "fresh", "Produce", r"onion(?! powder| granules| salt)")
_add("bell-pepper", "Bell peppers", "fresh", "Produce", r"bell pepper|capsicum|(red|green|yellow|orange|mixed) pepper|peppers\b")
_add("jalapeno", "Jalapeño / fresh chilli", "fresh", "Produce", r"jalape|fresh chil+i|green chil+i|red chil+i(?! flake| powder)|habanero|scotch bonnet")
_add("mushroom", "Mushrooms", "fresh", "Produce", r"mushroom")
_add("broccoli", "Broccoli", "fresh", "Produce", r"broccoli")
_add("spinach", "Spinach", "fresh", "Produce", r"spinach|kale")
_add("lettuce", "Lettuce / salad leaves", "fresh", "Produce", r"lettuce|salad|rocket|arugula|leafy|mixed greens")
_add("cabbage", "Cabbage / slaw", "fresh", "Produce", r"cabbage|slaw|bok choy|pak choi")
_add("cucumber", "Cucumber", "fresh", "Produce", r"cucumber|pickles?\b|gherkin")
_add("carrot", "Carrot", "fresh", "Produce", r"carrot")
_add("corn", "Sweetcorn", "staple", "Pantry", r"\bcorn\b(?! ?flour| ?starch| tortilla| flake)|sweetcorn|sweecorn")
_add("avocado", "Avocado", "fresh", "Produce", r"avocado|guacamole")
_add("courgette", "Courgette / zucchini", "fresh", "Produce", r"zucchini|courgette|aubergine|eggplant|asparagus|green beans|celery|beansprout|bean sprout|peas\b|mixed veg|stir.?fry veg|vegetables|veggies|edamame|cauliflower")
_add("kimchi", "Kimchi", "fresh", "Produce", r"kimchi")
_add("lemon", "Lemon", "fresh", "Produce", r"lemon(?! pepper)")
_add("lime", "Lime", "fresh", "Produce", r"\blime")
_add("orange", "Orange / orange juice", "fresh", "Produce", r"orange")
_add("banana", "Banana", "fresh", "Produce", r"banana")
_add("berries", "Berries", "fresh", "Produce", r"berr(y|ies)|merries|strawberr|blueberr|raspberr")
_add("mango", "Mango / pineapple", "fresh", "Produce", r"mango|pineapple")
_add("apple", "Apple / apple sauce", "fresh", "Produce", r"apple")
_add("fruit", "Other fruit", "fresh", "Produce", r"watermelon|kiwi|grape|pomegranate|dates\b|peach|papaya|beetroot|cherries")
_add("parsley", "Fresh parsley", "fresh", "Produce", r"parsley(?! flake)")
_add("coriander", "Coriander / cilantro", "fresh", "Produce", r"cilantro|coriander(?! powder| seed)|fresh coriander")
_add("basil", "Fresh basil", "fresh", "Produce", r"fresh basil|basil leaves")
_add("mint", "Fresh mint", "fresh", "Produce", r"\bmint\b")
# --- pantry ---
_add("beans", "Beans / chickpeas", "staple", "Pantry", r"beans\b|chickpea|lentil")
_add("olives", "Olives", "staple", "Pantry", r"olives\b")
_add("oil", "Olive oil / cooking spray", "staple", "Pantry", r"\boil|o\|il|cooking spray|fry ?light|spray")
_add("cornflour", "Cornflour / cornstarch", "staple", "Pantry", r"corn ?flour|corn ?starch")
_add("breadcrumbs", "Breadcrumbs / cornflakes", "staple", "Pantry", r"breadcrumb|panko")
_add("flour", "Flour", "staple", "Pantry", r"flour")
_add("baking", "Baking powder / soda", "staple", "Pantry", r"baking (powder|soda)|bicarb|yeast")
_add("protein-powder", "Protein powder", "staple", "Pantry", r"protein powder|whey|casein|scoop")
_add("cocoa", "Cocoa / chocolate", "staple", "Pantry", r"cocoa|cacao|chocolate|choc chip|nutella|biscoff|caramel")
_add("sweetener", "Sugar / sweetener", "staple", "Pantry", r"sweetener|sugar|stevia|erythritol")
_add("vanilla", "Vanilla extract", "staple", "Pantry", r"vanilla")
_add("nuts", "Nuts & seeds", "staple", "Pantry", r"sesame seed|cashew|peanut|almond|walnut|pecan|chia|flax|seeds\b|\bnuts?\b|coconut(?! water| milk)")
_add("coffee", "Coffee", "staple", "Pantry", r"coffee|espresso")
_add("jam", "Jam / spreads", "staple", "Pantry", r"\bjam\b|jelly|grenadine")
_add("water", "", "skip", "", r"^(cold |hot |warm |boiling |pasta |a splash of |splash of )?water\b|\bice\b|pasta water|\bwater$|coconut water|collagen")
# --- spices: one bucket each, all staples ---
for _id, _name, _pat in [
    ("salt-pepper", "Salt & black pepper", r"\bsalt\b|sxalt|black pepper|white pepper|^pepper|lemon pepper|seasoning to taste"),
    ("paprika", "Paprika / smoked paprika", r"paprika|gaprika"),
    ("garlic-powder", "Garlic powder", r"garlic (powder|granules|salt)"),
    ("onion-powder", "Onion powder", r"onion (powder|granules|salt)"),
    ("chilli-flakes", "Chilli flakes / powder", r"chil+i (flake|powder)|cayenne|red pepper flake|pepper flakes|chipotle"),
    ("cumin", "Cumin", r"cumin"),
    ("oregano", "Oregano / Italian herbs", r"oregano|italian (herb|season)|mixed herb|thyme|rosemary|dried basil|basil|parsley flake|dried parsley|herbs?\b"),
    ("curry-powder", "Curry powder / garam masala", r"curry powder|garam masala|turmeric|coriander powder|tandoori|tikka|biryani|masala|fenugreek|methi|cardamom"),
    ("cinnamon", "Cinnamon / nutmeg", r"cinnamon|nutmeg|all ?spice|5 spice|ginger powder|pumpkin spice"),
    ("sumac", "Sumac", r"sumac|za'?atar"),
    ("cajun", "Cajun / taco / fajita seasoning", r"cajun|taco season|fajita season|seasoning|spice mix|all purpose|old bay|jerk"),
]:
    _add(_id, _name, "staple", "Spices", _pat)

_QTY = re.compile(
    r"^\s*(?:(?:\d+(?:[.,/]\d+)?|[½¼¾⅓⅔])\s*(?:-|–|to\b)?\s*)*"
    r"(?:(?:g|kg|ml|l|oz|lbs?|tsp|tbsp|cups?|scoops?|cloves?|slices?|pinch|dash|handful|medium|large|small|whole|x)\b\.?\s*)*", re.I)


def strip_qty(item):
    s = re.sub(r"\([^)]*\)", " ", item)
    for _ in range(3):
        s = _QTY.sub("", s, count=1)
    s = re.sub(r"^(of|each)\s+", "", s.strip(), flags=re.I)
    return re.sub(r"\s+", " ", s).strip(" ,.-–")


def canon_for(item):
    name = strip_qty(item)
    if not name:
        return None
    for pat, id_ in RULES:
        if pat.search(name):
            return None if CANON[id_][1] == "skip" else id_
    return None
