"""
Simple CLI for training Euromillions models.
Provides easy access to training and prediction functionality.
"""
import sys
from pathlib import Path
import argparse
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from train_models import (
    train_latest, predict_next_draw, get_model_info,
    score_balls, score_stars, suggest_combinations
)
from repository import get_repository, init_database
from demo_scraper import MockEuromillionsScraper


def cmd_train(args):
    """Train models command."""
    print("🏋️ Training Euromillions Models")
    print("=" * 40)
    
    # Check data availability
    repo = get_repository()
    df = repo.all_draws_df()
    
    if df.empty:
        print("⚠️  No data found in repository.")
        if args.demo_data:
            print("📝 Adding demo data...")
            scraper = MockEuromillionsScraper()
            draws = scraper.scrape_latest(args.demo_data)
            result = repo.upsert_draws(draws)
            print(f"   Added {result['inserted']} demo draws")
            df = repo.all_draws_df()
        else:
            print("   Use --demo-data N to add N demo draws, or populate repository with real data")
            return
    
    print(f"📊 Available data: {len(df)} draws from {df['draw_date'].min()} to {df['draw_date'].max()}")
    
    if len(df) < args.min_rows:
        print(f"❌ Insufficient data: {len(df)} < {args.min_rows} required")
        print(f"   Use --min-rows to lower requirement or add more data")
        return
    
    # Train models
    print(f"\n🚀 Starting training with min_rows={args.min_rows}...")
    try:
        metrics = train_latest(min_rows=args.min_rows)
        
        print("✅ Training completed successfully!")
        print(f"\n📈 Results:")
        print(f"   🎱 Main model log loss: {metrics['models']['main']['logloss']:.4f}")
        print(f"   ⭐ Star model log loss: {metrics['models']['star']['logloss']:.4f}")
        print(f"   📊 Training samples: {metrics['data_range']['n_samples']}")
        print(f"   📅 Data range: {metrics['data_range']['from']} to {metrics['data_range']['to']}")
        
        print(f"\n💾 Models saved:")
        print(f"   {metrics['models']['main']['path']}")
        print(f"   {metrics['models']['star']['path']}")
        print(f"   {metrics['meta_path']}")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def cmd_predict(args):
    """Predict next draw command."""
    print("🔮 Predicting Next Draw")
    print("=" * 25)
    
    try:
        prediction = predict_next_draw(return_probabilities=args.probabilities)
        
        print("✅ Prediction completed!")
        print(f"\n🎯 Next Draw Prediction:")
        print(f"   🎱 Main balls: {' - '.join(map(str, prediction['predicted_main']))}")
        print(f"   ⭐ Stars: {' - '.join(map(str, prediction['predicted_stars']))}")
        
        print(f"\n📊 Model Info:")
        print(f"   📅 Trained: {prediction['model_trained_at']}")
        print(f"   📅 Data: {prediction['data_range']['from']} to {prediction['data_range']['to']}")
        
        if args.probabilities:
            print(f"\n🎯 Top Main Ball Probabilities:")
            main_probs = prediction['main_probabilities']
            sorted_main = sorted(main_probs.items(), key=lambda x: x[1], reverse=True)
            
            for i, (ball, prob) in enumerate(sorted_main[:10], 1):
                ball_num = int(ball.split('_')[1])
                selected = "⭐" if ball_num in prediction['predicted_main'] else "  "
                print(f"      {i:2d}. Ball {ball_num:2d}: {prob:.4f} {selected}")
            
            print(f"\n🌟 Star Probabilities:")
            star_probs = prediction['star_probabilities']
            sorted_stars = sorted(star_probs.items(), key=lambda x: x[1], reverse=True)
            
            for i, (star, prob) in enumerate(sorted_stars, 1):
                star_num = int(star.split('_')[1])
                selected = "⭐" if star_num in prediction['predicted_stars'] else "  "
                print(f"      {i:2d}. Star {star_num:2d}: {prob:.4f} {selected}")
        
    except FileNotFoundError:
        print("❌ No trained models found")
        print("   Run: python cli_train.py train --demo-data 350")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def cmd_info(args):
    """Show model information command."""
    print("📋 Model Information")
    print("=" * 25)
    
    try:
        info = get_model_info()
        
        if info['models_available']:
            print("✅ Trained models are available")
            print(f"\n📊 Training Details:")
            print(f"   📅 Trained: {info['trained_at']}")
            print(f"   📊 Data: {info['data_range']['n_draws']} draws")
            print(f"   📅 Range: {info['data_range']['from']} to {info['data_range']['to']}")
            
            print(f"\n🎯 Performance:")
            print(f"   🎱 Main log loss: {info['performance']['main_logloss']:.4f}")
            print(f"   ⭐ Star log loss: {info['performance']['star_logloss']:.4f}")
            
            print(f"\n🔧 Features: {', '.join(info['features'])}")
            
        else:
            print("❌ No trained models found")
            print(f"   📝 {info['message']}")
            print("   Run training first: python cli_train.py train --demo-data 350")
        
    except Exception as e:
        print(f"❌ Failed to get model info: {e}")


