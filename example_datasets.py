"""
Simple example of dataset building for machine learning.
This script demonstrates the core functionality with clear examples.
"""

def example_usage():
    """Example of how to use the dataset building functions."""
    
    print("📚 Euromillions Dataset Building Example")
    print("=" * 50)
    
    print("""
🎯 Purpose:
   Build machine learning features from historical Euromillions draws
   to predict which balls/stars will appear in the next draw.

📊 Input:
   DataFrame with columns: draw_date, n1, n2, n3, n4, n5, s1, s2
   
🔧 Features Created:
   For each ball (1-50) and star (1-12):
   1. Rolling frequency over last K draws (default K=100)
   2. Gap since last seen (draws ago)
   
🎯 Labels:
   Binary indicators: does ball/star appear in NEXT draw?

📈 Output:
   - X_main: Features for main balls (samples × 100 features)
   - y_main: Labels for main balls (samples × 50 labels) 
   - X_star: Features for stars (samples × 24 features)
   - y_star: Labels for stars (samples × 12 labels)
   - meta: Metadata about the dataset
""")

    print("\n💻 Code Example:")
    print("""
# 1. Get historical data
from repository import get_repository
repo = get_repository()
df = repo.all_draws_df()  # Gets all draws sorted by date

# 2. Build ML datasets
from build_datasets import build_datasets
X_main, y_main, X_star, y_star, meta = build_datasets(df, window_size=100)

# 3. Split for training/testing
from build_datasets import split_datasets
splits = split_datasets(X_main, y_main, X_star, y_star, train_ratio=0.8)
X_main_train, X_main_test, y_main_train, y_main_test = splits[:4]
X_star_train, X_star_test, y_star_train, y_star_test = splits[4:]

# 4. Train models (example with scikit-learn)
from sklearn.ensemble import RandomForestClassifier
from sklearn.multioutput import MultiOutputClassifier

# Model for main balls (predicts 5 balls out of 50)
main_model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100))
main_model.fit(X_main_train, y_main_train)

# Model for stars (predicts 2 stars out of 12)  
star_model = MultiOutputClassifier(RandomForestClassifier(n_estimators=100))
star_model.fit(X_star_train, y_star_train)

# 5. Make predictions
main_pred = main_model.predict_proba(X_main_test)
star_pred = star_model.predict_proba(X_star_test)

# 6. Generate next draw prediction
# Get probabilities for each ball/star and select top ones
next_X_main = X_main[-1:]  # Features for most recent draw
next_X_star = X_star[-1:]

main_probs = main_model.predict_proba(next_X_main)[0][:, 1]  # Probability of appearing
star_probs = star_model.predict_proba(next_X_star)[0][:, 1]

# Select top 5 main balls and top 2 stars
predicted_main = np.argsort(main_probs)[-5:] + 1  # Convert to 1-based
predicted_stars = np.argsort(star_probs)[-2:] + 1

print(f"Predicted main balls: {sorted(predicted_main)}")
print(f"Predicted stars: {sorted(predicted_stars)}")
""")

    print("\n🔍 Feature Interpretation:")
    print("""
Each ball/star has 2 features:
1. Frequency: How often it appeared in last K draws (0.0 to 1.0)
   - 0.2 = appeared in 20% of recent draws
   - Higher = "hot" numbers, Lower = "cold" numbers

2. Gap: How many draws since it last appeared
   - 1 = appeared in previous draw
   - 10 = appeared 10 draws ago
   - Higher = longer absence, may be "due"
""")

    print("\n📊 Dataset Shapes:")
    print("""
Example with 500 historical draws:
- X_main: (499, 100) - 499 samples, 100 features (50 balls × 2 features each)
- y_main: (499, 50)  - 499 samples, 50 labels (one per ball)
- X_star: (499, 24)  - 499 samples, 24 features (12 stars × 2 features each)  
- y_star: (499, 12)  - 499 samples, 12 labels (one per star)

Note: 499 samples from 500 draws because we predict the NEXT draw
""")

    print("\n🎪 Enhanced Features:")
    print("""
Use build_enhanced_datasets() for additional features:
1. Long-term frequency (default window)
2. Gap since last seen  
3. Short-term frequency (window/3)
4. Streak count (positive=consecutive appearances, negative=consecutive absences)

This gives 4 features per ball/star instead of 2.
""")

    print("\n⚡ Quick Start:")
    print("""
1. Run: python test_build_datasets.py
2. This will create sample data and demonstrate all functions
3. Adapt the code for your own machine learning experiments
""")

if __name__ == "__main__":
    example_usage()
