#!/bin/bash
# Deploy to Railway - Automated Script

echo "🚂 Deploying to Railway..."
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo ""
    echo "Install it first:"
    echo "  npm i -g @railway/cli"
    echo "  OR"
    echo "  brew install railway"
    echo ""
    exit 1
fi

# Check if logged in
echo "Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

echo "✅ Authenticated"
echo ""

# Check if project is linked
if [ ! -f ".railway_deploy" ]; then
    echo "🔗 Linking Railway project..."
    railway link
    touch .railway_deploy
fi

echo "📦 Committing latest changes..."
git add -A
git commit -m "Deploy to Railway - $(date '+%Y-%m-%d %H:%M:%S')" || echo "No changes to commit"

echo ""
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "📊 Checking deployment status..."
sleep 3
railway status

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Open your app:"
railway open

echo ""
echo "📋 Next steps:"
echo "1. Set environment variables (if not already set):"
echo "   railway variables set GROQ_API_KEY=\"your_key\""
echo "   railway variables set PIN_SALT=\"your_salt\""
echo "   railway variables set ENCRYPTION_KEY=\"your_key\""
echo ""
echo "2. Add database volume for persistence:"
echo "   Railway Dashboard → Storage → + New Volume → /app/data"
echo ""
echo "3. Check health:"
echo "   curl \$(railway domain)/api/health"
echo ""
echo "4. View logs:"
echo "   railway logs"
