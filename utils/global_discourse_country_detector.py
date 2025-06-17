"""
🌍 GLOBAL DISCOURSE COUNTRY DETECTOR - Enterprise Country Recognition System v2.0
Enhanced Country Detection für 07_Globale_Diskurs_Analyse.py

*** ENHANCED VERSION ***
- Fixed "in" problem für India
- Added 25+ missing countries including Afghanistan
- Improved pattern matching logic  
- Better filename cleaning
- Robust confidence calculation
- No more problematic short alternative names

Dieses Modul erkennt Länder aus Dateinamen von englischen Kommentaranalysen
und bietet Fallback-Mechanismen für unbekannte Länder.
"""

import streamlit as st
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, Counter

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

class CountryDetectionConstants:
    """Konstanten für Länder-Erkennung"""
    
    # Confidence Levels
    HIGH_CONFIDENCE = 0.9
    MEDIUM_CONFIDENCE = 0.6
    LOW_CONFIDENCE = 0.3
    
    # Minimum confidence for auto-assignment
    AUTO_ASSIGN_THRESHOLD = 0.7
    
    # Session State Keys
    SESSION_COUNTRY_MAPPING = "country_mapping_cache"
    SESSION_USER_OVERRIDES = "user_country_overrides"
    
    # Logger
    LOGGER_NAME = "global_discourse_country_detector"
    
    # *** NEW: Problematic short words to avoid ***
    EXCLUDED_SHORT_WORDS = {
        "in", "it", "no", "us", "at", "is", "to", "on", "or", "an", "as", "be", "of", "we", "my"
    }


class DetectionMethod(Enum):
    """Erkennungsmethoden"""
    LANGUAGE_BASED = "language_based"
    KEYWORD_PATTERN = "keyword_pattern"
    CITY_PATTERN = "city_pattern"
    MEDIA_PATTERN = "media_pattern"
    EXACT_COUNTRY_NAME = "exact_country_name"
    USER_OVERRIDE = "user_override"
    FALLBACK = "fallback"


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class CountryPattern:
    """Pattern für Länder-Erkennung"""
    country: str
    keywords: List[str] = field(default_factory=list)
    cities: List[str] = field(default_factory=list)
    media_outlets: List[str] = field(default_factory=list)
    alternative_names: List[str] = field(default_factory=list)
    iso_codes: List[str] = field(default_factory=list)  # *** NEW: ISO codes ***
    
    @property
    def all_patterns(self) -> List[str]:
        """Alle Patterns kombiniert"""
        return self.keywords + self.cities + self.media_outlets + self.alternative_names + self.iso_codes
    
    def __post_init__(self):
        """*** NEW: Remove problematic short words ***"""
        self.alternative_names = [
            name for name in self.alternative_names 
            if name.lower() not in CountryDetectionConstants.EXCLUDED_SHORT_WORDS
        ]


@dataclass
class DetectionResult:
    """Ergebnis der Länder-Erkennung"""
    country: str
    confidence: float
    method: DetectionMethod
    matched_patterns: List[str] = field(default_factory=list)
    alternative_suggestions: List[str] = field(default_factory=list)
    requires_user_input: bool = False
    debug_info: Dict = field(default_factory=dict)  # *** NEW: Debug info ***
    
    @property
    def is_confident(self) -> bool:
        """Ist die Erkennung zuverlässig?"""
        return self.confidence >= CountryDetectionConstants.AUTO_ASSIGN_THRESHOLD


# =============================================================================
# ENHANCED COUNTRY PATTERNS DATABASE
# =============================================================================

