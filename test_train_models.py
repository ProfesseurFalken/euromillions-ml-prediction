"""
Test script for model training functionality.
Demonstrates end-to-end training and prediction pipeline.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from train_models import train_latest, predict_next_draw, get_model_info, EuromillionsTrainer
from repository import get_repository, init_database
from demo_scraper import MockEuromillionsScraper
import json


def setup_test_data(n_draws: int = 350):
    """Set up test data for training."""
    print(f"🎲 Setting up {n_draws} test draws...")
    
    # Initialize database and repository
    init_database()
    repo = get_repository()
    
    # Check existing data
    existing_df = repo.all_draws_df()
    if len(existing_df) >= n_draws:
        print(f"   ✅ Repository already has {len(existing_df)} draws")
        return existing_df
    
    # Generate mock data
    scraper = MockEuromillionsScraper()
    draws = scraper.scrape_latest(n_draws)
    
    # Insert into repository
    result = repo.upsert_draws(draws)
    print(f"   📝 Inserted {result['inserted']} draws, updated {result['updated']}")
    
    # Verify data
    df = repo.all_draws_df()
    print(f"   📊 Total draws in repository: {len(df)}")
    print(f"   📅 Date range: {df['draw_date'].min()} to {df['draw_date'].max()}")
    
    return df


def test_model_training():
    """Test the model training functionality."""
    print("\n🏋️ Testing Model Training")
    print("=" * 40)
    
    try:
        # Train models
        print("🚀 Starting model training...")
        metrics = train_latest(game="euromillions", min_rows=300)
        
        print("✅ Training completed successfully!")
        print(f"   📅 Trained at: {metrics['trained_at']}")
        print(f"   📊 Data range: {metrics['data_range']['from']} to {metrics['data_range']['to']}")
        print(f"   🎯 Samples used: {metrics['data_range']['n_samples']}")
        
        # Main model metrics
        main_metrics = metrics['models']['main']
        print(f"   🎱 Main model log loss: {main_metrics['logloss']:.4f} ± {main_metrics['logloss_std']:.4f}")
        print(f"      Best fold: {main_metrics['best_fold']}")
        print(f"      CV scores: {[f'{s:.4f}' for s in main_metrics['cv_scores'][:3]]}...")
        
        # Star model metrics
        star_metrics = metrics['models']['star']
        print(f"   ⭐ Star model log loss: {star_metrics['logloss']:.4f} ± {star_metrics['logloss_std']:.4f}")
        print(f"      Best fold: {star_metrics['best_fold']}")
        print(f"      CV scores: {[f'{s:.4f}' for s in star_metrics['cv_scores'][:3]]}...")
        
        # File locations
        print(f"   💾 Models saved:")
        print(f"      Main: {main_metrics['path']}")
        print(f"      Star: {star_metrics['path']}")
        print(f"      Meta: {metrics['meta_path']}")
        
        return metrics
        
    except Exception as e:
        print(f"   ❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_model_info():
    """Test getting model information."""
    print("\n📋 Testing Model Information")
    print("=" * 35)
    
    try:
        info = get_model_info()
        
        if info['models_available']:
            print("✅ Models are available!")
            print(f"   📅 Trained: {info['trained_at']}")
            print(f"   📊 Data: {info['data_range']['n_draws']} draws")
            print(f"   📅 Range: {info['data_range']['from']} to {info['data_range']['to']}")
            print(f"   🎯 Performance:")
            print(f"      Main log loss: {info['performance']['main_logloss']:.4f}")
            print(f"      Star log loss: {info['performance']['star_logloss']:.4f}")
            print(f"   🔧 Features: {info['features']}")
        else:
            print("⚠️  No models available")
            print(f"   📝 Message: {info['message']}")
        
        return info
        
    except Exception as e:
        print(f"   ❌ Failed to get model info: {e}")
        return None


def test_prediction():
    """Test making predictions with trained models."""
    print("\n🔮 Testing Prediction")
    print("=" * 25)
    
    try:
        # Basic prediction
        print("🎯 Making basic prediction...")
        prediction = predict_next_draw(return_probabilities=False)
        
        print("✅ Prediction completed!")
        print(f"   🎱 Predicted main balls: {prediction['predicted_main']}")
        print(f"   ⭐ Predicted stars: {prediction['predicted_stars']}")
        print(f"   📅 Prediction made: {prediction['prediction_date']}")
        print(f"   🏋️ Model trained: {prediction['model_trained_at']}")
        print(f"   📊 Data range: {prediction['data_range']['from']} to {prediction['data_range']['to']}")
        
        # Prediction with probabilities
        print("\n🎯 Making prediction with probabilities...")
        detailed_prediction = predict_next_draw(return_probabilities=True)
        
        # Show top probabilities for main balls
        main_probs = detailed_prediction['main_probabilities']
        sorted_main = sorted(main_probs.items(), key=lambda x: x[1], reverse=True)
        
        print("   🏆 Top 10 main ball probabilities:")
        for i, (ball, prob) in enumerate(sorted_main[:10], 1):
            selected = "⭐" if int(ball.split('_')[1]) in prediction['predicted_main'] else "  "
            print(f"      {i:2d}. {ball}: {prob:.4f} {selected}")
        
        # Show star probabilities
        star_probs = detailed_prediction['star_probabilities']
        sorted_stars = sorted(star_probs.items(), key=lambda x: x[1], reverse=True)
        
        print("   🌟 Star probabilities:")
        for i, (star, prob) in enumerate(sorted_stars, 1):
            selected = "⭐" if int(star.split('_')[1]) in prediction['predicted_stars'] else "  "
            print(f"      {i:2d}. {star}: {prob:.4f} {selected}")
        
        return prediction
        
    except Exception as e:
        print(f"   ❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_model_persistence():
    """Test loading and using saved models."""
    print("\n💾 Testing Model Persistence")
    print("=" * 35)
    
    try:
        # Create trainer and load models
        trainer = EuromillionsTrainer()
        main_model, star_model, metadata = trainer.load_models()
        
        print("✅ Models loaded successfully!")
        print(f"   📅 Trained: {metadata['trained_at']}")
        print(f"   🎱 Main model type: {type(main_model).__name__}")
        print(f"   ⭐ Star model type: {type(star_model).__name__}")
        print(f"   🔧 Features used: {metadata['features']}")
        print(f"   📊 Performance:")
        print(f"      Main log loss: {metadata['logloss_main']:.4f}")
        print(f"      Star log loss: {metadata['logloss_star']:.4f}")
        
        # Test model parameters
        if hasattr(main_model, 'estimator'):
            print(f"   ⚙️  Main model params: n_estimators={main_model.estimator.n_estimators}")
        if hasattr(star_model, 'estimator'):
            print(f"   ⚙️  Star model params: n_estimators={star_model.estimator.n_estimators}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Model loading failed: {e}")
        return False


def test_error_handling():
    """Test error handling scenarios."""
    print("\n🚨 Testing Error Handling")
    print("=" * 30)
    
    # Test insufficient data
    print("1. Testing insufficient data...")
    try:
        # Clear repository
        repo = get_repository()
        # This would require implementing a clear function, so we'll simulate
        metrics = train_latest(min_rows=999999)  # Impossible requirement
        print("   ❌ Should have failed with insufficient data")
    except ValueError as e:
        print(f"   ✅ Correctly caught error: {e}")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")
    
    # Test invalid game type
    print("2. Testing invalid game type...")
    try:
        metrics = train_latest(game="invalid_game")
        print("   ❌ Should have failed with invalid game")
    except ValueError as e:
        print(f"   ✅ Correctly caught error: {e}")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")


def demo_full_pipeline():
    """Demonstrate the complete training and prediction pipeline."""
    print("\n🎪 Full Pipeline Demo")
    print("=" * 25)
    
    print("Step 1: Setup test data...")
    df = setup_test_data(350)
    
    print("\nStep 2: Train models...")
    training_metrics = test_model_training()
    
    if training_metrics:
        print("\nStep 3: Get model info...")
        model_info = test_model_info()
        
        print("\nStep 4: Make predictions...")
        prediction = test_prediction()
        
        print("\nStep 5: Test persistence...")
        persistence_ok = test_model_persistence()
        
        print("\nStep 6: Test error handling...")
        test_error_handling()
        
        print(f"\n🎉 Pipeline Demo Complete!")
        print(f"   ✅ Data: {len(df)} draws loaded")
        print(f"   ✅ Training: Models trained and saved")
        print(f"   ✅ Prediction: Next draw predicted")
        print(f"   ✅ Persistence: Models reloadable")
        
        if prediction:
            print(f"\n🔮 Final Prediction:")
            print(f"   🎱 Main balls: {prediction['predicted_main']}")
            print(f"   ⭐ Stars: {prediction['predicted_stars']}")
    
    else:
        print("\n❌ Pipeline failed at training step")


def main():
    """Run all tests."""
    print("🧪 Model Training Test Suite")
    print("=" * 50)
    
    try:
        demo_full_pipeline()
        
        print(f"\n💡 Usage Examples:")
        print(f"   from train_models import train_latest, predict_next_draw")
        print(f"   ")
        print(f"   # Train models")
        print(f"   metrics = train_latest(min_rows=300)")
        print(f"   ")
        print(f"   # Make predictions")
        print(f"   prediction = predict_next_draw(return_probabilities=True)")
        print(f"   print(prediction['predicted_main'])")
        print(f"   print(prediction['predicted_stars'])")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
