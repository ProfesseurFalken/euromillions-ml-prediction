#!/usr/bin/env python3
"""
EuroMillions ML Prediction System - Advanced Launcher
====================================================

A comprehensive command-line interface for the EuroMillions ML system.
Supports multiple commands for different operations.
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path
from typing import Optional

try:
    import click
except ImportError:
    print("Installing click...")
    subprocess.run([sys.executable, "-m", "pip", "install", "click"], check=True)
    import click

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """EuroMillions ML Prediction System - Advanced Launcher"""
    pass

@cli.command()
@click.option('--port', '-p', default=8501, help='Port to run Streamlit on')
@click.option('--no-browser', is_flag=True, help='Don\'t open browser automatically')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def run(port: int, no_browser: bool, debug: bool):
    """Launch the Streamlit web application"""
    click.echo("🚀 EuroMillions ML Prediction System")
    click.echo("=" * 40)
    
    # Check virtual environment
    venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        click.echo("❌ Virtual environment not found!")
        click.echo("Please run: python launcher.py setup")
        return
    
    click.echo(f"🌐 Starting web server on port {port}...")
    
    # Prepare environment
    env = os.environ.copy()
    if debug:
        env['STREAMLIT_LOGGER_LEVEL'] = 'debug'
    
    # Launch application
    try:
        if not no_browser:
            # Open browser after a delay
            def open_browser():
                time.sleep(3)
                webbrowser.open(f"http://localhost:{port}")
            
            import threading
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
        
        # Run the application
        cmd = [str(venv_python), "main.py"]
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        click.echo("\n👋 Application stopped by user")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@cli.command()
def setup():
    """Set up the virtual environment and install dependencies"""
    click.echo("🔧 Setting up EuroMillions ML system...")
    click.echo("=" * 40)
    
    try:
        # Run bootstrap script
        if os.name == 'nt':  # Windows
            bootstrap_script = PROJECT_ROOT / "bootstrap.ps1"
            cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(bootstrap_script)]
        else:  # Unix-like
            bootstrap_script = PROJECT_ROOT / "bootstrap.sh"
            cmd = ["bash", str(bootstrap_script)]
        
        click.echo("Running bootstrap script...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            click.echo("✅ Setup completed successfully!")
            click.echo("You can now run: python launcher.py run")
        else:
            click.echo(f"❌ Setup failed: {result.stderr}")
            
    except Exception as e:
        click.echo(f"❌ Setup error: {e}")

@cli.command()
@click.option('--method', '-m', default='random', 
              type=click.Choice(['random', 'topk', 'hybrid']),
              help='Prediction method to use')
@click.option('--count', '-c', default=5, help='Number of tickets to generate')
def predict(method: str, count: int):
    """Generate lottery number predictions"""
    click.echo(f"🎰 Generating {count} tickets using {method} method...")
    click.echo("=" * 40)
    
    try:
        # Check if system is ready
        venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            click.echo("❌ Please run setup first: python launcher.py setup")
            return
        
        # Generate predictions
        cmd = [
            str(venv_python), "-c",
            f"""
import sys
sys.path.append('.')
from streamlit_adapters import suggest_tickets_ui

try:
    tickets = suggest_tickets_ui(n={count}, method='{method}')
    print(f'\\n🎲 Generated {{len(tickets)}} tickets:')
    print('=' * 50)
    
    for i, ticket in enumerate(tickets, 1):
        balls = ' - '.join(f'{{b:02d}}' for b in ticket['balls'])
        stars = ' - '.join(f'{{s:02d}}' for s in ticket['stars'])
        score = ticket['combined_score']
        print(f'Ticket {{i:2d}}: {{balls}} | Stars: {{stars}} (Score: {{score:.3f}})')
    
    print('\\n✨ Good luck!')
    
except Exception as e:
    print(f'❌ Error generating predictions: {{e}}')
    import traceback
    traceback.print_exc()