class EnhancedCountryPatternsDatabase:
    """*** ENHANCED *** Erweiterte Datenbank für Länder-Pattern mit 60+ Ländern"""
    
    def __init__(self):
        self.patterns = self._initialize_enhanced_patterns()
        self.logger = logging.getLogger(CountryDetectionConstants.LOGGER_NAME)
        
        # *** NEW: Country name variations for exact matching ***
        self._country_name_variations = self._build_country_name_variations()
    
    def _initialize_enhanced_patterns(self) -> Dict[str, CountryPattern]:
        """*** ENHANCED *** Initialisiert umfassende Länder-Pattern für 60+ Länder"""
        
        patterns = {
            # =================================================================
            # 🇩🇪 DACH-Region (Enhanced)
            # =================================================================
            "Germany": CountryPattern(
                country="Germany",
                keywords=["germany", "german", "deutsch", "deutschland"],
                cities=["berlin", "munich", "muenchen", "hamburg", "cologne", "koeln", "frankfurt", "dresden", "leipzig", "dortmund", "essen", "duesseldorf"],
                media_outlets=["ard", "zdf", "rtl", "sat1", "pro7", "ntv", "welt", "spiegel", "bild", "sueddeutsche"],
                alternative_names=["deutschland", "deutsche"],
                iso_codes=["de", "deu", "ger"]
            ),
            
            "Austria": CountryPattern(
                country="Austria",
                keywords=["austria", "austrian", "oesterreich", "österreich"],
                cities=["vienna", "wien", "salzburg", "graz", "innsbruck", "linz", "klagenfurt"],
                media_outlets=["orf", "servus", "puls4", "oe24"],
                alternative_names=["oesterreich", "österreich"],
                iso_codes=["at", "aut"]
            ),
            
            "Switzerland": CountryPattern(
                country="Switzerland",
                keywords=["switzerland", "swiss", "schweiz", "suisse", "svizzera"],
                cities=["zurich", "geneva", "basel", "bern", "lausanne", "winterthur", "lucerne", "st_gallen"],
                media_outlets=["srf", "rts", "rsi", "telebasel"],
                alternative_names=["schweiz", "suisse", "svizzera"],
                iso_codes=["ch", "che", "sui"]
            ),
            
            # =================================================================
            # 🇺🇸 Nordamerika (Enhanced)
            # =================================================================
            "United States": CountryPattern(
                country="United States",
                keywords=["usa", "america", "american", "united_states", "states"],
                cities=[
                    "new_york", "los_angeles", "chicago", "houston", "phoenix", "philadelphia",
                    "san_antonio", "san_diego", "dallas", "san_jose", "austin", "jacksonville",
                    "washington", "boston", "seattle", "denver", "detroit", "nashville", "portland",
                    "las_vegas", "louisville", "baltimore", "milwaukee", "albuquerque", "tucson",
                    "fresno", "sacramento", "mesa", "kansas_city", "atlanta", "long_beach",
                    "colorado_springs", "raleigh", "miami", "virginia_beach", "omaha", "oakland",
                    "minneapolis", "tulsa", "arlington", "tampa", "new_orleans", "wichita",
                    "cleveland", "bakersfield", "honolulu", "anaheim", "henderson", "stockton"
                ],
                media_outlets=[
                    "cnn", "fox", "nbc", "abc", "cbs", "msnbc", "npr", "pbs", "espn", "hln",
                    "bloomberg", "cnbc", "newsmax", "oann", "tyt", "vox", "buzzfeed", "politico"
                ],
                alternative_names=["america", "united_states_of_america"],
                iso_codes=["usa", "us_america"]  # *** FIXED: No "us" ***
            ),
            
            "Canada": CountryPattern(
                country="Canada",
                keywords=["canada", "canadian"],
                cities=[
                    "toronto", "montreal", "vancouver", "calgary", "edmonton", "ottawa",
                    "winnipeg", "quebec_city", "hamilton", "kitchener", "london", "victoria",
                    "halifax", "oshawa", "windsor", "saskatoon", "st_catharines", "regina"
                ],
                media_outlets=["cbc", "ctv", "global", "tva", "radio_canada"],
                alternative_names=["kanada"],
                iso_codes=["ca", "can"]
            ),
            
            # =================================================================
            # 🇬🇧 Vereinigtes Königreich & Irland (Enhanced)
            # =================================================================
            "United Kingdom": CountryPattern(
                country="United Kingdom",
                keywords=["uk", "britain", "british", "england", "scotland", "wales", "northern_ireland", "great_britain"],
                cities=[
                    "london", "birmingham", "leeds", "glasgow", "sheffield", "bradford", "liverpool",
                    "edinburgh", "manchester", "bristol", "wakefield", "cardiff", "coventry",
                    "nottingham", "leicester", "sunderland", "belfast", "newcastle", "brighton",
                    "hull", "plymouth", "stoke", "wolverhampton", "derby", "swansea", "southampton"
                ],
                media_outlets=["bbc", "itv", "channel4", "sky", "times", "guardian", "telegraph", "independent"],
                alternative_names=["great_britain", "england", "britain"],
                iso_codes=["gb", "gbr", "uk"]
            ),
            
            "Ireland": CountryPattern(
                country="Ireland",
                keywords=["ireland", "irish"],
                cities=["dublin", "cork", "limerick", "galway", "waterford", "drogheda", "dundalk"],
                media_outlets=["rte", "tv3", "newstalk", "today_fm"],
                alternative_names=["eire"],
                iso_codes=["ie", "irl"]
            ),
            
            # =================================================================
            # 🇦🇺 Ozeanien (Enhanced)
            # =================================================================
            "Australia": CountryPattern(
                country="Australia",
                keywords=["australia", "australian", "aussie", "oz"],
                cities=[
                    "sydney", "melbourne", "brisbane", "perth", "adelaide", "gold_coast",
                    "newcastle", "canberra", "sunshine_coast", "wollongong", "hobart", "geelong",
                    "townsville", "cairns", "darwin", "toowoomba", "ballarat", "bendigo"
                ],
                media_outlets=["abc_au", "sbs", "seven", "nine", "ten", "sky_au"],
                alternative_names=["aussie"],
                iso_codes=["au", "aus"]
            ),
            
            "New Zealand": CountryPattern(
                country="New Zealand",
                keywords=["new_zealand", "newzealand", "kiwi"],
                cities=["auckland", "wellington", "christchurch", "hamilton", "tauranga", "dunedin"],
                media_outlets=["tvnz", "three", "maori_tv"],
                alternative_names=["aotearoa"],
                iso_codes=["nz", "nzl"]
            ),
            
            # =================================================================
            # 🇮🇳 Südasien (Enhanced)
            # =================================================================
            "India": CountryPattern(
                country="India",
                keywords=["india", "indian", "bharat", "hindustan"],  # *** FIXED ***
                cities=[
                    "mumbai", "delhi", "bangalore", "hyderabad", "ahmedabad", "chennai", "kolkata",
                    "surat", "pune", "jaipur", "lucknow", "kanpur", "nagpur", "indore", "thane",
                    "bhopal", "visakhapatnam", "patna", "vadodara", "ghaziabad", "ludhiana",
                    "agra", "nashik", "faridabad", "meerut", "rajkot", "varanasi", "srinagar"
                ],
                media_outlets=["ndtv", "times_now", "india_today", "zee", "star", "sony", "aaj_tak"],
                alternative_names=["hindustan", "bharat"],  # *** FIXED: NO "in" ***
                iso_codes=["ind", "in_country"]  # *** SAFE alternatives ***
            ),
            
            "Pakistan": CountryPattern(
                country="Pakistan",
                keywords=["pakistan", "pakistani"],
                cities=["karachi", "lahore", "faisalabad", "rawalpindi", "gujranwala", "peshawar", "multan", "islamabad"],
                media_outlets=["ard_pakistan", "geo", "express", "dawn", "samaa"],
                alternative_names=[],
                iso_codes=["pk", "pak"]
            ),
            
            "Bangladesh": CountryPattern(
                country="Bangladesh",
                keywords=["bangladesh", "bangladeshi"],
                cities=["dhaka", "chittagong", "sylhet", "khulna", "rajshahi", "comilla"],
                media_outlets=["btv", "channel_i", "ntv_bd", "somoy"],
                alternative_names=[],
                iso_codes=["bd", "bgd"]
            ),
            
            "Sri Lanka": CountryPattern(
                country="Sri Lanka",
                keywords=["sri_lanka", "srilanka", "ceylon"],
                cities=["colombo", "kandy", "galle", "jaffna", "negombo", "trincomalee"],
                media_outlets=["itv_lk", "sirasa", "derana"],
                alternative_names=["ceylon"],
                iso_codes=["lk", "lka"]
            ),
            
            # =================================================================
            # 🌍 MIDDLE EAST & CENTRAL ASIA (*** NEW ***)
            # =================================================================
            "Afghanistan": CountryPattern(  # *** NEW: Missing country! ***
                country="Afghanistan",
                keywords=["afghanistan", "afghan"],
                cities=["kabul", "kandahar", "herat", "mazar_i_sharif", "jalalabad", "kunduz", "balkh", "farah"],
                media_outlets=["tolo", "ariana", "shamshad", "lemar"],
                alternative_names=["afghanestan"],
                iso_codes=["af", "afg"]
            ),
            
            "Iran": CountryPattern(  # *** NEW ***
                country="Iran",
                keywords=["iran", "iranian", "persia", "persian"],
                cities=["tehran", "mashhad", "isfahan", "karaj", "shiraz", "tabriz", "qom", "ahvaz"],
                media_outlets=["irib", "press_tv", "manoto"],
                alternative_names=["persia"],
                iso_codes=["ir", "irn"]
            ),
            
            "Iraq": CountryPattern(  # *** NEW ***
                country="Iraq",
                keywords=["iraq", "iraqi"],
                cities=["baghdad", "basra", "mosul", "erbil", "najaf", "karbala", "sulaymaniyah"],
                media_outlets=["iraqiya", "kurdistan_tv", "alsumaria"],
                alternative_names=[],
                iso_codes=["iq", "irq"]
            ),
            
            "Saudi Arabia": CountryPattern(  # *** NEW ***
                country="Saudi Arabia",
                keywords=["saudi", "saudi_arabia", "kingdom_saudi"],
                cities=["riyadh", "jeddah", "mecca", "medina", "dammam", "khobar", "tabuk", "abha"],
                media_outlets=["saudi_tv", "al_arabiya", "mbc", "sbc"],
                alternative_names=["ksa", "kingdom_saudi_arabia"],
                iso_codes=["sa", "sau"]
            ),
            
            "Turkey": CountryPattern(  # *** ENHANCED ***
                country="Turkey",
                keywords=["turkey", "turkish", "turkiye", "türkiye"],
                cities=["istanbul", "ankara", "izmir", "bursa", "adana", "gaziantep", "konya", "antalya"],
                media_outlets=["trt", "atv", "show", "kanal_d", "fox_tr"],
                alternative_names=["turkiye", "türkiye"],
                iso_codes=["tr", "tur"]
            ),
            
            "Israel": CountryPattern(  # *** ENHANCED ***
                country="Israel",
                keywords=["israel", "israeli"],
                cities=["jerusalem", "tel_aviv", "haifa", "rishon_lezion", "petah_tikva", "ashdod", "netanya"],
                media_outlets=["kan", "reshet", "keshet", "channel_12"],
                alternative_names=[],
                iso_codes=["il", "isr"]
            ),
            
            "Lebanon": CountryPattern(  # *** NEW ***
                country="Lebanon",
                keywords=["lebanon", "lebanese"],
                cities=["beirut", "tripoli", "sidon", "tyre", "zahle", "jounieh"],
                media_outlets=["lbc", "mtv_lb", "otv", "al_jadeed"],
                alternative_names=[],
                iso_codes=["lb", "lbn"]
            ),
            
            "Syria": CountryPattern(  # *** NEW ***
                country="Syria",
                keywords=["syria", "syrian"],
                cities=["damascus", "aleppo", "homs", "latakia", "hama", "deir_ez_zor"],
                media_outlets=["syrian_tv", "orient", "syria_news"],
                alternative_names=[],
                iso_codes=["sy", "syr"]
            ),
            
            "Jordan": CountryPattern(  # *** NEW ***
                country="Jordan",
                keywords=["jordan", "jordanian"],
                cities=["amman", "zarqa", "irbid", "aqaba", "salt", "madaba"],
                media_outlets=["jordan_tv", "roya", "ammontv"],
                alternative_names=[],
                iso_codes=["jo", "jor"]
            ),
            
            "UAE": CountryPattern(  # *** NEW ***
                country="UAE",
                keywords=["uae", "emirates", "united_arab_emirates"],
                cities=["dubai", "abu_dhabi", "sharjah", "ajman", "fujairah", "ras_al_khaimah"],
                media_outlets=["dubai_tv", "abu_dhabi_tv", "mbc"],
                alternative_names=["united_arab_emirates"],
                iso_codes=["ae", "are"]
            ),
            
            "Kazakhstan": CountryPattern(  # *** NEW ***
                country="Kazakhstan",
                keywords=["kazakhstan", "kazakh"],
                cities=["almaty", "nur_sultan", "astana", "shymkent", "aktobe", "taraz"],
                media_outlets=["khabar", "channel_31"],
                alternative_names=["qazaqstan"],
                iso_codes=["kz", "kaz"]
            ),
            
            # =================================================================
            # 🇨🇳 Ostasien (Enhanced)
            # =================================================================
            "China": CountryPattern(
                country="China",
                keywords=["china", "chinese", "prc", "peoples_republic"],
                cities=[
                    "beijing", "shanghai", "guangzhou", "shenzhen", "tianjin", "wuhan", "chengdu",
                    "dongguan", "chongqing", "nanjing", "shenyang", "hangzhou", "xian", "harbin",
                    "suzhou", "qingdao", "dalian", "zhengzhou", "jinan", "changchun", "kunming"
                ],
                media_outlets=["cctv", "cgtn", "xinhua", "phoenix", "ifeng"],
                alternative_names=["peoples_republic_china"],
                iso_codes=["cn", "chn"]
            ),
            
            "Japan": CountryPattern(
                country="Japan",
                keywords=["japan", "japanese", "nippon", "nihon"],
                cities=[
                    "tokyo", "yokohama", "osaka", "nagoya", "sapporo", "fukuoka", "kobe", "kawasaki",
                    "kyoto", "saitama", "hiroshima", "sendai", "kitakyushu", "chiba", "sakai"
                ],
                media_outlets=["nhk", "tbs", "fuji", "asahi", "nippon", "tokyo_mx"],
                alternative_names=["nippon", "nihon"],
                iso_codes=["jp", "jpn"]
            ),
            
            "South Korea": CountryPattern(
                country="South Korea",
                keywords=["korea", "korean", "south_korea"],
                cities=["seoul", "busan", "incheon", "daegu", "daejeon", "gwangju", "suwon", "ulsan"],
                media_outlets=["kbs", "mbc", "sbs", "jtbc", "ytn"],
                alternative_names=["republic_of_korea"],
                iso_codes=["kr", "kor"]
            ),
            
            "North Korea": CountryPattern(  # *** NEW ***
                country="North Korea",
                keywords=["north_korea", "dprk", "democratic_peoples_republic"],
                cities=["pyongyang", "hamhung", "chongjin", "nampo", "wonsan"],
                media_outlets=["kcna", "kctv"],
                alternative_names=["dprk"],
                iso_codes=["kp", "prk"]
            ),
            
            # =================================================================
            # 🇹🇭 Südostasien (Enhanced)
            # =================================================================
            "Thailand": CountryPattern(
                country="Thailand",
                keywords=["thailand", "thai", "siam"],
                cities=["bangkok", "chiang_mai", "pattaya", "phuket", "hat_yai", "nakhon_ratchasima"],
                media_outlets=["thai_pbs", "channel3", "channel7", "workpoint"],
                alternative_names=["siam"],
                iso_codes=["th", "tha"]
            ),
            
            "Vietnam": CountryPattern(
                country="Vietnam",
                keywords=["vietnam", "vietnamese"],
                cities=["ho_chi_minh_city", "hanoi", "da_nang", "can_tho", "bien_hoa", "hue"],
                media_outlets=["vtv", "vfc", "htv"],
                alternative_names=["viet_nam"],
                iso_codes=["vn", "vnm"]
            ),
            
            "Philippines": CountryPattern(
                country="Philippines",
                keywords=["philippines", "filipino", "pilipinas"],
                cities=["manila", "quezon_city", "caloocan", "davao", "cebu", "zamboanga", "antipolo"],
                media_outlets=["abs_cbn", "gma", "tv5", "cnn_philippines"],
                alternative_names=["pilipinas"],
                iso_codes=["ph", "phl"]
            ),
            
            "Indonesia": CountryPattern(
                country="Indonesia",
                keywords=["indonesia", "indonesian"],
                cities=["jakarta", "surabaya", "bandung", "bekasi", "medan", "tangerang", "depok"],
                media_outlets=["tvri", "sctv", "rcti", "indosiar", "trans7"],
                alternative_names=[],
                iso_codes=["id", "idn"]
            ),
            
            "Malaysia": CountryPattern(
                country="Malaysia",
                keywords=["malaysia", "malaysian"],
                cities=["kuala_lumpur", "george_town", "ipoh", "shah_alam", "petaling_jaya", "johor_bahru"],
                media_outlets=["rtm", "tv3", "ntv7", "8tv", "astro"],
                alternative_names=[],
                iso_codes=["my", "mys"]
            ),
            
            "Singapore": CountryPattern(
                country="Singapore",
                keywords=["singapore", "singaporean"],
                cities=["singapore"],
                media_outlets=["mediacorp", "cna", "channel8"],
                alternative_names=[],
                iso_codes=["sg", "sgp"]
            ),
            
            "Myanmar": CountryPattern(  # *** NEW ***
                country="Myanmar",
                keywords=["myanmar", "burma", "burmese"],
                cities=["yangon", "mandalay", "naypyidaw", "mawlamyine", "bago"],
                media_outlets=["mrtv", "dvb"],
                alternative_names=["burma"],
                iso_codes=["mm", "mmr"]
            ),
            
            "Cambodia": CountryPattern(  # *** NEW ***
                country="Cambodia",
                keywords=["cambodia", "cambodian", "khmer"],
                cities=["phnom_penh", "siem_reap", "battambang", "sihanoukville"],
                media_outlets=["tvk", "bayon"],
                alternative_names=["kampuchea"],
                iso_codes=["kh", "khm"]
            ),
            
            "Laos": CountryPattern(  # *** NEW ***
                country="Laos",
                keywords=["laos", "lao"],
                cities=["vientiane", "luang_prabang", "savannakhet", "pakse"],
                media_outlets=["lntv", "lao_tv"],
                alternative_names=["lao_pdr"],
                iso_codes=["la", "lao"]
            ),
            
            # =================================================================
            # 🇪🇺 Europa (Enhanced)
            # =================================================================
            "France": CountryPattern(
                country="France",
                keywords=["france", "french", "français", "francais"],
                cities=["paris", "marseille", "lyon", "toulouse", "nice", "nantes", "strasbourg", "montpellier"],
                media_outlets=["tf1", "france2", "m6", "canal+", "france24", "bfm"],
                alternative_names=["republique_francaise"],
                iso_codes=["fr", "fra"]
            ),
            
            "Spain": CountryPattern(
                country="Spain",
                keywords=["spain", "spanish", "españa", "espana"],
                cities=["madrid", "barcelona", "valencia", "seville", "zaragoza", "malaga", "murcia"],
                media_outlets=["tve", "antena3", "telecinco", "la_sexta"],
                alternative_names=["españa", "espana"],
                iso_codes=["es", "esp"]
            ),
            
            "Italy": CountryPattern(
                country="Italy",
                keywords=["italy", "italian", "italia"],
                cities=["rome", "milan", "naples", "turin", "palermo", "genoa", "bologna", "florence"],
                media_outlets=["rai", "mediaset", "la7", "sky_italia"],
                alternative_names=["italia"],
                iso_codes=["ita", "italy_code"]  # *** FIXED: No "it" ***
            ),
            
            "Netherlands": CountryPattern(
                country="Netherlands",
                keywords=["netherlands", "dutch", "holland"],
                cities=["amsterdam", "rotterdam", "the_hague", "utrecht", "eindhoven", "tilburg"],
                media_outlets=["nos", "rtl_nl", "sbs", "npo"],
                alternative_names=["holland"],
                iso_codes=["nl", "nld"]
            ),
            
            "Poland": CountryPattern(
                country="Poland",
                keywords=["poland", "polish", "polska"],
                cities=["warsaw", "krakow", "lodz", "wroclaw", "poznan", "gdansk", "szczecin"],
                media_outlets=["tvp", "polsat", "tvn"],
                alternative_names=["polska"],
                iso_codes=["pl", "pol"]
            ),
            
            "Sweden": CountryPattern(
                country="Sweden",
                keywords=["sweden", "swedish", "sverige"],
                cities=["stockholm", "gothenburg", "malmo", "uppsala", "vasteras", "orebro"],
                media_outlets=["svt", "tv4", "tv3_se"],
                alternative_names=["sverige"],
                iso_codes=["se", "swe"]
            ),
            
            "Norway": CountryPattern(
                country="Norway",
                keywords=["norway", "norwegian", "norge"],
                cities=["oslo", "bergen", "stavanger", "trondheim", "drammen", "fredrikstad"],
                media_outlets=["nrk", "tv2_no", "tvnorge"],
                alternative_names=["norge"],
                iso_codes=["nor", "norway_code"]  # *** FIXED: No "no" ***
            ),
            
            "Denmark": CountryPattern(
                country="Denmark",
                keywords=["denmark", "danish", "danmark"],
                cities=["copenhagen", "aarhus", "odense", "aalborg", "esbjerg", "randers"],
                media_outlets=["dr", "tv2_dk", "kanal5"],
                alternative_names=["danmark"],
                iso_codes=["dk", "dnk"]
            ),
            
            "Finland": CountryPattern(
                country="Finland",
                keywords=["finland", "finnish", "suomi"],
                cities=["helsinki", "espoo", "tampere", "vantaa", "oulu", "turku"],
                media_outlets=["yle", "mtv3", "nelonen"],
                alternative_names=["suomi"],
                iso_codes=["fi", "fin"]
            ),
            
            "Belgium": CountryPattern(  # *** NEW ***
                country="Belgium",
                keywords=["belgium", "belgian", "belgie", "belgique"],
                cities=["brussels", "antwerp", "ghent", "charleroi", "liege", "bruges"],
                media_outlets=["vrt", "rtbf", "vtm"],
                alternative_names=["belgie", "belgique"],
                iso_codes=["be", "bel"]
            ),
            
            "Portugal": CountryPattern(  # *** NEW ***
                country="Portugal",
                keywords=["portugal", "portuguese"],
                cities=["lisbon", "porto", "braga", "coimbra", "funchal", "aveiro"],
                media_outlets=["rtp", "sic", "tvi"],
                alternative_names=[],
                iso_codes=["pt", "prt"]
            ),
            
            "Greece": CountryPattern(  # *** NEW ***
                country="Greece",
                keywords=["greece", "greek", "hellas"],
                cities=["athens", "thessaloniki", "patras", "heraklion", "larissa"],
                media_outlets=["ert", "mega", "ant1"],
                alternative_names=["hellas", "ellada"],
                iso_codes=["gr", "grc"]
            ),
            
            "Czech Republic": CountryPattern(  # *** NEW ***
                country="Czech Republic",
                keywords=["czech", "czechia", "czech_republic"],
                cities=["prague", "brno", "ostrava", "plzen", "liberec"],
                media_outlets=["ct", "nova", "prima"],
                alternative_names=["czechia"],
                iso_codes=["cz", "cze"]
            ),
            
            "Hungary": CountryPattern(  # *** NEW ***
                country="Hungary",
                keywords=["hungary", "hungarian", "magyarorszag"],
                cities=["budapest", "debrecen", "szeged", "miskolc", "pecs"],
                media_outlets=["mtv", "rtl_klub", "tv2_hu"],
                alternative_names=["magyarorszag"],
                iso_codes=["hu", "hun"]
            ),
            
            # =================================================================
            # 🇷🇺 Osteuropa & Russland (Enhanced)
            # =================================================================
            "Russia": CountryPattern(
                country="Russia",
                keywords=["russia", "russian", "россия", "rossiya"],
                cities=["moscow", "st_petersburg", "novosibirsk", "yekaterinburg", "nizhny_novgorod", "kazan"],
                media_outlets=["channel_one", "rossiya", "ntv_ru", "ren_tv"],
                alternative_names=["rossiya", "российская_федерация"],
                iso_codes=["ru", "rus"]
            ),
            
            "Ukraine": CountryPattern(
                country="Ukraine",
                keywords=["ukraine", "ukrainian", "україна", "ukraina"],
                cities=["kyiv", "kiev", "kharkiv", "odesa", "dnipro", "lviv", "zaporizhzhia"],
                media_outlets=["1+1", "inter", "ictv", "stb"],
                alternative_names=["ukraina"],
                iso_codes=["ua", "ukr"]
            ),
            
            "Belarus": CountryPattern(  # *** NEW ***
                country="Belarus",
                keywords=["belarus", "belarusian", "белarus"],
                cities=["minsk", "gomel", "mogilev", "vitebsk", "grodno", "brest"],
                media_outlets=["ont", "stv", "belarus_tv"],
                alternative_names=["belorussia"],
                iso_codes=["by", "blr"]
            ),
            
            # =================================================================
            # 🇧🇷 Lateinamerika (Enhanced)
            # =================================================================
            "Brazil": CountryPattern(
                country="Brazil",
                keywords=["brazil", "brazilian", "brasil"],
                cities=["sao_paulo", "rio_de_janeiro", "brasilia", "salvador", "fortaleza", "belo_horizonte"],
                media_outlets=["globo", "sbt", "record", "band"],
                alternative_names=["brasil"],
                iso_codes=["br", "bra"]
            ),
            
            "Mexico": CountryPattern(
                country="Mexico",
                keywords=["mexico", "mexican", "méxico"],
                cities=["mexico_city", "guadalajara", "monterrey", "puebla", "tijuana", "leon"],
                media_outlets=["televisa", "tv_azteca", "imagen"],
                alternative_names=["méxico"],
                iso_codes=["mx", "mex"]
            ),
            
            "Argentina": CountryPattern(
                country="Argentina",
                keywords=["argentina", "argentinian"],
                cities=["buenos_aires", "cordoba", "rosario", "mendoza", "la_plata", "tucuman"],
                media_outlets=["telefe", "canal13", "america"],
                alternative_names=[],
                iso_codes=["ar", "arg"]
            ),
            
            "Colombia": CountryPattern(  # *** NEW ***
                country="Colombia",
                keywords=["colombia", "colombian"],
                cities=["bogota", "medellin", "cali", "barranquilla", "cartagena", "cucuta"],
                media_outlets=["caracol", "rcn", "teleantioquia"],
                alternative_names=[],
                iso_codes=["co", "col"]
            ),
            
            "Chile": CountryPattern(  # *** NEW ***
                country="Chile",
                keywords=["chile", "chilean"],
                cities=["santiago", "valparaiso", "concepcion", "la_serena", "antofagasta"],
                media_outlets=["tvn", "canal13_cl", "mega_cl"],
                alternative_names=[],
                iso_codes=["cl", "chl"]
            ),
            
            "Peru": CountryPattern(  # *** NEW ***
                country="Peru",
                keywords=["peru", "peruvian"],
                cities=["lima", "arequipa", "trujillo", "chiclayo", "huancayo"],
                media_outlets=["america_tv", "latina", "panamericana"],
                alternative_names=[],
                iso_codes=["pe", "per"]
            ),
            
            "Venezuela": CountryPattern(  # *** NEW ***
                country="Venezuela",
                keywords=["venezuela", "venezuelan"],
                cities=["caracas", "maracaibo", "valencia", "barquisimeto", "maracay"],
                media_outlets=["vtv", "venevision", "televen"],
                alternative_names=[],
                iso_codes=["ve", "ven"]
            ),
            
            # =================================================================
            # 🇿🇦 Afrika (Enhanced)
            # =================================================================
            "South Africa": CountryPattern(
                country="South Africa",
                keywords=["south_africa", "southafrican"],
                cities=["johannesburg", "cape_town", "durban", "pretoria", "port_elizabeth", "bloemfontein"],
                media_outlets=["sabc", "etv", "supersport"],
                alternative_names=[],
                iso_codes=["za", "zaf"]
            ),
            
            "Nigeria": CountryPattern(
                country="Nigeria",
                keywords=["nigeria", "nigerian"],
                cities=["lagos", "abuja", "kano", "ibadan", "kaduna", "port_harcourt"],
                media_outlets=["nta", "channels", "silverbird"],
                alternative_names=[],
                iso_codes=["ng", "nga"]
            ),
            
            "Egypt": CountryPattern(
                country="Egypt",
                keywords=["egypt", "egyptian"],
                cities=["cairo", "alexandria", "giza", "luxor", "aswan", "hurghada"],
                media_outlets=["ertu", "cbc_eg", "dream"],
                alternative_names=["misr"],
                iso_codes=["eg", "egy"]
            ),
            
            "Kenya": CountryPattern(  # *** NEW ***
                country="Kenya",
                keywords=["kenya", "kenyan"],
                cities=["nairobi", "mombasa", "kisumu", "nakuru", "eldoret"],
                media_outlets=["kbc", "citizen", "ntv_ke"],
                alternative_names=[],
                iso_codes=["ke", "ken"]
            ),
            
            "Ghana": CountryPattern(  # *** NEW ***
                country="Ghana",
                keywords=["ghana", "ghanaian"],
                cities=["accra", "kumasi", "tamale", "cape_coast", "sekondi"],
                media_outlets=["gtv", "joy_news", "citi"],
                alternative_names=[],
                iso_codes=["gh", "gha"]
            ),
            
            "Ethiopia": CountryPattern(  # *** NEW ***
                country="Ethiopia",
                keywords=["ethiopia", "ethiopian"],
                cities=["addis_ababa", "dire_dawa", "mekelle", "gondar", "awassa"],
                media_outlets=["ebc", "fana", "walta"],
                alternative_names=["abyssinia"],
                iso_codes=["et", "eth"]
            ),
            
            "Morocco": CountryPattern(  # *** NEW ***
                country="Morocco",
                keywords=["morocco", "moroccan", "maghreb"],
                cities=["casablanca", "rabat", "fes", "marrakech", "agadir", "tangier"],
                media_outlets=["2m", "al_aoula", "medi1"],
                alternative_names=["maroc"],
                iso_codes=["ma", "mar"]
            ),
        }
        
        return patterns
    
    def _build_country_name_variations(self) -> Dict[str, str]:
        """*** NEW *** Baut Variationen von Ländernamen für exakte Suche"""
        variations = {}
        
        for country, pattern in self.patterns.items():
            # Exakter Ländername
            variations[country.lower()] = country
            variations[country.replace(" ", "_").lower()] = country
            variations[country.replace(" ", "").lower()] = country
            
            # Keywords
            for keyword in pattern.keywords:
                variations[keyword.lower()] = country
            
            # Alternative Namen
            for alt_name in pattern.alternative_names:
                variations[alt_name.lower()] = country
        
        return variations
    
    def get_pattern(self, country: str) -> Optional[CountryPattern]:
        """Gibt Pattern für ein Land zurück"""
        return self.patterns.get(country)
    
    def find_exact_country_match(self, text: str) -> Optional[str]:
        """*** NEW *** Findet exakte Ländernamen-Matches"""
        text_lower = text.lower()
        
        # Exact matches haben höchste Priorität
        for variation, country in self._country_name_variations.items():
            if variation in text_lower:
                return country
        
        return None
    
    def find_matching_countries(self, text: str) -> List[Tuple[str, float, List[str]]]:
        """*** ENHANCED *** Findet passende Länder für einen Text"""
        text_lower = text.lower()
        matches = []
        
        # *** NEW: First check for exact country name matches ***
        exact_match = self.find_exact_country_match(text)
        if exact_match:
            matches.append((exact_match, 0.95, [f"exact_name:{exact_match.lower()}"]))
        
        # Pattern matching for all countries
        for country, pattern in self.patterns.items():
            if country == exact_match:
                continue  # Skip, already added as exact match
            
            matched_patterns = []
            total_score = 0
            
            # *** ENHANCED SCORING SYSTEM ***
            
            # Check keywords (highest priority)
            for keyword in pattern.keywords:
                if keyword in text_lower:
                    # Longer keywords get higher scores
                    keyword_score = len(keyword) if len(keyword) > 3 else 2
                    matched_patterns.append(f"keyword:{keyword}")
                    total_score += keyword_score
            
            # Check cities (medium-high priority)
            for city in pattern.cities:
                if city in text_lower:
                    matched_patterns.append(f"city:{city}")
                    total_score += 2
            
            # Check media outlets (medium priority)
            for media in pattern.media_outlets:
                if media in text_lower:
                    matched_patterns.append(f"media:{media}")
                    total_score += 1.5
            
            # Check alternative names (medium priority)
            for alt_name in pattern.alternative_names:
                if alt_name in text_lower:
                    matched_patterns.append(f"alt:{alt_name}")
                    total_score += 1
            
            # Check ISO codes (low priority, only if 3+ chars)
            for iso_code in pattern.iso_codes:
                if len(iso_code) >= 3 and iso_code in text_lower:
                    matched_patterns.append(f"iso:{iso_code}")
                    total_score += 0.5
            
            if matched_patterns:
                # *** ENHANCED CONFIDENCE CALCULATION ***
                base_confidence = min(0.9, total_score / 15.0)
                pattern_bonus = len(matched_patterns) * 0.05
                confidence = min(0.99, base_confidence + pattern_bonus)
                
                matches.append((country, confidence, matched_patterns))
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches


