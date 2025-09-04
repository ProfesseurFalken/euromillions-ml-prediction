"""
Example usage of the settings system.
Run this script to test the configuration loading and directory creation.
"""
from config import get_settings, get_paths

def main():
    """Demonstrate settings usage."""
    print("🔧 Loading settings...")
    settings = get_settings()
    
    print(f"📁 Storage Directory: {settings.storage_dir}")
    print(f"🗄️  Database URL: {settings.db_url}")
    print(f"🌐 User Agent: {settings.user_agent}")
    print(f"⏱️  Request Timeout: {settings.request_timeout}s")
    print(f"🔄 Max Retries: {settings.max_retries}")
    print(f"🔑 API Token: {'Set' if settings.api_token else 'Not set'}")
    
    print("\n📂 Directory paths:")
    paths = get_paths()
    print(f"   Storage: {paths.storage}")
    print(f"   Raw: {paths.raw}")
    print(f"   Processed: {paths.processed}")
    print(f"   Models: {paths.models}")
    
    print("\n✅ All directories have been created!")
    print("   You can now use these settings throughout your application.")

if __name__ == "__main__":
    main()
