"""
seed.py  –  Full demo data for AquaConnect.
Re-runnable: skips rows that already exist.

Users
─────────────────────────────────────────────────────
  admin@aquaconnect.com   / Admin@123    (admin)
  ravi.kumar@farm.com     / Farmer@123  (farmer)
  priya.sharma@farm.com   / Farmer@123  (farmer)
  dr.expert@aqua.com      / Expert@123  (expert)
  ananya.das@farm.com     / Farmer@123  (farmer)
"""

import json, random
from datetime import datetime, timezone, date, timedelta
from app import create_app, db, bcrypt
from app.models import User, Farm, WaterQualityLog, Transaction, ForumPost, ForumReply

app = create_app()

# ─── Helpers ──────────────────────────────────────────────────────────────────
def days_ago(n):
    return datetime.now(timezone.utc) - timedelta(days=n)

def date_ago(n):
    return date.today() - timedelta(days=n)

def wq_status(ph, do, ammonia):
    alerts = []
    if ph < 6.5 or ph > 8.5:
        alerts.append(f"pH {ph} is outside safe range (6.5–8.5)")
    if do < 5:
        alerts.append(f"Dissolved oxygen {do} mg/L is critically low")
    if ammonia > 0.5:
        alerts.append(f"Ammonia {ammonia} ppm is too high")
    if alerts:
        status = "critical" if (ph < 6 or ph > 9 or do < 3 or ammonia > 1.0) else "warning"
    else:
        status = "good"
    return status, alerts

# ─── USERS ────────────────────────────────────────────────────────────────────
USERS = [
    dict(full_name="Admin User",       email="admin@aquaconnect.com",  password="Admin@123",  role="admin"),
    dict(full_name="Ravi Kumar",        email="ravi.kumar@farm.com",    password="Farmer@123", role="farmer"),
    dict(full_name="Priya Sharma",      email="priya.sharma@farm.com",  password="Farmer@123", role="farmer"),
    dict(full_name="Dr. Arjun Expert",  email="dr.expert@aqua.com",     password="Expert@123", role="expert"),
    dict(full_name="Ananya Das",        email="ananya.das@farm.com",    password="Farmer@123", role="farmer"),
    dict(full_name="Vikram Singh",      email="vikram.s@aqua.com",      password="Expert@123", role="expert"),
    dict(full_name="Sita Devi",         email="sita.farm@gmail.com",    password="Farmer@123", role="farmer"),
]

# ─── FARMS ────────────────────────────────────────────────────────────────────
FARMS = [
    dict(owner="ravi.kumar@farm.com",   name="Ravi's Tilapia Farm",
         location="Andhra Pradesh", area_hectares=3.5, fish_species="Tilapia",  water_source="River"),
    dict(owner="priya.sharma@farm.com", name="Priya's Catfish Pond",
         location="West Bengal",   area_hectares=1.8, fish_species="Catfish",  water_source="Borewell"),
    dict(owner="ananya.das@farm.com",   name="Ananya's Rohu Estate",
         location="Odisha",         area_hectares=5.0, fish_species="Rohu",    water_source="Canal"),
    dict(owner="sita.farm@gmail.com",   name="Sita's Shrimp Colony",
         location="Gujarat",        area_hectares=2.5, fish_species="Shrimp",  water_source="Sea Water"),
]