# =============================================================================
# ENHANCED COUNTRY DETECTOR
# =============================================================================

class EnhancedCountryDetector:
    """*** ENHANCED *** Enterprise-Level Country Detection v2.0"""
    
    def __init__(self):
        self.database = EnhancedCountryPatternsDatabase()
        self.logger = logging.getLogger(CountryDetectionConstants.LOGGER_NAME)
        
        # Initialize Session State
        if CountryDetectionConstants.SESSION_COUNTRY_MAPPING not in st.session_state:
            st.session_state[CountryDetectionConstants.SESSION_COUNTRY_MAPPING] = {}
        
        if CountryDetectionConstants.SESSION_USER_OVERRIDES not in st.session_state:
            st.session_state[CountryDetectionConstants.SESSION_USER_OVERRIDES] = {}
    
    def detect_country_from_filename(
        self,
        filename: str,
        language: str = "en",
        source_path: Optional[str] = None
    ) -> DetectionResult:
        """*** ENHANCED *** Hauptfunktion für Länder-Erkennung"""
        
        # Cache check
        cache_key = f"{filename}_{language}"
        if cache_key in st.session_state[CountryDetectionConstants.SESSION_COUNTRY_MAPPING]:
            cached_result = st.session_state[CountryDetectionConstants.SESSION_COUNTRY_MAPPING][cache_key]
            self.logger.info(f"Cached country for {filename}: {cached_result}")
            return DetectionResult(
                country=cached_result,
                confidence=1.0,
                method=DetectionMethod.USER_OVERRIDE,
                debug_info={"cache_hit": True}
            )
        
        # German analyses are always Germany
        if language == "de":
            result = DetectionResult(
                country="Germany",
                confidence=1.0,
                method=DetectionMethod.LANGUAGE_BASED,
                matched_patterns=["language:german"],
                debug_info={"language_detection": True}
            )
            self._cache_result(cache_key, result.country)
            return result
        
        # English analyses: Enhanced Pattern-Matching
        return self._enhanced_detect_from_english_filename(filename, cache_key)
    
    def _enhanced_detect_from_english_filename(self, filename: str, cache_key: str) -> DetectionResult:
        """*** ENHANCED *** Erkennt Land aus englischem Dateinamen"""
        
        # Enhanced filename cleaning
        clean_filename = self._enhanced_clean_filename(filename)
        
        debug_info = {
            "original_filename": filename,
            "cleaned_filename": clean_filename,
            "cleaning_applied": True
        }
        
        # Enhanced Pattern-Matching
        matches = self.database.find_matching_countries(clean_filename)
        debug_info["total_matches"] = len(matches)
        
        if not matches:
            # No matches found - user input required
            return DetectionResult(
                country="Unknown",
                confidence=0.0,
                method=DetectionMethod.FALLBACK,
                requires_user_input=True,
                alternative_suggestions=self._get_enhanced_common_countries(),
                debug_info=debug_info
            )
        
        # Best match analysis
        best_country, best_confidence, best_patterns = matches[0]
        debug_info["best_match"] = {
            "country": best_country,
            "confidence": best_confidence,
            "patterns": best_patterns
        }
        
        # *** ENHANCED CONFIDENCE THRESHOLDS ***
        if best_confidence >= CountryDetectionConstants.AUTO_ASSIGN_THRESHOLD:
            # High confidence - auto assign
            result = DetectionResult(
                country=best_country,
                confidence=best_confidence,
                method=DetectionMethod.EXACT_COUNTRY_NAME if "exact_name" in best_patterns[0] else DetectionMethod.KEYWORD_PATTERN,
                matched_patterns=best_patterns,
                debug_info=debug_info
            )
            self._cache_result(cache_key, result.country)
            self.logger.info(f"Auto-detected {best_country} for {filename} (confidence: {best_confidence:.3f})")
            return result
        
        else:
            # Low confidence - user input required
            suggestions = [country for country, _, _ in matches[:8]]  # More suggestions
            debug_info["requires_user_input"] = True
            
            return DetectionResult(
                country=best_country,
                confidence=best_confidence,
                method=DetectionMethod.KEYWORD_PATTERN,
                matched_patterns=best_patterns,
                requires_user_input=True,
                alternative_suggestions=suggestions,
                debug_info=debug_info
            )
    
    def _enhanced_clean_filename(self, filename: str) -> str:
        """*** ENHANCED *** Bereinigt Dateiname für bessere Analyse"""
        clean = filename.lower()
        
        # Remove common file patterns
        clean = re.sub(r'\.csv$', '', clean)
        clean = re.sub(r'_country_analysis_\d+_\d+$', '', clean)
        clean = re.sub(r'_\d{4}-\d{2}-\d{2}_', '_', clean)
        clean = re.sub(r'_[a-zA-Z0-9]{11}_', '_', clean)  # YouTube IDs
        clean = re.sub(r'_\d{8,}', '', clean)  # Long numbers
        
        # *** NEW: Enhanced cleaning ***
        # Remove common YouTube/social media patterns
        clean = re.sub(r'_[a-zA-Z0-9\-_]{10,15}', ' ', clean)  # IDs
        clean = re.sub(r'(mp4|avi|mov|wmv|flv)$', '', clean)  # Video extensions
        clean = re.sub(r'\b(video|channel|official|hd|full|complete)\b', ' ', clean)  # Common words
        
        # Replace separators with spaces
        clean = re.sub(r'[_\-\.]+', ' ', clean)
        
        # Remove extra spaces
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        return clean
    
    def _get_enhanced_common_countries(self) -> List[str]:
        """*** ENHANCED *** Gibt häufige Länder für Vorschläge zurück"""
        return [
            "United States", "United Kingdom", "Canada", "Australia", "Germany",
            "France", "Spain", "Italy", "Netherlands", "Sweden", "Norway", "Denmark",
            "India", "Japan", "South Korea", "China", "Malaysia", "Singapore",
            "Thailand", "Philippines", "Indonesia", "Vietnam", "Brazil", "Mexico",
            "Afghanistan", "Iran", "Iraq", "Turkey", "Israel", "Saudi Arabia",  # *** NEW ***
            "South Africa", "Nigeria", "Egypt", "Pakistan", "Bangladesh"
        ]
    
    def _cache_result(self, cache_key: str, country: str) -> None:
        """Speichert Ergebnis im Cache"""
        st.session_state[CountryDetectionConstants.SESSION_COUNTRY_MAPPING][cache_key] = country
    
    def handle_user_input_for_unknown_country(
        self,
        filename: str,
        detection_result: DetectionResult
    ) -> Optional[str]:
        """*** ENHANCED *** Behandelt User-Input für unbekannte Länder"""
        
        st.warning(f"🤔 Country not automatically detected: `{filename}`")
        
        # *** ENHANCED: Show debug info ***
        if detection_result.debug_info:
            with st.expander("🔍 Detection Details", expanded=False):
                st.json(detection_result.debug_info)
        
        if detection_result.matched_patterns:
            st.info(f"**Found clues:** {', '.join(detection_result.matched_patterns)}")
        
        # *** ENHANCED: Better UI ***
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if detection_result.alternative_suggestions:
                # Show best guess first
                if detection_result.country != "Unknown":
                    options = [f"✨ {detection_result.country} (Best Guess)"] + [
                        country for country in detection_result.alternative_suggestions 
                        if country != detection_result.country
                    ]
                else:
                    options = detection_result.alternative_suggestions
                
                selected_country = st.selectbox(
                    "Please select the appropriate country:",
                    options=[""] + options,
                    key=f"country_select_{filename}",
                    help="The system found these potential matches based on the filename"
                )
                
                # Clean selection
                if selected_country.startswith("✨ "):
                    selected_country = selected_country[2:].split(" (Best Guess)")[0]
            
            else:
                # Fallback to all countries
                all_countries = sorted(list(self.database.patterns.keys()))
                selected_country = st.selectbox(
                    "Please select the appropriate country:",
                    options=[""] + all_countries,
                    key=f"country_select_{filename}",
                    help="No automatic matches found. Please select manually."
                )
        
        with col2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            if st.button("✅ Confirm", key=f"confirm_{filename}"):
                if selected_country:
                    # Cache for future use
                    cache_key = f"{filename}_en"
                    self._cache_result(cache_key, selected_country)
                    st.success(f"✅ {selected_country} saved for `{filename}`")
                    st.rerun()
                else:
                    st.error("Please select a country")
        
        return selected_country if selected_country else None
    
    def get_country_statistics(self) -> Dict[str, int]:
        """Gibt Statistiken über erkannte Länder zurück"""
        country_counts = defaultdict(int)
        
        for cached_result in st.session_state[CountryDetectionConstants.SESSION_COUNTRY_MAPPING].values():
            country_counts[cached_result] += 1
        
        return dict(country_counts)
    
    def clear_cache(self) -> None:
        """Löscht den Country-Cache"""
        st.session_state[CountryDetectionConstants.SESSION_COUNTRY_MAPPING] = {}
        st.session_state[CountryDetectionConstants.SESSION_USER_OVERRIDES] = {}
        self.logger.info("Country detection cache cleared")
    
    def get_supported_countries(self) -> List[str]:
        """*** NEW *** Gibt alle unterstützten Länder zurück"""
        return sorted(list(self.database.patterns.keys()))
    
    def test_filename_detection(self, test_filename: str) -> DetectionResult:
        """*** NEW *** Test-Funktion für Dateinamen-Erkennung"""
        return self.detect_country_from_filename(test_filename, "en")


