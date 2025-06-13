"""
Enterprise-level English emotion detection module.

This module provides emotion detection functionality with advanced linguistic analysis,
enterprise architecture, type safety, and contextual emotion recognition.
"""

import streamlit as st
import pandas as pd
import numpy as np
import re
from collections import Counter
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================

class EnglishEmotionDetectionConstants:
    """Central constants for English emotion detection"""
    
    # Processing constants
    DEFAULT_CHUNK_SIZE = 512
    MAX_CHUNK_SIZE = 2048
    MIN_CHUNK_SIZE = 128
    DEFAULT_OVERLAP = 100
    MAX_OVERLAP = 200
    MIN_OVERLAP = 50
    
    # Text validation
    MIN_TEXT_LENGTH = 10
    MIN_SENTENCE_LENGTH = 5
    MIN_CHUNK_LENGTH = 10
    
    # Scoring constants
    NEGATION_MULTIPLIER = 0.5
    INTENSIFIER_MULTIPLIER = 1.2
    LINGUISTIC_WEIGHT = 0.3
    MODEL_WEIGHT = 0.7
    
    # Thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.1
    HIGH_CONFIDENCE_THRESHOLD = 0.7
    
    # Logging
    LOGGER_NAME = "english_emotion_detection"


class EmotionType(str, Enum):
    """Standard emotion types for English analysis"""
    ANGER = "anger"
    FEAR = "fear" 
    SADNESS = "sadness"
    JOY = "joy"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    LOVE = "love"
    NEUTRAL = "neutral"


class AnalysisMode(Enum):
    """Analysis modes for different use cases"""
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class LinguisticFeature(Enum):
    """Linguistic features for enhanced analysis"""
    NEGATION = "negation"
    CONTRAST = "contrast"
    INTENSIFIER = "intensifier"
    QUESTION = "question"
    EXCLAMATION = "exclamation"


# =============================================================================
# EMOTION COLORS AND VISUALIZATION
# =============================================================================

class EmotionVisualizationConfig:
    """Configuration for emotion visualization"""
    
    EMOTION_COLORS = {
        EmotionType.ANGER: "#FF5252",       # Red
        EmotionType.FEAR: "#FF9800",        # Orange
        EmotionType.SADNESS: "#757575",     # Dark gray
        EmotionType.JOY: "#FFD700",         # Gold
        EmotionType.SURPRISE: "#9C27B0",    # Purple
        EmotionType.DISGUST: "#8BC34A",     # Olive green
        EmotionType.LOVE: "#E91E63",        # Pink
        EmotionType.NEUTRAL: "#64B5F6"      # Light blue
    }
    
    EMOTION_ICONS = {
        EmotionType.ANGER: "😠",
        EmotionType.FEAR: "😨",
        EmotionType.SADNESS: "😢",
        EmotionType.JOY: "😊",
        EmotionType.SURPRISE: "😲",
        EmotionType.DISGUST: "🤢",
        EmotionType.LOVE: "❤️",
        EmotionType.NEUTRAL: "😐"
    }


# =============================================================================
# LINGUISTIC PATTERNS AND KEYWORDS
# =============================================================================

class EnglishLinguisticPatterns:
    """Comprehensive English linguistic patterns for emotion detection"""
    
    NEGATION_WORDS = [
        "not", "no", "never", "nothing", "nowhere", "nobody", "none", 
        "neither", "nor", "hardly", "barely", "scarcely", "seldom",
        "rarely", "without", "lacking", "absent", "missing", "void"
    ]

    CONTRAST_WORDS = [
        "but", "however", "although", "though", "nevertheless", "nonetheless", 
        "yet", "still", "on the other hand", "while", "whereas", "despite",
        "in spite of", "conversely", "alternatively", "instead", "rather"
    ]

    INTENSIFIER_WORDS = [
        "very", "extremely", "absolutely", "completely", "totally", "quite", 
        "really", "so", "too", "incredibly", "highly", "deeply", "utterly",
        "thoroughly", "exceptionally", "remarkably", "extraordinarily", "tremendously"
    ]

    QUESTION_INDICATORS = ["?", "what", "how", "why", "when", "where", "who", "which"]
    EXCLAMATION_INDICATORS = ["!", "wow", "oh", "ah", "hey", "amazing", "incredible"]