# ─── WATER QUALITY readings per farm (ph, temp, do, ammonia, salinity, days_ago) ──
WATER_DATA = {
    "Ravi's Tilapia Farm": [
        (7.2, 28.5, 6.8, 0.02, 0.1, 0),
        (7.0, 29.0, 6.5, 0.03, 0.1, 1),
        (7.4, 27.8, 7.1, 0.01, 0.1, 3),
        (6.8, 30.2, 5.9, 0.05, 0.1, 5),
        (7.1, 28.0, 6.7, 0.02, 0.1, 7),
        (6.3, 31.5, 4.8, 0.12, 0.2, 10),  # warning
        (7.3, 28.3, 6.9, 0.02, 0.1, 12),
        (7.5, 27.5, 7.3, 0.01, 0.1, 14),
        (5.8, 29.8, 3.1, 1.20, 0.2, 18),  # critical
        (7.2, 28.5, 6.8, 0.02, 0.1, 21),
        (7.0, 28.0, 6.6, 0.03, 0.1, 25),
        (7.3, 27.9, 7.0, 0.01, 0.1, 30),
    ],
    "Priya's Catfish Pond": [
        (7.1, 26.0, 7.2, 0.01, 0.0, 0),
        (7.3, 25.5, 7.5, 0.01, 0.0, 2),
        (6.9, 27.0, 6.8, 0.03, 0.0, 4),
        (7.2, 26.5, 7.0, 0.02, 0.0, 6),
        (6.5, 28.8, 5.5, 0.08, 0.0, 9),   # warning
        (7.1, 26.2, 7.1, 0.02, 0.0, 11),
        (7.4, 25.8, 7.4, 0.01, 0.0, 13),
        (7.0, 27.3, 6.9, 0.02, 0.0, 16),
        (7.2, 26.0, 7.2, 0.01, 0.0, 20),
    ],
    "Ananya's Rohu Estate": [
        (7.5, 29.5, 7.0, 0.01, 0.5, 0),
        (7.3, 30.0, 6.8, 0.02, 0.5, 2),
        (7.6, 29.2, 7.2, 0.01, 0.5, 4),
        (6.8, 31.0, 5.8, 0.06, 0.5, 7),   # warning
        (7.4, 29.8, 7.0, 0.02, 0.5, 9),
        (7.5, 29.5, 7.1, 0.01, 0.5, 12),
        (7.2, 30.5, 6.7, 0.03, 0.6, 15),
        (7.6, 29.0, 7.3, 0.01, 0.5, 18),
        (7.4, 29.5, 7.0, 0.02, 0.5, 22),
        (7.3, 30.0, 6.9, 0.02, 0.5, 26),
    ],
    "Sita's Shrimp Colony": [
        (8.1, 28.0, 6.5, 0.01, 28.0, 0),
        (8.2, 28.5, 6.2, 0.02, 28.5, 2),
        (8.0, 29.0, 5.8, 0.04, 29.0, 5),   # warning (DO)
        (7.9, 28.2, 6.6, 0.02, 28.0, 8),
        (8.3, 27.5, 7.0, 0.01, 27.5, 12),
        (7.5, 30.0, 4.2, 0.15, 30.0, 15),  # warning
        (8.1, 28.3, 6.4, 0.02, 28.0, 20),
        (8.0, 28.0, 6.5, 0.01, 28.0, 25),
    ],
}

