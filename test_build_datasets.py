"""
Test script for dataset building functionality.
Demonstrates feature engineering for machine learning.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from build_datasets import (
    build_datasets, build_enhanced_datasets, get_feature_statistics,
    analyze_label_distribution, split_datasets
)
from repository import get_repository, init_database
from demo_scraper import MockEuromillionsScraper
import pandas as pd
import numpy as np


def create_sample_data(n_draws: int = 150) -> pd.DataFrame:
    """Create sample data for testing."""
    print(f"🎲 Creating {n_draws} sample draws...")
    
    # Use mock scraper to generate realistic test data
    scraper = MockEuromillionsScraper()
    draws = scraper.scrape_latest(n_draws)
    
    # Convert to DataFrame format expected by build_datasets
    df_data = []
    for draw in draws:
        df_data.append({
            'draw_id': draw['draw_id'],
            'draw_date': draw['draw_date'],
            'n1': draw['n1'],
            'n2': draw['n2'],
            'n3': draw['n3'],
            'n4': draw['n4'],
            'n5': draw['n5'],
            's1': draw['s1'],
            's2': draw['s2'],
            'jackpot': draw['jackpot'],
            'prize_table_json': str(draw['prize_table_json'])
        })
    
    df = pd.DataFrame(df_data)
    df['draw_date'] = pd.to_datetime(df['draw_date'])
    df = df.sort_values('draw_date').reset_index(drop=True)
    
    print(f"   📊 Created DataFrame with {len(df)} draws")
    print(f"   📅 Date range: {df['draw_date'].min()} to {df['draw_date'].max()}")
    
    return df


def test_basic_dataset_building():
    """Test basic dataset building functionality."""
    print("\n🏗️ Testing Basic Dataset Building")
    print("=" * 50)
    
    # Create sample data
    df = create_sample_data(120)  # 120 draws for good window coverage
    
    # Build datasets
    print(f"\n📊 Building datasets with window size 50...")
    X_main, y_main, X_star, y_star, meta = build_datasets(df, window_size=50)
    
    # Display results
    print(f"✅ Dataset building completed!")
    print(f"   📈 X_main shape: {X_main.shape}")
    print(f"   📈 y_main shape: {y_main.shape}")
    print(f"   ⭐ X_star shape: {X_star.shape}")
    print(f"   ⭐ y_star shape: {y_star.shape}")
    print(f"   📅 Date range: {meta['data_from']} to {meta['data_to']}")
    print(f"   🎯 Total samples: {meta['n_samples']}")
    
    # Analyze feature statistics
    print(f"\n📊 Feature Statistics (Main Balls - First 10):")
    main_stats = get_feature_statistics(X_main, meta['feature_names_main'])
    print(main_stats.head(10).round(4))
    
    print(f"\n📊 Feature Statistics (Stars - First 6):")
    star_stats = get_feature_statistics(X_star, meta['feature_names_star'])
    print(star_stats.head(6).round(4))
    
    # Analyze label distribution
    print(f"\n🎯 Label Distribution Analysis:")
    main_labels = analyze_label_distribution(y_main, "main")
    star_labels = analyze_label_distribution(y_star, "star")
    
    print(f"   🎱 Main balls - Most frequent:")
    most_frequent_main = main_labels.nlargest(5, 'frequency')[['main_number', 'appearances', 'frequency']]
    print(most_frequent_main)
    
    print(f"   ⭐ Stars - Most frequent:")
    most_frequent_star = star_labels.nlargest(3, 'frequency')[['star_number', 'appearances', 'frequency']]
    print(most_frequent_star)
    
    return X_main, y_main, X_star, y_star, meta


def test_enhanced_dataset_building():
    """Test enhanced dataset building with additional features."""
    print("\n🚀 Testing Enhanced Dataset Building")
    print("=" * 50)
    
    df = create_sample_data(150)
    
    print(f"\n📊 Building enhanced datasets...")
    X_main, y_main, X_star, y_star, meta = build_enhanced_datasets(df, window_size=75)
    
    print(f"✅ Enhanced dataset building completed!")
    print(f"   📈 X_main shape: {X_main.shape} (enhanced features)")
    print(f"   📈 y_main shape: {y_main.shape}")
    print(f"   ⭐ X_star shape: {X_star.shape} (enhanced features)")
    print(f"   ⭐ y_star shape: {y_star.shape}")
    print(f"   🎯 Features: {meta['features']}")
    
    # Show sample feature values for first ball
    print(f"\n🔍 Sample Features for Ball #1 (last 5 samples):")
    ball_1_features = X_main[-5:, :4]  # Last 5 samples, first 4 features (ball 1)
    feature_names = ['long_freq', 'gap', 'short_freq', 'streak']
    for i, sample in enumerate(ball_1_features):
        print(f"   Sample {i+1}: {dict(zip(feature_names, sample.round(3)))}")
    
    return X_main, y_main, X_star, y_star, meta


def test_dataset_splitting():
    """Test train/test splitting."""
    print("\n✂️ Testing Dataset Splitting")
    print("=" * 40)
    
    df = create_sample_data(100)
    X_main, y_main, X_star, y_star, meta = build_datasets(df, window_size=30)
    
    # Split datasets
    splits = split_datasets(X_main, y_main, X_star, y_star, train_ratio=0.8)
    X_main_train, X_main_test, y_main_train, y_main_test, X_star_train, X_star_test, y_star_train, y_star_test = splits
    
    print(f"✅ Dataset splitting completed!")
    print(f"   🏋️ Main training: X{X_main_train.shape}, y{y_main_train.shape}")
    print(f"   🧪 Main testing: X{X_main_test.shape}, y{y_main_test.shape}")
    print(f"   🏋️ Star training: X{X_star_train.shape}, y{y_star_train.shape}")
    print(f"   🧪 Star testing: X{X_star_test.shape}, y{y_star_test.shape}")
    
    # Calculate label frequencies in train vs test
    train_main_freq = y_main_train.mean(axis=0).mean()
    test_main_freq = y_main_test.mean(axis=0).mean()
    train_star_freq = y_star_train.mean(axis=0).mean()
    test_star_freq = y_star_test.mean(axis=0).mean()
    
    print(f"   📊 Label frequencies:")
    print(f"      Main balls - Train: {train_main_freq:.3f}, Test: {test_main_freq:.3f}")
    print(f"      Stars - Train: {train_star_freq:.3f}, Test: {test_star_freq:.3f}")


def test_with_real_repository():
    """Test with real repository data if available."""
    print("\n💾 Testing with Repository Integration")
    print("=" * 45)
    
    try:
        # Try to use repository data
        init_database()
        repo = get_repository()
        
        # Check if we have data
        df = repo.all_draws_df()
        
        if df.empty:
            print("   ⚠️  No data in repository, using mock data...")
            # Add some mock data to repository
            scraper = MockEuromillionsScraper()
            draws = scraper.scrape_latest(50)
            result = repo.upsert_draws(draws)
            print(f"   📝 Added {result['inserted']} mock draws to repository")
            df = repo.all_draws_df()
        
        print(f"   📊 Repository has {len(df)} draws")
        
        if len(df) >= 20:  # Need minimum data for meaningful features
            X_main, y_main, X_star, y_star, meta = build_datasets(df, window_size=min(50, len(df)//2))
            
            print(f"   ✅ Built datasets from repository data:")
            print(f"      📈 Samples: {meta['n_samples']}")
            print(f"      📅 Range: {meta['data_from']} to {meta['data_to']}")
            print(f"      🎯 Features per ball: {len(meta['features'])}")
        else:
            print(f"   ⚠️  Not enough data ({len(df)} draws) for meaningful features")
    
    except Exception as e:
        print(f"   ❌ Repository integration failed: {e}")


def demonstrate_feature_interpretation():
    """Demonstrate how to interpret the features."""
    print("\n🧠 Feature Interpretation Guide")
    print("=" * 40)
    
    df = create_sample_data(80)
    X_main, y_main, X_star, y_star, meta = build_datasets(df, window_size=30)
    
    # Show interpretation for a specific example
    sample_idx = -1  # Last sample
    ball_num = 7  # Ball number 7 (index 6)
    ball_idx = ball_num - 1
    
    # Extract features for this ball
    freq_idx = ball_idx * 2  # frequency feature index
    gap_idx = ball_idx * 2 + 1  # gap feature index
    
    frequency = X_main[sample_idx, freq_idx]
    gap = X_main[sample_idx, gap_idx]
    label = y_main[sample_idx, ball_idx]
    
    print(f"   🎱 Ball #{ball_num} in most recent sample:")
    print(f"      📊 Rolling frequency: {frequency:.3f} ({frequency*100:.1f}% of last {meta['window_size']} draws)")
    print(f"      📅 Gap since last seen: {gap:.0f} draws ago")
    print(f"      🎯 Appears in next draw: {'Yes' if label else 'No'}")
    
    # Show top 5 most frequent balls in this sample
    freq_features = X_main[sample_idx, ::2]  # Every other feature (frequencies)
    top_balls = np.argsort(freq_features)[-5:][::-1] + 1  # Convert to 1-based
    
    print(f"\n   🏆 Top 5 most frequent balls in this sample:")
    for i, ball in enumerate(top_balls, 1):
        ball_idx = ball - 1
        freq = freq_features[ball_idx]
        gap = X_main[sample_idx, ball_idx * 2 + 1]
        print(f"      {i}. Ball #{ball}: {freq:.3f} frequency, {gap:.0f} gap")


def main():
    """Run all tests."""
    print("🧪 Dataset Building Test Suite")
    print("=" * 60)
    
    # Run tests
    test_basic_dataset_building()
    test_enhanced_dataset_building()
    test_dataset_splitting()
    test_with_real_repository()
    demonstrate_feature_interpretation()
    
    print("\n🎉 All tests completed!")
    print("\n💡 Next steps:")
    print("   1. Use X_main, y_main for main ball prediction models")
    print("   2. Use X_star, y_star for star prediction models")
    print("   3. Try different window sizes and feature combinations")
    print("   4. Apply machine learning algorithms (RandomForest, XGBoost, etc.)")


if __name__ == "__main__":
    main()
