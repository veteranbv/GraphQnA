#!/bin/bash
# Secure deployment script for GraphQnA

set -e # Exit on error

echo "GraphQnA Secure Deployment Helper"
echo "================================="

# Generate a new API key if needed
if [[ "$1" == "--new-key" ]]; then
  NEW_API_KEY=$(openssl rand -hex 32)
  echo "Generated new API key: ${NEW_API_KEY:0:5}..."
  echo
  echo "Important: Update your .env file with this new API key:"
  echo "GRAPHQNA_API_KEY=$NEW_API_KEY"
  echo
  echo "Also update your production server's .env file with the same key."
  exit 0
fi

# Check if API key is configured
if grep -q "GRAPHQNA_API_KEY=" .env; then
  API_KEY=$(grep "GRAPHQNA_API_KEY=" .env | cut -d'=' -f2)
  echo "API key is configured: ${API_KEY:0:5}..."
else
  echo "Error: GRAPHQNA_API_KEY not found in .env file"
  echo "Run this script with --new-key to generate a new API key"
  exit 1
fi

# Security checks
echo
echo "Security checklist:"
echo "==================="

# Check API key length
if [[ ${#API_KEY} -lt 32 ]]; then
  echo "❌ API key is too short (less than 32 characters)"
else
  echo "✅ API key length is good (${#API_KEY} characters)"
fi

# Check for slack integration
if grep -q "SLACK_BOT_TOKEN=" .env; then
  echo "✅ Slack integration is configured"
else
  echo "❌ Slack integration is not configured"
fi

# Check domain configuration
if [[ -f "./graphqna/config/domain_config.py" ]]; then
  echo "✅ Domain configuration is present"
else
  echo "❌ Domain configuration is missing"
fi

echo
echo "Deployment reminder:"
echo "==================="
echo "1. Make sure to update your production server's .env file with your API key"
echo "2. Add proper HTTPS using a reverse proxy or API Gateway"
echo "3. Restrict access to your server using appropriate firewall rules"
echo "4. Enable monitoring for your services"
echo
echo "To test API key authentication on your server:"
echo "curl https://your-server/api/health"
echo "curl -H \"X-API-Key: $API_KEY\" https://your-server/api/info"
echo

echo "Deployment completed!"
