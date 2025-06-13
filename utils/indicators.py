"""
Modernisierte Bildungsindikatoren
Strukturierte Datenverwaltung für internationale Bildungsstandards

Autor: Sandra Störkel - HerEducation
Version: 2.0 - Modernisiert mit bewährten Patterns
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional, Union
import logging

# ===== KONSTANTEN =====
class IndicatorConstants:
    """Zentrale Konstanten für Bildungsindikatoren"""
    
    # Altersgrenzen
    MINIMUM_MARRIAGE_AGE = 18
    MINIMUM_EMPLOYMENT_AGE = 15
    COMPULSORY_EDUCATION_YEARS = 9
    FREE_EDUCATION_YEARS = 12
    
    # Sprachen
    DEFAULT_LANGUAGE = "de"
    SUPPORTED_LANGUAGES = ["de", "en"]
    
    # Kategorien-Emojis
    CATEGORY_EMOJIS = {
        "access_education": "1️⃣",
        "legal_protection": "2️⃣", 
        "international_obligations": "3️⃣",
        "age_limits_coherence": "4️⃣"
    }

# ===== ENUMS =====
class IndicatorCategory(Enum):
    """Kategorien der Bildungsindikatoren"""
    ACCESS_EDUCATION = "access_education"
    LEGAL_PROTECTION = "legal_protection"
    INTERNATIONAL_OBLIGATIONS = "international_obligations"
    AGE_LIMITS_COHERENCE = "age_limits_coherence"
    
    @property
    def emoji(self) -> str:
        """Gibt das Emoji für die Kategorie zurück"""
        return IndicatorConstants.CATEGORY_EMOJIS.get(self.value, "📊")
    
    def get_title(self, language: str = "de") -> str:
        """Gibt den lokalisierten Titel der Kategorie zurück"""
        titles = {
            "de": {
                self.ACCESS_EDUCATION: "Zugang und Pflicht zur Bildung",
                self.LEGAL_PROTECTION: "Rechtlicher Schutz & Gleichbehandlung",
                self.INTERNATIONAL_OBLIGATIONS: "Internationale Verpflichtungen",
                self.AGE_LIMITS_COHERENCE: "Altersgrenzen & Kohärenz im Rechtssystem"
            },
            "en": {
                self.ACCESS_EDUCATION: "Access and Compulsory Education",
                self.LEGAL_PROTECTION: "Legal Protection & Equal Treatment",
                self.INTERNATIONAL_OBLIGATIONS: "International Obligations",
                self.AGE_LIMITS_COHERENCE: "Age Limits & Legal System Coherence"
            }
        }
        return titles.get(language, titles["de"]).get(self, "Unknown Category")
    
    def get_display_title(self, language: str = "de") -> str:
        """Gibt den formatierten Titel mit Emoji zurück"""
        return f"{self.emoji} {self.get_title(language)}"

class Language(Enum):
    """Unterstützte Sprachen"""
    GERMAN = "de"
    ENGLISH = "en"

# ===== DATACLASSES =====
@dataclass
class IndicatorText:
    """Mehrsprachige Texte für einen Indikator"""
    english: str
    german: str
    description_german: str
    description_english: Optional[str] = None
    
    def get_text(self, language: str = "de") -> str:
        """Gibt den Text in der gewünschten Sprache zurück"""
        if language == "en":
            return self.english
        return self.german
    
    def get_description(self, language: str = "de") -> str:
        """Gibt die Beschreibung in der gewünschten Sprache zurück"""
        if language == "en" and self.description_english:
            return self.description_english
        return self.description_german

@dataclass
class EducationIndicator:
    """Strukturierte Repräsentation eines Bildungsindikators"""
    id: str
    category: IndicatorCategory
    text: IndicatorText
    priority: int = 1
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def category_title(self) -> str:
        """Formatierter Kategorie-Titel mit Emoji"""
        return self.category.get_display_title()
    
    def get_question(self, language: str = "de") -> str:
        """Gibt die Indikator-Frage in der gewünschten Sprache zurück"""
        return self.text.get_text(language)
    
    def get_description(self, language: str = "de") -> str:
        """Gibt die Indikator-Beschreibung in der gewünschten Sprache zurück"""
        return self.text.get_description(language)
    
    def to_tuple(self, language: str = "de") -> Tuple[str, str, str]:
        """Backward-compatibility: Konvertiert zu altem Tupel-Format"""
        if language == "de":
            return (self.text.english, self.text.german, self.text.description_german)
        else:
            return (self.text.english, self.text.english, self.text.get_description("en"))

@dataclass
class IndicatorSection:
    """Abschnitt mit mehreren Indikatoren"""
    category: IndicatorCategory
    indicators: List[EducationIndicator]
    
    @property
    def title(self) -> str:
        """Titel des Abschnitts mit Emoji"""
        return self.category.get_display_title()
    
    def get_title(self, language: str = "de") -> str:
        """Lokalisierter Titel des Abschnitts"""
        return self.category.get_display_title(language)
    
    def get_indicator_count(self) -> int:
        """Anzahl der Indikatoren in diesem Abschnitt"""
        return len(self.indicators)
    
    def get_indicators_as_tuples(self, language: str = "de") -> List[Tuple[str, str, str]]:
        """Backward-compatibility: Gibt Indikatoren als Tupel zurück"""
        return [indicator.to_tuple(language) for indicator in self.indicators]

# ===== INDIKATOR-DEFINITIONEN =====
class IndicatorDefinitions:
    """Zentrale Definition aller Bildungsindikatoren"""
    
    @staticmethod
    def _create_access_education_indicators() -> List[EducationIndicator]:
        """Erstellt Indikatoren für Zugang und Bildungspflicht"""
        return [
            EducationIndicator(
                id="free_12_years",
                category=IndicatorCategory.ACCESS_EDUCATION,
                text=IndicatorText(
                    english="Are 12 years of primary and secondary education legally free?",
                    german="Sind 12 Jahre Grund- und Sekundarbildung gesetzlich kostenfrei?",
                    description_german="Dieser Indikator untersucht, ob ein Land gesetzlich festgelegt hat, dass 12 Jahre schulische Bildung kostenfrei sein müssen. Dies ist ein wichtiger Maßstab für die Bildungszugänglichkeit.",
                    description_english="This indicator examines whether a country has legally established that 12 years of school education must be free of charge. This is an important benchmark for educational accessibility."
                ),
                priority=1,
                tags=["free_education", "accessibility", "primary", "secondary"]
            ),
            
            EducationIndicator(
                id="compulsory_9_years",
                category=IndicatorCategory.ACCESS_EDUCATION,
                text=IndicatorText(
                    english="Are 9 years of primary and secondary education legally compulsory?",
                    german="Sind 9 Jahre Grund- und Sekundarbildung gesetzlich verpflichtend?",
                    description_german="Dieser Indikator erfasst, ob ein Land eine 9-jährige Schulpflicht gesetzlich festgeschrieben hat, was ein globales Mindestniveau darstellt.",
                    description_english="This indicator captures whether a country has legally established a 9-year compulsory education, which represents a global minimum level."
                ),
                priority=1,
                tags=["compulsory_education", "minimum_standard", "primary", "secondary"]
            ),
            
            EducationIndicator(
                id="pre_primary_free_compulsory",
                category=IndicatorCategory.ACCESS_EDUCATION,
                text=IndicatorText(
                    english="Is pre-primary education legally free and compulsory?",
                    german="Ist Vorschulbildung gesetzlich kostenfrei und verpflichtend?",
                    description_german="Dieser Indikator prüft, ob frühkindliche Bildung sowohl kostenfrei als auch verpflichtend ist, was einen wichtigen Grundstein für Bildungsgerechtigkeit legt.",
                    description_english="This indicator examines whether early childhood education is both free and compulsory, which lays an important foundation for educational equity."
                ),
                priority=2,
                tags=["pre_primary", "early_childhood", "free_education", "compulsory_education"]
            ),
            
            EducationIndicator(
                id="equal_access_post_secondary",
                category=IndicatorCategory.ACCESS_EDUCATION,
                text=IndicatorText(
                    english="Is equal access to post-secondary education legally guaranteed?",
                    german="Ist der gleichberechtigte Zugang zur Hochschulbildung gesetzlich garantiert?",
                    description_german="Dieser Indikator untersucht, ob ein rechtlicher Rahmen für diskriminierungsfreien Zugang zu höherer Bildung existiert.",
                    description_english="This indicator examines whether a legal framework for discrimination-free access to higher education exists."
                ),
                priority=2,
                tags=["post_secondary", "higher_education", "equal_access", "anti_discrimination"]
            )
        ]
    
    @staticmethod
    def _create_legal_protection_indicators() -> List[EducationIndicator]:
        """Erstellt Indikatoren für rechtlichen Schutz"""
        return [
            EducationIndicator(
                id="constitution_right_education",
                category=IndicatorCategory.LEGAL_PROTECTION,
                text=IndicatorText(
                    english="Does the Constitution enshrine the right to education without discrimination?",
                    german="Garantiert die Verfassung das Recht auf diskriminierungsfreie Bildung?",
                    description_german="Dieser Indikator erfasst, ob auf höchster rechtlicher Ebene (Verfassung) das Recht auf diskriminierungsfreie Bildung verankert ist.",
                    description_english="This indicator captures whether the right to discrimination-free education is enshrined at the highest legal level (constitution)."
                ),
                priority=1,
                tags=["constitution", "fundamental_rights", "anti_discrimination"]
            ),
            
            EducationIndicator(
                id="legislation_right_education", 
                category=IndicatorCategory.LEGAL_PROTECTION,
                text=IndicatorText(
                    english="Does the legislation enshrine the right to education without discrimination?",
                    german="Garantiert die Gesetzgebung das Recht auf diskriminierungsfreie Bildung?",
                    description_german="Dieser Indikator prüft, ob in der regulären Gesetzgebung explizite Schutzrechte gegen Bildungsdiskriminierung bestehen.",
                    description_english="This indicator examines whether explicit protection rights against educational discrimination exist in regular legislation."
                ),
                priority=1,
                tags=["legislation", "legal_protection", "anti_discrimination"]
            ),
            
            EducationIndicator(
                id="pregnant_parenting_girls_protection",
                category=IndicatorCategory.LEGAL_PROTECTION,
                text=IndicatorText(
                    english="Is pregnant and parenting girls' right to education protected in the legal framework?",
                    german="Ist das Recht auf Bildung für schwangere und erziehende Mädchen gesetzlich geschützt?",
                    description_german="Dieser Indikator untersucht spezifische Schutzmaßnahmen für eine besonders vulnerable Gruppe, deren Bildungsweg häufig unterbrochen wird.",
                    description_english="This indicator examines specific protective measures for a particularly vulnerable group whose educational path is frequently interrupted."
                ),
                priority=2,
                tags=["vulnerable_groups", "girls_education", "pregnancy", "parenting", "continuity"]
            ),
            
            EducationIndicator(
                id="protection_violence_corporal_punishment",
                category=IndicatorCategory.LEGAL_PROTECTION,
                text=IndicatorText(
                    english="Are learners legally protected against all violence and corporal punishment in educational institutions?",
                    german="Sind Lernende gesetzlich vor Gewalt und Körperstrafen in Bildungseinrichtungen geschützt?",
                    description_german="Dieser Indikator betrachtet den gesetzlichen Schutz vor jeglicher Form von Gewalt im Bildungskontext.",
                    description_english="This indicator examines legal protection against all forms of violence in educational contexts."
                ),
                priority=1,
                tags=["violence_prevention", "corporal_punishment", "safe_schools", "child_protection"]
            )
        ]
    
    @staticmethod
    def _create_international_obligations_indicators() -> List[EducationIndicator]:
        """Erstellt Indikatoren für internationale Verpflichtungen"""
        return [
            EducationIndicator(
                id="unesco_convention_discrimination",
                category=IndicatorCategory.INTERNATIONAL_OBLIGATIONS,
                text=IndicatorText(
                    english="Is the country party to UNESCO Convention against Discrimination in Education?",
                    german="Ist das Land Vertragsstaat des UNESCO-Übereinkommens gegen Diskriminierung im Bildungswesen?",
                    description_german="Dieser Indikator zeigt, ob ein Land das wichtigste internationale Abkommen speziell zum Schutz vor Bildungsdiskriminierung ratifiziert hat.",
                    description_english="This indicator shows whether a country has ratified the most important international agreement specifically for protection against educational discrimination."
                ),
                priority=1,
                tags=["unesco", "international_law", "anti_discrimination", "ratification"]
            ),
            
            EducationIndicator(
                id="cedaw_convention",
                category=IndicatorCategory.INTERNATIONAL_OBLIGATIONS,
                text=IndicatorText(
                    english="Is the country party to the UN Convention on the Elimination of Discrimination against Women?",
                    german="Ist das Land Vertragsstaat des UN-Übereinkommens zur Beseitigung der Diskriminierung der Frau?",
                    description_german="Dieser Indikator erfasst die Ratifizierung eines zentralen Abkommens mit wichtigen Bildungsaspekten für Mädchen und Frauen.",
                    description_english="This indicator captures the ratification of a central agreement with important educational aspects for girls and women."
                ),
                priority=1,
                tags=["cedaw", "womens_rights", "girls_education", "international_law", "ratification"]
            )
        ]
    
    @staticmethod
    def _create_age_limits_coherence_indicators() -> List[EducationIndicator]:
        """Erstellt Indikatoren für Altersgrenzen und Kohärenz"""
        return [
            EducationIndicator(
                id="marriage_age_18",
                category=IndicatorCategory.AGE_LIMITS_COHERENCE,
                text=IndicatorText(
                    english="Is the legal age of marriage set at least at 18 years old?",
                    german="Ist das gesetzliche Heiratsalter auf mindestens 18 Jahre festgelegt?",
                    description_german="Dieser Indikator prüft, ob das gesetzliche Heiratsalter hoch genug ist, um die Schulbildung nicht zu unterbrechen, was besonders Mädchen betrifft.",
                    description_english="This indicator examines whether the legal marriage age is high enough not to interrupt school education, which particularly affects girls."
                ),
                priority=1,
                tags=["marriage_age", "child_marriage", "girls_education", "age_coherence"]
            ),
            
            EducationIndicator(
                id="employment_age_education_alignment",
                category=IndicatorCategory.AGE_LIMITS_COHERENCE,
                text=IndicatorText(
                    english="Is the minimum age of employment at least 15 and aligned with the end of compulsory education?",
                    german="Liegt das gesetzliche Mindestarbeitsalter bei mindestens 15 Jahren und stimmt mit dem Ende der Schulpflicht überein?",
                    description_german="Dieser Indikator betrachtet die Abstimmung zwischen Arbeitsrecht und Bildungspflicht, um sicherzustellen, dass Kinder ihre Schulbildung abschließen können.",
                    description_english="This indicator examines the alignment between labor law and compulsory education to ensure that children can complete their school education."
                ),
                priority=1,
                tags=["employment_age", "child_labor", "education_completion", "age_coherence"]
            )
        ]
    
    @classmethod
    def get_all_indicators(cls) -> List[EducationIndicator]:
        """Gibt alle definierten Bildungsindikatoren zurück"""
        indicators = []
        indicators.extend(cls._create_access_education_indicators())
        indicators.extend(cls._create_legal_protection_indicators())
        indicators.extend(cls._create_international_obligations_indicators())
        indicators.extend(cls._create_age_limits_coherence_indicators())
        return indicators

# ===== HAUPTKLASSE =====
class EducationIndicatorManager:
    """Zentrale Verwaltung der Bildungsindikatoren"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._indicators = IndicatorDefinitions.get_all_indicators()
        self._sections = self._build_sections()
    
    def _build_sections(self) -> Dict[IndicatorCategory, IndicatorSection]:
        """Erstellt Abschnitte gruppiert nach Kategorien"""
        sections = {}
        
        for category in IndicatorCategory:
            category_indicators = [
                indicator for indicator in self._indicators 
                if indicator.category == category
            ]
            # Sortiere nach Priorität
            category_indicators.sort(key=lambda x: x.priority)
            
            sections[category] = IndicatorSection(
                category=category,
                indicators=category_indicators
            )
        
        return sections
    
    def get_all_indicators(self) -> List[EducationIndicator]:
        """Gibt alle Indikatoren zurück"""
        return self._indicators.copy()
    
    def get_indicator_by_id(self, indicator_id: str) -> Optional[EducationIndicator]:
        """Sucht einen Indikator nach ID"""
        for indicator in self._indicators:
            if indicator.id == indicator_id:
                return indicator
        return None
    
    def get_indicators_by_category(self, category: IndicatorCategory) -> List[EducationIndicator]:
        """Gibt alle Indikatoren einer Kategorie zurück"""
        return [ind for ind in self._indicators if ind.category == category]
    
    def get_indicators_by_tags(self, tags: List[str]) -> List[EducationIndicator]:
        """Sucht Indikatoren nach Tags"""
        result = []
        for indicator in self._indicators:
            if any(tag in indicator.tags for tag in tags):
                result.append(indicator)
        return result
    
    def get_sections(self) -> Dict[IndicatorCategory, IndicatorSection]:
        """Gibt alle Abschnitte zurück"""
        return self._sections.copy()
    
    def get_section_by_category(self, category: IndicatorCategory) -> Optional[IndicatorSection]:
        """Gibt einen spezifischen Abschnitt zurück"""
        return self._sections.get(category)
    
    def get_statistics(self) -> Dict[str, Union[int, Dict[str, int]]]:
        """Gibt Statistiken über die Indikatoren zurück"""
        stats = {
            "total_indicators": len(self._indicators),
            "categories_count": len(IndicatorCategory),
            "by_category": {},
            "by_priority": {},
            "total_tags": len(set(tag for ind in self._indicators for tag in ind.tags))
        }
        
        # Nach Kategorie
        for category in IndicatorCategory:
            count = len(self.get_indicators_by_category(category))
            stats["by_category"][category.value] = count
        
        # Nach Priorität
        for priority in [1, 2, 3]:
            count = len([ind for ind in self._indicators if ind.priority == priority])
            stats["by_priority"][priority] = count
        
        return stats

