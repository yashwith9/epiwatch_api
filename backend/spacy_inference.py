"""
spaCy NLP Inference for Disease Classification
"""
import spacy
from pathlib import Path
from typing import Dict, List, Optional
import json

class SpacyDiseaseClassifier:
    """Disease classification using trained spaCy model"""
    
    def __init__(self, model_path: str = "nlp/models/spacy_disease_classifier"):
        """Initialize the spaCy model"""
        self.model_path = Path(model_path)
        self.nlp = None
        self.categories = []
        self._load_model()
    
    def _load_model(self):
        """Load the trained spaCy model"""
        try:
            # Try to load from local path
            if self.model_path.exists():
                print(f"Loading spaCy model from: {self.model_path}")
                self.nlp = spacy.load(self.model_path)
                
                # Load categories
                cat_file = self.model_path / "categories.json"
                if cat_file.exists():
                    with open(cat_file, 'r') as f:
                        self.categories = json.load(f)
                else:
                    # Get categories from model
                    self.categories = list(self.nlp.get_pipe("textcat").labels)
                
                print(f"✓ Model loaded successfully with {len(self.categories)} categories")
            else:
                raise FileNotFoundError(f"Model not found at {self.model_path}")
                
        except Exception as e:
            print(f"✗ Error loading spaCy model: {e}")
            print("Please train the model first by running: python nlp/train_spacy_model.py")
            raise RuntimeError(
                "spaCy model not found. Please train the model first or provide model path."
            )
    
    def predict(self, text: str, top_k: int = 3) -> Dict:
        """
        Predict disease category for given text
        
        Args:
            text: Input text (e.g., "Kenya - Africa")
            top_k: Number of top predictions to return
            
        Returns:
            Dictionary with prediction results
        """
        if not self.nlp:
            raise RuntimeError("Model not loaded")
        
        # Get prediction
        doc = self.nlp(text)
        
        # Sort predictions by confidence
        sorted_cats = sorted(doc.cats.items(), key=lambda x: x[1], reverse=True)
        
        # Get top prediction
        top_disease = sorted_cats[0][0]
        top_confidence = sorted_cats[0][1]
        
        # Get top-k predictions
        top_k_predictions = [
            {"disease": disease, "confidence": float(confidence)}
            for disease, confidence in sorted_cats[:top_k]
        ]
        
        return {
            "text": text,
            "predicted_disease": top_disease,
            "confidence": float(top_confidence),
            "top_predictions": top_k_predictions
        }
    
    def predict_country_region(self, country: str, who_region: str, top_k: int = 3) -> Dict:
        """
        Predict disease for a country-region pair
        
        Args:
            country: Country name
            who_region: WHO region
            top_k: Number of top predictions
            
        Returns:
            Prediction results
        """
        text = f"{country} - {who_region}"
        return self.predict(text, top_k)
    
    def batch_predict(self, texts: List[str], top_k: int = 3) -> List[Dict]:
        """
        Predict for multiple texts at once
        
        Args:
            texts: List of input texts
            top_k: Number of top predictions per text
            
        Returns:
            List of prediction results
        """
        return [self.predict(text, top_k) for text in texts]


# Singleton instance
_classifier_instance: Optional[SpacyDiseaseClassifier] = None

def get_classifier() -> SpacyDiseaseClassifier:
    """Get or create the classifier instance (singleton pattern)"""
    global _classifier_instance
    
    if _classifier_instance is None:
        try:
            _classifier_instance = SpacyDiseaseClassifier()
        except Exception as e:
            print(f"Failed to initialize classifier: {e}")
            raise
    
    return _classifier_instance
