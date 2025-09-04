"""
Test script for scoring and combination suggestion functionality.
Demonstrates ball/star scoring and different combination generation methods.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from train_models import (
    load_models, score_balls, score_stars, suggest_combinations, 
    train_latest, EuromillionsTrainer
)
from repository import get_repository, init_database
from demo_scraper import MockEuromillionsScraper
import json


def setup_test_environment():
    """Set up test environment with models and data."""
    print("🔧 Setting up test environment...")
    
    # Initialize database
    init_database()
    repo = get_repository()
    
    # Check if we have sufficient data
    df = repo.all_draws_df()
    if len(df) < 300:
        print(f"   📝 Adding demo data (current: {len(df)} draws)...")
        scraper = MockEuromillionsScraper()
        draws = scraper.scrape_latest(350)
        result = repo.upsert_draws(draws)
        print(f"   ✅ Added {result['inserted']} draws")
        df = repo.all_draws_df()
    
    # Check if models exist
    try:
        load_models()
        print("   ✅ Models already available")
        return True
    except FileNotFoundError:
        print("   🏋️ Training models...")
        try:
            metrics = train_latest(min_rows=250)
            print(f"   ✅ Models trained (main: {metrics['models']['main']['logloss']:.4f})")
            return True
        except Exception as e:
            print(f"   ❌ Training failed: {e}")
            return False


def test_model_loading():
    """Test model loading with caching."""
    print("\n💾 Testing Model Loading")
    print("=" * 30)
    
    trainer = EuromillionsTrainer()
    
    # First load (from disk)
    print("1. Loading models from disk...")
    try:
        main_model, star_model, metadata = trainer.load_models(force=True)
        print("   ✅ Models loaded successfully")
        print(f"   📅 Trained: {metadata['trained_at']}")
        print(f"   🎯 Main loss: {metadata['logloss_main']:.4f}")
        print(f"   ⭐ Star loss: {metadata['logloss_star']:.4f}")
    except Exception as e:
        print(f"   ❌ Loading failed: {e}")
        return False
    
    # Second load (from cache)
    print("\n2. Loading models from cache...")
    try:
        main_model2, star_model2, metadata2 = trainer.load_models(force=False)
        print("   ✅ Models loaded from cache")
        print(f"   🔗 Same main model: {main_model is main_model2}")
        print(f"   🔗 Same star model: {star_model is star_model2}")
        print(f"   🔗 Same metadata: {metadata is metadata2}")
    except Exception as e:
        print(f"   ❌ Cache loading failed: {e}")
        return False
    
    return True


def test_ball_scoring():
    """Test main ball scoring functionality."""
    print("\n🎱 Testing Ball Scoring")
    print("=" * 25)
    
    try:
        ball_scores = score_balls()
        
        print("✅ Ball scoring completed!")
        print(f"   📊 Total balls scored: {len(ball_scores)}")
        
        # Verify structure
        if len(ball_scores) != 50:
            print(f"   ❌ Expected 50 balls, got {len(ball_scores)}")
            return False
        
        # Check ball numbers and probabilities
        ball_numbers = [ball for ball, prob in ball_scores]
        probabilities = [prob for ball, prob in ball_scores]
        
        if ball_numbers != list(range(1, 51)):
            print(f"   ❌ Ball numbers not 1-50: {ball_numbers[:5]}...")
            return False
        
        if not all(0 <= prob <= 1 for prob in probabilities):
            print(f"   ❌ Probabilities not in [0,1]: {probabilities[:5]}...")
            return False
        
        # Show top and bottom balls
        sorted_balls = sorted(ball_scores, key=lambda x: x[1], reverse=True)
        
        print(f"   🏆 Top 10 balls by probability:")
        for i, (ball, prob) in enumerate(sorted_balls[:10], 1):
            print(f"      {i:2d}. Ball {ball:2d}: {prob:.4f}")
        
        print(f"   🔻 Bottom 5 balls by probability:")
        for i, (ball, prob) in enumerate(sorted_balls[-5:], 46):
            print(f"      {i:2d}. Ball {ball:2d}: {prob:.4f}")
        
        # Statistics
        avg_prob = sum(probabilities) / len(probabilities)
        max_prob = max(probabilities)
        min_prob = min(probabilities)
        
        print(f"   📈 Statistics:")
        print(f"      Average: {avg_prob:.4f}")
        print(f"      Range: {min_prob:.4f} - {max_prob:.4f}")
        print(f"      Expected avg: ~{5/50:.4f} (5 balls out of 50)")
        
        return ball_scores
        
    except Exception as e:
        print(f"   ❌ Ball scoring failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_star_scoring():
    """Test star scoring functionality."""
    print("\n⭐ Testing Star Scoring")
    print("=" * 25)
    
    try:
        star_scores = score_stars()
        
        print("✅ Star scoring completed!")
        print(f"   📊 Total stars scored: {len(star_scores)}")
        
        # Verify structure
        if len(star_scores) != 12:
            print(f"   ❌ Expected 12 stars, got {len(star_scores)}")
            return False
        
        # Check star numbers and probabilities
        star_numbers = [star for star, prob in star_scores]
        probabilities = [prob for star, prob in star_scores]
        
        if star_numbers != list(range(1, 13)):
            print(f"   ❌ Star numbers not 1-12: {star_numbers}")
            return False
        
        if not all(0 <= prob <= 1 for prob in probabilities):
            print(f"   ❌ Probabilities not in [0,1]: {probabilities}")
            return False
        
        # Show all stars sorted by probability
        sorted_stars = sorted(star_scores, key=lambda x: x[1], reverse=True)
        
        print(f"   🌟 All stars by probability:")
        for i, (star, prob) in enumerate(sorted_stars, 1):
            print(f"      {i:2d}. Star {star:2d}: {prob:.4f}")
        
        # Statistics
        avg_prob = sum(probabilities) / len(probabilities)
        max_prob = max(probabilities)
        min_prob = min(probabilities)
        
        print(f"   📈 Statistics:")
        print(f"      Average: {avg_prob:.4f}")
        print(f"      Range: {min_prob:.4f} - {max_prob:.4f}")
        print(f"      Expected avg: ~{2/12:.4f} (2 stars out of 12)")
        
        return star_scores
        
    except Exception as e:
        print(f"   ❌ Star scoring failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_combination_suggestions():
    """Test different combination suggestion methods."""
    print("\n🎯 Testing Combination Suggestions")
    print("=" * 40)
    
    methods = ["topk", "random", "hybrid"]
    
    for method in methods:
        print(f"\n📋 Testing {method.upper()} method:")
        
        try:
            combinations = suggest_combinations(k=5, method=method, seed=42)
            
            print(f"   ✅ Generated {len(combinations)} combinations")
            
            # Verify structure
            for i, combo in enumerate(combinations, 1):
                balls = combo["balls"]
                stars = combo["stars"]
                score = combo["combined_score"]
                
                # Validate structure
                if len(balls) != 5 or len(stars) != 2:
                    print(f"   ❌ Invalid combination {i}: {len(balls)} balls, {len(stars)} stars")
                    continue
                
                if not all(1 <= ball <= 50 for ball in balls):
                    print(f"   ❌ Invalid ball range in combination {i}: {balls}")
                    continue
                
                if not all(1 <= star <= 12 for star in stars):
                    print(f"   ❌ Invalid star range in combination {i}: {stars}")
                    continue
                
                if balls != sorted(balls) or stars != sorted(stars):
                    print(f"   ❌ Combination {i} not sorted: balls={balls}, stars={stars}")
                    continue
                
                print(f"      {i}. {'-'.join(map(str, balls))} + {'-'.join(map(str, stars))} (score: {score:.4f})")
            
            # Check for duplicates
            combo_strs = []
            for combo in combinations:
                combo_str = f"{combo['balls']}-{combo['stars']}"
                combo_strs.append(combo_str)
            
            if len(set(combo_strs)) != len(combo_strs):
                print(f"   ⚠️  Warning: Duplicate combinations found")
            else:
                print(f"   ✅ All combinations unique")
                
        except Exception as e:
            print(f"   ❌ {method} method failed: {e}")
            import traceback
            traceback.print_exc()


def test_scores_file():
    """Test that scores are saved to JSON file."""
    print("\n💾 Testing Scores File Generation")
    print("=" * 35)
    
    try:
        # Generate combinations to trigger score saving
        combinations = suggest_combinations(k=3, method="hybrid", seed=123)
        
        # Check if file was created
        scores_file = Path("models/euromillions/latest_scores.json")
        
        if not scores_file.exists():
            print("   ❌ Scores file not created")
            return False
        
        # Load and validate file content
        with open(scores_file, 'r') as f:
            scores_data = json.load(f)
        
        print("   ✅ Scores file created successfully")
        print(f"   📅 Scored at: {scores_data['scored_at']}")
        
        # Validate structure
        required_keys = ["ball_scores", "star_scores", "top_balls", "top_stars", "combinations", "statistics"]
        for key in required_keys:
            if key not in scores_data:
                print(f"   ❌ Missing key in scores file: {key}")
                return False
        
        print(f"   📊 File contains:")
        print(f"      🎱 Ball scores: {len(scores_data['ball_scores'])}")
        print(f"      ⭐ Star scores: {len(scores_data['star_scores'])}")
        print(f"      🏆 Top balls: {len(scores_data['top_balls'])}")
        print(f"      🌟 Top stars: {len(scores_data['top_stars'])}")
        print(f"      🎯 Combinations: {len(scores_data['combinations'])}")
        
        # Show top balls and stars from file
        print(f"   🏆 Top 5 balls from file:")
        for i, (ball, prob) in enumerate(scores_data['top_balls'][:5], 1):
            print(f"      {i}. Ball {ball}: {prob:.4f}")
        
        print(f"   🌟 Top 3 stars from file:")
        for i, (star, prob) in enumerate(scores_data['top_stars'][:3], 1):
            print(f"      {i}. Star {star}: {prob:.4f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Scores file test failed: {e}")
        return False


def demo_practical_usage():
    """Demonstrate practical usage scenarios."""
    print("\n🎪 Practical Usage Demo")
    print("=" * 25)
    
    print("Scenario 1: Quick prediction for next draw")
    try:
        combinations = suggest_combinations(k=1, method="topk", seed=42)
        combo = combinations[0]
        print(f"   🎯 Best prediction: {'-'.join(map(str, combo['balls']))} + {'-'.join(map(str, combo['stars']))}")
        print(f"   📈 Confidence score: {combo['combined_score']:.4f}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\nScenario 2: Multiple ticket strategy")
    try:
        combinations = suggest_combinations(k=5, method="hybrid", seed=42)
        print(f"   🎫 Generated {len(combinations)} diverse tickets:")
        for i, combo in enumerate(combinations, 1):
            print(f"      Ticket {i}: {'-'.join(map(str, combo['balls']))} + {'-'.join(map(str, combo['stars']))} (score: {combo['combined_score']:.3f})")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\nScenario 3: Risk analysis")
    try:
        ball_scores = score_balls()
        star_scores = score_stars()
        
        # Find most and least likely numbers
        sorted_balls = sorted(ball_scores, key=lambda x: x[1], reverse=True)
        sorted_stars = sorted(star_scores, key=lambda x: x[1], reverse=True)
        
        hot_balls = [ball for ball, _ in sorted_balls[:10]]
        cold_balls = [ball for ball, _ in sorted_balls[-10:]]
        hot_stars = [star for star, _ in sorted_stars[:3]]
        cold_stars = [star for star, _ in sorted_stars[-3:]]
        
        print(f"   🔥 Hot balls (top 10): {hot_balls}")
        print(f"   🧊 Cold balls (bottom 10): {cold_balls}")
        print(f"   🔥 Hot stars (top 3): {hot_stars}")
        print(f"   🧊 Cold stars (bottom 3): {cold_stars}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")


def main():
    """Run all scoring tests."""
    print("🧪 Scoring & Suggestions Test Suite")
    print("=" * 50)
    
    # Setup
    if not setup_test_environment():
        print("❌ Setup failed, aborting tests")
        return
    
    # Run tests
    print("\n" + "="*50)
    
    # Test model loading
    if not test_model_loading():
        print("❌ Model loading failed, aborting further tests")
        return
    
    # Test scoring
    ball_scores = test_ball_scoring()
    if ball_scores is None:
        print("❌ Ball scoring failed")
        return
    
    star_scores = test_star_scoring()
    if star_scores is None:
        print("❌ Star scoring failed")
        return
    
    # Test suggestions
    test_combination_suggestions()
    
    # Test file output
    test_scores_file()
    
    # Demo practical usage
    demo_practical_usage()
    
    print(f"\n🎉 All tests completed!")
    print(f"\n💡 Usage examples:")
    print(f"   from train_models import score_balls, score_stars, suggest_combinations")
    print(f"   ")
    print(f"   # Get ball/star probabilities")
    print(f"   balls = score_balls()  # [(1, 0.123), (2, 0.456), ...]")
    print(f"   stars = score_stars()  # [(1, 0.234), (2, 0.567), ...]")
    print(f"   ")
    print(f"   # Generate combinations")
    print(f"   combos = suggest_combinations(k=10, method='hybrid')")
    print(f"   print(combos[0]['balls'])  # [7, 15, 23, 31, 45]")
    print(f"   print(combos[0]['stars'])  # [3, 8]")


if __name__ == "__main__":
    main()