# ─── TRANSACTIONS per farm ─────────────────────────────────────────────────────
TRANSACTIONS = {
    "Ravi's Tilapia Farm": [
        # income
        dict(type="income",  amount=45000, category="Fish Sales",    description="Sold 450kg Tilapia @ ₹100/kg",    days=5),
        dict(type="income",  amount=28000, category="Fish Sales",    description="Wholesale batch to processor",    days=18),
        dict(type="income",  amount=12000, category="Fish Sales",    description="Local market sale",               days=35),
        dict(type="income",  amount=62000, category="Fish Sales",    description="Quarterly major harvest",         days=65),
        # expense
        dict(type="expense", amount=8500,  category="Feed",          description="Fish pellets – 2 bags",           days=3),
        dict(type="expense", amount=3200,  category="Medicines",     description="Antibiotics & vitamins",          days=8),
        dict(type="expense", amount=6000,  category="Labour",        description="Farm workers wages – March",      days=10),
        dict(type="expense", amount=1800,  category="Electricity",   description="Aeration pump power bill",        days=12),
        dict(type="expense", amount=5500,  category="Feed",          description="Fish pellets – 1.5 bags",         days=22),
        dict(type="expense", amount=9000,  category="Equipment",     description="Replacement aerator motor",       days=28),
        dict(type="expense", amount=6000,  category="Labour",        description="Farm workers wages – Feb",        days=42),
        dict(type="expense", amount=2200,  category="Water Quality", description="pH & DO test kits",               days=45),
        dict(type="expense", amount=4500,  category="Feed",          description="Fish pellets – 1.2 bags",         days=55),
        dict(type="expense", amount=1600,  category="Electricity",   description="Monthly power bill",              days=72),
    ],
    "Priya's Catfish Pond": [
        dict(type="income",  amount=22000, category="Fish Sales",    description="Catfish sale – local market",     days=4),
        dict(type="income",  amount=18500, category="Fish Sales",    description="Restaurant supply",               days=25),
        dict(type="income",  amount=31000, category="Fish Sales",    description="Festive season harvest",          days=60),
        dict(type="expense", amount=4200,  category="Feed",          description="Catfish feed – starter",          days=2),
        dict(type="expense", amount=2800,  category="Labour",        description="Pond cleaning service",           days=6),
        dict(type="expense", amount=1500,  category="Electricity",   description="Pump electricity",                days=15),
        dict(type="expense", amount=3500,  category="Medicines",     description="Disease prevention meds",         days=20),
        dict(type="expense", amount=4000,  category="Feed",          description="Catfish grower pellets",          days=32),
        dict(type="expense", amount=2800,  category="Labour",        description="Harvesting labour",               days=62),
    ],
    "Ananya's Rohu Estate": [
        dict(type="income",  amount=78000, category="Fish Sales",    description="Rohu bulk export – 780kg",        days=3),
        dict(type="income",  amount=42000, category="Fish Sales",    description="State govt. procurement",         days=30),
        dict(type="income",  amount=25000, category="Fish Sales",    description="Local wholesale",                 days=58),
        dict(type="income",  amount=15000, category="Consulting",    description="Farm visit consultation fee",     days=70),
        dict(type="expense", amount=14000, category="Feed",          description="Rohu fingerling feed – bulk",     days=5),
        dict(type="expense", amount=8500,  category="Labour",        description="Workers wages + overtime",        days=8),
        dict(type="expense", amount=3200,  category="Electricity",   description="Canal pump electricity",          days=18),
        dict(type="expense", amount=6500,  category="Equipment",     description="Seine net replacement",           days=22),
        dict(type="expense", amount=4800,  category="Medicines",     description="Parasite treatment",              days=33),
        dict(type="expense", amount=12000, category="Feed",          description="Rohu grower feed",                days=48),
        dict(type="expense", amount=8500,  category="Labour",        description="Workers wages – Feb",             days=65),
        dict(type="expense", amount=2500,  category="Water Quality", description="Water testing lab fees",          days=72),
    ],
    "Sita's Shrimp Colony": [
        dict(type="income",  amount=120000, category="Fish Sales",    description="Export Grade Shrimp - 1 Ton",    days=10),
        dict(type="income",  amount=45000,  category="Fish Sales",    description="Local wholesale batch",          days=40),
        dict(type="expense", amount=25000, category="Feed",          description="Bio-active shrimp feed",         days=2),
        dict(type="expense", amount=12000, category="Equipment",     description="Automatic paddle wheel aerator", days=15),
        dict(type="expense", amount=5000,  category="Water Quality", description="Salt & Mineral additives",       days=20),
        dict(type="expense", amount=8000,  category="Labour",        description="Monthly wages",                  days=30),
    ],
}

