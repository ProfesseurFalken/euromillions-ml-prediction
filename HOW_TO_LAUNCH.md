# 🚀 How to Launch EuroMillions ML System

This guide shows you different ways to run the EuroMillions ML Prediction System.

## 📦 Quick Start (Recommended)

### For First-Time Users:
1. **Double-click** `setup_and_run.bat`
   - This will set up everything and launch the app automatically
   - Your browser will open to http://localhost:8501

### For Regular Use:
1. **Double-click** `launch_app.bat`
   - Quick launch of the web application
   - Opens browser automatically

## 🎯 All Available Launchers

### 1. **Simple Batch Files** (Windows)
Perfect for users who prefer point-and-click:

| File | Purpose |
|------|---------|
| `setup_and_run.bat` | First-time setup + launch |
| `launch_app.bat` | Quick launch of web app |
| `test_system.bat` | Run system tests |

**Usage:** Just double-click the file you want!

### 2. **Advanced Python Launcher** (All Platforms)
Perfect for power users and command-line enthusiasts:

```bash
# See all available commands
python launcher.py --help

# First-time setup
python launcher.py setup

# Launch web application
python launcher.py run
python launcher.py run --port 8502 --no-browser

# Generate predictions directly in terminal
python launcher.py predict
python launcher.py predict --method topk --count 5
python launcher.py predict --method hybrid --count 10

# System operations
python launcher.py status          # Check system health
python launcher.py update          # Update lottery data
python launcher.py train           # Retrain ML models
python launcher.py test            # Run comprehensive tests
```

### 3. **Direct Python Execution** (Developers)
For development and customization:

```bash
# Activate virtual environment first
.venv\Scripts\activate

# Launch main application
python main.py

# Use Streamlit directly
streamlit run ui\streamlit_app.py --server.port 8501

# Run specific tests
python comprehensive_test.py
python -m pytest test_*.py
```

## 🌐 Web Interface Access

Once launched, the application is available at:
- **Primary:** http://localhost:8501
- **Custom port:** http://localhost:YOUR_PORT (if specified)

## 🎰 Prediction Methods

When generating tickets, you can choose from:

| Method | Description | Best For |
|--------|-------------|----------|
| `random` | Weighted random selection | Balanced approach |
| `topk` | Highest probability numbers | Maximum ML confidence |
| `hybrid` | Mix of top predictions + randomness | Best of both worlds |

## 🔧 Troubleshooting

### Common Issues:

**"Port already in use"**
```bash
# Kill existing processes
taskkill /F /IM python.exe
# Or use a different port
python launcher.py run --port 8502
```

**"Virtual environment not found"**
```bash
# Run setup first
python launcher.py setup
# Or use the batch file
setup_and_run.bat
```

**"Missing dependencies"**
```bash
# Reinstall everything
python launcher.py setup
```

## 📊 System Requirements

- **Python:** 3.9+ required
- **Memory:** 2GB+ recommended
- **Storage:** 500MB for models and data
- **Network:** Internet connection for data updates

## 🎉 Quick Examples

**Generate 5 lucky numbers:**
```bash
python launcher.py predict --count 5
```

**Check if system is healthy:**
```bash
python launcher.py status
```

**Update with latest lottery results:**
```bash
python launcher.py update
```

**Launch with custom settings:**
```bash
python launcher.py run --port 9000 --debug
```

---

## 🏆 Pro Tips

1. **Use batch files** for simplicity
2. **Use Python launcher** for flexibility  
3. **Check status** before generating predictions
4. **Update data** regularly for best results
5. **Try different methods** to compare results

Happy predicting! 🍀