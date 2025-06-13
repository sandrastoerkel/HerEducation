"""
🌍 GLOBAL DISCOURSE COUNTRY DETECTOR - Enterprise Country Recognition System
Erweiterte Länder-Erkennung für 07_Globale_Diskurs_Analyse.py

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
from collections import defaultdict

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


class DetectionMethod(Enum):
    """Erkennungsmethoden"""
    LANGUAGE_BASED = "language_based"
    KEYWORD_PATTERN = "keyword_pattern"
    CITY_PATTERN = "city_pattern"
    MEDIA_PATTERN = "media_pattern"
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
    
    @property
    def all_patterns(self) -> List[str]:
        """Alle Patterns kombiniert"""
        return self.keywords + self.cities + self.media_outlets + self.alternative_names


@dataclass
class DetectionResult:
    """Ergebnis der Länder-Erkennung"""
    country: str
    confidence: float
    method: DetectionMethod
    matched_patterns: List[str] = field(default_factory=list)
    alternative_suggestions: List[str] = field(default_factory=list)
    requires_user_input: bool = False
    
    @property
    def is_confident(self) -> bool:
        """Ist die Erkennung zuverlässig?"""
        return self.confidence >= CountryDetectionConstants.AUTO_ASSIGN_THRESHOLD


# =============================================================================
# COUNTRY PATTERNS DATABASE
# =============================================================================

class CountryPatternsDatabase:
    """Erweiterte Datenbank für Länder-Pattern"""
    
    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.logger = logging.getLogger(CountryDetectionConstants.LOGGER_NAME)
    
    def _initialize_patterns(self) -> Dict[str, CountryPattern]:
        """Initialisiert umfassende Länder-Pattern"""
        
        patterns = {
            # 🇩🇪 DACH-Region
            "Germany": CountryPattern(  # ← Dictionary Key englisch  
            country="Germany",      # ← Country Name englisch
            keywords=["germany", "german", "deutsch", "deutschland"],  # ← Detection keywords bleiben
            cities=["berlin", "munich", "hamburg", "cologne", "frankfurt", "dresden", "leipzig"],
            media_outlets=["ard", "zdf", "rtl", "sat1", "pro7", "ntv", "welt", "spiegel"],
            alternative_names=["de", "ger", "brd", "deutschland"]  # ← Deutschland als Alternative
            ),
            
            
            "Austria": CountryPattern(  # ✅ Key = englisch für Weltkarte
                country="Austria",      # ✅ Name = englisch für Weltkarte
                keywords=["austria", "austrian", "österreich"],  # ✅ österreich bleibt für YouTube Detection!
                cities=["vienna", "wien", "salzburg", "graz", "innsbruck"],  # ✅ wien bleibt für Detection!
                media_outlets=["orf", "servus", "puls4"],
                alternative_names=["at", "aut", "österreich"]  # ✅ österreich als Alternative
            ),
            
            "Schweiz": CountryPattern(
                country="Schweiz",
                keywords=["switzerland", "swiss", "schweiz"],
                cities=["zurich", "geneva", "basel", "bern", "lausanne"],
                media_outlets=["srf", "rts", "rsi"],
                alternative_names=["ch", "sui"]
            ),
            
            # 🇺🇸 Nordamerika
            "United States": CountryPattern(
                country="United States",
                keywords=["usa", "america", "american", "united_states", "us"],
                cities=[
                    "new_york", "los_angeles", "chicago", "houston", "phoenix", "philadelphia",
                    "san_antonio", "san_diego", "dallas", "san_jose", "austin", "jacksonville",
                    "washington", "boston", "seattle", "denver", "detroit", "nashville", "portland",
                    "las_vegas", "louisville", "baltimore", "milwaukee", "albuquerque", "tucson",
                    "fresno", "sacramento", "mesa", "kansas_city", "atlanta", "long_beach",
                    "colorado_springs", "raleigh", "miami", "virginia_beach", "omaha", "oakland",
                    "minneapolis", "tulsa", "arlington", "tampa", "new_orleans", "wichita",
                    "cleveland", "bakersfield", "honolulu", "anaheim", "henderson", "stockton",
                    "chula_vista", "buffalo", "madison", "reno", "toledo", "st_paul", "st_petersburg",
                    "chandler", "laredo", "norfolk", "durham", "jersey_city", "cheyenne", "fort_worth"
                ],
                media_outlets=[
                    "cnn", "fox", "nbc", "abc", "cbs", "msnbc", "npr", "pbs", "espn", "hln",
                    "bloomberg", "cnbc", "newsmax", "oann", "tyt", "vox", "buzzfeed", "politico"
                ],
                alternative_names=["america", "united_states_of_america", "usa"]
            ),
            
            "Canada": CountryPattern(
                country="Canada",
                keywords=["canada", "canadian"],
                cities=[
                    "toronto", "montreal", "vancouver", "calgary", "edmonton", "ottawa",
                    "winnipeg", "quebec_city", "hamilton", "kitchener", "london", "victoria",
                    "halifax", "oshawa", "windsor", "saskatoon", "st_catharines", "regina",
                    "st_johns", "barrie", "kelowna", "abbotsford", "greater_sudbury", "kingston",
                    "saguenay", "sherbrooke", "guelph", "kanata", "chicoutimi", "trois_rivieres"
                ],
                media_outlets=["cbc", "ctv", "global", "tva", "radio_canada"],
                alternative_names=["ca", "can"]
            ),
            
            # 🇬🇧 Vereinigtes Königreich & Irland
            "United Kingdom": CountryPattern(
                country="United Kingdom",
                keywords=["uk", "britain", "british", "england", "scotland", "wales", "northern_ireland"],
                cities=[
                    "london", "birmingham", "leeds", "glasgow", "sheffield", "bradford", "liverpool",
                    "edinburgh", "manchester", "bristol", "wakefield", "cardiff", "coventry",
                    "nottingham", "leicester", "sunderland", "belfast", "newcastle", "brighton",
                    "hull", "plymouth", "stoke", "wolverhampton", "derby", "swansea", "southampton",
                    "salford", "aberdeen", "westminster", "portsmouth", "york", "peterborough",
                    "dundee", "lancaster", "oxford", "newport", "preston", "st_albans", "norwich",
                    "chester", "cambridge", "salisbury", "exeter", "gloucester", "lisburn", "chichester"
                ],
                media_outlets=["bbc", "itv", "channel4", "sky", "times", "guardian", "telegraph", "independent"],
                alternative_names=["gb", "great_britain", "england", "scotland", "wales"]
            ),
            
            "Ireland": CountryPattern(
                country="Ireland",
                keywords=["ireland", "irish"],
                cities=["dublin", "cork", "limerick", "galway", "waterford", "drogheda", "dundalk"],
                media_outlets=["rte", "tv3", "newstalk"],
                alternative_names=["ie", "eire"]
            ),
            
            # 🇦🇺 Ozeanien
            "Australia": CountryPattern(
                country="Australia",
                keywords=["australia", "australian", "aussie", "oz"],
                cities=[
                    "sydney", "melbourne", "brisbane", "perth", "adelaide", "gold_coast",
                    "newcastle", "canberra", "sunshine_coast", "wollongong", "hobart", "geelong",
                    "townsville", "cairns", "darwin", "toowoomba", "ballarat", "bendigo",
                    "albury", "launceston", "mackay", "rockhampton", "bunbury", "bundaberg",
                    "coffs_harbour", "wagga_wagga", "hervey_bay", "mildura", "shepparton",
                    "port_macquarie", "gladstone", "tamworth", "traralgon", "orange", "dubbo"
                ],
                media_outlets=["abc_au", "sbs", "seven", "nine", "ten", "sky_au"],
                alternative_names=["au", "aus"]
            ),
            
            "New Zealand": CountryPattern(
                country="New Zealand",
                keywords=["new_zealand", "newzealand", "kiwi"],
                cities=["auckland", "wellington", "christchurch", "hamilton", "tauranga", "dunedin"],
                media_outlets=["tvnz", "three", "maori_tv"],
                alternative_names=["nz", "aotearoa"]
            ),
            
            # 🇮🇳 Südasien
            "India": CountryPattern(
                country="India",
                keywords=["india", "indian", "bharat"],
                cities=[
                    "mumbai", "delhi", "bangalore", "hyderabad", "ahmedabad", "chennai", "kolkata",
                    "surat", "pune", "jaipur", "lucknow", "kanpur", "nagpur", "indore", "thane",
                    "bhopal", "visakhapatnam", "pimpri_chinchwad", "patna", "vadodara", "ghaziabad",
                    "ludhiana", "agra", "nashik", "faridabad", "meerut", "rajkot", "kalyan_dombivli",
                    "vasai_virar", "varanasi", "srinagar", "aurangabad", "dhanbad", "amritsar",
                    "navi_mumbai", "allahabad", "howrah", "ranchi", "gwalior", "jabalpur", "coimbatore"
                ],
                media_outlets=["ndtv", "times_now", "india_today", "zee", "star", "sony", "aaj_tak"],
                alternative_names=["in", "ind", "hindustan"]
            ),
            
            "Pakistan": CountryPattern(
                country="Pakistan",
                keywords=["pakistan", "pakistani"],
                cities=["karachi", "lahore", "faisalabad", "rawalpindi", "gujranwala", "peshawar", "multan", "islamabad"],
                media_outlets=["ard", "geo", "express", "dawn", "samaa"],
                alternative_names=["pk", "pak"]
            ),
            
            "Bangladesh": CountryPattern(
                country="Bangladesh",
                keywords=["bangladesh", "bangladeshi"],
                cities=["dhaka", "chittagong", "sylhet", "khulna", "rajshahi", "comilla"],
                media_outlets=["btv", "channel_i", "ntv", "somoy"],
                alternative_names=["bd", "ban"]
            ),
            
            "Sri Lanka": CountryPattern(
                country="Sri Lanka",
                keywords=["sri_lanka", "srilanka", "ceylon"],
                cities=["colombo", "kandy", "galle", "jaffna", "negombo", "trincomalee"],
                media_outlets=["itv", "sirasa", "derana"],
                alternative_names=["lk", "sri"]
            ),
            
            # 🇨🇳 Ostasien
            "China": CountryPattern(
                country="China",
                keywords=["china", "chinese", "prc"],
                cities=[
                    "beijing", "shanghai", "guangzhou", "shenzhen", "tianjin", "wuhan", "chengdu",
                    "dongguan", "chongqing", "nanjing", "shenyang", "hangzhou", "xian", "harbin",
                    "suzhou", "qingdao", "dalian", "zhengzhou", "shantou", "jinan", "changchun",
                    "kunming", "changsha", "taiyuan", "xiamen", "hefei", "urumqi", "fuzhou",
                    "wuxi", "zhongshan", "wenzhou", "yantai", "zibo", "nanning", "guiyang",
                    "lanzhou", "shijiazhuang", "luoyang", "weifang", "maoming", "zhuhai",
                    "handan", "jining", "anshan", "kaifeng", "tangshan", "pingdingshan"
                ],
                media_outlets=["cctv", "cgtn", "xinhua", "phoenix", "ifeng"],
                alternative_names=["cn", "chn", "peoples_republic"]
            ),
            
            "Japan": CountryPattern(
                country="Japan",
                keywords=["japan", "japanese", "nippon"],
                cities=[
                    "tokyo", "yokohama", "osaka", "nagoya", "sapporo", "fukuoka", "kobe", "kawasaki",
                    "kyoto", "saitama", "hiroshima", "sendai", "kitakyushu", "chiba", "sakai",
                    "niigata", "hamamatsu", "okayama", "sagamihara", "shizuoka", "kumamoto",
                    "kagoshima", "matsuyama", "kanazawa", "utsunomiya", "matsudo", "kawaguchi",
                    "takatsuki", "toyama", "nara", "suita", "wakayama", "nishinomiya", "kurashiki",
                    "maebashi", "naha", "akita", "fukuyama", "koriyama", "ichikawa", "iwaki"
                ],
                media_outlets=["nhk", "tbs", "fuji", "asahi", "nippon", "tokyo_mx"],
                alternative_names=["jp", "jpn"]
            ),
            
            "South Korea": CountryPattern(
                country="South Korea",
                keywords=["korea", "korean", "south_korea"],
                cities=["seoul", "busan", "incheon", "daegu", "daejeon", "gwangju", "suwon", "ulsan"],
                media_outlets=["kbs", "mbc", "sbs", "jtbc", "ytn"],
                alternative_names=["kr", "kor", "republic_of_korea"]
            ),
            
            # 🇹🇭 Südostasien
            "Thailand": CountryPattern(
                country="Thailand",
                keywords=["thailand", "thai", "siam"],
                cities=["bangkok", "chiang_mai", "pattaya", "phuket", "hat_yai", "nakhon_ratchasima"],
                media_outlets=["thai_pbs", "channel3", "channel7", "workpoint"],
                alternative_names=["th", "tha"]
            ),
            
            "Vietnam": CountryPattern(
                country="Vietnam",
                keywords=["vietnam", "vietnamese"],
                cities=["ho_chi_minh_city", "hanoi", "da_nang", "can_tho", "bien_hoa", "hue"],
                media_outlets=["vtv", "vfc", "htv"],
                alternative_names=["vn", "vie"]
            ),
            
            "Philippines": CountryPattern(
                country="Philippines",
                keywords=["philippines", "filipino", "pilipinas"],
                cities=["manila", "quezon_city", "caloocan", "davao", "cebu", "zamboanga", "antipolo"],
                media_outlets=["abs_cbn", "gma", "tv5", "cnn_philippines"],
                alternative_names=["ph", "phl"]
            ),
            
            "Indonesia": CountryPattern(
                country="Indonesia",
                keywords=["indonesia", "indonesian"],
                cities=["jakarta", "surabaya", "bandung", "bekasi", "medan", "tangerang", "depok"],
                media_outlets=["tvri", "sctv", "rcti", "indosiar", "trans7"],
                alternative_names=["id", "idn"]
            ),
            
            "Malaysia": CountryPattern(
                country="Malaysia",
                keywords=["malaysia", "malaysian"],
                cities=["kuala_lumpur", "george_town", "ipoh", "shah_alam", "petaling_jaya", "johor_bahru"],
                media_outlets=["rtm", "tv3", "ntv7", "8tv", "astro"],
                alternative_names=["my", "mys"]
            ),
            
            "Singapore": CountryPattern(
                country="Singapore",
                keywords=["singapore", "singaporean"],
                cities=["singapore"],
                media_outlets=["mediacorp", "cna", "channel8"],
                alternative_names=["sg", "sgp"]
            ),
            
            # 🇪🇺 Europa
            "France": CountryPattern(
                country="France",
                keywords=["france", "french", "français"],
                cities=["paris", "marseille", "lyon", "toulouse", "nice", "nantes", "strasbourg", "montpellier"],
                media_outlets=["tf1", "france2", "m6", "canal+", "france24", "bfm"],
                alternative_names=["fr", "fra"]
            ),
            
            "Spain": CountryPattern(
                country="Spain",
                keywords=["spain", "spanish", "españa"],
                cities=["madrid", "barcelona", "valencia", "seville", "zaragoza", "malaga", "murcia"],
                media_outlets=["tve", "antena3", "telecinco", "la_sexta"],
                alternative_names=["es", "esp"]
            ),
            
            "Italy": CountryPattern(
                country="Italy",
                keywords=["italy", "italian", "italia"],
                cities=["rome", "milan", "naples", "turin", "palermo", "genoa", "bologna", "florence"],
                media_outlets=["rai", "mediaset", "la7", "sky_italia"],
                alternative_names=["it", "ita"]
            ),
            
            "Netherlands": CountryPattern(
                country="Netherlands",
                keywords=["netherlands", "dutch", "holland"],
                cities=["amsterdam", "rotterdam", "the_hague", "utrecht", "eindhoven", "tilburg"],
                media_outlets=["nos", "rtl", "sbs", "npo"],
                alternative_names=["nl", "nld"]
            ),
            
            "Poland": CountryPattern(
                country="Poland",
                keywords=["poland", "polish", "polska"],
                cities=["warsaw", "krakow", "lodz", "wroclaw", "poznan", "gdansk", "szczecin"],
                media_outlets=["tvp", "polsat", "tvn"],
                alternative_names=["pl", "pol"]
            ),
            
            # 🇧🇷 Lateinamerika
            "Brazil": CountryPattern(
                country="Brazil",
                keywords=["brazil", "brazilian", "brasil"],
                cities=["sao_paulo", "rio_de_janeiro", "brasilia", "salvador", "fortaleza", "belo_horizonte"],
                media_outlets=["globo", "sbt", "record", "band"],
                alternative_names=["br", "bra"]
            ),
            
            "Mexico": CountryPattern(
                country="Mexico",
                keywords=["mexico", "mexican", "méxico"],
                cities=["mexico_city", "guadalajara", "monterrey", "puebla", "tijuana", "leon"],
                media_outlets=["televisa", "tv_azteca", "imagen"],
                alternative_names=["mx", "mex"]
            ),
            
            "Argentina": CountryPattern(
                country="Argentina",
                keywords=["argentina", "argentinian"],
                cities=["buenos_aires", "cordoba", "rosario", "mendoza", "la_plata", "tucuman"],
                media_outlets=["telefe", "canal13", "america"],
                alternative_names=["ar", "arg"]
            ),
            
            # 🇿🇦 Afrika
            "South Africa": CountryPattern(
                country="South Africa",
                keywords=["south_africa", "southafrican"],
                cities=["johannesburg", "cape_town", "durban", "pretoria", "port_elizabeth", "bloemfontein"],
                media_outlets=["sabc", "etv", "supersport"],
                alternative_names=["za", "rsa"]
            ),
            
            "Nigeria": CountryPattern(
                country="Nigeria",
                keywords=["nigeria", "nigerian"],
                cities=["lagos", "abuja", "kano", "ibadan", "kaduna", "port_harcourt"],
                media_outlets=["nta", "channels", "silverbird"],
                alternative_names=["ng", "nga"]
            ),
            
            "Egypt": CountryPattern(
                country="Egypt",
                keywords=["egypt", "egyptian"],
                cities=["cairo", "alexandria", "giza", "luxor", "aswan", "hurghada"],
                media_outlets=["ertu", "cbc", "dream"],
                alternative_names=["eg", "egy"]
            ),
            
            # 🇮🇱 Naher Osten
            "Israel": CountryPattern(
                country="Israel",
                keywords=["israel", "israeli"],
                cities=["jerusalem", "tel_aviv", "haifa", "rishon_lezion", "petah_tikva", "ashdod"],
                media_outlets=["kan", "reshet", "keshet"],
                alternative_names=["il", "isr"]
            ),
            
            "Turkey": CountryPattern(
                country="Turkey",
                keywords=["turkey", "turkish", "türkiye"],
                cities=["istanbul", "ankara", "izmir", "bursa", "adana", "gaziantep", "konya"],
                media_outlets=["trt", "atv", "show", "kanal_d"],
                alternative_names=["tr", "tur"]
            ),
            
            # 🇷🇺 Osteuropa
            "Russia": CountryPattern(
                country="Russia",
                keywords=["russia", "russian", "россия"],
                cities=["moscow", "st_petersburg", "novosibirsk", "yekaterinburg", "nizhny_novgorod"],
                media_outlets=["channel_one", "rossiya", "ntv", "ren_tv"],
                alternative_names=["ru", "rus"]
            ),
            
            "Ukraine": CountryPattern(
                country="Ukraine",
                keywords=["ukraine", "ukrainian", "україна"],
                cities=["kyiv", "kharkiv", "odesa", "dnipro", "lviv", "zaporizhzhia"],
                media_outlets=["1+1", "inter", "ictv", "stb"],
                alternative_names=["ua", "ukr"]
            ),
            
            # 🇸🇪 Nordeuropa
            "Sweden": CountryPattern(
                country="Sweden",
                keywords=["sweden", "swedish", "sverige"],
                cities=["stockholm", "gothenburg", "malmo", "uppsala", "vasteras", "orebro"],
                media_outlets=["svt", "tv4", "tv3"],
                alternative_names=["se", "swe"]
            ),
            
            "Norway": CountryPattern(
                country="Norway",
                keywords=["norway", "norwegian", "norge"],
                cities=["oslo", "bergen", "stavanger", "trondheim", "drammen", "fredrikstad"],
                media_outlets=["nrk", "tv2", "tvnorge"],
                alternative_names=["no", "nor"]
            ),
            
            "Denmark": CountryPattern(
                country="Denmark",
                keywords=["denmark", "danish", "danmark"],
                cities=["copenhagen", "aarhus", "odense", "aalborg", "esbjerg", "randers"],
                media_outlets=["dr", "tv2_dk", "kanal5"],
                alternative_names=["dk", "dnk"]
            ),
            
            "Finland": CountryPattern(
                country="Finland",
                keywords=["finland", "finnish", "suomi"],
                cities=["helsinki", "espoo", "tampere", "vantaa", "oulu", "turku"],
                media_outlets=["yle", "mtv3", "nelonen"],
                alternative_names=["fi", "fin"]
            )
        }
        
        return patterns
    
    def get_pattern(self, country: str) -> Optional[CountryPattern]:
        """Gibt Pattern für ein Land zurück"""
        return self.patterns.get(country)
    
    def find_matching_countries(self, text: str) -> List[Tuple[str, float, List[str]]]:
        """Findet passende Länder für einen Text
        
        Args:
            text: Zu analysierender Text
            
        Returns:
            Liste von (country, confidence, matched_patterns)
        """
        text_lower = text.lower()
        matches = []
        
        for country, pattern in self.patterns.items():
            matched_patterns = []
            total_score = 0
            
            # Prüfe alle Pattern-Typen
            for keyword in pattern.keywords:
                if keyword in text_lower:
                    matched_patterns.append(f"keyword:{keyword}")
                    total_score += 3  # Keywords haben höchste Priorität
            
            for city in pattern.cities:
                if city in text_lower:
                    matched_patterns.append(f"city:{city}")
                    total_score += 2  # Städte haben mittlere Priorität
            
            for media in pattern.media_outlets:
                if media in text_lower:
                    matched_patterns.append(f"media:{media}")
                    total_score += 2  # Medien haben mittlere Priorität
            
            for alt_name in pattern.alternative_names:
                if alt_name in text_lower:
                    matched_patterns.append(f"alt:{alt_name}")
                    total_score += 1  # Alternative Namen haben niedrige Priorität
            
            if matched_patterns:
                # Berechne Confidence basierend auf Score und Pattern-Anzahl
                confidence = min(0.99, total_score / 10.0 + len(matched_patterns) * 0.1)
                matches.append((country, confidence, matched_patterns))
        
        # Sortiere nach Confidence
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches


# =============================================================================
# ENHANCED COUNTRY DETECTOR
# =============================================================================

class EnhancedCountryDetector:
    """Enterprise-Level Country Detection mit User-Fallback"""
    
    def __init__(self):
        self.database = CountryPatternsDatabase()
        self.logger = logging.getLogger(CountryDetectionConstants.LOGGER_NAME)
        
        # Initialisiere Session State
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
        """Hauptfunktion für Länder-Erkennung
        
        Args:
            filename: Dateiname zur Analyse
            language: Sprache der Analyse (de/en)
            source_path: Optionaler vollständiger Pfad
            
        Returns:
            DetectionResult mit Erkennungsergebnis
        """
        # Cache prüfen
        cache_key = f"{filename}_{language}"
        if cache_key in st.session_state[CountryDetectionConstants.SESSION_COUNTRY_MAPPING]:
            cached_result = st.session_state[CountryDetectionConstants.SESSION_COUNTRY_MAPPING][cache_key]
            self.logger.info(f"Cached country for {filename}: {cached_result}")
            return DetectionResult(
                country=cached_result,
                confidence=1.0,
                method=DetectionMethod.USER_OVERRIDE
            )
        
        # Deutsche Analysen sind immer Deutschland
        if language == "de":
            result = DetectionResult(
                country="Germany",
                confidence=1.0,
                method=DetectionMethod.LANGUAGE_BASED,
                matched_patterns=["language:german"]
            )
            self._cache_result(cache_key, result.country)
            return result
        
        # Englische Analysen: Pattern-Matching
        return self._detect_from_english_filename(filename, cache_key)
    
    def _detect_from_english_filename(self, filename: str, cache_key: str) -> DetectionResult:
        """Erkennt Land aus englischem Dateinamen"""
        # Bereinige Dateiname für Analyse
        clean_filename = self._clean_filename_for_analysis(filename)
        
        # Pattern-Matching
        matches = self.database.find_matching_countries(clean_filename)
        
        if not matches:
            # Keine Matches gefunden - User-Input erforderlich
            return DetectionResult(
                country="Unknown",
                confidence=0.0,
                method=DetectionMethod.FALLBACK,
                requires_user_input=True,
                alternative_suggestions=self._get_common_countries()
            )
        
        # Bestes Match prüfen
        best_country, best_confidence, best_patterns = matches[0]
        
        if best_confidence >= CountryDetectionConstants.AUTO_ASSIGN_THRESHOLD:
            # Hohe Confidence - automatisch zuweisen
            result = DetectionResult(
                country=best_country,
                confidence=best_confidence,
                method=DetectionMethod.KEYWORD_PATTERN,
                matched_patterns=best_patterns
            )
            self._cache_result(cache_key, result.country)
            self.logger.info(f"Auto-detected {best_country} for {filename} (confidence: {best_confidence:.2f})")
            return result
        
        else:
            # Niedrige Confidence - User-Input erforderlich
            suggestions = [country for country, _, _ in matches[:5]]
            return DetectionResult(
                country=best_country,
                confidence=best_confidence,
                method=DetectionMethod.KEYWORD_PATTERN,
                matched_patterns=best_patterns,
                requires_user_input=True,
                alternative_suggestions=suggestions
            )
    
    def _clean_filename_for_analysis(self, filename: str) -> str:
        """Bereinigt Dateiname für bessere Analyse"""
        # Entferne Dateiendungen und Timestamps
        clean = filename.lower()
        clean = re.sub(r'\.csv$', '', clean)
        clean = re.sub(r'_country_analysis_\d+_\d+$', '', clean)
        clean = re.sub(r'_\d{4}-\d{2}-\d{2}_', '_', clean)
        clean = re.sub(r'_[a-zA-Z0-9]{11}_', '_', clean)  # YouTube IDs
        
        # Ersetze Unterstriche und Bindestriche durch Leerzeichen
        clean = re.sub(r'[_-]+', ' ', clean)
        
        return clean
    
    def _get_common_countries(self) -> List[str]:
        """Gibt häufige Länder für Vorschläge zurück"""
        return [
            "United States", "United Kingdom", "Canada", "Australia", "Germany",
            "France", "Spain", "Italy", "Netherlands", "Sweden", "Norway", "Denmark",
            "India", "Japan", "South Korea", "China", "Malaysia", "Singapore",
            "Thailand", "Philippines", "Indonesia", "Vietnam", "Brazil", "Mexico"
        ]
    
    def _cache_result(self, cache_key: str, country: str) -> None:
        """Speichert Ergebnis im Cache"""
        st.session_state[CountryDetectionConstants.SESSION_COUNTRY_MAPPING][cache_key] = country
    
    def handle_user_input_for_unknown_country(
        self,
        filename: str,
        detection_result: DetectionResult
    ) -> Optional[str]:
        """Behandelt User-Input für unbekannte Länder
        
        Args:
            filename: Dateiname
            detection_result: Erkennungsergebnis
            
        Returns:
            Gewähltes Land oder None
        """
        st.warning(f"🤔 Land nicht automatisch erkennbar: `{filename}`")
        
        if detection_result.matched_patterns:
            st.info(f"**Gefundene Hinweise:** {', '.join(detection_result.matched_patterns)}")
        
        # User-Auswahl Interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if detection_result.alternative_suggestions:
                selected_country = st.selectbox(
                    "Bitte wählen Sie das passende Land:",
                    options=[""] + detection_result.alternative_suggestions,
                    key=f"country_select_{filename}"
                )
            else:
                all_countries = list(self.database.patterns.keys())
                selected_country = st.selectbox(
                    "Bitte wählen Sie das passende Land:",
                    options=[""] + sorted(all_countries),
                    key=f"country_select_{filename}"
                )
        
        with col2:
            if st.button("✅ Bestätigen", key=f"confirm_{filename}"):
                if selected_country:
                    # Cache für zukünftige Verwendung
                    cache_key = f"{filename}_en"
                    self._cache_result(cache_key, selected_country)
                    st.success(f"✅ {selected_country} gespeichert für `{filename}`")
                    st.rerun()
                else:
                    st.error("Bitte wählen Sie ein Land aus")
        
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


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_country_detection_interface(
    analysis_files: List,
    detector: EnhancedCountryDetector
) -> Dict[str, str]:
    """Rendert Interface für Country Detection mit User-Input
    
    Args:
        analysis_files: Liste der Analysis-Dateien
        detector: EnhancedCountryDetector Instanz
        
    Returns:
        Dictionary mapping filename -> country
    """
    st.subheader("🌍 Länder-Erkennung")
    
    file_country_mapping = {}
    files_needing_input = []
    
    # Erste Runde: Automatische Erkennung
    for file in analysis_files:
        detection_result = detector.detect_country_from_filename(
            file.filename,
            file.language,
            str(file.file_path)
        )
        
        if detection_result.requires_user_input:
            files_needing_input.append((file, detection_result))
        else:
            file_country_mapping[file.filename] = detection_result.country
    
    # Zeige automatisch erkannte Länder
    if file_country_mapping:
        st.success(f"✅ {len(file_country_mapping)} Länder automatisch erkannt")
        
        with st.expander("🤖 Automatisch erkannte Länder", expanded=False):
            for filename, country in file_country_mapping.items():
                st.write(f"📁 `{filename[:50]}...` → 🌍 **{country}**")
    
    # Behandle Dateien, die User-Input benötigen
    if files_needing_input:
        st.warning(f"⚠️ {len(files_needing_input)} Dateien benötigen manuelle Zuordnung")
        
        for file, detection_result in files_needing_input:
            with st.expander(f"🤔 Unbekanntes Land: {file.filename[:50]}...", expanded=True):
                user_country = detector.handle_user_input_for_unknown_country(
                    file.filename,
                    detection_result
                )
                
                if user_country:
                    file_country_mapping[file.filename] = user_country
    
    # Cache-Management
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Cache neu laden"):
            st.rerun()
    
    with col2:
        if st.button("🗑️ Cache löschen"):
            detector.clear_cache()
            st.success("Cache gelöscht")
            st.rerun()
    
    # Statistiken
    if file_country_mapping:
        stats = Counter(file_country_mapping.values())
        st.subheader("📊 Länder-Verteilung")
        
        stats_data = []
        for country, count in stats.most_common():
            stats_data.append({"Land": country, "Analysen": count})
        
        import pandas as pd
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)
    
    return file_country_mapping


def render_country_detection_debug(detector: EnhancedCountryDetector) -> None:
    """Rendert Debug-Interface für Country Detection"""
    with st.expander("🔧 Country Detection Debug", expanded=False):
        st.subheader("Test Country Detection")
        
        test_filename = st.text_input(
            "Test Dateiname:",
            value="Why_Malaysia_Education_System_Is_A_Failure"
        )
        
        if test_filename:
            result = detector.detect_country_from_filename(test_filename, "en")
            
            st.write("**Erkennungsergebnis:**")
            st.json({
                "country": result.country,
                "confidence": result.confidence,
                "method": result.method.value,
                "matched_patterns": result.matched_patterns,
                "requires_user_input": result.requires_user_input,
                "suggestions": result.alternative_suggestions
            })


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

def create_enhanced_country_detector() -> EnhancedCountryDetector:
    """Factory-Funktion für EnhancedCountryDetector"""
    return EnhancedCountryDetector()


def detect_country_from_analysis_file(
    filename: str,
    language: str = "en",
    detector: Optional[EnhancedCountryDetector] = None
) -> DetectionResult:
    """Convenience-Funktion für Country Detection
    
    Args:
        filename: Dateiname
        language: Sprache (de/en)
        detector: Optionaler Detector (wird erstellt falls None)
        
    Returns:
        DetectionResult
    """
    if detector is None:
        detector = create_enhanced_country_detector()
    
    return detector.detect_country_from_filename(filename, language)


# =============================================================================
# EXPORT
# =============================================================================

__all__ = [
    # Main Classes
    'EnhancedCountryDetector',
    'CountryPatternsDatabase',
    
    # Data Models
    'CountryPattern',
    'DetectionResult',
    
    # Enums
    'DetectionMethod',
    
    # UI Functions
    'render_country_detection_interface',
    'render_country_detection_debug',
    
    # Factory Functions
    'create_enhanced_country_detector',
    'detect_country_from_analysis_file',
    
    # Constants
    'CountryDetectionConstants'
]