class EnglishEmotionKeywords:
    """Comprehensive English emotion keyword dictionaries"""
    
    JOY_KEYWORDS = [
        "happy", "joy", "excited", "delighted", "pleased", "cheerful", "glad", "satisfied", 
        "content", "elated", "euphoric", "thrilled", "overjoyed", "blissful", "ecstatic", 
        "upbeat", "optimistic", "positive", "wonderful", "amazing", "fantastic", "great", 
        "awesome", "brilliant", "excellent", "superb", "marvelous", "fabulous", "terrific", 
        "outstanding", "incredible", "remarkable", "admirable", "impressive", "spectacular", 
        "smile", "laugh", "laughter", "giggle", "beam", "grin", "celebrate", "celebration", 
        "party", "fun", "enjoy", "appreciate", "love", "adore", "treasure", "cherish"
    ]

    SADNESS_KEYWORDS = [
        "sad", "unhappy", "depressed", "disappointed", "upset", "sorrowful", "heartbroken", 
        "grief", "mourning", "melancholy", "blue", "down", "low", "dejected", "despondent", 
        "dispirited", "disheartened", "discouraged", "crestfallen", "forlorn", "miserable", 
        "wretched", "gloomy", "morose", "sullen", "somber", "pensive", "tearful", "weep", 
        "cry", "tears", "sob", "wail", "lament", "regret", "remorse", "sorry", "pity", 
        "sympathy", "compassion", "condolence", "loss", "bereaved", "anguish", "suffering", 
        "pain", "hurt", "wound", "broken", "shattered", "crushed", "devastated"
    ]

    FEAR_KEYWORDS = [
        "afraid", "scared", "frightened", "terrified", "anxious", "nervous", "worried", 
        "concerned", "apprehensive", "fearful", "panicked", "alarmed", "startled", "shocked", 
        "horrified", "petrified", "paranoid", "phobic", "timid", "cowardly", "intimidated", 
        "threatened", "menaced", "danger", "dangerous", "threat", "risk", "scary", "spooky", 
        "creepy", "eerie", "sinister", "ominous", "foreboding", "dreadful", "horrible", 
        "terrible", "awful", "nightmare", "haunting", "haunted", "ghost", "monster", 
        "demon", "evil", "wicked", "dark", "shadow", "unknown", "uncertainty", "doubt"
    ]

    ANGER_KEYWORDS = [
        "angry", "mad", "furious", "enraged", "irate", "livid", "outraged", "infuriated", 
        "incensed", "irritated", "annoyed", "frustrated", "aggravated", "exasperated", 
        "resentful", "indignant", "bitter", "hostile", "aggressive", "violent", "fierce", 
        "savage", "brutal", "cruel", "harsh", "rude", "disrespectful", "offensive", 
        "insulting", "abusive", "vicious", "mean", "nasty", "spiteful", "malicious", 
        "vindictive", "vengeful", "hateful", "loathe", "despise", "detest", "scorn", 
        "contempt", "disgust", "revolt", "sicken", "rage", "fury", "wrath", "temper"
    ]

    DISGUST_KEYWORDS = [
        "disgusting", "disgusted", "revolting", "repulsive", "nauseating", "sickening", 
        "gross", "yucky", "icky", "nasty", "foul", "vile", "horrible", "terrible", 
        "awful", "dreadful", "appalling", "shocking", "outrageous", "scandalous", 
        "offensive", "inappropriate", "unacceptable", "intolerable", "unbearable", 
        "abhorrent", "abominable", "detestable", "loathsome", "reprehensible", 
        "contemptible", "despicable", "deplorable", "shameful", "disgraceful", 
        "embarrassing", "mortifying", "humiliating", "degrading", "vulgar", "crude"
    ]

    SURPRISE_KEYWORDS = [
        "surprised", "shocked", "astonished", "amazed", "stunned", "bewildered", 
        "confused", "puzzled", "perplexed", "baffled", "flabbergasted", "speechless", 
        "aghast", "astounded", "dumbfounded", "thunderstruck", "startled", "jolted", 
        "taken aback", "caught off guard", "unexpected", "sudden", "abrupt", "surprising", 
        "astonishing", "amazing", "incredible", "unbelievable", "extraordinary", 
        "remarkable", "unusual", "strange", "weird", "odd", "peculiar", "curious", 
        "mysterious", "enigmatic", "puzzling", "confusing", "wonder", "marvel", "miracle"
    ]

    LOVE_KEYWORDS = [
        "love", "adore", "cherish", "treasure", "worship", "idolize", "admire", "respect", 
        "appreciate", "value", "prize", "honor", "revere", "venerate", "esteem", "regard", 
        "care", "concern", "compassion", "kindness", "tenderness", "affection", "fondness", 
        "attachment", "devotion", "dedication", "loyalty", "faithfulness", "commitment", 
        "passion", "romance", "romantic", "intimate", "beloved", "darling", "sweetheart", 
        "honey", "dear", "precious", "special", "wonderful", "beautiful", "gorgeous", 
        "stunning", "attractive", "lovely", "charming", "delightful", "enchanting"
    ]

    NEUTRAL_KEYWORDS = [
        "neutral", "objective", "factual", "actual", "real", "true", "indeed", 
        "essentially", "basically", "generally", "usually", "typically", "normally", 
        "commonly", "ordinarily", "regularly", "frequently", "often", "sometimes", 
        "occasionally", "perhaps", "maybe", "possibly", "probably", "likely", "unlikely", 
        "certainly", "definitely", "surely", "clearly", "obviously", "evidently", 
        "apparently", "seemingly", "presumably", "supposedly", "allegedly", "reportedly", 
        "according", "however", "nevertheless", "nonetheless", "furthermore", "moreover", 
        "additionally", "also", "besides", "therefore", "thus", "hence", "consequently"
    ]

    @classmethod
    def get_emotion_keywords(cls) -> Dict[EmotionType, List[str]]:
        """Get all emotion keywords as a dictionary"""
        return {
            EmotionType.JOY: cls.JOY_KEYWORDS,
            EmotionType.SADNESS: cls.SADNESS_KEYWORDS,
            EmotionType.FEAR: cls.FEAR_KEYWORDS,
            EmotionType.ANGER: cls.ANGER_KEYWORDS,
            EmotionType.DISGUST: cls.DISGUST_KEYWORDS,
            EmotionType.SURPRISE: cls.SURPRISE_KEYWORDS,
            EmotionType.LOVE: cls.LOVE_KEYWORDS,
            EmotionType.NEUTRAL: cls.NEUTRAL_KEYWORDS
        }


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class EnglishEmotionDetectionConfig:
    """Enterprise configuration for English emotion detection"""
    
    # Processing settings
    chunk_size: int = EnglishEmotionDetectionConstants.DEFAULT_CHUNK_SIZE
    overlap: int = EnglishEmotionDetectionConstants.DEFAULT_OVERLAP
    analysis_mode: AnalysisMode = AnalysisMode.STANDARD
    
    # Text validation
    min_text_length: int = EnglishEmotionDetectionConstants.MIN_TEXT_LENGTH
    min_sentence_length: int = EnglishEmotionDetectionConstants.MIN_SENTENCE_LENGTH
    min_chunk_length: int = EnglishEmotionDetectionConstants.MIN_CHUNK_LENGTH
    
    # Scoring weights
    negation_multiplier: float = EnglishEmotionDetectionConstants.NEGATION_MULTIPLIER
    intensifier_multiplier: float = EnglishEmotionDetectionConstants.INTENSIFIER_MULTIPLIER
    linguistic_weight: float = EnglishEmotionDetectionConstants.LINGUISTIC_WEIGHT
    model_weight: float = EnglishEmotionDetectionConstants.MODEL_WEIGHT
    
    # Confidence thresholds
    min_confidence: float = EnglishEmotionDetectionConstants.MIN_CONFIDENCE_THRESHOLD
    high_confidence: float = EnglishEmotionDetectionConstants.HIGH_CONFIDENCE_THRESHOLD
    
    # Feature flags
    enable_linguistic_analysis: bool = True
    enable_sentence_structure: bool = True
    enable_contextual_analysis: bool = True
    enable_confidence_filtering: bool = True
    
    def validate(self) -> bool:
        """Validate configuration parameters"""
        return (
            EnglishEmotionDetectionConstants.MIN_CHUNK_SIZE <= self.chunk_size <= EnglishEmotionDetectionConstants.MAX_CHUNK_SIZE and
            EnglishEmotionDetectionConstants.MIN_OVERLAP <= self.overlap <= EnglishEmotionDetectionConstants.MAX_OVERLAP and
            0 <= self.min_confidence <= 1.0 and
            0 <= self.high_confidence <= 1.0 and
            0 <= self.linguistic_weight <= 1.0 and
            0 <= self.model_weight <= 1.0
        )


