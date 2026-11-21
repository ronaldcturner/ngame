# NGAME UI Troubleshooting Guide

## 🚨 **Common Installation Issues**

### **1. "Getting requirements to build wheel ... error"**

This error occurs when Python packages require compilation and system dependencies are missing.

#### **Solution 1: Use the Installation Script**
```bash
# Make the script executable
chmod +x install.sh

# Run the installation script
./install.sh
```

#### **Solution 2: Install System Dependencies**

**On macOS:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required dependencies
brew install openssl python3

# Upgrade pip and setuptools
pip3 install --upgrade pip setuptools wheel
```

**On Ubuntu/Debian:**
```bash
# Update package list
sudo apt-get update

# Install build dependencies
sudo apt-get install -y python3-dev build-essential libssl-dev libffi-dev

# Upgrade pip
pip3 install --upgrade pip setuptools wheel
```

**On CentOS/RHEL:**
```bash
# Install build dependencies
sudo yum install -y python3-devel gcc openssl-devel libffi-devel

# Upgrade pip
pip3 install --upgrade pip setuptools wheel
```

#### **Solution 3: Use Minimal Installation**
```bash
# Install only essential packages
pip3 install -r requirements-minimal.txt

# Run the simplified version
python3 app-simple.py
```

#### **Solution 4: Use Virtual Environment**
```bash
# Create virtual environment
python3 -m venv ngame_env

# Activate virtual environment
source ngame_env/bin/activate  # On Windows: ngame_env\Scripts\activate

# Upgrade pip in virtual environment
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt
```

### **2. "Permission denied" Errors**

#### **Solution: Use --user Flag**
```bash
pip3 install --user -r requirements.txt
```

#### **Solution: Fix Permissions**
```bash
# Fix directory permissions
chmod 755 ngame_ui/
chmod 755 ngame_ui/output/
chmod 755 ngame_ui/uploads/
chmod 755 ngame_ui/logs/
```

### **3. "Module not found" Errors**

#### **Solution: Check Python Path**
```bash
# Check Python version
python3 --version

# Check pip installation
pip3 list

# Install missing modules individually
pip3 install Flask
pip3 install requests
```

### **4. "Port already in use" Error**

#### **Solution: Use Different Port**
```bash
# Run on different port
python3 app.py --port 5001

# Or modify the app.py file
# Change: app.run(port=5000) to app.run(port=5001)
```

## 🔧 **Runtime Issues**

### **1. "NGAME components not available"**

This is normal if you're running in demo mode without the full NGAME system.

#### **Solution: Install NGAME Components**
```bash
# Ensure NGAME components are in parent directory
ls ../ngame_ontology_workflow.py
ls ../quickbooks_chart_of_accounts_extractor.py
ls ../quickbooks_chart_of_accounts_creator.py

# If missing, the UI will run in demo mode
```

### **2. "WebSocket connection failed"**

#### **Solution: Use Simplified Version**
```bash
# Run the simplified version without WebSocket dependencies
python3 app-simple.py
```

### **3. "Template not found" Errors**

#### **Solution: Check Template Directory**
```bash
# Ensure templates directory exists
ls ngame_ui/templates/

# Create missing templates
mkdir -p ngame_ui/templates/
```

### **4. "Import Error" for NGAME Components**

#### **Solution: Check Python Path**
```python
# Add parent directory to Python path
import sys
sys.path.append('..')

# Or set PYTHONPATH environment variable
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.."
```

## 🛠 **Alternative Installation Methods**

### **Method 1: Conda Installation**
```bash
# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create conda environment
conda create -n ngame python=3.9
conda activate ngame

# Install packages
conda install flask requests
pip install Flask-SocketIO
```

### **Method 2: Docker Installation**
```dockerfile
# Create Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

```bash
# Build and run Docker container
docker build -t ngame-ui .
docker run -p 5000:5000 ngame-ui
```

### **Method 3: Manual Installation**
```bash
# Install packages one by one
pip3 install Flask
pip3 install requests
pip3 install Werkzeug
pip3 install Jinja2
pip3 install MarkupSafe
pip3 install itsdangerous
pip3 install click
pip3 install blinker

# Optional packages (for full functionality)
pip3 install Flask-SocketIO
pip3 install python-socketio
pip3 install python-engineio
```

## 🔍 **Debugging Steps**

### **1. Enable Debug Mode**
```bash
# Set debug environment variables
export FLASK_DEBUG=1
export FLASK_ENV=development

# Run with debug output
python3 app.py
```

### **2. Check Logs**
```bash
# View application logs
tail -f logs/ngame_ui.log

# Check system logs
journalctl -u ngame-ui -f
```

### **3. Test Individual Components**
```python
# Test Flask installation
python3 -c "import flask; print('Flask version:', flask.__version__)"

# Test NGAME components
python3 -c "import sys; sys.path.append('..'); from ngame_ontology_workflow import NGAMEOntologyWorkflow; print('NGAME available')"
```

## 📋 **System Requirements**

### **Minimum Requirements**
- Python 3.8+
- 2GB RAM
- 1GB disk space
- Modern web browser

### **Recommended Requirements**
- Python 3.9+
- 4GB RAM
- 2GB disk space
- Chrome/Firefox/Safari/Edge

### **Supported Operating Systems**
- macOS 10.14+
- Ubuntu 18.04+
- CentOS 7+
- Windows 10+ (with WSL recommended)

## 🆘 **Getting Help**

### **1. Check Common Issues**
- Review this troubleshooting guide
- Check the README.md file
- Look for similar issues in the logs

### **2. Enable Verbose Logging**
```python
# Add to app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **3. Test Minimal Setup**
```bash
# Test with minimal requirements
pip3 install Flask requests
python3 app-simple.py
```

### **4. Check Dependencies**
```bash
# List installed packages
pip3 list

# Check for conflicts
pip3 check
```

## 🔄 **Reset and Clean Installation**

### **Complete Reset**
```bash
# Remove virtual environment
rm -rf ngame_env/

# Remove installed packages
pip3 uninstall -r requirements.txt -y

# Clear pip cache
pip3 cache purge

# Reinstall from scratch
python3 -m venv ngame_env
source ngame_env/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### **Clean Python Environment**
```bash
# Remove all user-installed packages
pip3 freeze | xargs pip3 uninstall -y

# Reinstall only what you need
pip3 install Flask requests
```

---

**Note**: Most installation issues can be resolved by using the installation script (`./install.sh`) or the simplified version (`python3 app-simple.py`). The UI will work in demo mode even without the full NGAME system components. 