# ─── FORUM POSTS & REPLIES ─────────────────────────────────────────────────────
POSTS = [
    dict(
        author="ravi.kumar@farm.com",
        title="Best water temperature range for Tilapia?",
        category="Water Quality",
        content="Hi everyone, I've been noticing my Tilapia seem stressed when temperatures go above 31°C. What is the ideal temperature range and how do you manage it during summer? Any tips for keeping the pond cool without expensive equipment?",
        views=142,
        days=15,
        replies=[
            dict(author="dr.expert@aqua.com", is_expert=True, days=14,
                 content="Great question Ravi! Tilapia thrive between 25–30°C. Above 32°C, their metabolism spikes, oxygen demand increases, and immunity drops. Practical cooling methods: (1) Increase water exchange rate by 20%, (2) Add shade nets over 30–40% of the pond surface, (3) Aerate aggressively at night when temperatures are lower. Also monitor DO closely in summer — it drops fast."),
            dict(author="priya.sharma@farm.com", is_expert=False, days=13,
                 content="I had the same issue last year. Shade nets made a huge difference for me! I used 50% shade cloth above the pond and temperatures dropped by almost 3°C. Combined with extra aeration it worked really well."),
            dict(author="ananya.das@farm.com", is_expert=False, days=12,
                 content="We also use bamboo structures with coconut frond thatch as shade — very cheap and effective. Traditional methods still work great!"),
        ]
    ),
    dict(
        author="priya.sharma@farm.com",
        title="Catfish pond suddenly producing foul smell – what's happening?",
        category="Disease & Health",
        content="My 1.8 hectare catfish pond has started producing a very bad smell over the past 3 days. The water also looks slightly greenish. Fish are still eating but seem lethargic. I'm worried this might be something serious. Has anyone experienced this before?",
        views=98,
        days=10,
        replies=[
            dict(author="dr.expert@aqua.com", is_expert=True, days=9,
                 content="Priya, this sounds like an algal bloom combined with poor bottom conditions. The green colour is likely blue-green algae (cyanobacteria), which is toxic. Foul smell = anaerobic decomposition at the pond bottom. Immediate steps: (1) Do NOT feed for 24–48 hours to reduce organic load, (2) Increase aeration dramatically, (3) Do a 25–30% partial water exchange, (4) Test ammonia and check if it's above 0.5 ppm. Share your water parameters when you can."),
            dict(author="ravi.kumar@farm.com", is_expert=False, days=8,
                 content="I had exactly this problem 6 months ago! The doctor's advice is spot on. I also added lime (calcium hydroxide) at 20kg/hectare after water exchange which helped neutralize the excess acidity at the bottom. Fish recovered within a week."),
            dict(author="priya.sharma@farm.com", is_expert=False, days=7,
                 content="Thank you both! I've stopped feeding and increased aeration. The water quality check showed ammonia at 0.8 ppm which is high. Will do the water exchange today and report back."),
        ]
    ),
    dict(
        author="ananya.das@farm.com",
        title="How to maximize Rohu yield – my experience and tips",
        category="Feeding & Nutrition",
        content="After 3 years of farming Rohu in Odisha, here are my top tips for maximizing yield: 1) Stocking density should be 5,000–8,000 fingerlings per hectare, 2) Feed a combination of rice bran + mustard oil cake at 2–3% of body weight daily, 3) Supplement with water hyacinth as natural green feed, 4) Polyculture with Catla and Mrigal maximizes pond productivity. What are your experiences?",
        views=234,
        days=20,
        replies=[
            dict(author="dr.expert@aqua.com", is_expert=True, days=19,
                 content="Excellent insights Ananya! I'd add that protein content in feed should be 28–32% for optimal growth in Rohu. Also, consider probiotic supplementation in feed — trials show 15–20% faster growth rates. For polyculture, the Catla + Rohu + Mrigal combination at 30:50:20 ratio is scientifically validated."),
            dict(author="ravi.kumar@farm.com", is_expert=False, days=18,
                 content="Very helpful! Do you do water quality checks before and after feeding? I've found that DO drops significantly after heavy feeding."),
            dict(author="ananya.das@farm.com", is_expert=False, days=17,
                 content="Yes Ravi! I always check DO an hour after feeding. If it drops below 5 mg/L, I reduce the next feeding by 30%. Feed conversion efficiency is everything in aquaculture economics."),
        ]
    ),
    dict(
        author="ravi.kumar@farm.com",
        title="Which online platforms do you use to sell fish directly?",
        category="Market & Sales",
        content="I'm trying to cut out the middlemen and sell directly to consumers/restaurants. Are there any good online platforms for fish sales in India? I'm in Andhra Pradesh but willing to try anything that works. Also interested in setting up WhatsApp business for local orders.",
        views=187,
        days=8,
        replies=[
            dict(author="ananya.das@farm.com", is_expert=False, days=7,
                 content="In Odisha I've had great success with local Facebook groups and WhatsApp communities. Just post photos of fresh catch in the morning and orders come in! Also check out iSattva and FarmersFresh Zone — both are marketplaces with good farmer support."),
            dict(author="dr.expert@aqua.com", is_expert=True, days=6,
                 content="For Andhra Pradesh specifically, check out the NFDB (National Fisheries Development Board) portal which connects farmers to institutional buyers. State fisheries cooperative societies also aggregate produce. For restaurants, cold-chain logistics is key — partner with a local logistics company that handles perishables."),
        ]
    ),
    dict(
        author="ananya.das@farm.com",
        title="Using IoT sensors for pond monitoring – worth the investment?",
        category="Technology",
        content="I've been looking at IoT water quality sensors that measure pH, DO, temperature, and ammonia automatically. They can send alerts to your phone. Prices range from ₹15,000 to ₹80,000 per unit. Has anyone invested in these? What's the ROI? I want to make a data-driven decision.",
        views=156,
        days=25,
        replies=[
            dict(author="dr.expert@aqua.com", is_expert=True, days=24,
                 content="IoT sensors are absolutely worth it for farms over 2 hectares. The math: one disease event from missed water quality alerts can cost ₹50,000–2,00,000 in losses. A ₹30,000 sensor pays for itself if it prevents just one such event per year. Look at Kisan Agri Shop and AquaSmart devices — good quality, Indian-made, with decent app support."),
            dict(author="priya.sharma@farm.com", is_expert=False, days=23,
                 content="I just installed a basic pH and temperature sensor last month from a local supplier for ₹18,000. Very happy with it! Got an alert at 2am when pH dropped — would have missed it otherwise. The WhatsApp alert feature is really handy."),
            dict(author="ravi.kumar@farm.com", is_expert=False, days=22,
                 content="Which brand did you get Priya? And does it work offline if your internet goes down? I'm in a rural area with patchy connectivity."),
        ]
    ),
    dict(
        author="priya.sharma@farm.com",
        title="Government subsidies for fish farmers in 2025 – what's available?",
        category="Financial",
        content="I've heard there are new subsidies available under PM Matsya Sampada Yojana for 2025. Can anyone share details about what subsidies are available for: 1) Pond construction, 2) Equipment purchase, 3) Feed subsidy? I'm from West Bengal. How do you apply and what documents are needed?",
        views=312,
        days=5,
        replies=[
            dict(author="dr.expert@aqua.com", is_expert=True, days=4,
                 content="Great question! Under PMMSY 2025 Update: (1) Pond construction: 40% subsidy for general, 60% for SC/ST/women farmers. (2) Motorized boats & gear: 40% subsidy up to ₹1.5 lakh. (3) Recirculating Aquaculture Systems: 25% subsidy. For West Bengal, contact the Matsya Bhavan in Kolkata or visit the state fisheries website. Documents needed: Aadhaar, land records, bank account linked to Aadhaar, and a project report. Chief Minister's Matsya Prokolpo scheme adds additional state subsidies."),
            dict(author="ananya.das@farm.com", is_expert=False, days=3,
                 content="In Odisha the application process is fully online now through the Fisheries portal. I got 40% subsidy on my aerator purchase last year. The key is getting all paperwork right — especially the land measurement certificate from the Tehsildar office. Took me 3 months from application to disbursement."),
        ]
    ),
    dict(
        author="vikram.s@aqua.com",
        title="Biofloc Technology: A beginner's guide to zero-water exchange",
        category="Technology",
        content="I've been successfully running a biofloc system for 18 months now. The ammonia is managed by beneficial bacteria, and water exchange is almost zero. It saves water and reduces feed costs, but it requires 24/7 power for aeration. Ask me anything!",
        views=450,
        days=30,
        replies=[
            dict(author="dr.expert@aqua.com", is_expert=True, days=28,
                 content="Excellent overview Vikram! Biofloc is the future for land-constrained farmers. One tip: keep your C:N ratio at 15:1 for optimal microbial growth."),
            dict(author="sita.farm@gmail.com", is_expert=False, days=25,
                 content="Is biofloc suitable for shrimp farming? I'm worried about the floc settling on the bottom and causing infections."),
        ]
    ),
]