def cmd_score(args):
    """Score balls and stars command."""
    print("📊 Scoring Balls and Stars")
    print("=" * 30)
    
    try:
        from train_models import EuromillionsTrainer
        
        print("🤖 Loading models...")
        trainer = EuromillionsTrainer()
        trainer.load_models()
        
        print("🎱 Scoring main balls...")
        ball_scores = trainer.score_balls()
        
        print("⭐ Scoring stars...")
        star_scores = trainer.score_stars()
        
        # Sort by probability
        sorted_balls = sorted(ball_scores, key=lambda x: x[1], reverse=True)
        sorted_stars = sorted(star_scores, key=lambda x: x[1], reverse=True)
        
        print("✅ Scoring completed!")
        
        # Show top balls
        print(f"\n🏆 Top {args.top} Main Balls:")
        for i, (ball, prob) in enumerate(sorted_balls[:args.top], 1):
            print(f"   {i:2d}. Ball {ball:2d}: {prob:.4f} ({prob*100:.1f}%)")
        
        # Show top stars
        print(f"\n🌟 Top {min(args.top, 12)} Stars:")
        for i, (star, prob) in enumerate(sorted_stars[:min(args.top, 12)], 1):
            print(f"   {i:2d}. Star {star:2d}: {prob:.4f} ({prob*100:.1f}%)")
        
        if args.all:
            print(f"\n📋 All Ball Scores:")
            for ball, prob in ball_scores:
                print(f"   Ball {ball:2d}: {prob:.4f}")
            
            print(f"\n📋 All Star Scores:")
            for star, prob in star_scores:
                print(f"   Star {star:2d}: {prob:.4f}")
        
        # Statistics
        ball_probs = [prob for _, prob in ball_scores]
        star_probs = [prob for _, prob in star_scores]
        
        print(f"\n📈 Statistics:")
        print(f"   Ball avg: {sum(ball_probs)/len(ball_probs):.4f} (expected: ~{5/50:.4f})")
        print(f"   Star avg: {sum(star_probs)/len(star_probs):.4f} (expected: ~{2/12:.4f})")
        print(f"   Ball range: {min(ball_probs):.4f} - {max(ball_probs):.4f}")
        print(f"   Star range: {min(star_probs):.4f} - {max(star_probs):.4f}")
        
    except FileNotFoundError:
        print("❌ No trained models found")
        print("   Run: python cli_train.py train --demo-data 350")
    except Exception as e:
        print(f"❌ Scoring failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def cmd_suggest(args):
    """Suggest combinations command."""
    print("🎯 Generating Combination Suggestions")
    print("=" * 40)
    
    try:
        from train_models import EuromillionsTrainer
        
        print("🤖 Loading models...")
        trainer = EuromillionsTrainer()
        trainer.load_models()
        
        print(f"🎲 Generating {args.count} combinations using {args.method} method...")
        combinations = trainer.suggest_combinations(
            k=args.count, 
            method=args.method, 
            seed=args.seed
        )
        
        print(f"✅ Generated {len(combinations)} combinations")
        
        for i, combo in enumerate(combinations, 1):
            balls = combo[:5]
            stars = combo[5:]
            balls_str = "-".join(f"{b:2d}" for b in sorted(balls))
            stars_str = "-".join(f"{s:2d}" for s in sorted(stars))
            
            print(f"\n🎫 Combination {i}:")
            print(f"   🎱 Balls: {balls_str}")
            print(f"   ⭐ Stars: {stars_str}")
            
            if args.probabilities:
                ball_scores = dict(trainer.score_balls())
                star_scores = dict(trainer.score_stars())
                
                ball_probs = [ball_scores[b] for b in balls]
                star_probs = [star_scores[s] for s in stars]
                
                print(f"   📈 Ball probs: {', '.join(f'{p:.3f}' for p in ball_probs)}")
                print(f"   📈 Star probs: {', '.join(f'{p:.3f}' for p in star_probs)}")
                print(f"   📊 Avg ball: {sum(ball_probs)/len(ball_probs):.4f}")
                print(f"   📊 Avg star: {sum(star_probs)/len(star_probs):.4f}")
        
        # Show method explanation
        if args.explain:
            print(f"\n💡 Method: {args.method.upper()}")
            if args.method == "topk":
                print("   - Selects balls/stars with highest probabilities")
                print("   - Most conservative approach")
            elif args.method == "random":
                print("   - Weighted random sampling based on probabilities")
                print("   - More diverse combinations")
            elif args.method == "hybrid":
                print("   - Mix of top-probability and weighted random")
                print("   - Balanced between conservative and diverse")
        
        print(f"\n💡 Try different methods:")
        print(f"   python cli_train.py suggest --method topk --count 5")
        print(f"   python cli_train.py suggest --method random --count 10")
        
    except FileNotFoundError:
        print("❌ No trained models found")
        print("   Run: python cli_train.py train --demo-data 350")
    except Exception as e:
        print(f"❌ Combination generation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()


def cmd_status(args):
    """Show overall status command."""
    print("📊 Euromillions System Status")
    print("=" * 35)
    
    # Check repository
    try:
        init_database()
        repo = get_repository()
        df = repo.all_draws_df()
        
        print(f"📄 Repository:")
        if df.empty:
            print(f"   ❌ No data available")
        else:
            print(f"   ✅ {len(df)} draws available")
            print(f"   📅 Range: {df['draw_date'].min()} to {df['draw_date'].max()}")
            
    except Exception as e:
        print(f"   ❌ Repository error: {e}")
    
    # Check models
    try:
        info = get_model_info()
        print(f"\n🤖 Models:")
        if info['models_available']:
            print(f"   ✅ Trained models available")
            print(f"   📅 Trained: {info['trained_at']}")
            print(f"   🎯 Main loss: {info['performance']['main_logloss']:.4f}")
            print(f"   ⭐ Star loss: {info['performance']['star_logloss']:.4f}")
        else:
            print(f"   ❌ No trained models")
            
    except Exception as e:
        print(f"   ❌ Models error: {e}")
    
    # Recommendations
    print(f"\n💡 Recommendations:")
    if df.empty:
        print(f"   1. Add data: python cli_train.py train --demo-data 350")
    elif len(df) < 300:
        print(f"   1. Add more data (current: {len(df)}, recommended: 300+)")
    
    if not info.get('models_available', False):
        print(f"   2. Train models: python cli_train.py train")
    else:
        print(f"   2. Generate suggestions: python cli_train.py suggest")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Euromillions ML Training CLI")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Train prediction models")
    train_parser.add_argument("--min-rows", type=int, default=300, 
                             help="Minimum number of draws required (default: 300)")
    train_parser.add_argument("--demo-data", type=int, metavar="N",
                             help="Add N demo draws if no data exists")
    train_parser.set_defaults(func=cmd_train)
    
    # Predict command  
    predict_parser = subparsers.add_parser("predict", help="Predict next draw")
    predict_parser.add_argument("-p", "--probabilities", action="store_true",
                               help="Show probability scores for all balls/stars")
    predict_parser.set_defaults(func=cmd_predict)
    
    # Score command
    score_parser = subparsers.add_parser("score", help="Score all balls and stars")
    score_parser.add_argument("--top", type=int, default=10,
                             help="Number of top balls/stars to show (default: 10)")
    score_parser.add_argument("--all", action="store_true",
                             help="Show scores for all balls and stars")
    score_parser.set_defaults(func=cmd_score)
    
    # Suggest command
    suggest_parser = subparsers.add_parser("suggest", help="Generate combination suggestions")
    suggest_parser.add_argument("-k", "--count", type=int, default=10,
                               help="Number of combinations to generate (default: 10)")
    suggest_parser.add_argument("-m", "--method", choices=["topk", "random", "hybrid"],
                               default="hybrid", help="Generation method (default: hybrid)")
    suggest_parser.add_argument("--seed", type=int, default=42,
                               help="Random seed for reproducibility (default: 42)")
    suggest_parser.add_argument("-p", "--probabilities", action="store_true",
                               help="Show individual ball/star probabilities")
    suggest_parser.add_argument("--explain", action="store_true",
                               help="Explain the selected method")
    suggest_parser.set_defaults(func=cmd_suggest)
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show model information")
    info_parser.set_defaults(func=cmd_info)
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        print(f"\n💡 Quick start:")
        print(f"   python cli_train.py train --demo-data 350")
        print(f"   python cli_train.py suggest")
        print(f"   python cli_train.py score --top 15")
        return
    
    # Run the command
    args.func(args)


if __name__ == "__main__":
    main()