@dataclass
class EnglishSentenceAnalysis:
    """Analysis result for English sentence structure"""
    text: str
    length: int
    features: Dict[LinguisticFeature, bool] = field(default_factory=dict)
    emotion_indicators: Dict[EmotionType, int] = field(default_factory=dict)
    confidence_score: float = 0.0
    
    @property
    def has_modifiers(self) -> bool:
        """Check if sentence has any linguistic modifiers"""
        return any(self.features.values())
    
    @property
    def dominant_emotion_indicator(self) -> Optional[EmotionType]:
        """Get the emotion with most indicators"""
        if not self.emotion_indicators:
            return None
        return max(self.emotion_indicators, key=self.emotion_indicators.get)


@dataclass
class EnglishEmotionScores:
    """Container for English emotion scores with enhanced metadata"""
    model_scores: Dict[str, float] = field(default_factory=dict)
    linguistic_scores: Dict[str, float] = field(default_factory=dict)
    combined_scores: Dict[str, float] = field(default_factory=dict)
    sentence_analyses: List[EnglishSentenceAnalysis] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def dominant_emotion(self) -> Optional[str]:
        """Get the dominant emotion from combined scores"""
        if not self.combined_scores:
            return None
        return max(self.combined_scores, key=self.combined_scores.get)
    
    @property
    def confidence_score(self) -> float:
        """Calculate overall confidence score"""
        if not self.combined_scores:
            return 0.0
        return max(self.combined_scores.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization"""
        return {
            "model_scores": self.model_scores,
            "linguistic_scores": self.linguistic_scores,
            "combined_scores": self.combined_scores,
            "dominant_emotion": self.dominant_emotion,
            "confidence_score": self.confidence_score,
            "sentence_count": len(self.sentence_analyses),
            "metadata": self.metadata
        }


@dataclass
class EnglishEmotionDetectionResults:
    """Results of English emotion detection analysis"""
    text: str
    emotion_scores: EnglishEmotionScores
    processing_time: float
    config_used: EnglishEmotionDetectionConfig
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary"""
        result = self.emotion_scores.to_dict()
        result.update({
            "text_length": len(self.text),
            "processing_time": self.processing_time,
            "success": self.success,
            "error_message": self.error_message
        })
        return result


# =============================================================================
# SPECIALIZED COMPONENTS
# =============================================================================

class EnglishTextValidator:
    """Validates and prepares English text for emotion detection"""
    
    def __init__(self, config: EnglishEmotionDetectionConfig):
        self.config = config
        self.logger = logging.getLogger(EnglishEmotionDetectionConstants.LOGGER_NAME)
    
    def validate_and_prepare(self, text: Any) -> Optional[str]:
        """Validate and prepare text input"""
        try:
            if pd.isna(text) or text is None or text == "":
                return None
            
            text_str = str(text).strip()
            
            if len(text_str) < self.config.min_text_length:
                return None
            
            return text_str
            
        except Exception as e:
            self.logger.warning(f"Text validation error: {e}")
            return None


class EnglishTextChunker:
    """Handles text chunking for large texts"""
    
    def __init__(self, config: EnglishEmotionDetectionConfig):
        self.config = config
        self.logger = logging.getLogger(EnglishEmotionDetectionConstants.LOGGER_NAME)
    
    def create_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        try:
            if len(text) <= self.config.chunk_size:
                return [text]
            
            chunks = []
            step = self.config.chunk_size - self.config.overlap
            
            for i in range(0, len(text), step):
                chunk = text[i:i + self.config.chunk_size]
                if len(chunk) >= self.config.min_chunk_length:
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Text chunking error: {e}")
            return [text]


class EnglishSentenceAnalyzer:
    """Analyzes English sentences for linguistic features"""
    
    def __init__(self, config: EnglishEmotionDetectionConfig):
        self.config = config
        self.patterns = EnglishLinguisticPatterns()
        self.keywords = EnglishEmotionKeywords()
        self.logger = logging.getLogger(EnglishEmotionDetectionConstants.LOGGER_NAME)
    
    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences with English language specifics"""
        try:
            # Enhanced pattern for English sentence endings
            pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=[.!?])\s+'
            sentences = re.split(pattern, text)
            
            # Filter by minimum length
            return [
                s.strip() for s in sentences 
                if s.strip() and len(s.strip()) >= self.config.min_sentence_length
            ]
            
        except Exception as e:
            self.logger.warning(f"Sentence splitting error: {e}")
            return [text]
    
    def analyze_sentence(self, sentence: str) -> EnglishSentenceAnalysis:
        """Analyze a single sentence for linguistic features"""
        try:
            sentence_lower = sentence.lower()
            sentence_words = sentence_lower.split()
            
            # Detect linguistic features
            features = {
                LinguisticFeature.NEGATION: any(word in sentence_words for word in self.patterns.NEGATION_WORDS),
                LinguisticFeature.CONTRAST: any(word in sentence_lower for word in self.patterns.CONTRAST_WORDS),
                LinguisticFeature.INTENSIFIER: any(word in sentence_words for word in self.patterns.INTENSIFIER_WORDS),
                LinguisticFeature.QUESTION: any(indicator in sentence_lower for indicator in self.patterns.QUESTION_INDICATORS),
                LinguisticFeature.EXCLAMATION: any(indicator in sentence_lower for indicator in self.patterns.EXCLAMATION_INDICATORS)
            }
            
            # Count emotion indicators
            emotion_indicators = {}
            emotion_keywords = self.keywords.get_emotion_keywords()
            
            for emotion, keywords in emotion_keywords.items():
                count = sum(1 for keyword in keywords if keyword in sentence_lower)
                if count > 0:
                    emotion_indicators[emotion] = count
            
            # Calculate confidence based on indicators
            total_indicators = sum(emotion_indicators.values())
            confidence = min(total_indicators / 5.0, 1.0) if total_indicators > 0 else 0.0
            
            return EnglishSentenceAnalysis(
                text=sentence,
                length=len(sentence),
                features=features,
                emotion_indicators=emotion_indicators,
                confidence_score=confidence
            )
            
        except Exception as e:
            self.logger.warning(f"Sentence analysis error: {e}")
            return EnglishSentenceAnalysis(text=sentence, length=len(sentence))


class EnglishModelEmotionDetector:
    """Handles model-based emotion detection"""
    
    def __init__(self, config: EnglishEmotionDetectionConfig):
        self.config = config
        self.chunker = EnglishTextChunker(config)
        self.logger = logging.getLogger(EnglishEmotionDetectionConstants.LOGGER_NAME)
    
    def detect_emotions(self, text: str, emotion_classifier: Any) -> Dict[str, float]:
        """Detect emotions using the model"""
        try:
            if emotion_classifier is None:
                return {}
            
            # For short texts, analyze directly
            if len(text) <= self.config.chunk_size:
                return self._analyze_single_chunk(text, emotion_classifier)
            
            # For longer texts, use chunking
            chunks = self.chunker.create_chunks(text)
            return self._analyze_multiple_chunks(chunks, emotion_classifier)
            
        except Exception as e:
            self.logger.error(f"Model emotion detection error: {e}")
            return {}
    
    def _analyze_single_chunk(self, text: str, emotion_classifier: Any) -> Dict[str, float]:
        """Analyze a single chunk of text"""
        try:
            predictions = emotion_classifier(text)
            result = {}
            
            for item in predictions[0]:
                emotion = item['label']
                score = item['score']
                
                if self.config.enable_confidence_filtering:
                    if score >= self.config.min_confidence:
                        result[emotion] = score
                else:
                    result[emotion] = score
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Single chunk analysis error: {e}")
            return {}
    
    def _analyze_multiple_chunks(self, chunks: List[str], emotion_classifier: Any) -> Dict[str, float]:
        """Analyze multiple chunks and aggregate results"""
        try:
            all_scores = {}
            
            for chunk in chunks:
                chunk_scores = self._analyze_single_chunk(chunk, emotion_classifier)
                
                for emotion, score in chunk_scores.items():
                    if emotion not in all_scores:
                        all_scores[emotion] = []
                    all_scores[emotion].append(score)
            
            # Aggregate using maximum (strong emotions shouldn't be diluted)
            result = {}
            for emotion, scores in all_scores.items():
                result[emotion] = max(scores) if scores else 0.0
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Multiple chunk analysis error: {e}")
            return {}


class EnglishLinguisticEmotionDetector:
    """Handles linguistic-based emotion detection"""
    
    def __init__(self, config: EnglishEmotionDetectionConfig):
        self.config = config
        self.sentence_analyzer = EnglishSentenceAnalyzer(config)
        self.logger = logging.getLogger(EnglishEmotionDetectionConstants.LOGGER_NAME)
    
    def detect_emotions(self, text: str) -> Tuple[Dict[str, float], List[EnglishSentenceAnalysis]]:
        """Detect emotions using linguistic analysis"""
        try:
            sentences = self.sentence_analyzer.split_into_sentences(text)
            sentence_analyses = []
            emotion_accumulator = {}
            
            for sentence in sentences:
                analysis = self.sentence_analyzer.analyze_sentence(sentence)
                sentence_analyses.append(analysis)
                
                # Process emotion indicators with modifiers
                for emotion, count in analysis.emotion_indicators.items():
                    emotion_str = emotion.value
                    score = count
                    
                    # Apply linguistic modifiers
                    if analysis.features.get(LinguisticFeature.INTENSIFIER, False):
                        score *= self.config.intensifier_multiplier
                    
                    if analysis.features.get(LinguisticFeature.NEGATION, False):
                        if emotion in [EmotionType.JOY, EmotionType.LOVE]:
                            # Negated positive emotions become neutral
                            emotion_str = EmotionType.NEUTRAL.value
                            score *= self.config.negation_multiplier
                        elif emotion == EmotionType.NEUTRAL:
                            # Negated neutral becomes slightly negative
                            emotion_str = EmotionType.SADNESS.value
                            score *= 0.5
                    
                    # Accumulate scores
                    if emotion_str not in emotion_accumulator:
                        emotion_accumulator[emotion_str] = []
                    emotion_accumulator[emotion_str].append(score)
            
            # Calculate final linguistic scores
            linguistic_scores = {}
            for emotion, scores in emotion_accumulator.items():
                linguistic_scores[emotion] = sum(scores) / len(scores) if scores else 0.0
            
            return linguistic_scores, sentence_analyses
            
        except Exception as e:
            self.logger.error(f"Linguistic emotion detection error: {e}")
            return {}, []


class EnglishEmotionScoreCombiner:
    """Combines model and linguistic emotion scores"""
    
    def __init__(self, config: EnglishEmotionDetectionConfig):
        self.config = config
        self.logger = logging.getLogger(EnglishEmotionDetectionConstants.LOGGER_NAME)
    
    def combine_scores(
        self, 
        model_scores: Dict[str, float], 
        linguistic_scores: Dict[str, float]
    ) -> Dict[str, float]:
        """Combine model and linguistic scores"""
        try:
            # Get all unique emotions
            all_emotions = set(model_scores.keys()) | set(linguistic_scores.keys())
            combined_scores = {}
            
            for emotion in all_emotions:
                model_score = model_scores.get(emotion, 0.0)
                linguistic_score = linguistic_scores.get(emotion, 0.0)
                
                # Weighted combination
                combined_score = (
                    model_score * self.config.model_weight + 
                    linguistic_score * self.config.linguistic_weight
                )
                
                combined_scores[emotion] = combined_score
            
            # Normalize scores to sum to 1
            total = sum(combined_scores.values())
            if total > 0:
                combined_scores = {k: v/total for k, v in combined_scores.items()}
            
            return combined_scores
            
        except Exception as e:
            self.logger.error(f"Score combination error: {e}")
            return model_scores.copy()


# =============================================================================
# MANAGER CLASS
# =============================================================================

class EnglishEmotionDetectionManager:
    """Enterprise manager for English emotion detection"""
    
    def __init__(self, config: Optional[EnglishEmotionDetectionConfig] = None):
        self.config = config or EnglishEmotionDetectionConfig()
        
        if not self.config.validate():
            raise ValueError("Invalid configuration parameters")
        
        # Initialize components
        self.text_validator = EnglishTextValidator(self.config)
        self.model_detector = EnglishModelEmotionDetector(self.config)
        self.linguistic_detector = EnglishLinguisticEmotionDetector(self.config)
        self.score_combiner = EnglishEmotionScoreCombiner(self.config)
        
        self.logger = logging.getLogger(EnglishEmotionDetectionConstants.LOGGER_NAME)
    
    def detect_emotions(
        self, 
        text: Any, 
        emotion_classifier: Any
    ) -> Optional[EnglishEmotionDetectionResults]:
        """Comprehensive emotion detection with enterprise features"""
        import time
        start_time = time.time()
        
        try:
            # Validate input
            validated_text = self.text_validator.validate_and_prepare(text)
            if validated_text is None:
                return EnglishEmotionDetectionResults(
                    text=str(text) if text else "",
                    emotion_scores=EnglishEmotionScores(),
                    processing_time=time.time() - start_time,
                    config_used=self.config,
                    success=False,
                    error_message="Invalid or empty text input"
                )
            
            # Model-based detection
            model_scores = {}
            if emotion_classifier is not None:
                model_scores = self.model_detector.detect_emotions(validated_text, emotion_classifier)
            
            # Linguistic detection
            linguistic_scores = {}
            sentence_analyses = []
            
            if self.config.enable_linguistic_analysis:
                linguistic_scores, sentence_analyses = self.linguistic_detector.detect_emotions(validated_text)
            
            # Combine scores
            combined_scores = self.score_combiner.combine_scores(model_scores, linguistic_scores)
            
            # Create emotion scores object
            emotion_scores = EnglishEmotionScores(
                model_scores=model_scores,
                linguistic_scores=linguistic_scores,
                combined_scores=combined_scores,
                sentence_analyses=sentence_analyses,
                metadata={
                    "text_length": len(validated_text),
                    "sentence_count": len(sentence_analyses),
                    "analysis_mode": self.config.analysis_mode.value,
                    "features_enabled": {
                        "linguistic": self.config.enable_linguistic_analysis,
                        "sentence_structure": self.config.enable_sentence_structure,
                        "contextual": self.config.enable_contextual_analysis
                    }
                }
            )
            
            processing_time = time.time() - start_time
            
            return EnglishEmotionDetectionResults(
                text=validated_text,
                emotion_scores=emotion_scores,
                processing_time=processing_time,
                config_used=self.config,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Emotion detection error: {e}")
            return EnglishEmotionDetectionResults(
                text=str(text) if text else "",
                emotion_scores=EnglishEmotionScores(),
                processing_time=time.time() - start_time,
                config_used=self.config,
                success=False,
                error_message=str(e)
            )
    
    def batch_detect_emotions(
        self, 
        texts: List[Any], 
        emotion_classifier: Any
    ) -> List[EnglishEmotionDetectionResults]:
        """Batch emotion detection for multiple texts"""
        try:
            results = []
            
            for text in texts:
                result = self.detect_emotions(text, emotion_classifier)
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Batch emotion detection error: {e}")
            return []


# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_english_emotion_detection_config() -> EnglishEmotionDetectionConfig:
    """Render English emotion detection configuration UI"""
    st.subheader("🔤 English Emotion Detection Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Processing Settings**")
        chunk_size = st.slider(
            "Chunk Size",
            min_value=EnglishEmotionDetectionConstants.MIN_CHUNK_SIZE,
            max_value=EnglishEmotionDetectionConstants.MAX_CHUNK_SIZE,
            value=EnglishEmotionDetectionConstants.DEFAULT_CHUNK_SIZE,
            step=64
        )
        
        overlap = st.slider(
            "Chunk Overlap",
            min_value=EnglishEmotionDetectionConstants.MIN_OVERLAP,
            max_value=EnglishEmotionDetectionConstants.MAX_OVERLAP,
            value=EnglishEmotionDetectionConstants.DEFAULT_OVERLAP,
            step=10
        )
        
        analysis_mode = st.selectbox(
            "Analysis Mode",
            options=[mode.value for mode in AnalysisMode],
            index=1  # Standard
        )
    
    with col2:
        st.write("**Feature Settings**")
        enable_linguistic = st.checkbox("Enable Linguistic Analysis", value=True)
        enable_sentence = st.checkbox("Enable Sentence Structure", value=True)
        enable_contextual = st.checkbox("Enable Contextual Analysis", value=True)
        enable_confidence = st.checkbox("Enable Confidence Filtering", value=True)
        
        if enable_confidence:
            min_confidence = st.slider(
                "Minimum Confidence",
                min_value=0.0,
                max_value=1.0,
                value=EnglishEmotionDetectionConstants.MIN_CONFIDENCE_THRESHOLD,
                step=0.05
            )
        else:
            min_confidence = 0.0
    
    return EnglishEmotionDetectionConfig(
        chunk_size=chunk_size,
        overlap=overlap,
        analysis_mode=AnalysisMode(analysis_mode),
        enable_linguistic_analysis=enable_linguistic,
        enable_sentence_structure=enable_sentence,
        enable_contextual_analysis=enable_contextual,
        enable_confidence_filtering=enable_confidence,
        min_confidence=min_confidence
    )


def render_english_emotion_results(results: EnglishEmotionDetectionResults) -> None:
    """Render English emotion detection results"""
    st.subheader("📊 English Emotion Detection Results")
    
    if not results.success:
        st.error(f"Detection failed: {results.error_message}")
        return
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Dominant Emotion", results.emotion_scores.dominant_emotion or "None")
    
    with col2:
        st.metric("Confidence", f"{results.emotion_scores.confidence_score:.2%}")
    
    with col3:
        st.metric("Sentences", len(results.emotion_scores.sentence_analyses))
    
    with col4:
        st.metric("Processing Time", f"{results.processing_time:.3f}s")
    
    # Emotion scores
    if results.emotion_scores.combined_scores:
        st.subheader("🎭 Emotion Scores")
        
        # Create columns for different score types
        score_col1, score_col2, score_col3 = st.columns(3)
        
        with score_col1:
            st.write("**Model Scores**")
            for emotion, score in sorted(results.emotion_scores.model_scores.items()):
                st.write(f"{emotion}: {score:.3f}")
        
        with score_col2:
            st.write("**Linguistic Scores**")
            for emotion, score in sorted(results.emotion_scores.linguistic_scores.items()):
                st.write(f"{emotion}: {score:.3f}")
        
        with score_col3:
            st.write("**Combined Scores**")
            for emotion, score in sorted(results.emotion_scores.combined_scores.items()):
                color = EmotionVisualizationConfig.EMOTION_COLORS.get(EmotionType(emotion), "#64B5F6")
                st.write(f"<span style='color: {color}'>{emotion}: {score:.3f}</span>", unsafe_allow_html=True)
    
    # Sentence analysis
    if results.emotion_scores.sentence_analyses and st.checkbox("Show Sentence Analysis"):
        st.subheader("📝 Sentence Analysis")
        
        for i, analysis in enumerate(results.emotion_scores.sentence_analyses):
            with st.expander(f"Sentence {i+1} (Confidence: {analysis.confidence_score:.2f})"):
                st.write(f"**Text:** {analysis.text}")
                st.write(f"**Length:** {analysis.length} characters")
                
                if analysis.features:
                    st.write("**Linguistic Features:**")
                    for feature, present in analysis.features.items():
                        if present:
                            st.write(f"- {feature.value.title()}")
                
                if analysis.emotion_indicators:
                    st.write("**Emotion Indicators:**")
                    for emotion, count in analysis.emotion_indicators.items():
                        icon = EmotionVisualizationConfig.EMOTION_ICONS.get(emotion, "")
                        st.write(f"- {icon} {emotion.value}: {count}")


def render_english_emotion_statistics(results_list: List[EnglishEmotionDetectionResults]) -> None:
    """Render statistics for multiple emotion detection results"""
    if not results_list:
        st.warning("No results to display statistics for.")
        return
    
    st.subheader("📈 English Emotion Detection Statistics")
    
    # Overall statistics
    successful_results = [r for r in results_list if r.success]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Texts", len(results_list))
    
    with col2:
        st.metric("Successful", len(successful_results))
    
    with col3:
        success_rate = len(successful_results) / len(results_list) if results_list else 0
        st.metric("Success Rate", f"{success_rate:.1%}")
    
    if successful_results:
        # Emotion distribution
        emotion_counts = {}
        for result in successful_results:
            dominant = result.emotion_scores.dominant_emotion
            if dominant:
                emotion_counts[dominant] = emotion_counts.get(dominant, 0) + 1
        
        if emotion_counts:
            st.subheader("🎭 Emotion Distribution")
            for emotion, count in sorted(emotion_counts.items()):
                percentage = count / len(successful_results)
                st.write(f"{emotion}: {count} ({percentage:.1%})")


# =============================================================================
# BACKWARD COMPATIBILITY - LEGACY API (FIXED!)
# =============================================================================

def validate_text_input(text: Any) -> Optional[str]:
    """
    LEGACY FUNCTION: Validate and prepare text input for emotion detection.
    
    Args:
        text: Input text to validate
        
    Returns:
        Cleaned text string or None if invalid
    """
    if pd.isna(text) or text is None or text == "":
        return None
    
    text_str = str(text)
    
    if len(text_str) < EnglishEmotionDetectionConstants.MIN_TEXT_LENGTH:
        return None
    
    return text_str


def create_text_chunks(text: str, chunk_size: int = EnglishEmotionDetectionConstants.DEFAULT_CHUNK_SIZE, overlap: int = EnglishEmotionDetectionConstants.DEFAULT_OVERLAP) -> List[str]:
    """
    LEGACY FUNCTION: Split text into overlapping chunks for processing.
    
    Args:
        text: Text to split
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if len(chunk) >= EnglishEmotionDetectionConstants.MIN_CHUNK_LENGTH:
            chunks.append(chunk)
    
    return chunks


def detect_emotions_in_chunks(text: str, emotion_classifier: Any, config: Optional[EnglishEmotionDetectionConfig] = None) -> Optional[Dict[str, float]]:
    """
    LEGACY FUNCTION: Detect emotions in text using chunk-based approach.
    
    Args:
        text: Text to analyze
        emotion_classifier: Emotion recognition model
        config: Detection configuration (optional)
        
    Returns:
        Dictionary with emotion scores or None if failed
    """
    if emotion_classifier is None:
        return None
    
    if config is None:
        config = EnglishEmotionDetectionConfig()
    
    try:
        # For short texts, analyze directly
        if len(text) <= config.chunk_size:
            preds = emotion_classifier(text)
            
            # Extract emotion scores
            result = {}
            for item in preds[0]:
                result[item['label']] = item['score']
            
            return result
        
        # For longer texts, split into overlapping chunks
        chunks = create_text_chunks(text, config.chunk_size, config.overlap)
        
        if not chunks:
            return None
        
        # Collect emotion scores for each chunk
        all_scores = {}
        
        for chunk in chunks:
            preds = emotion_classifier(chunk)
            
            # Extract scores from this chunk
            for item in preds[0]:
                emotion_name = item['label']
                if emotion_name not in all_scores:
                    all_scores[emotion_name] = []
                
                all_scores[emotion_name].append(item['score'])
        
        # Aggregate the scores using maximum value
        # Maximum is used because strong emotional expressions in one part
        # should not be weakened by neutral parts
        result = {}
        for emotion, scores in all_scores.items():
            result[emotion] = max(scores) if scores else 0
        
        return result
        
    except Exception:
        return None


def detect_emotions(
    text: Any, 
    emotion_classifier: Any, 
    chunk_size: int = EnglishEmotionDetectionConstants.DEFAULT_CHUNK_SIZE, 
    overlap: int = EnglishEmotionDetectionConstants.DEFAULT_OVERLAP
) -> Optional[Dict[str, float]]:
    """
    LEGACY FUNCTION: Detect emotions in text by splitting into overlapping chunks.
    
    Args:
        text: Text to analyze
        emotion_classifier: Emotion recognition model
        chunk_size: Size of text chunks
        overlap: Overlap between chunks in characters
        
    Returns:
        Dictionary with aggregated emotion scores
    """
    # Validate input
    validated_text = validate_text_input(text)
    if validated_text is None:
        return None
    
    # Create configuration
    config = EnglishEmotionDetectionConfig(chunk_size=chunk_size, overlap=overlap)
    
    # Detect emotions using chunks
    return detect_emotions_in_chunks(validated_text, emotion_classifier, config)


def perform_linguistic_analysis(text: str, config: Optional[EnglishEmotionDetectionConfig] = None) -> Tuple[Dict[str, float], Dict[str, int]]:
    """
    LEGACY FUNCTION: Perform comprehensive linguistic analysis of text.
    
    Args:
        text: Text to analyze
        config: Detection configuration (optional)
        
    Returns:
        Tuple of (linguistic_emotions, sentence_counts)
    """
    if config is None:
        config = EnglishEmotionDetectionConfig()
        
    try:
        # Use new system internally
        manager = EnglishEmotionDetectionManager(config)
        linguistic_scores, sentence_analyses = manager.linguistic_detector.detect_emotions(text)
        
        # Convert to legacy format
        sentence_counts = {}
        for analysis in sentence_analyses:
            for emotion, count in analysis.emotion_indicators.items():
                emotion_str = emotion.value
                sentence_counts[emotion_str] = sentence_counts.get(emotion_str, 0) + 1
        
        return linguistic_scores, sentence_counts
        
    except Exception:
        return {}, {}


def contextual_emotion_detection(text: Any, emotion_classifier: Any) -> Optional[Dict[str, Any]]:
    """
    LEGACY FUNCTION: Enhanced emotion recognition with precise linguistic analysis.
    
    Args:
        text: Text to analyze
        emotion_classifier: Emotion recognition model
        
    Returns:
        Dictionary with combined emotion scores
    """
    # Validate input
    validated_text = validate_text_input(text)
    if validated_text is None:
        return None
    
    # Create configuration
    config = EnglishEmotionDetectionConfig()
    
    # Get model-based emotion scores
    model_emotions = detect_emotions_in_chunks(validated_text, emotion_classifier, config)
    if model_emotions is None:
        return None
    
    # Perform linguistic analysis
    linguistic_emotions, sentence_counts = perform_linguistic_analysis(validated_text, config)
    
    # Combine results in legacy format
    result = model_emotions.copy()
    
    # Add linguistic scores
    for emotion, score in linguistic_emotions.items():
        result[f"{emotion}_linguistic"] = score
    
    # Add sentence counts
    for emotion, count in sentence_counts.items():
        result[f"{emotion}_sentence_count"] = count
    
    return result


def get_emotion_keywords() -> Dict[str, List[str]]:
    """
    LEGACY FUNCTION: Get emotion keywords dictionary for analysis.
    
    Returns:
        Dictionary with emotions and associated keywords
    """
    keywords = EnglishEmotionKeywords.get_emotion_keywords()
    return {emotion.value: words for emotion, words in keywords.items()}


def analyze_sentence_structure_enhanced(text: str, config: Optional[EnglishEmotionDetectionConfig] = None) -> Dict[str, bool]:
    """
    LEGACY FUNCTION: Analyze sentence structure for better emotion recognition.
    
    Args:
        text: Text to analyze
        config: Detection configuration (optional)
        
    Returns:
        Dictionary with sentence structure analysis
    """
    if not text:
        return {
            "negation_present": False,
            "contrast_present": False,
            "intensifier_present": False,
            "question_present": False,
            "exclamation_present": False
        }
    
    if config is None:
        config = EnglishEmotionDetectionConfig()
    
    try:
        analyzer = EnglishSentenceAnalyzer(config)
        analysis = analyzer.analyze_sentence(text)
        
        return {
            "negation_present": analysis.features.get(LinguisticFeature.NEGATION, False),
            "contrast_present": analysis.features.get(LinguisticFeature.CONTRAST, False),
            "intensifier_present": analysis.features.get(LinguisticFeature.INTENSIFIER, False),
            "question_present": analysis.features.get(LinguisticFeature.QUESTION, False),
            "exclamation_present": analysis.features.get(LinguisticFeature.EXCLAMATION, False)
        }
    except Exception:
        return {
            "negation_present": False,
            "contrast_present": False,
            "intensifier_present": False,
            "question_present": False,
            "exclamation_present": False
        }


def split_text_into_sentences_enhanced(text: str, config: Optional[EnglishEmotionDetectionConfig] = None) -> List[str]:
    """
    LEGACY FUNCTION: Split text into sentences with English language specifics.
    
    Args:
        text: Text to split
        config: Detection configuration (optional)
        
    Returns:
        List of sentences
    """
    if not text:
        return []
    
    if config is None:
        config = EnglishEmotionDetectionConfig()
    
    try:
        analyzer = EnglishSentenceAnalyzer(config)
        return analyzer.split_into_sentences(text)
    except Exception:
        # Fallback to simple splitting
        sentences = re.split(r'[.!?]+\s+', text)
        return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]