with app.app_context():
    print("\n🌱 AquaConnect Data Seeder")
    print("=" * 55)

    # ── 1. Users ──────────────────────────────────────────────
    print("\n👥 Users")
    user_map = {}
    for u in USERS:
        existing = User.query.filter_by(email=u["email"]).first()
        if existing:
            print(f"   ⚠️  Exists: {u['email']}")
            user_map[u["email"]] = existing
        else:
            pw = bcrypt.generate_password_hash(u["password"]).decode("utf-8")
            obj = User(full_name=u["full_name"], email=u["email"],
                       password_hash=pw, role=u["role"])
            db.session.add(obj)
            db.session.flush()
            user_map[u["email"]] = obj
            print(f"   ✅ {u['role']:8s}  {u['email']}")
    db.session.commit()

    # ── 2. Farms ──────────────────────────────────────────────
    print("\n🐠 Farms")
    farm_map = {}
    for f in FARMS:
        owner = user_map[f["owner"]]
        existing = Farm.query.filter_by(owner_id=owner.id, name=f["name"]).first()
        if existing:
            print(f"   ⚠️  Exists: {f['name']}")
            farm_map[f["name"]] = existing
        else:
            obj = Farm(owner_id=owner.id, name=f["name"], location=f["location"],
                       area_hectares=f["area_hectares"], fish_species=f["fish_species"],
                       water_source=f["water_source"])
            db.session.add(obj)
            db.session.flush()
            farm_map[f["name"]] = obj
            print(f"   ✅ {f['name']} ({f['location']})")
    db.session.commit()

    # ── 3. Water Quality Logs ────────────────────────────────
    print("\n🌊 Water Quality Logs")
    for farm_name, readings in WATER_DATA.items():
        farm = farm_map.get(farm_name)
        if not farm:
            continue
        existing_count = WaterQualityLog.query.filter_by(farm_id=farm.id).count()
        if existing_count >= len(readings):
            print(f"   ⚠️  {farm_name}: already has {existing_count} logs, skipping")
            continue
        added = 0
        for (ph, temp, do, ammonia, salinity, d) in readings:
            status, alerts = wq_status(ph, do, ammonia)
            log = WaterQualityLog(
                farm_id=farm.id, ph=ph, temperature=temp,
                dissolved_oxygen=do, ammonia=ammonia, salinity=salinity,
                health_status=status, alerts=json.dumps(alerts),
                recorded_at=days_ago(d)
            )
            db.session.add(log)
            added += 1
        db.session.commit()
        print(f"   ✅ {farm_name}: {added} readings ({sum(1 for r in readings if wq_status(r[0],r[2],r[3])[0]=='critical')} critical, {sum(1 for r in readings if wq_status(r[0],r[2],r[3])[0]=='warning')} warnings)")

    # ── 4. Transactions ───────────────────────────────────────
    print("\n💰 Financial Transactions")
    for farm_name, txs in TRANSACTIONS.items():
        farm = farm_map.get(farm_name)
        if not farm:
            continue
        existing_count = Transaction.query.filter_by(farm_id=farm.id).count()
        if existing_count >= len(txs):
            print(f"   ⚠️  {farm_name}: already has {existing_count} transactions, skipping")
            continue
        added = 0
        for t in txs:
            obj = Transaction(
                farm_id=farm.id, type=t["type"], amount=t["amount"],
                category=t["category"], description=t["description"],
                date=date_ago(t["days"])
            )
            db.session.add(obj)
            added += 1
        db.session.commit()
        income = sum(t["amount"] for t in txs if t["type"] == "income")
        expense = sum(t["amount"] for t in txs if t["type"] == "expense")
        print(f"   ✅ {farm_name}: {added} transactions | Income ₹{income:,}  Expense ₹{expense:,}  Net ₹{income-expense:,}")

    # ── 5. Forum Posts & Replies ──────────────────────────────
    print("\n💬 Forum Posts & Replies")
    for p in POSTS:
        author = user_map.get(p["author"])
        if not author:
            continue
        existing = ForumPost.query.filter_by(author_id=author.id, title=p["title"]).first()
        if existing:
            print(f"   ⚠️  Exists: {p['title'][:50]}")
            continue
        post = ForumPost(
            author_id=author.id, title=p["title"], content=p["content"],
            category=p["category"], views=p["views"],
            created_at=days_ago(p["days"])
        )
        db.session.add(post)
        db.session.flush()
        for r in p.get("replies", []):
            reply_author = user_map.get(r["author"])
            if not reply_author:
                continue
            reply = ForumReply(
                post_id=post.id, author_id=reply_author.id, content=r["content"],
                is_expert_answer=r.get("is_expert", False),
                created_at=days_ago(r["days"])
            )
            db.session.add(reply)
        db.session.commit()
        print(f"   ✅ [{p['category']}] {p['title'][:48]} ({len(p.get('replies',[]))} replies)")

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 55)
    print("✨ Seeding complete! Platform overview:")
    print(f"   👥 Users:          {User.query.count()}")
    print(f"   🐠 Farms:          {Farm.query.count()}")
    print(f"   🌊 Water Readings: {WaterQualityLog.query.count()}")
    print(f"   💰 Transactions:   {Transaction.query.count()}")
    print(f"   💬 Forum Posts:    {ForumPost.query.count()}")
    print(f"   💬 Forum Replies:  {ForumReply.query.count()}")
    print("=" * 55)
    print("\n🔑 Login credentials:")
    print(f"   {'Role':<10} {'Email':<35} Password")
    print("   " + "─" * 58)
    for u in USERS:
        print(f"   {u['role']:<10} {u['email']:<35} {u['password']}")
