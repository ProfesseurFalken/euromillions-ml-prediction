"""
Streamlit UI Adapters
====================

Thin adapter layer between Streamlit UI and the core ML/data pipeline.
Provides simple, UI-friendly interfaces that handle errors gracefully
and return consistent data structures for the web interface.
"""

import io
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from loguru import logger

from config import get_settings
from repository import get_repository, init_database
from scraper import EuromillionsScraper
from train_models import EuromillionsTrainer, train_latest, get_model_info


class StreamlitAdapters:
    """
    Streamlit UI adapter class providing simple interfaces for web UI.
    All methods return consistent data structures and handle errors gracefully.
    """
    
    def __init__(self):
        """Initialize adapters with database and settings."""
        self.settings = get_settings()
        init_database()
        self.repo = get_repository()
        self.scraper = EuromillionsScraper()
        self.trainer = EuromillionsTrainer()
    
    def init_full_history(self) -> Dict[str, Any]:
        """
        Initialize full historical data by crawling archive pages.
        
        Returns:
            dict: Summary with inserted, updated, skipped counts and date range
                 {inserted, updated, skipped, first_date, last_date, success, message}
        """
        logger.info("Starting full history initialization")
        
        try:
            # Get initial count
            initial_df = self.repo.all_draws_df()
            initial_count = len(initial_df)
            
            # Crawl archive pages (this may take a while)
            logger.info("Crawling historical archive pages...")
            all_draws = []
            
            # Try to scrape a reasonable amount of history
            # We'll loop through pages until we get enough data or hit a limit
            max_pages = 50  # Reasonable limit to prevent infinite loops
            draws_per_page = 20  # Typical number of draws per page
            
            for page in range(1, max_pages + 1):
                try:
                    logger.info(f"Crawling page {page}/{max_pages}")
                    page_draws = self.scraper.scrape_latest(draws_per_page, offset=(page-1)*draws_per_page)
                    
                    if not page_draws:
                        logger.info(f"No more draws found at page {page}, stopping")
                        break
                    
                    all_draws.extend(page_draws)
                    
                    # Stop if we have a good amount of data
                    if len(all_draws) >= 1000:
                        logger.info(f"Collected {len(all_draws)} draws, sufficient for analysis")
                        break
                        
                except Exception as e:
                    logger.warning(f"Error on page {page}: {e}")
                    break
            
            if not all_draws:
                return {
                    "success": False,
                    "message": "No historical data could be retrieved",
                    "inserted": 0,
                    "updated": 0,
                    "skipped": 0,
                    "first_date": None,
                    "last_date": None
                }
            
            # Upsert all draws
            logger.info(f"Upserting {len(all_draws)} historical draws")
            result = self.repo.upsert_draws(all_draws)
            inserted = result.get("inserted", 0)
            updated = result.get("updated", 0)
            
            # Get final statistics
            final_df = self.repo.all_draws_df()
            final_count = len(final_df)
            skipped = len(all_draws) - inserted - updated
            
            first_date = final_df['draw_date'].min() if not final_df.empty else None
            last_date = final_df['draw_date'].max() if not final_df.empty else None
            
            result = {
                "success": True,
                "message": f"Successfully initialized with {final_count} total draws",
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped,
                "first_date": str(first_date) if first_date else None,
                "last_date": str(last_date) if last_date else None,
                "total_draws": final_count
            }
            
            logger.info(f"Full history initialization complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Full history initialization failed: {e}")
            return {
                "success": False,
                "message": f"Initialization failed: {str(e)}",
                "inserted": 0,
                "updated": 0,
                "skipped": 0,
                "first_date": None,
                "last_date": None
            }
    
    def update_incremental(self) -> Dict[str, Any]:
        """
        Update with recent draws by scraping latest pages.
        
        Returns:
            dict: Summary with inserted, updated, skipped counts
        """
        logger.info("Starting incremental update")
        
        try:
            # Get current latest date
            current_df = self.repo.all_draws_df()
            
            # Scrape recent draws (last few pages)
            recent_draws = self.scraper.scrape_latest(100)  # Get recent 100 draws
            
            if not recent_draws:
                return {
                    "success": True,
                    "message": "No new draws found",
                    "inserted": 0,
                    "updated": 0,
                    "skipped": 0
                }
            
            # Upsert recent draws
            result = self.repo.upsert_draws(recent_draws)
            inserted = result.get("inserted", 0)
            updated = result.get("updated", 0)
            skipped = len(recent_draws) - inserted - updated
            
            result = {
                "success": True,
                "message": f"Update complete: {inserted} new, {updated} updated",
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped
            }
            
            logger.info(f"Incremental update complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Incremental update failed: {e}")
            return {
                "success": False,
                "message": f"Update failed: {str(e)}",
                "inserted": 0,
                "updated": 0,
                "skipped": 0
            }
    
    def train_from_scratch(self) -> Dict[str, Any]:
        """
        Train models from scratch using current data.
        
        Returns:
            dict: Training metrics and status
        """
        logger.info("Starting training from scratch")
        
        try:
            # Check if we have enough data
            df = self.repo.all_draws_df()
            
            if df.empty:
                return {
                    "success": False,
                    "message": "No training data available. Please fetch historical data first.",
                    "main_logloss": None,
                    "star_logloss": None
                }
            
            if len(df) < 100:
                return {
                    "success": False,
                    "message": f"Insufficient training data: {len(df)} draws (minimum: 100)",
                    "main_logloss": None,
                    "star_logloss": None
                }
            
            # Train models
            result = train_latest(min_rows=min(len(df), 100))
            
            if result and result.get("success", False):
                metrics = result.get("performance", {})
                
                return {
                    "success": True,
                    "message": f"Training completed successfully with {len(df)} draws",
                    "main_logloss": metrics.get("main_logloss"),
                    "star_logloss": metrics.get("star_logloss"),
                    "cv_main_mean": metrics.get("cv_details", {}).get("main_mean"),
                    "cv_star_mean": metrics.get("cv_details", {}).get("star_mean"),
                    "training_data_size": len(df)
                }
            else:
                return {
                    "success": False,
                    "message": "Training failed. Check logs for details.",
                    "main_logloss": None,
                    "star_logloss": None
                }
                
        except Exception as e:
            logger.error(f"Training from scratch failed: {e}")
            return {
                "success": False,
                "message": f"Training failed: {str(e)}",
                "main_logloss": None,
                "star_logloss": None
            }
    
    def reload_models(self) -> Dict[str, Any]:
        """
        Reload models from disk, forcing refresh.
        
        Returns:
            dict: Model loading status and info
        """
        logger.info("Reloading models")
        
        try:
            # Force reload models
            self.trainer.load_models(force=True)
            
            # Get model info
            info = get_model_info()
            
            if info.get("models_available", False):
                return {
                    "success": True,
                    "message": "Models reloaded successfully",
                    "trained_at": info.get("trained_at"),
                    "main_logloss": info.get("performance", {}).get("main_logloss"),
                    "star_logloss": info.get("performance", {}).get("star_logloss")
                }
            else:
                return {
                    "success": False,
                    "message": "No trained models found to reload",
                    "trained_at": None,
                    "main_logloss": None,
                    "star_logloss": None
                }
                
        except Exception as e:
            logger.error(f"Model reload failed: {e}")
            return {
                "success": False,
                "message": f"Model reload failed: {str(e)}",
                "trained_at": None,
                "main_logloss": None,
                "star_logloss": None
            }
    
    def get_scores(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get ball and star probability scores as sorted DataFrames.
        
        Returns:
            tuple: (balls_df, stars_df) sorted by probability descending
        """
        try:
            # Ensure models are loaded
            self.trainer.load_models()
            
            # Get scores
            ball_scores = self.trainer.score_balls()
            star_scores = self.trainer.score_stars()
            
            # Convert to DataFrames
            balls_df = pd.DataFrame(ball_scores, columns=['ball', 'probability'])
            balls_df = balls_df.sort_values('probability', ascending=False).reset_index(drop=True)
            balls_df['rank'] = range(1, len(balls_df) + 1)
            balls_df['percentage'] = (balls_df['probability'] * 100).round(2)
            
            stars_df = pd.DataFrame(star_scores, columns=['star', 'probability'])
            stars_df = stars_df.sort_values('probability', ascending=False).reset_index(drop=True)
            stars_df['rank'] = range(1, len(stars_df) + 1)
            stars_df['percentage'] = (stars_df['probability'] * 100).round(2)
            
            return balls_df, stars_df
            
        except Exception as e:
            logger.error(f"Failed to get scores: {e}")
            # Return empty DataFrames with correct structure
            empty_balls = pd.DataFrame(columns=['ball', 'probability', 'rank', 'percentage'])
            empty_stars = pd.DataFrame(columns=['star', 'probability', 'rank', 'percentage'])
            return empty_balls, empty_stars
    
    def suggest_tickets_ui(self, n: int = 10, method: str = "hybrid", seed: int = 42) -> List[Dict[str, Any]]:
        """
        Generate lottery ticket suggestions for UI display.
        
        Args:
            n: Number of tickets to generate
            method: Generation method ("topk", "random", "hybrid")
            seed: Random seed for reproducibility
            
        Returns:
            list: List of ticket dictionaries with balls, stars, and metadata
        """
        try:
            # Ensure models are loaded
            self.trainer.load_models()
            
            # Generate combinations
            combinations = self.trainer.suggest_combinations(k=n, method=method, seed=seed)
            
            # Convert to UI-friendly format
            tickets = []
            
            for i, combo in enumerate(combinations, 1):
                balls = sorted(combo[:5])
                stars = sorted(combo[5:])
                
                ticket = {
                    "ticket_id": i,
                    "balls": balls,
                    "stars": stars,
                    "balls_str": " - ".join(f"{b:02d}" for b in balls),
                    "stars_str": " - ".join(f"{s:02d}" for s in stars),
                    "method": method,
                    "seed": seed
                }
                
                tickets.append(ticket)
            
            return tickets
            
        except Exception as e:
            logger.error(f"Failed to generate ticket suggestions: {e}")
            return []
    
    def fetch_last_draws(self, limit: int = 20) -> pd.DataFrame:
        """
        Fetch the most recent draws from database.
        
        Args:
            limit: Number of recent draws to fetch
            
        Returns:
            pd.DataFrame: Recent draws sorted by date descending
        """
        try:
            df = self.repo.all_draws_df()
            
            if df.empty:
                return pd.DataFrame(columns=['draw_date', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2'])
            
            # Sort by date and take most recent
            recent_df = df.sort_values('draw_date', ascending=False).head(limit).copy()
            
            # Format for display
            recent_df['draw_date'] = pd.to_datetime(recent_df['draw_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            recent_df['balls'] = recent_df.apply(
                lambda row: f"{row['n1']:02d}-{row['n2']:02d}-{row['n3']:02d}-{row['n4']:02d}-{row['n5']:02d}", 
                axis=1
            )
            recent_df['stars'] = recent_df.apply(
                lambda row: f"{row['s1']:02d}-{row['s2']:02d}", 
                axis=1
            )
            
            # Select display columns
            display_df = recent_df[['draw_date', 'balls', 'stars', 'n1', 'n2', 'n3', 'n4', 'n5', 's1', 's2']].copy()
            
            return display_df
            
        except Exception as e:
            logger.error(f"Failed to fetch recent draws: {e}")
            return pd.DataFrame(columns=['draw_date', 'balls', 'stars'])
    
    def export_all_draws_csv(self) -> Tuple[str, bytes]:
        """
        Export all draws to CSV format for download.
        
        Returns:
            tuple: (filename, csv_bytes) for Streamlit download
        """
        try:
            df = self.repo.all_draws_df()
            
            if df.empty:
                # Return empty CSV
                empty_csv = "draw_date,n1,n2,n3,n4,n5,s1,s2\n"
                return "euromillions_draws_empty.csv", empty_csv.encode()
            
            # Sort by date
            df_sorted = df.sort_values('draw_date', ascending=False).copy()
            
            # Format date column
            df_sorted['draw_date'] = pd.to_datetime(df_sorted['draw_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            
            # Convert to CSV
            csv_buffer = io.StringIO()
            df_sorted.to_csv(csv_buffer, index=False)
            csv_bytes = csv_buffer.getvalue().encode()
            
            # Generate filename with date range
            first_date = df_sorted['draw_date'].iloc[-1]  # Oldest (last in desc order)
            last_date = df_sorted['draw_date'].iloc[0]    # Newest (first in desc order)
            filename = f"euromillions_draws_{first_date}_to_{last_date}.csv"
            
            return filename, csv_bytes
            
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            error_csv = f"# Export failed: {str(e)}\n"
            return "euromillions_export_error.csv", error_csv.encode()
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status for dashboard.
        
        Returns:
            dict: System status including data, models, and recommendations
        """
        try:
            # Database status
            df = self.repo.all_draws_df()
            data_status = {
                "available": not df.empty,
                "count": len(df),
                "first_date": df['draw_date'].min().strftime('%Y-%m-%d') if not df.empty else None,
                "last_date": df['draw_date'].max().strftime('%Y-%m-%d') if not df.empty else None
            }
            
            # Model status
            info = get_model_info()
            model_status = {
                "available": info.get("models_available", False),
                "trained_at": info.get("trained_at"),
                "main_logloss": info.get("performance", {}).get("main_logloss"),
                "star_logloss": info.get("performance", {}).get("star_logloss")
            }
            
            # Recommendations
            recommendations = []
            if not data_status["available"]:
                recommendations.append("Initialize historical data")
            elif data_status["count"] < 300:
                recommendations.append(f"Add more data (current: {data_status['count']}, recommended: 300+)")
            
            if not model_status["available"]:
                recommendations.append("Train prediction models")
            
            if not recommendations:
                recommendations.append("System ready for predictions!")
            
            return {
                "data": data_status,
                "models": model_status,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                "data": {"available": False, "count": 0},
                "models": {"available": False},
                "recommendations": ["System check failed"],
                "error": str(e)
            }


# Global instance for easy import
streamlit_adapters = StreamlitAdapters()


# Convenience functions for direct import
def init_full_history() -> dict:
    """Initialize full historical data."""
    return streamlit_adapters.init_full_history()


def update_incremental() -> dict:
    """Update with recent draws."""
    return streamlit_adapters.update_incremental()


def train_from_scratch() -> dict:
    """Train models from scratch."""
    return streamlit_adapters.train_from_scratch()


def reload_models() -> dict:
    """Reload models from disk."""
    return streamlit_adapters.reload_models()


def get_scores() -> tuple:
    """Get ball and star scores as DataFrames."""
    return streamlit_adapters.get_scores()


def suggest_tickets_ui(n: int = 10, method: str = "hybrid", seed: int = 42) -> list:
    """Generate lottery ticket suggestions."""
    return streamlit_adapters.suggest_tickets_ui(n, method, seed)


def fetch_last_draws(limit: int = 20) -> pd.DataFrame:
    """Fetch recent draws."""
    return streamlit_adapters.fetch_last_draws(limit)


def export_all_draws_csv() -> tuple:
    """Export all draws to CSV."""
    return streamlit_adapters.export_all_draws_csv()


def get_system_status() -> dict:
    """Get comprehensive system status."""
    return streamlit_adapters.get_system_status()