def analyze_emotional_content_in_sentence(sentence: str, emotion_keywords: Dict[str, List[str]], config: Optional[EnglishEmotionDetectionConfig] = None) -> Dict[str, float]:
    """
    LEGACY FUNCTION: Analyze emotional content in a single sentence.
    
    Args:
        sentence: Sentence to analyze
        emotion_keywords: Dictionary with emotion keywords
        config: Detection configuration (optional)
        
    Returns:
        Dictionary with emotion scores
    """
    if not sentence or not emotion_keywords:
        return {}
    
    if config is None:
        config = EnglishEmotionDetectionConfig()
    
    try:
        analyzer = EnglishSentenceAnalyzer(config)
        analysis = analyzer.analyze_sentence(sentence)
        
        # Convert emotion indicators to the expected format
        result = {}
        for emotion, count in analysis.emotion_indicators.items():
            result[emotion.value] = float(count)
        
        # Normalize if needed
        total = sum(result.values())
        if total > 0:
            result = {k: v/total for k, v in result.items()}
        
        return result
        
    except Exception:
        # Fallback to simple analysis
        results = {}
        sentence_lower = sentence.lower()
        
        # Check for each emotion
        for emotion, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in sentence_lower)
            if count > 0:
                results[emotion] = count
        
        # Normalize results
        if results:
            total = sum(results.values())
            return {k: v/total for k, v in results.items()}
        
        return {}


