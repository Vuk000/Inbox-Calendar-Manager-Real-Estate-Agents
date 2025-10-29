# ENV Restoration Helper Script
# This script will help you quickly restore your .env file with minimal typing

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host "        .ENV FILE RESTORATION HELPER" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "`nI sincerely apologize for overwriting your .env file." -ForegroundColor Yellow
Write-Host "This script will help you restore it as quickly as possible.`n" -ForegroundColor Yellow

# Read the current .env to preserve the structure
$envPath = ".env"
$envContent = Get-Content $envPath -Raw

Write-Host "REQUIRED API KEYS (please paste when prompted):`n" -ForegroundColor Green

# Anthropic API Key
Write-Host "1. ANTHROPIC_API_KEY" -ForegroundColor Cyan
Write-Host "   (should start with sk-ant-)" -ForegroundColor Gray
$anthropicKey = Read-Host "   Paste your Anthropic key"
if ($anthropicKey) {
    $envContent = $envContent -replace 'ANTHROPIC_API_KEY=.*', "ANTHROPIC_API_KEY=$anthropicKey"
}

# Pinecone API Key
Write-Host "`n2. PINECONE_API_KEY" -ForegroundColor Cyan
$pineconeKey = Read-Host "   Paste your Pinecone API key"
if ($pineconeKey) {
    $envContent = $envContent -replace 'PINECONE_API_KEY=.*', "PINECONE_API_KEY=$pineconeKey"
}

# Pinecone Environment
Write-Host "`n3. PINECONE_ENVIRONMENT" -ForegroundColor Cyan
Write-Host "   (e.g., us-east-1-aws, gcp-starter, etc.)" -ForegroundColor Gray
$pineconeEnv = Read-Host "   Paste your Pinecone environment"
if ($pineconeEnv) {
    $envContent = $envContent -replace 'PINECONE_ENVIRONMENT=.*', "PINECONE_ENVIRONMENT=$pineconeEnv"
}

# Google Client ID
Write-Host "`n4. GOOGLE_CLIENT_ID" -ForegroundColor Cyan
Write-Host "   (ends with .apps.googleusercontent.com)" -ForegroundColor Gray
$googleClientId = Read-Host "   Paste your Google Client ID"
if ($googleClientId) {
    $envContent = $envContent -replace 'GOOGLE_CLIENT_ID=.*', "GOOGLE_CLIENT_ID=$googleClientId"
}

# Google Client Secret
Write-Host "`n5. GOOGLE_CLIENT_SECRET" -ForegroundColor Cyan
$googleSecret = Read-Host "   Paste your Google Client Secret"
if ($googleSecret) {
    $envContent = $envContent -replace 'GOOGLE_CLIENT_SECRET=.*', "GOOGLE_CLIENT_SECRET=$googleSecret"
}

# Database URL
Write-Host "`n6. DATABASE_URL" -ForegroundColor Cyan
Write-Host "   Options:" -ForegroundColor Gray
Write-Host "   A) PostgreSQL: postgresql://user:pass@localhost:5432/realinbox_db" -ForegroundColor Gray
Write-Host "   B) SQLite (quick): sqlite:///./realinbox_test.db" -ForegroundColor Gray
$dbUrl = Read-Host "   Paste your Database URL (or press Enter for SQLite)"
if (-not $dbUrl) {
    $dbUrl = "sqlite:///./realinbox_test.db"
}
$envContent = $envContent -replace 'DATABASE_URL=.*', "DATABASE_URL=$dbUrl"

# Optional: Microsoft credentials
Write-Host "`n=== OPTIONAL (press Enter to skip) ===" -ForegroundColor Yellow
$addMicrosoft = Read-Host "`nAdd Microsoft OAuth credentials? (y/N)"
if ($addMicrosoft -eq 'y' -or $addMicrosoft -eq 'Y') {
    Write-Host "MICROSOFT_CLIENT_ID" -ForegroundColor Cyan
    $msClientId = Read-Host "   Paste"
    if ($msClientId) {
        $envContent = $envContent -replace 'MICROSOFT_CLIENT_ID=.*', "MICROSOFT_CLIENT_ID=$msClientId"
    }
    
    Write-Host "MICROSOFT_CLIENT_SECRET" -ForegroundColor Cyan
    $msSecret = Read-Host "   Paste"
    if ($msSecret) {
        $envContent = $envContent -replace 'MICROSOFT_CLIENT_SECRET=.*', "MICROSOFT_CLIENT_SECRET=$msSecret"
    }
}