"""
        ]
        
        subprocess.run(cmd)
        
    except Exception as e:
        click.echo(f"❌ Prediction error: {e}")

@cli.command()
def train():
    """Train the machine learning models"""
    click.echo("🤖 Training ML models...")
    click.echo("=" * 40)
    
    try:
        venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            click.echo("❌ Please run setup first: python launcher.py setup")
            return
        
        cmd = [
            str(venv_python), "-c",
            """
import sys
sys.path.append('.')
from streamlit_adapters import train_from_scratch

try:
    print('Starting model training...')
    result = train_from_scratch()
    
    if result['success']:
        print(f'✅ Training completed: {result["message"]}')
    else:
        print(f'❌ Training failed: {result["message"]}')
        
except Exception as e:
    print(f'❌ Training error: {e}')
    import traceback
    traceback.print_exc()
"""
        ]
        
        subprocess.run(cmd)
        
    except Exception as e:
        click.echo(f"❌ Training error: {e}")

@cli.command()
def update():
    """Update lottery data from online sources"""
    click.echo("📊 Updating lottery data...")
    click.echo("=" * 40)
    
    try:
        venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            click.echo("❌ Please run setup first: python launcher.py setup")
            return
        
        cmd = [
            str(venv_python), "-c",
            """
import sys
sys.path.append('.')
from streamlit_adapters import update_incremental

try:
    print('Fetching latest lottery data...')
    result = update_incremental()
    
    if result['success']:
        print(f'✅ Update completed: {result["message"]}')
        print(f'   New: {result["inserted"]}, Updated: {result["updated"]}, Skipped: {result["skipped"]}')
    else:
        print(f'❌ Update failed: {result["message"]}')
        
except Exception as e:
    print(f'❌ Update error: {e}')
    import traceback
    traceback.print_exc()
"""
        ]
        
        subprocess.run(cmd)
        
    except Exception as e:
        click.echo(f"❌ Update error: {e}")

@cli.command()
def status():
    """Show system status and information"""
    click.echo("📋 System Status")
    click.echo("=" * 40)
    
    try:
        venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            click.echo("❌ Virtual environment not found")
            click.echo("Run: python launcher.py setup")
            return
        
        cmd = [
            str(venv_python), "-c",
            """
import sys
sys.path.append('.')
from streamlit_adapters import get_system_status

try:
    status = get_system_status()
    
    print('🗄️  Database:')
    data = status['data']
    print(f'   Available: {"✅ Yes" if data["available"] else "❌ No"}')
    print(f'   Total draws: {data["count"]}')
    print(f'   Date range: {data["first_date"]} to {data["last_date"]}')
    
    print('\\n🤖 Models:')
    models = status['models']
    print(f'   Available: {"✅ Yes" if models["available"] else "❌ No"}')
    if models['available']:
        print(f'   Trained: {models["trained_at"]}')
        print(f'   Main model accuracy: {models["main_logloss"]:.4f}')
        print(f'   Star model accuracy: {models["star_logloss"]:.4f}')
    
    print('\\n💡 Recommendations:')
    for rec in status['recommendations']:
        print(f'   • {rec}')
        
except Exception as e:
    print(f'❌ Status error: {e}')
    import traceback
    traceback.print_exc()
"""
        ]
        
        subprocess.run(cmd)
        
    except Exception as e:
        click.echo(f"❌ Status error: {e}")

@cli.command()
def test():
    """Run comprehensive system tests"""
    click.echo("🧪 Running system tests...")
    click.echo("=" * 40)
    
    try:
        venv_python = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
        if not venv_python.exists():
            click.echo("❌ Please run setup first: python launcher.py setup")
            return
        
        # Run comprehensive test
        cmd = [str(venv_python), "comprehensive_test.py"]
        subprocess.run(cmd)
        
    except Exception as e:
        click.echo(f"❌ Test error: {e}")

if __name__ == '__main__':
    cli()