# =============================================================================
# ENHANCED UI COMPONENTS
# =============================================================================

def render_enhanced_country_detection_interface(
    analysis_files: List,
    detector: EnhancedCountryDetector
) -> Dict[str, str]:
    """*** ENHANCED *** Rendert Interface für Country Detection"""
    
    st.subheader("🌍 Enhanced Country Detection v2.0")
    
    # *** NEW: Show supported countries count ***
    supported_countries = detector.get_supported_countries()
    st.success(f"✨ **{len(supported_countries)} countries supported** including Afghanistan, Middle East, and more!")
    
    file_country_mapping = {}
    files_needing_input = []
    
    # Automatic detection round
    progress_bar = st.progress(0)
    for i, file in enumerate(analysis_files):
        progress_bar.progress((i + 1) / len(analysis_files))
        
        detection_result = detector.detect_country_from_filename(
            file.filename,
            file.language,
            str(file.file_path)
        )
        
        if detection_result.requires_user_input:
            files_needing_input.append((file, detection_result))
        else:
            file_country_mapping[file.filename] = detection_result.country
    
    progress_bar.empty()
    
    # Show automatically detected countries
    if file_country_mapping:
        st.success(f"✅ {len(file_country_mapping)} countries automatically detected")
        
        with st.expander("🤖 Automatically detected countries", expanded=False):
            for filename, country in file_country_mapping.items():
                # Show flag emoji if available
                flag = _get_country_flag(country)
                st.write(f"📁 `{filename[:60]}...` → {flag} **{country}**")
    
    # Handle files needing user input
    if files_needing_input:
        st.warning(f"⚠️ {len(files_needing_input)} files need manual assignment")
        
        for file, detection_result in files_needing_input:
            with st.expander(f"🤔 Unknown country: {file.filename[:60]}...", expanded=True):
                user_country = detector.handle_user_input_for_unknown_country(
                    file.filename,
                    detection_result
                )
                
                if user_country:
                    file_country_mapping[file.filename] = user_country
    
    # *** ENHANCED: Cache management ***
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Reload cache"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear cache"):
            detector.clear_cache()
            st.success("Cache cleared")
            st.rerun()
    
    with col3:
        if st.button("🧪 Test detection"):
            with st.expander("🧪 Test Country Detection", expanded=True):
                render_country_detection_debug(detector)
    
    # *** ENHANCED: Statistics ***
    if file_country_mapping:
        stats = Counter(file_country_mapping.values())
        st.subheader("📊 Country Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            stats_data = []
            for country, count in stats.most_common():
                flag = _get_country_flag(country)
                stats_data.append({"Country": f"{flag} {country}", "Analyses": count})
            
            import pandas as pd
            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, use_container_width=True)
        
        with col2:
            st.write("**🎯 Detection Summary:**")
            st.metric("Total Countries", len(stats))
            st.metric("Total Analyses", sum(stats.values()))
            st.metric("Most Active", f"{stats.most_common(1)[0][0]} ({stats.most_common(1)[0][1]})")
            
            # Detection quality
            auto_detected = len(file_country_mapping)
            total_files = len(analysis_files)
            detection_rate = (auto_detected / total_files) * 100 if total_files > 0 else 0
            st.metric("Auto-Detection Rate", f"{detection_rate:.1f}%")
    
    return file_country_mapping