def analyze_sentence_structure(text: str) -> Dict[str, bool]:
    """
    LEGACY FUNCTION: Legacy function for backward compatibility.
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with sentence structure analysis
    """
    return analyze_sentence_structure_enhanced(text)


def split_text_into_sentences(text: str) -> List[str]:
    """
    LEGACY FUNCTION: Legacy function for backward compatibility.
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    return split_text_into_sentences_enhanced(text)


def analyze_emotional_content(sentence: str, emotion_keywords: Dict[str, List[str]]) -> Dict[str, float]:
    """
    LEGACY FUNCTION: Legacy function for backward compatibility.
    
    Args:
        sentence: Sentence to analyze
        emotion_keywords: Dictionary with emotion keywords
        
    Returns:
        Dictionary with emotion scores
    """
    return analyze_emotional_content_in_sentence(sentence, emotion_keywords)


# =============================================================================
# LEGACY COMPATIBILITY - ORIGINAL CONSTANTS (RESTORED!)
# =============================================================================

# Legacy constants for full backward compatibility
DEFAULT_CHUNK_SIZE = EnglishEmotionDetectionConstants.DEFAULT_CHUNK_SIZE
DEFAULT_OVERLAP = EnglishEmotionDetectionConstants.DEFAULT_OVERLAP
MIN_TEXT_LENGTH = EnglishEmotionDetectionConstants.MIN_TEXT_LENGTH
MIN_SENTENCE_LENGTH = EnglishEmotionDetectionConstants.MIN_SENTENCE_LENGTH
MIN_CHUNK_LENGTH = EnglishEmotionDetectionConstants.MIN_CHUNK_LENGTH

# Scoring constants
NEGATION_MULTIPLIER = EnglishEmotionDetectionConstants.NEGATION_MULTIPLIER
INTENSIFIER_MULTIPLIER = EnglishEmotionDetectionConstants.INTENSIFIER_MULTIPLIER
LINGUISTIC_WEIGHT = EnglishEmotionDetectionConstants.LINGUISTIC_WEIGHT
MODEL_WEIGHT = EnglishEmotionDetectionConstants.MODEL_WEIGHT

# Emotion colors for visualization (restored)
EMOTION_COLORS = EmotionVisualizationConfig.EMOTION_COLORS

# Linguistic analysis patterns (restored)
NEGATION_WORDS = EnglishLinguisticPatterns.NEGATION_WORDS
CONTRAST_WORDS = EnglishLinguisticPatterns.CONTRAST_WORDS  
INTENSIFIER_WORDS = EnglishLinguisticPatterns.INTENSIFIER_WORDS

# Comprehensive emotion keyword dictionaries (restored)
JOY_KEYWORDS = EnglishEmotionKeywords.JOY_KEYWORDS
SADNESS_KEYWORDS = EnglishEmotionKeywords.SADNESS_KEYWORDS
FEAR_KEYWORDS = EnglishEmotionKeywords.FEAR_KEYWORDS
ANGER_KEYWORDS = EnglishEmotionKeywords.ANGER_KEYWORDS
DISGUST_KEYWORDS = EnglishEmotionKeywords.DISGUST_KEYWORDS
SURPRISE_KEYWORDS = EnglishEmotionKeywords.SURPRISE_KEYWORDS
LOVE_KEYWORDS = EnglishEmotionKeywords.LOVE_KEYWORDS
NEUTRAL_KEYWORDS = EnglishEmotionKeywords.NEUTRAL_KEYWORDS

# Master emotion keywords dictionary (restored)
EMOTION_KEYWORDS = {
    EmotionType.JOY.value: JOY_KEYWORDS,
    EmotionType.SADNESS.value: SADNESS_KEYWORDS,
    EmotionType.FEAR.value: FEAR_KEYWORDS,
    EmotionType.ANGER.value: ANGER_KEYWORDS,
    EmotionType.DISGUST.value: DISGUST_KEYWORDS,
    EmotionType.SURPRISE.value: SURPRISE_KEYWORDS,
    EmotionType.LOVE.value: LOVE_KEYWORDS,
    EmotionType.NEUTRAL.value: NEUTRAL_KEYWORDS
}


# =============================================================================
# LEGACY DATA MODELS (RESTORED!)
# =============================================================================

@dataclass
class EmotionDetectionConfig:
    """Legacy configuration for emotion detection (restored)"""
    chunk_size: int = DEFAULT_CHUNK_SIZE
    overlap: int = DEFAULT_OVERLAP
    min_text_length: int = MIN_TEXT_LENGTH
    min_sentence_length: int = MIN_SENTENCE_LENGTH
    negation_multiplier: float = NEGATION_MULTIPLIER
    intensifier_multiplier: float = INTENSIFIER_MULTIPLIER
    
    def to_modern_config(self) -> EnglishEmotionDetectionConfig:
        """Convert to modern configuration"""
        return EnglishEmotionDetectionConfig(
            chunk_size=self.chunk_size,
            overlap=self.overlap,
            min_text_length=self.min_text_length,
            min_sentence_length=self.min_sentence_length,
            negation_multiplier=self.negation_multiplier,
            intensifier_multiplier=self.intensifier_multiplier
        )


@dataclass
class SentenceAnalysis:
    """Legacy analysis result for sentence structure (restored)"""
    negation_present: bool = False
    contrast_present: bool = False
    intensifier_present: bool = False
    question_present: bool = False
    exclamation_present: bool = False
    
    @property
    def has_modifiers(self) -> bool:
        """Check if sentence has any linguistic modifiers."""
        return (self.negation_present or self.contrast_present or 
                self.intensifier_present or self.exclamation_present)


@dataclass
class EmotionScores:
    """Legacy container for emotion scores (restored)"""
    model_scores: Dict[str, float] = field(default_factory=dict)
    linguistic_scores: Dict[str, float] = field(default_factory=dict)
    sentence_counts: Dict[str, int] = field(default_factory=dict)
    
    def combine_scores(self) -> Dict[str, Any]:
        """Combine all scores into a single dictionary."""
        result = self.model_scores.copy()
        
        # Add linguistic scores
        for emotion, score in self.linguistic_scores.items():
            result[f"{emotion}_linguistic"] = score
        
        # Add sentence counts
        for emotion, count in self.sentence_counts.items():
            result[f"{emotion}_sentence_count"] = count
        
        return result
    
    @property
    def dominant_emotion(self) -> Optional[str]:
        """Get the dominant emotion from model scores."""
        if not self.model_scores:
            return None
        return max(self.model_scores, key=self.model_scores.get)

def create_english_emotion_detection_manager(
    config: Optional[EnglishEmotionDetectionConfig] = None
) -> EnglishEmotionDetectionManager:
    """Factory function for EnglishEmotionDetectionManager"""
    return EnglishEmotionDetectionManager(config)


def create_english_emotion_detection_config(**kwargs) -> EnglishEmotionDetectionConfig:
    """Factory function for creating custom configuration"""
    return EnglishEmotionDetectionConfig(**kwargs)


def get_english_emotion_visualization_config() -> EmotionVisualizationConfig:
    """Get visualization configuration for emotions"""
    return EmotionVisualizationConfig()


def validate_english_emotion_detection_config(config: EnglishEmotionDetectionConfig) -> Tuple[bool, List[str]]:
    """Validate emotion detection configuration"""
    errors = []
    
    if not config.validate():
        errors.append("Configuration validation failed")
    
    if config.chunk_size < config.overlap:
        errors.append("Chunk size must be greater than overlap")
    
    if config.linguistic_weight + config.model_weight != 1.0:
        errors.append("Linguistic and model weights must sum to 1.0")
    
    return len(errors) == 0, errors