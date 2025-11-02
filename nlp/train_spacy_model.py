"""
Train a spaCy text classification model for disease outbreak prediction
"""
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import pandas as pd
import random
from pathlib import Path
import json

def load_disease_data(csv_path: str = "results/disease_country_year_aggregates.csv"):
    """Load and prepare disease outbreak data"""
    df = pd.read_csv(csv_path)
    
    # Create text from Country and WHO region (if columns exist)
    if 'Country' in df.columns and 'who_region' in df.columns:
        df['text'] = df['Country'].astype(str) + " - " + df['who_region'].astype(str)
        disease_col = 'Disease'
    else:
        # Handle different column names
        print("Available columns:", df.columns.tolist())
        raise ValueError("Expected columns 'Country', 'who_region', and 'Disease'")
    
    # Get unique diseases as categories
    diseases = df[disease_col].unique().tolist()
    
    # Create training data in spaCy format
    train_data = []
    for _, row in df.iterrows():
        text = row['text']
        disease = row[disease_col]
        
        # spaCy format: (text, {"cats": {label: 1.0 or 0.0}})
        cats = {d: 1.0 if d == disease else 0.0 for d in diseases}
        train_data.append((text, {"cats": cats}))
    
    return train_data, diseases

def create_spacy_model(train_data, categories, n_iter=20):
    """Create and train spaCy text classification model"""
    
    # Create blank English model
    nlp = spacy.blank("en")
    
    # Add text classifier to pipeline
    textcat = nlp.add_pipe("textcat", last=True)
    
    # Add labels to text classifier
    for cat in categories:
        textcat.add_label(cat)
    
    # Train the model
    print(f"Training spaCy model with {len(categories)} disease categories...")
    print(f"Training examples: {len(train_data)}")
    
    # Disable other pipeline components during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "textcat"]
    
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
        
        for iteration in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            
            # Batch the examples
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            
            for batch in batches:
                texts, annotations = zip(*batch)
                examples = []
                for text, annot in zip(texts, annotations):
                    doc = nlp.make_doc(text)
                    example = Example.from_dict(doc, annot)
                    examples.append(example)
                
                nlp.update(examples, drop=0.2, losses=losses, sgd=optimizer)
            
            print(f"Iteration {iteration + 1}/{n_iter} - Loss: {losses['textcat']:.4f}")
    
    return nlp

def evaluate_model(nlp, test_data):
    """Evaluate the trained model"""
    correct = 0
    total = 0
    
    for text, annotations in test_data:
        doc = nlp(text)
        predicted = max(doc.cats.items(), key=lambda x: x[1])[0]
        true_label = max(annotations['cats'].items(), key=lambda x: x[1])[0]
        
        if predicted == true_label:
            correct += 1
        total += 1
    
    accuracy = correct / total if total > 0 else 0
    print(f"\nModel Accuracy: {accuracy:.4f} ({correct}/{total})")
    return accuracy

def save_model(nlp, output_dir="nlp/models/spacy_disease_classifier"):
    """Save the trained model"""
    output_path = Path(output_dir)
    nlp.to_disk(output_path)
    print(f"\nModel saved to: {output_path}")
    
    # Save category list for reference
    categories = list(nlp.get_pipe("textcat").labels)
    with open(output_path / "categories.json", "w") as f:
        json.dump(categories, f, indent=2)

def main():
    """Main training function"""
    print("="*60)
    print("spaCy Disease Classification Model Training")
    print("="*60)
    
    # Load data
    print("\n1. Loading data...")
    train_data, categories = load_disease_data()
    
    # Split into train/test (80/20)
    random.shuffle(train_data)
    split_idx = int(len(train_data) * 0.8)
    train_set = train_data[:split_idx]
    test_set = train_data[split_idx:]
    
    print(f"   Training samples: {len(train_set)}")
    print(f"   Test samples: {len(test_set)}")
    print(f"   Disease categories: {len(categories)}")
    
    # Train model
    print("\n2. Training model...")
    nlp = create_spacy_model(train_set, categories, n_iter=20)
    
    # Evaluate
    print("\n3. Evaluating model...")
    accuracy = evaluate_model(nlp, test_set)
    
    # Save
    print("\n4. Saving model...")
    save_model(nlp)
    
    # Test predictions
    print("\n5. Testing predictions...")
    test_examples = [
        "Kenya - Africa",
        "United States - Americas",
        "India - South-East Asia",
        "Brazil - Americas"
    ]
    
    for text in test_examples:
        doc = nlp(text)
        top_prediction = max(doc.cats.items(), key=lambda x: x[1])
        print(f"   Input: '{text}'")
        print(f"   Predicted: {top_prediction[0]} (confidence: {top_prediction[1]:.4f})")
    
    print("\n" + "="*60)
    print("Training complete!")
    print("="*60)

if __name__ == "__main__":
    main()
