"""
Dataset builder for Euromillions machine learning features.
Creates features based on historical patterns and frequencies.
"""
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
from loguru import logger


def build_datasets(df: pd.DataFrame, window_size: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Build machine learning datasets from historical draw data.
    
    Args:
        df: DataFrame from repository.all_draws_df() with columns:
            draw_id, draw_date, n1, n2, n3, n4, n5, s1, s2, ...
        window_size: Rolling window size for frequency calculations (default: 100)
    
    Returns:
        Tuple containing:
        - X_main: Features for main balls (n_samples, 50 * n_features)
        - y_main: Labels for main balls (n_samples, 50) - binary whether ball appears
        - X_star: Features for star balls (n_samples, 12 * n_features) 
        - y_star: Labels for star balls (n_samples, 12) - binary whether star appears
        - meta: Dictionary with metadata about the dataset
    """
    logger.info(f"Building datasets from {len(df)} draws with window size {window_size}")
    
    if df.empty:
        raise ValueError("Input DataFrame is empty")
    
    # Ensure DataFrame is sorted by date
    df = df.sort_values('draw_date').reset_index(drop=True)
    
    # Prepare data structures
    n_draws = len(df)
    n_samples = n_draws - 1  # We predict the next draw, so last draw has no target
    
    # Feature dimensions: frequency + gap_since_last for each ball/star
    n_main_features = 2  # frequency, gap_since_last
    n_star_features = 2  # frequency, gap_since_last
    
    # Initialize feature matrices
    X_main = np.zeros((n_samples, 50, n_main_features))  # 50 main balls
    X_star = np.zeros((n_samples, 12, n_star_features))  # 12 stars
    
    # Initialize label matrices (binary: does ball/star appear in next draw?)
    y_main = np.zeros((n_samples, 50), dtype=int)
    y_star = np.zeros((n_samples, 12), dtype=int)
    
    # Track last seen positions for gap calculation
    main_last_seen = np.full(50, -1)  # Index of last draw where each ball appeared
    star_last_seen = np.full(12, -1)  # Index of last draw where each star appeared
    
    # Track frequency counts for rolling window
    main_counts = np.zeros(50)  # Running count for each main ball
    star_counts = np.zeros(12)  # Running count for each star
    
    logger.info("Processing draws and building features...")
    
    for i in range(n_samples):
        current_draw = df.iloc[i]
        next_draw = df.iloc[i + 1]
        
        # Extract current draw numbers (convert to 0-based indexing)
        current_main = [
            current_draw['n1'] - 1, current_draw['n2'] - 1, current_draw['n3'] - 1,
            current_draw['n4'] - 1, current_draw['n5'] - 1
        ]
        current_stars = [current_draw['s1'] - 1, current_draw['s2'] - 1]
        
        # Extract next draw numbers for labels (convert to 0-based indexing)
        next_main = [
            next_draw['n1'] - 1, next_draw['n2'] - 1, next_draw['n3'] - 1,
            next_draw['n4'] - 1, next_draw['n5'] - 1
        ]
        next_stars = [next_draw['s1'] - 1, next_draw['s2'] - 1]
        
        # Update counts and last seen for current draw
        for ball in current_main:
            main_counts[ball] += 1
            main_last_seen[ball] = i
        
        for star in current_stars:
            star_counts[star] += 1
            star_last_seen[star] = i
        
        # Calculate effective window size (smaller at beginning)
        effective_window = min(window_size, i + 1)
        
        # Remove old counts if window is full
        if i >= window_size:
            old_draw = df.iloc[i - window_size]
            old_main = [
                old_draw['n1'] - 1, old_draw['n2'] - 1, old_draw['n3'] - 1,
                old_draw['n4'] - 1, old_draw['n5'] - 1
            ]
            old_stars = [old_draw['s1'] - 1, old_draw['s2'] - 1]
            
            for ball in old_main:
                main_counts[ball] = max(0, main_counts[ball] - 1)
            
            for star in old_stars:
                star_counts[star] = max(0, star_counts[star] - 1)
        
        # Build features for each main ball (1-50)
        for ball_idx in range(50):
            # Feature 1: Rolling frequency (normalized by effective window)
            frequency = main_counts[ball_idx] / effective_window
            
            # Feature 2: Gap since last seen
            if main_last_seen[ball_idx] == -1:
                gap_since_last = i + 1  # Never seen before
            else:
                gap_since_last = i - main_last_seen[ball_idx]
            
            X_main[i, ball_idx, 0] = frequency
            X_main[i, ball_idx, 1] = gap_since_last
        
        # Build features for each star (1-12)
        for star_idx in range(12):
            # Feature 1: Rolling frequency (normalized by effective window)
            frequency = star_counts[star_idx] / effective_window
            
            # Feature 2: Gap since last seen
            if star_last_seen[star_idx] == -1:
                gap_since_last = i + 1  # Never seen before
            else:
                gap_since_last = i - star_last_seen[star_idx]
            
            X_star[i, star_idx, 0] = frequency
            X_star[i, star_idx, 1] = gap_since_last
        
        # Build labels (binary: does ball/star appear in next draw?)
        for ball in next_main:
            y_main[i, ball] = 1
        
        for star in next_stars:
            y_star[i, star] = 1
    
    # Reshape feature matrices for ML algorithms
    # From (n_samples, n_balls, n_features) to (n_samples, n_balls * n_features)
    X_main_flat = X_main.reshape(n_samples, -1)  # Shape: (n_samples, 50 * 2)
    X_star_flat = X_star.reshape(n_samples, -1)  # Shape: (n_samples, 12 * 2)
    
    # Create metadata
    meta = {
        "data_from": df.iloc[0]['draw_date'],
        "data_to": df.iloc[-1]['draw_date'],
        "n_draws": n_draws,
        "n_samples": n_samples,
        "window_size": window_size,
        "main_balls_range": "1-50",
        "stars_range": "1-12",
        "features": ["rolling_frequency", "gap_since_last"],
        "X_main_shape": X_main_flat.shape,
        "X_star_shape": X_star_flat.shape,
        "y_main_shape": y_main.shape,
        "y_star_shape": y_star.shape,
        "feature_names_main": [f"ball_{b+1}_{feat}" for b in range(50) for feat in ["freq", "gap"]],
        "feature_names_star": [f"star_{s+1}_{feat}" for s in range(12) for feat in ["freq", "gap"]]
    }
    
    logger.info(f"Dataset built successfully:")
    logger.info(f"  - X_main shape: {X_main_flat.shape}")
    logger.info(f"  - y_main shape: {y_main.shape}")
    logger.info(f"  - X_star shape: {X_star_flat.shape}")
    logger.info(f"  - y_star shape: {y_star.shape}")
    logger.info(f"  - Date range: {meta['data_from']} to {meta['data_to']}")
    
    return X_main_flat, y_main, X_star_flat, y_star, meta


def get_feature_statistics(X: np.ndarray, feature_names: list) -> pd.DataFrame:
    """
    Get descriptive statistics for features.
    
    Args:
        X: Feature matrix
        feature_names: List of feature names
    
    Returns:
        DataFrame with feature statistics
    """
    stats_df = pd.DataFrame({
        'feature': feature_names,
        'mean': X.mean(axis=0),
        'std': X.std(axis=0),
        'min': X.min(axis=0),
        'max': X.max(axis=0),
        'median': np.median(X, axis=0)
    })
    
    return stats_df


def analyze_label_distribution(y: np.ndarray, ball_type: str = "main") -> pd.DataFrame:
    """
    Analyze the distribution of labels (how often each ball/star appears).
    
    Args:
        y: Label matrix (n_samples, n_balls)
        ball_type: "main" or "star"
    
    Returns:
        DataFrame with appearance statistics
    """
    n_samples, n_balls = y.shape
    
    stats = []
    for i in range(n_balls):
        ball_num = i + 1
        appearances = y[:, i].sum()
        frequency = appearances / n_samples
        
        stats.append({
            f'{ball_type}_number': ball_num,
            'appearances': appearances,
            'frequency': frequency,
            'never_appeared': appearances == 0,
            'always_appeared': appearances == n_samples
        })
    
    return pd.DataFrame(stats)


def split_datasets(X_main: np.ndarray, y_main: np.ndarray, 
                  X_star: np.ndarray, y_star: np.ndarray,
                  train_ratio: float = 0.8) -> Tuple[np.ndarray, ...]:
    """
    Split datasets into train/test sets chronologically.
    
    Args:
        X_main, y_main: Main ball features and labels
        X_star, y_star: Star features and labels
        train_ratio: Ratio of data to use for training
    
    Returns:
        Tuple of (X_main_train, X_main_test, y_main_train, y_main_test,
                 X_star_train, X_star_test, y_star_train, y_star_test)
    """
    n_samples = X_main.shape[0]
    split_idx = int(n_samples * train_ratio)
    
    X_main_train, X_main_test = X_main[:split_idx], X_main[split_idx:]
    y_main_train, y_main_test = y_main[:split_idx], y_main[split_idx:]
    X_star_train, X_star_test = X_star[:split_idx], X_star[split_idx:]
    y_star_train, y_star_test = y_star[:split_idx], y_star[split_idx:]
    
    logger.info(f"Dataset split: {split_idx} training samples, {n_samples - split_idx} test samples")
    
    return (X_main_train, X_main_test, y_main_train, y_main_test,
            X_star_train, X_star_test, y_star_train, y_star_test)


def build_enhanced_datasets(df: pd.DataFrame, window_size: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Build enhanced datasets with additional features.
    
    Enhanced features include:
    - Rolling frequency over different windows
    - Gap since last seen
    - Streak counts (consecutive appearances/absences)
    - Relative position features
    
    Args:
        df: DataFrame from repository.all_draws_df()
        window_size: Base window size for calculations
    
    Returns:
        Same structure as build_datasets but with more features
    """
    logger.info(f"Building enhanced datasets with additional features")
    
    if df.empty:
        raise ValueError("Input DataFrame is empty")
    
    # Ensure DataFrame is sorted by date
    df = df.sort_values('draw_date').reset_index(drop=True)
    
    n_draws = len(df)
    n_samples = n_draws - 1
    
    # Enhanced features: frequency, gap, short_freq, streak
    n_main_features = 4
    n_star_features = 4
    
    X_main = np.zeros((n_samples, 50, n_main_features))
    X_star = np.zeros((n_samples, 12, n_star_features))
    y_main = np.zeros((n_samples, 50), dtype=int)
    y_star = np.zeros((n_samples, 12), dtype=int)
    
    # Tracking arrays
    main_last_seen = np.full(50, -1)
    star_last_seen = np.full(12, -1)
    main_counts = np.zeros(50)
    star_counts = np.zeros(12)
    main_short_counts = np.zeros(50)  # Shorter window counts
    star_short_counts = np.zeros(12)
    main_streaks = np.zeros(50)  # Current streak (positive=appearing, negative=absent)
    star_streaks = np.zeros(12)
    
    short_window = window_size // 3  # Shorter window for recent trends
    
    for i in range(n_samples):
        current_draw = df.iloc[i]
        next_draw = df.iloc[i + 1]
        
        # Current and next draw numbers (0-based)
        current_main = [current_draw[f'n{j}'] - 1 for j in range(1, 6)]
        current_stars = [current_draw['s1'] - 1, current_draw['s2'] - 1]
        next_main = [next_draw[f'n{j}'] - 1 for j in range(1, 6)]
        next_stars = [next_draw['s1'] - 1, next_draw['s2'] - 1]
        
        # Update counts and streaks
        for ball in range(50):
            if ball in current_main:
                main_counts[ball] += 1
                main_short_counts[ball] += 1
                main_last_seen[ball] = i
                main_streaks[ball] = max(1, main_streaks[ball] + 1) if main_streaks[ball] >= 0 else 1
            else:
                main_streaks[ball] = min(-1, main_streaks[ball] - 1) if main_streaks[ball] <= 0 else -1
        
        for star in range(12):
            if star in current_stars:
                star_counts[star] += 1
                star_short_counts[star] += 1
                star_last_seen[star] = i
                star_streaks[star] = max(1, star_streaks[star] + 1) if star_streaks[star] >= 0 else 1
            else:
                star_streaks[star] = min(-1, star_streaks[star] - 1) if star_streaks[star] <= 0 else -1
        
        # Handle window overflow
        effective_window = min(window_size, i + 1)
        effective_short_window = min(short_window, i + 1)
        
        if i >= window_size:
            old_draw = df.iloc[i - window_size]
            old_main = [old_draw[f'n{j}'] - 1 for j in range(1, 6)]
            old_stars = [old_draw['s1'] - 1, old_draw['s2'] - 1]
            for ball in old_main:
                main_counts[ball] = max(0, main_counts[ball] - 1)
            for star in old_stars:
                star_counts[star] = max(0, star_counts[star] - 1)
        
        if i >= short_window:
            old_short_draw = df.iloc[i - short_window]
            old_short_main = [old_short_draw[f'n{j}'] - 1 for j in range(1, 6)]
            old_short_stars = [old_short_draw['s1'] - 1, old_short_draw['s2'] - 1]
            for ball in old_short_main:
                main_short_counts[ball] = max(0, main_short_counts[ball] - 1)
            for star in old_short_stars:
                star_short_counts[star] = max(0, star_short_counts[star] - 1)
        
        # Build enhanced features
        for ball in range(50):
            X_main[i, ball, 0] = main_counts[ball] / effective_window  # Long-term frequency
            X_main[i, ball, 1] = (i - main_last_seen[ball]) if main_last_seen[ball] >= 0 else i + 1  # Gap
            X_main[i, ball, 2] = main_short_counts[ball] / effective_short_window  # Short-term frequency
            X_main[i, ball, 3] = main_streaks[ball]  # Streak
        
        for star in range(12):
            X_star[i, star, 0] = star_counts[star] / effective_window
            X_star[i, star, 1] = (i - star_last_seen[star]) if star_last_seen[star] >= 0 else i + 1
            X_star[i, star, 2] = star_short_counts[star] / effective_short_window
            X_star[i, star, 3] = star_streaks[star]
        
        # Build labels
        for ball in next_main:
            y_main[i, ball] = 1
        for star in next_stars:
            y_star[i, star] = 1
    
    # Reshape for ML
    X_main_flat = X_main.reshape(n_samples, -1)
    X_star_flat = X_star.reshape(n_samples, -1)
    
    meta = {
        "data_from": df.iloc[0]['draw_date'],
        "data_to": df.iloc[-1]['draw_date'],
        "n_draws": n_draws,
        "n_samples": n_samples,
        "window_size": window_size,
        "short_window_size": short_window,
        "features": ["long_frequency", "gap_since_last", "short_frequency", "streak"],
        "X_main_shape": X_main_flat.shape,
        "X_star_shape": X_star_flat.shape,
        "enhanced": True
    }
    
    return X_main_flat, y_main, X_star_flat, y_star, meta