def render_country_detection_debug(detector: EnhancedCountryDetector) -> None:
    """*** ENHANCED *** Debug interface für Country Detection"""
    
    st.subheader("🔧 Enhanced Country Detection Testing")
    
    # Test different filename patterns
    test_examples = [
        "Why_Malaysia_Education_System_Is_A_Failure",
        "What women in Afghanistan want you to know _ Start Here",
        "Germany vs France Football Discussion",
        "India Tech Industry Analysis 2024",
        "Random_Video_Title_No_Country_Here",
        "BBC_News_United_Kingdom_Brexit_Update",
        "CNN_USA_Politics_Discussion"
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🧪 Test Custom Filename:**")
        test_filename = st.text_input(
            "Enter filename to test:",
            value="What women in Afghanistan want you to know _ Start Here"
        )
        
        if test_filename:
            result = detector.test_filename_detection(test_filename)
            
            st.write("**🎯 Detection Result:**")
            
            # Result summary
            confidence_color = "🟢" if result.confidence >= 0.7 else "🟡" if result.confidence >= 0.4 else "🔴"
            st.info(f"{confidence_color} **{result.country}** (Confidence: {result.confidence:.2f})")
            
            # Detailed results
            result_data = {
                "country": result.country,
                "confidence": f"{result.confidence:.3f}",
                "method": result.method.value,
                "matched_patterns": result.matched_patterns,
                "requires_user_input": result.requires_user_input,
                "suggestions": result.alternative_suggestions,
                "debug_info": result.debug_info
            }
            
            st.json(result_data)
    
    with col2:
        st.write("**📝 Test Example Filenames:**")
        
        for example in test_examples:
            if st.button(f"Test: {example[:30]}...", key=f"test_{example}"):
                result = detector.test_filename_detection(example)
                confidence_emoji = "✅" if result.confidence >= 0.7 else "⚠️" if result.confidence >= 0.4 else "❌"
                st.write(f"{confidence_emoji} **{result.country}** ({result.confidence:.2f})")


def _get_country_flag(country: str) -> str:
    """*** NEW *** Gibt Flag-Emoji für Land zurück"""
    flag_map = {
        "Germany": "🇩🇪", "Austria": "🇦🇹", "Switzerland": "🇨🇭",
        "United States": "🇺🇸", "Canada": "🇨🇦", "United Kingdom": "🇬🇧",
        "Ireland": "🇮🇪", "Australia": "🇦🇺", "New Zealand": "🇳🇿",
        "India": "🇮🇳", "Pakistan": "🇵🇰", "Bangladesh": "🇧🇩", "Sri Lanka": "🇱🇰",
        "Afghanistan": "🇦🇫", "Iran": "🇮🇷", "Iraq": "🇮🇶", "Saudi Arabia": "🇸🇦",
        "Turkey": "🇹🇷", "Israel": "🇮🇱", "Lebanon": "🇱🇧", "Syria": "🇸🇾",
        "Jordan": "🇯🇴", "UAE": "🇦🇪", "China": "🇨🇳", "Japan": "🇯🇵",
        "South Korea": "🇰🇷", "North Korea": "🇰🇵", "Thailand": "🇹🇭",
        "Vietnam": "🇻🇳", "Philippines": "🇵🇭", "Indonesia": "🇮🇩",
        "Malaysia": "🇲🇾", "Singapore": "🇸🇬", "Myanmar": "🇲🇲",
        "France": "🇫🇷", "Spain": "🇪🇸", "Italy": "🇮🇹", "Netherlands": "🇳🇱",
        "Poland": "🇵🇱", "Sweden": "🇸🇪", "Norway": "🇳🇴", "Denmark": "🇩🇰",
        "Finland": "🇫🇮", "Belgium": "🇧🇪", "Portugal": "🇵🇹", "Greece": "🇬🇷",
        "Russia": "🇷🇺", "Ukraine": "🇺🇦", "Belarus": "🇧🇾", "Brazil": "🇧🇷",
        "Mexico": "🇲🇽", "Argentina": "🇦🇷", "Colombia": "🇨🇴", "Chile": "🇨🇱",
        "South Africa": "🇿🇦", "Nigeria": "🇳🇬", "Egypt": "🇪🇬", "Kenya": "🇰🇪"
    }
    return flag_map.get(country, "🌍")


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_enhanced_country_detector() -> EnhancedCountryDetector:
    """Factory-Funktion für EnhancedCountryDetector v2.0"""
    return EnhancedCountryDetector()


def detect_country_from_analysis_file(
    filename: str,
    language: str = "en",
    detector: Optional[EnhancedCountryDetector] = None
) -> DetectionResult:
    """*** ENHANCED *** Convenience-Funktion für Country Detection"""
    if detector is None:
        detector = create_enhanced_country_detector()
    
    return detector.detect_country_from_filename(filename, language)


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Main Classes
    'EnhancedCountryDetector',
    'EnhancedCountryPatternsDatabase',
    
    # Data Models
    'CountryPattern',
    'DetectionResult',
    
    # Enums
    'DetectionMethod',
    
    # UI Functions
    'render_enhanced_country_detection_interface',
    'render_country_detection_debug',
    
    # Factory Functions
    'create_enhanced_country_detector',
    'detect_country_from_analysis_file',
    
    # Constants
    'CountryDetectionConstants'
]