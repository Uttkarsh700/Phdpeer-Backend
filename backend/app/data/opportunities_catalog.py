"""
Static opportunities catalog.

This is a demo dataset of opportunities (grants, conferences, fellowships).
In production, this would be loaded from a database or external API.
"""

from datetime import date, timedelta


# Calculate dates relative to today for realistic deadlines
today = date.today()


STATIC_OPPORTUNITIES_CATALOG = [
    # Grants and Fellowships
    {
        "opportunity_id": "nsf_grfp_2026",
        "title": "NSF Graduate Research Fellowship Program",
        "opportunity_type": "fellowship",
        "disciplines": ["Computer Science", "Engineering", "Mathematics", "Physics", "Biology"],
        "eligible_stages": ["early"],
        "deadline": date(2026, 10, 15),
        "description": "The NSF GRFP provides three years of financial support for graduate study.",
        "keywords": ["graduate research", "STEM", "dissertation"],
        "funding_amount": 37000.0,
        "prestige_level": "high",
        "geographic_scope": "us",
        "source_url": "https://www.nsfgrfp.org/",
        "organization": "National Science Foundation",
        "requires_subscription": False,
        "subscription_tier": None
    },
    {
        "opportunity_id": "doe_scgsr_2026",
        "title": "DOE Office of Science Graduate Student Research",
        "opportunity_type": "fellowship",
        "disciplines": ["Physics", "Chemistry", "Engineering", "Computer Science"],
        "eligible_stages": ["mid", "late"],
        "deadline": today + timedelta(days=75),
        "description": "Research opportunities at DOE national laboratories.",
        "keywords": ["national lab", "research", "energy"],
        "funding_amount": 50000.0,
        "prestige_level": "high",
        "geographic_scope": "us",
        "source_url": "https://science.osti.gov/wdts/scgsr",
        "organization": "Department of Energy",
        "requires_subscription": False,
        "subscription_tier": None
    },
    {
        "opportunity_id": "ford_foundation_fellowship_2026",
        "title": "Ford Foundation Fellowship",
        "opportunity_type": "fellowship",
        "disciplines": ["Social Sciences", "Humanities", "STEM"],
        "eligible_stages": ["early", "mid", "late"],
        "deadline": date(2026, 12, 1),
        "description": "Supporting scholars committed to diversity in higher education.",
        "keywords": ["diversity", "inclusion", "underrepresented"],
        "funding_amount": 27000.0,
        "prestige_level": "high",
        "geographic_scope": "us",
        "source_url": "https://sites.nationalacademies.org/pga/fordfellowships/",
        "organization": "National Academies",
        "requires_subscription": False,
        "subscription_tier": None
    },
    {
        "opportunity_id": "google_phd_fellowship_2026",
        "title": "Google PhD Fellowship",
        "opportunity_type": "fellowship",
        "disciplines": ["Computer Science", "AI", "Machine Learning"],
        "eligible_stages": ["mid", "late"],
        "deadline": today + timedelta(days=45),
        "description": "Supporting outstanding graduate students in computer science.",
        "keywords": ["machine learning", "AI", "computer science"],
        "funding_amount": 60000.0,
        "prestige_level": "high",
        "geographic_scope": "global",
        "source_url": "https://research.google/outreach/phd-fellowship/",
        "organization": "Google Research",
        "requires_subscription": True,
        "subscription_tier": "premium"
    },
    
    # Conferences
    {
        "opportunity_id": "neurips_2026",
        "title": "NeurIPS 2026 - Conference on Neural Information Processing Systems",
        "opportunity_type": "conference",
        "disciplines": ["Computer Science", "AI", "Machine Learning"],
        "eligible_stages": ["mid", "late"],
        "deadline": today + timedelta(days=40),
        "description": "Premier conference in machine learning and neural networks.",
        "keywords": ["machine learning", "deep learning", "neural networks"],
        "funding_amount": None,
        "prestige_level": "high",
        "geographic_scope": "global",
        "source_url": "https://neurips.cc/",
        "organization": "NeurIPS Foundation",
        "requires_subscription": False,
        "subscription_tier": None
    },
    {
        "opportunity_id": "icml_2026",
        "title": "ICML 2026 - International Conference on Machine Learning",
        "opportunity_type": "conference",
        "disciplines": ["Computer Science", "AI", "Machine Learning"],
        "eligible_stages": ["mid", "late"],
        "deadline": today + timedelta(days=55),
        "description": "Leading conference in machine learning research.",
        "keywords": ["machine learning", "AI", "research"],
        "funding_amount": None,
        "prestige_level": "high",
        "geographic_scope": "global",
        "source_url": "https://icml.cc/",
        "organization": "IMLS",
        "requires_subscription": False,
        "subscription_tier": None
    },
    {
        "opportunity_id": "cvpr_2026",
        "title": "CVPR 2026 - Computer Vision and Pattern Recognition",
        "opportunity_type": "conference",
        "disciplines": ["Computer Science", "AI", "Computer Vision"],
        "eligible_stages": ["mid", "late"],
        "deadline": today + timedelta(days=30),
        "description": "Top conference in computer vision.",
        "keywords": ["computer vision", "image processing", "deep learning"],
        "funding_amount": None,
        "prestige_level": "high",
        "geographic_scope": "global",
        "source_url": "https://cvpr.thecvf.com/",
        "organization": "CVF",
        "requires_subscription": False,
        "subscription_tier": None
    },
    {
        "opportunity_id": "chi_2026",
        "title": "CHI 2026 - Human-Computer Interaction",
        "opportunity_type": "conference",
        "disciplines": ["Computer Science", "HCI", "Design"],
        "eligible_stages": ["early", "mid", "late"],
        "deadline": today + timedelta(days=60),
        "description": "Premier conference on human-computer interaction.",
        "keywords": ["HCI", "user experience", "interaction design"],
        "funding_amount": None,
        "prestige_level": "high",
        "geographic_scope": "global",
        "source_url": "https://chi.acm.org/",
        "organization": "ACM SIGCHI",
        "requires_subscription": False,
        "subscription_tier": None
    },
    {
        "opportunity_id": "aaai_2027",
        "title": "AAAI 2027 - Association for the Advancement of Artificial Intelligence",
        "opportunity_type": "conference",
        "disciplines": ["Computer Science", "AI"],
        "eligible_stages": ["mid", "late"],
        "deadline": today + timedelta(days=90),
        "description": "Major AI conference covering all aspects of artificial intelligence.",
        "keywords": ["artificial intelligence", "AI research"],
        "funding_amount": None,
        "prestige_level": "high",
        "geographic_scope": "global",
        "source_url": "https://aaai.org/",
        "organization": "AAAI",
        "requires_subscription": False,
        "subscription_tier": None
    },
    
    # Workshops
    {
        "opportunity_id": "ml_summer_school_2026",
        "title": "Machine Learning Summer School 2026",
        "opportunity_type": "workshop",
        "disciplines": ["Computer Science", "Machine Learning"],
        "eligible_stages": ["early", "mid"],
        "deadline": today + timedelta(days=50),
        "description": "Two-week intensive ML training program.",
        "keywords": ["machine learning", "summer school", "training"],
        "funding_amount": None,
        "prestige_level": "medium",
        "geographic_scope": "global",
        "source_url": "https://mlss.cc/",
        "organization": "MLSS",
        "requires_subscription": False,
        "subscription_tier": None
    },
    {
        "opportunity_id": "data_science_bootcamp_2026",
        "title": "Data Science for PhDs Bootcamp",
        "opportunity_type": "workshop",
        "disciplines": ["Computer Science", "Statistics", "Data Science"],
        "eligible_stages": ["early", "mid"],
        "deadline": today + timedelta(days=25),
        "description": "Intensive data science skills workshop.",
        "keywords": ["data science", "data analysis", "statistics"],
        "funding_amount": None,
        "prestige_level": "low",
        "geographic_scope": "us",
        "source_url": None,
        "organization": "DS Academy",
        "requires_subscription": False,
        "subscription_tier": None
    },
    
    # Grants
    {
        "opportunity_id": "aws_ml_research_grant_2026",
        "title": "AWS Machine Learning Research Grant",
        "opportunity_type": "grant",
        "disciplines": ["Computer Science", "Machine Learning", "AI"],
        "eligible_stages": ["mid", "late"],
        "deadline": today + timedelta(days=65),
        "description": "Research grants for ML projects using AWS infrastructure.",
        "keywords": ["machine learning", "cloud computing", "AWS"],
        "funding_amount": 20000.0,
        "prestige_level": "medium",
        "geographic_scope": "global",
        "source_url": "https://aws.amazon.com/grants/",
        "organization": "Amazon Web Services",
        "requires_subscription": True,
        "subscription_tier": "premium"
    },
    {
        "opportunity_id": "microsoft_research_grant_2026",
        "title": "Microsoft Research PhD Fellowship",
        "opportunity_type": "fellowship",
        "disciplines": ["Computer Science", "AI", "Systems"],
        "eligible_stages": ["mid"],
        "deadline": today + timedelta(days=80),
        "description": "Two-year fellowship for exceptional PhD students.",
        "keywords": ["systems", "AI", "software engineering"],
        "funding_amount": 42000.0,
        "prestige_level": "high",
        "geographic_scope": "global",
        "source_url": "https://www.microsoft.com/en-us/research/",
        "organization": "Microsoft Research",
        "requires_subscription": True,
        "subscription_tier": "premium"
    },
    
    # Competitions
    {
        "opportunity_id": "kaggle_competition_2026",
        "title": "Kaggle PhD Challenge 2026",
        "opportunity_type": "competition",
        "disciplines": ["Computer Science", "Data Science", "AI"],
        "eligible_stages": ["early", "mid", "late"],
        "deadline": today + timedelta(days=35),
        "description": "Data science competition for PhD students.",
        "keywords": ["data science", "machine learning", "competition"],
        "funding_amount": 10000.0,
        "prestige_level": "medium",
        "geographic_scope": "global",
        "source_url": "https://www.kaggle.com/",
        "organization": "Kaggle",
        "requires_subscription": False,
        "subscription_tier": None
    },
    
    # Biology opportunities
    {
        "opportunity_id": "nih_f31_2026",
        "title": "NIH Ruth L. Kirschstein Predoctoral Individual Fellowship (F31)",
        "opportunity_type": "fellowship",
        "disciplines": ["Biology", "Life Sciences", "Medical Sciences"],
        "eligible_stages": ["mid", "late"],
        "deadline": today + timedelta(days=70),
        "description": "NIH fellowship for predoctoral biomedical research training.",
        "keywords": ["biomedical research", "health sciences", "NIH"],
        "funding_amount": 30000.0,
        "prestige_level": "high",
        "geographic_scope": "us",
        "source_url": "https://grants.nih.gov/grants/guide/pa-files/pa-21-051.html",
        "organization": "National Institutes of Health",
        "requires_subscription": False,
        "subscription_tier": None
    },
    {
        "opportunity_id": "gordon_research_conference_2026",
        "title": "Gordon Research Conference - Cell Biology",
        "opportunity_type": "conference",
        "disciplines": ["Biology", "Cell Biology", "Molecular Biology"],
        "eligible_stages": ["mid", "late"],
        "deadline": today + timedelta(days=55),
        "description": "Premier forum for cell biology research.",
        "keywords": ["cell biology", "molecular biology", "research"],
        "funding_amount": None,
        "prestige_level": "high",
        "geographic_scope": "us",
        "source_url": "https://www.grc.org/",
        "organization": "Gordon Research Conferences",
        "requires_subscription": False,
        "subscription_tier": None
    },
]


def get_catalog():
    """Return the static opportunities catalog."""
    return STATIC_OPPORTUNITIES_CATALOG


def get_active_opportunities():
    """Return only active opportunities (deadline not passed)."""
    today = date.today()
    return [
        opp for opp in STATIC_OPPORTUNITIES_CATALOG
        if opp["deadline"] >= today
    ]


def get_opportunities_by_type(opportunity_type: str):
    """Get opportunities filtered by type."""
    return [
        opp for opp in STATIC_OPPORTUNITIES_CATALOG
        if opp["opportunity_type"] == opportunity_type
    ]


def get_free_opportunities():
    """Get opportunities that don't require subscription."""
    return [
        opp for opp in STATIC_OPPORTUNITIES_CATALOG
        if not opp["requires_subscription"]
    ]


def get_premium_opportunities():
    """Get opportunities that require premium subscription."""
    return [
        opp for opp in STATIC_OPPORTUNITIES_CATALOG
        if opp["requires_subscription"]
    ]
