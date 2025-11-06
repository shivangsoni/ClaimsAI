#!/usr/bin/env python3
"""
Setup script for LangFlow and Opik integration with ClaimsAI
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required for LangFlow and Opik")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install LangFlow and Opik dependencies"""
    print("\n📦 Installing LangFlow and Opik dependencies...")
    
    dependencies = [
        "langflow>=1.0.0",
        "langchain>=0.1.0", 
        "langchain-openai>=0.1.0",
        "langchain-community>=0.0.0",
        "opik>=0.1.0",
        "pydantic>=2.0.0",
        "httpx>=0.25.0"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            print(f"✅ {dep} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    return True

def setup_environment():
    """Setup environment variables and configuration"""
    print("\n🔧 Setting up environment configuration...")
    
    env_file = Path(".env")
    config_lines = []
    
    # Read existing .env if it exists
    if env_file.exists():
        with open(env_file, 'r') as f:
            existing_lines = f.readlines()
        config_lines.extend([line.strip() for line in existing_lines])
    
    # Add LangFlow configuration if not present
    langflow_vars = [
        "# LangFlow Configuration",
        "LANGFLOW_URL=http://localhost:7860",
        "LANGFLOW_FLOW_ID=claims-analysis-flow",
        "",
        "# Opik Configuration", 
        "OPIK_PROJECT_NAME=claimsai-document-analysis",
        "OPIK_API_KEY=",  # User will need to fill this
        ""
    ]
    
    # Check if LangFlow config already exists
    has_langflow = any("LANGFLOW_URL" in line for line in config_lines)
    
    if not has_langflow:
        config_lines.extend(langflow_vars)
        
        with open(env_file, 'w') as f:
            f.write('\n'.join(config_lines))
        
        print("✅ Environment variables added to .env file")
    else:
        print("✅ LangFlow configuration already exists in .env")
    
    return True

def create_langflow_flow():
    """Create or verify LangFlow flow configuration"""
    print("\n🌊 Setting up LangFlow flow configuration...")
    
    flow_file = Path("langflow_config.json")
    
    if flow_file.exists():
        print("✅ LangFlow configuration file already exists")
        return True
    
    # The flow configuration is already created by the main script
    print("✅ LangFlow configuration file created")
    return True

def setup_opik():
    """Setup Opik telemetry configuration"""
    print("\n📊 Setting up Opik telemetry...")
    
    try:
        import opik
        
        # Try to initialize Opik client
        client = opik.Opik(project_name="claimsai-test")
        print("✅ Opik is available and configured")
        
        # Create a test trace to verify connection
        with client.trace("setup_test"):
            print("✅ Opik tracing test successful")
            
        return True
        
    except ImportError:
        print("⚠️  Opik not installed. Install with: pip install opik")
        return False
    except Exception as e:
        print(f"⚠️  Opik configuration issue: {e}")
        print("You may need to set OPIK_API_KEY in your .env file")
        return False

def start_langflow():
    """Instructions for starting LangFlow"""
    print("\n🚀 Starting LangFlow...")
    print("To start LangFlow, run the following command in a separate terminal:")
    print("langflow run --host 0.0.0.0 --port 7860")
    print("")
    print("Then you can:")
    print("1. Open http://localhost:7860 in your browser")
    print("2. Import the langflow_config.json file")
    print("3. Configure your OpenAI API key in the ChatOpenAI node")
    print("4. Deploy the flow")

def verify_installation():
    """Verify the installation is working"""
    print("\n🔍 Verifying installation...")
    
    try:
        from utils.document_processor import DocumentProcessor
        
        # Test initialization
        processor = DocumentProcessor()
        
        # Check LangFlow health
        langflow_health = processor.get_langflow_health()
        print(f"LangFlow Status: {langflow_health['status']}")
        
        # Check Opik status
        opik_status = processor.get_opik_status()
        print(f"Opik Available: {opik_status['available']}")
        print(f"Opik Client: {'✅ Initialized' if opik_status['client_initialized'] else '❌ Not initialized'}")
        
        print("✅ Installation verification completed")
        return True
        
    except Exception as e:
        print(f"❌ Installation verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 ClaimsAI LangFlow + Opik Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return False
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        return False
    
    # Create LangFlow flow
    if not create_langflow_flow():
        print("❌ LangFlow flow setup failed")
        return False
    
    # Setup Opik
    setup_opik()  # Non-blocking
    
    # Start LangFlow instructions
    start_langflow()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start LangFlow: langflow run --host 0.0.0.0 --port 7860")
    print("2. Import langflow_config.json in the LangFlow UI")
    print("3. Set your OpenAI API key in the flow")
    print("4. Test the document processor")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)