# ===== BACKWARD-COMPATIBLE FUNCTIONS =====
class IndicatorCompatibility:
    """Backward-Compatibility Layer"""
    
    @staticmethod
    def get_indicators_sections(language: str = "de") -> Dict[str, List[Tuple[str, str, str]]]:
        """
        Backward-compatible Funktion - gibt das alte Format zurück
        
        Returns:
            dict: Dictionary mit Abschnitten und Tupel-Listen (altes Format)
        """
        manager = EducationIndicatorManager()
        sections = manager.get_sections()
        
        result = {}
        for category, section in sections.items():
            section_title = section.get_title(language)
            indicator_tuples = section.get_indicators_as_tuples(language)
            result[section_title] = indicator_tuples
        
        return result

# ===== ÖFFENTLICHE API =====
def get_indicators_sections(language: str = "de") -> Dict[str, List[Tuple[str, str, str]]]:
    """
    Hauptfunktion - Backward-compatible
    
    Args:
        language: Sprache für die Ausgabe ("de" oder "en")
        
    Returns:
        dict: Dictionary mit Abschnitten und zugehörigen Indikatoren
    """
    return IndicatorCompatibility.get_indicators_sections(language)

def get_indicator_manager() -> EducationIndicatorManager:
    """
    Neue API - Gibt den Indicator Manager zurück für erweiterte Funktionen
    
    Returns:
        EducationIndicatorManager: Manager-Instanz
    """
    return EducationIndicatorManager()

