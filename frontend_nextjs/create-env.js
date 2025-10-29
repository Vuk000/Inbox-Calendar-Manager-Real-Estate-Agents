const fs = require('fs');
const path = require('path');

const envContent = `# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# WebSocket Configuration
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# App Configuration
NEXT_PUBLIC_APP_NAME=AgentFlow
NEXT_PUBLIC_APP_ENV=development
`;

const envPath = path.join(__dirname, '.env.local');

if (fs.existsSync(envPath)) {
  console.log('✅ .env.local already exists');
} else {
  fs.writeFileSync(envPath, envContent);
  console.log('✅ Created .env.local file');
}

console.log('\n📋 Environment file contents:');
console.log(envContent);
console.log('\n🚀 Run "npm run dev" to start the development server');

