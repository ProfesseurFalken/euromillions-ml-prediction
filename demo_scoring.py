#!/usr/bin/env python3
"""
Quick demo of the scoring and suggestion functionality.
Creates a simple demo model to showcase the scoring API.
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import get_settings
from repository import get_repository, init_database
from scraper import EuromillionsScraper
from train_models import EuromillionsTrainer


def create_demo_model():
    """Create a very simple demo model for testing scoring functionality."""
    print("🎯 Creating Demo Model for Scoring")
    print("=" * 40)
    
    # Initialize
    settings = get_settings()
    init_database()
    repo = get_repository()
    
    # Add minimal data if needed
    df = repo.all_draws_df()
    if df.empty or len(df) < 50:
        print(f"📝 Adding demo data...")
        scraper = EuromillionsScraper()
        draws = scraper.scrape_latest(50)  # Just 50 draws for quick demo
        repo.add_draws(draws)
        df = repo.all_draws_df()
    
    print(f"📊 Using {len(df)} draws for demo")
    
    # Create trainer
    trainer = EuromillionsTrainer()
    
    # Create simple dummy models
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    
    # Ensure model directory exists
    model_dir = settings.models_path
    model_dir.mkdir(parents=True, exist_ok=True)
    
    print("🤖 Creating simple demo models...")
    
    # Create dummy main model (simplified)
    main_model = RandomForestClassifier(n_estimators=10, random_state=42)
    # Create simple training data (just use random features for demo)
    X_dummy = np.random.random((len(df), 50))
    y_dummy = np.random.randint(0, 2, (len(df), 50))  # Binary targets for each ball
    
    main_model.fit(X_dummy, y_dummy)
    
    # Create dummy star model
    star_model = RandomForestClassifier(n_estimators=10, random_state=42)
    X_star_dummy = np.random.random((len(df), 24))
    y_star_dummy = np.random.randint(0, 2, (len(df), 12))  # Binary targets for each star
    
    star_model.fit(X_star_dummy, y_star_dummy)
    
    # Save models
    joblib.dump(main_model, model_dir / "main_model.pkl")
    joblib.dump(star_model, model_dir / "star_model.pkl")
    
    # Create model info file
    model_info = {
        "trained_at": "2025-09-04T19:00:00",
        "models_available": True,
        "performance": {
            "main_logloss": 0.693,  # Random baseline
            "star_logloss": 0.693,
            "cv_details": {
                "main_mean": 0.693,
                "main_std": 0.05,
                "star_mean": 0.693,
                "star_std": 0.05
            }
        },
        "model_files": ["main_model.pkl", "star_model.pkl"]
    }
    
    import json
    with open(model_dir / "model_info.json", "w") as f:
        json.dump(model_info, f, indent=2)
    
    print("✅ Demo models created!")
    return trainer


def demo_scoring():
    """Demonstrate the scoring functionality."""
    print("\n🎯 Demo: Ball & Star Scoring")
    print("=" * 35)
    
    trainer = create_demo_model()
    
    try:
        # Load models
        trainer.load_models()
        print("✅ Models loaded")
        
        # Score balls
        print("\n🎱 Scoring main balls...")
        ball_scores = trainer.score_balls()
        print(f"✅ Got scores for {len(ball_scores)} balls")
        
        # Show top 10 balls
        sorted_balls = sorted(ball_scores, key=lambda x: x[1], reverse=True)
        print("\n🏆 Top 10 Main Balls:")
        for i, (ball, prob) in enumerate(sorted_balls[:10], 1):
            print(f"   {i:2d}. Ball {ball:2d}: {prob:.4f} ({prob*100:.1f}%)")
        
        # Score stars
        print("\n⭐ Scoring stars...")
        star_scores = trainer.score_stars()
        print(f"✅ Got scores for {len(star_scores)} stars")
        
        # Show top 5 stars
        sorted_stars = sorted(star_scores, key=lambda x: x[1], reverse=True)
        print("\n🌟 Top 5 Stars:")
        for i, (star, prob) in enumerate(sorted_stars[:5], 1):
            print(f"   {i:2d}. Star {star:2d}: {prob:.4f} ({prob*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Scoring failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_suggestions():
    """Demonstrate the combination suggestions."""
    print("\n🎲 Demo: Combination Suggestions")
    print("=" * 40)
    
    trainer = EuromillionsTrainer()
    
    try:
        trainer.load_models()
        
        # Test different methods
        methods = ["topk", "random", "hybrid"]
        
        for method in methods:
            print(f"\n📝 Method: {method.upper()}")
            print("-" * 20)
            
            combinations = trainer.suggest_combinations(k=3, method=method, seed=42)
            
            for i, combo in enumerate(combinations, 1):
                balls = combo[:5]
                stars = combo[5:]
                balls_str = "-".join(f"{b:2d}" for b in sorted(balls))
                stars_str = "-".join(f"{s:2d}" for s in sorted(stars))
                
                print(f"   {i}. [{balls_str}] + [{stars_str}]")
        
        return True
        
    except Exception as e:
        print(f"❌ Suggestions failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def demo_cli_commands():
    """Demonstrate CLI commands."""
    print("\n💻 Demo: CLI Commands")
    print("=" * 25)
    
    print("✅ Demo models created. You can now try:")
    print()
    print("📊 Scoring commands:")
    print("   .\\venv\\Scripts\\activate; python cli_train.py score --top 15")
    print("   .\\venv\\Scripts\\activate; python cli_train.py score --all")
    print()
    print("🎲 Suggestion commands:")
    print("   .\\venv\\Scripts\\activate; python cli_train.py suggest --count 5")
    print("   .\\venv\\Scripts\\activate; python cli_train.py suggest --method topk --count 3")
    print("   .\\venv\\Scripts\\activate; python cli_train.py suggest --method random --probabilities")
    print()
    print("ℹ️  Information commands:")
    print("   .\\venv\\Scripts\\activate; python cli_train.py info")
    print("   .\\venv\\Scripts\\activate; python cli_train.py status")


def main():
    """Run the scoring demo."""
    print("🚀 Euromillions Scoring & Suggestions Demo")
    print("=" * 50)
    
    # Demo scoring
    scoring_success = demo_scoring()
    
    if scoring_success:
        # Demo suggestions
        suggestions_success = demo_suggestions()
        
        if suggestions_success:
            # Show CLI commands
            demo_cli_commands()
            
            print("\n🎉 Demo completed successfully!")
            print("   All scoring and suggestion functionality is working.")
        else:
            print("\n⚠️  Scoring works, but suggestions had issues.")
    else:
        print("\n❌ Demo failed. Check the error messages above.")


if __name__ == "__main__":
    main()