# Optional: Twilio
$addTwilio = Read-Host "`nAdd Twilio credentials? (y/N)"
if ($addTwilio -eq 'y' -or $addTwilio -eq 'Y') {
    Write-Host "TWILIO_ACCOUNT_SID" -ForegroundColor Cyan
    $twilioSid = Read-Host "   Paste"
    if ($twilioSid) {
        $envContent = $envContent -replace 'TWILIO_ACCOUNT_SID=.*', "TWILIO_ACCOUNT_SID=$twilioSid"
    }
    
    Write-Host "TWILIO_AUTH_TOKEN" -ForegroundColor Cyan
    $twilioToken = Read-Host "   Paste"
    if ($twilioToken) {
        $envContent = $envContent -replace 'TWILIO_AUTH_TOKEN=.*', "TWILIO_AUTH_TOKEN=$twilioToken"
    }
    
    Write-Host "TWILIO_PHONE_NUMBER" -ForegroundColor Cyan
    $twilioPhone = Read-Host "   Paste"
    if ($twilioPhone) {
        $envContent = $envContent -replace 'TWILIO_PHONE_NUMBER=.*', "TWILIO_PHONE_NUMBER=$twilioPhone"
    }
}

# Optional: AWS
$addAWS = Read-Host "`nAdd AWS credentials? (y/N)"
if ($addAWS -eq 'y' -or $addAWS -eq 'Y') {
    Write-Host "AWS_ACCESS_KEY_ID" -ForegroundColor Cyan
    $awsKeyId = Read-Host "   Paste"
    if ($awsKeyId) {
        $envContent = $envContent -replace 'AWS_ACCESS_KEY_ID=.*', "AWS_ACCESS_KEY_ID=$awsKeyId"
    }
    
    Write-Host "AWS_SECRET_ACCESS_KEY" -ForegroundColor Cyan
    $awsSecret = Read-Host "   Paste"
    if ($awsSecret) {
        $envContent = $envContent -replace 'AWS_SECRET_ACCESS_KEY=.*', "AWS_SECRET_ACCESS_KEY=$awsSecret"
    }
    
    Write-Host "AWS_S3_BUCKET" -ForegroundColor Cyan
    $awsBucket = Read-Host "   Paste"
    if ($awsBucket) {
        $envContent = $envContent -replace 'AWS_S3_BUCKET=.*', "AWS_S3_BUCKET=$awsBucket"
    }
}

# Save the updated .env file
Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host "Saving updated .env file..." -ForegroundColor Yellow
$envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline

Write-Host "`n✅ .env file has been updated!" -ForegroundColor Green
Write-Host "`nVerifying configuration..." -ForegroundColor Cyan

# Test if config loads
try {
    python -c "from app.config import settings; print('✅ Configuration loaded successfully!')"
    Write-Host "`n=====================================================================" -ForegroundColor Green
    Write-Host "SUCCESS! Your .env file is restored and working!" -ForegroundColor Green
    Write-Host "=====================================================================" -ForegroundColor Green
    Write-Host "`nNext steps:" -ForegroundColor Cyan
    Write-Host "1. Run migrations: alembic upgrade head" -ForegroundColor White
    Write-Host "2. Start server: python -m app.main" -ForegroundColor White
    Write-Host "3. Run tests: pytest tests/ -v" -ForegroundColor White
} catch {
    Write-Host "`n⚠️ Configuration validation failed. Please check the values." -ForegroundColor Yellow
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host "`nYou can manually edit the .env file if needed." -ForegroundColor Yellow
}

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host