def get_supported_languages() -> List[str]:
    """Gibt unterstützte Sprachen zurück"""
    return IndicatorConstants.SUPPORTED_LANGUAGES.copy()

def get_indicator_statistics() -> Dict[str, Union[int, Dict[str, int]]]:
    """Gibt Statistiken über alle Indikatoren zurück"""
    manager = EducationIndicatorManager()
    return manager.get_statistics()

# ===== BEISPIEL-NUTZUNG =====
if __name__ == "__main__":
    # Backward-compatible Nutzung
    print("=== Backward-Compatible API ===")
    sections = get_indicators_sections()
    for section_title, indicators in sections.items():
        print(f"\n{section_title}:")
        for indicator in indicators:
            print(f"  - {indicator[1]}")  # Deutsche Frage
    
    # Neue erweiterte API
    print("\n=== Neue erweiterte API ===")
    manager = get_indicator_manager()
    
    # Statistiken
    stats = manager.get_statistics()
    print(f"Gesamt: {stats['total_indicators']} Indikatoren in {stats['categories_count']} Kategorien")
    
    # Suche nach Tags
    free_education_indicators = manager.get_indicators_by_tags(["free_education"])
    print(f"Indikatoren zu 'free_education': {len(free_education_indicators)}")
    
    # Spezifische Kategorie
    access_indicators = manager.get_indicators_by_category(IndicatorCategory.ACCESS_EDUCATION)
    print(f"Zugang-Indikatoren: {len(access_indicators)}")