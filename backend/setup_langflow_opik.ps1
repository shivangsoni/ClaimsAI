# ClaimsAI LangFlow + Opik Setup Script for Windows
# Run this script in PowerShell as Administrator

Write-Host "🤖 ClaimsAI LangFlow + Opik Setup" -ForegroundColor Green
Write-Host "=" * 40

# Check Python installation
Write-Host "`n🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
        
        # Check if version is 3.8+
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
                Write-Host "❌ Python 3.8+ required. Current: $pythonVersion" -ForegroundColor Red
                exit 1
            }
        }
    } else {
        Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error checking Python: $_" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
try {
    Write-Host "Installing LangFlow..." -ForegroundColor Cyan
    python -m pip install --upgrade pip
    python -m pip install langflow>=1.0.0
    
    Write-Host "Installing LangChain dependencies..." -ForegroundColor Cyan
    python -m pip install langchain>=0.1.0 langchain-openai>=0.1.0 langchain-community>=0.0.0
    
    Write-Host "Installing Opik..." -ForegroundColor Cyan
    python -m pip install opik>=0.1.0
    
    Write-Host "Installing additional dependencies..." -ForegroundColor Cyan
    python -m pip install pydantic>=2.0.0 httpx>=0.25.0
    
    Write-Host "✅ All dependencies installed successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Error installing dependencies: $_" -ForegroundColor Red
    Write-Host "Try running: python -m pip install -r requirements.txt" -ForegroundColor Yellow
}

# Setup environment file
Write-Host "`n🔧 Setting up environment configuration..." -ForegroundColor Yellow
$envFile = ".env"
$envContent = @"
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LangFlow Configuration
LANGFLOW_URL=http://localhost:7860
LANGFLOW_FLOW_ID=claims-analysis-flow

# Opik Configuration
OPIK_PROJECT_NAME=claimsai-document-analysis
OPIK_API_KEY=your_opik_api_key_here
"@

if (Test-Path $envFile) {
    $existingContent = Get-Content $envFile -Raw
    if ($existingContent -notmatch "LANGFLOW_URL") {
        Add-Content $envFile "`n$envContent"
        Write-Host "✅ LangFlow/Opik configuration added to existing .env file" -ForegroundColor Green
    } else {
        Write-Host "✅ LangFlow configuration already exists in .env" -ForegroundColor Green
    }
} else {
    Set-Content $envFile $envContent
    Write-Host "✅ Created .env file with LangFlow/Opik configuration" -ForegroundColor Green
}

# Check if LangFlow is already running
Write-Host "`n🌊 Checking LangFlow status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:7860/health" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ LangFlow is already running at http://localhost:7860" -ForegroundColor Green
} catch {
    Write-Host "⚠️  LangFlow is not running. Starting LangFlow..." -ForegroundColor Yellow
    
    # Start LangFlow in background
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "langflow run --host 0.0.0.0 --port 7860" -WindowStyle Minimized
    
    Write-Host "🚀 LangFlow started in background window" -ForegroundColor Green
    Write-Host "   Access the UI at: http://localhost:7860" -ForegroundColor Cyan
    
    # Wait for LangFlow to start
    Write-Host "   Waiting for LangFlow to initialize..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:7860/health" -TimeoutSec 10 -ErrorAction Stop
        Write-Host "✅ LangFlow is now running!" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  LangFlow may still be starting up. Check http://localhost:7860" -ForegroundColor Yellow
    }
}

# Run setup script
Write-Host "`n🔧 Running Python setup script..." -ForegroundColor Yellow
try {
    python setup_langflow_opik.py
    Write-Host "✅ Python setup completed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Python setup script not found or failed" -ForegroundColor Yellow
    Write-Host "   You can run it manually: python setup_langflow_opik.py" -ForegroundColor Cyan
}

# Test integration
Write-Host "`n🧪 Testing integration..." -ForegroundColor Yellow
try {
    python test_langflow_integration.py
    Write-Host "✅ Integration test completed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Integration test failed or script not found" -ForegroundColor Yellow
    Write-Host "   You can run it manually: python test_langflow_integration.py" -ForegroundColor Cyan
}

# Display next steps
Write-Host "`n🎉 Setup completed!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Set your OpenAI API key in the .env file" -ForegroundColor Cyan
Write-Host "2. Open http://localhost:7860 and import langflow_config.json" -ForegroundColor Cyan
Write-Host "2. Configure your OpenAI API key in the LangFlow ChatOpenAI node (GPT-5)" -ForegroundColor Cyan
Write-Host "4. Test document processing in your ClaimsAI application" -ForegroundColor Cyan

Write-Host "`n🔗 Useful URLs:" -ForegroundColor Yellow
Write-Host "   LangFlow UI: http://localhost:7860" -ForegroundColor Cyan
Write-Host "   API Status: http://localhost:5000/api/integration/status" -ForegroundColor Cyan
Write-Host "   ClaimsAI Frontend: http://localhost:3000" -ForegroundColor Cyan

Write-Host "`n💡 Troubleshooting:" -ForegroundColor Yellow
Write-Host "   - If LangFlow fails to start, try: langflow run --host 0.0.0.0 --port 7860" -ForegroundColor Cyan
Write-Host "   - Check integration status with: python test_langflow_integration.py" -ForegroundColor Cyan
Write-Host "   - View logs in the LangFlow UI and Opik dashboard" -ForegroundColor Cyan

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")