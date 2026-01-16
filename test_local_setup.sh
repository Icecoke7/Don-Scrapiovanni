#!/bin/bash

echo "=========================================="
echo "Local Setup Verification"
echo "=========================================="
echo ""

# Check 1: .env file exists
echo "1. Checking .env file..."
if [ -f .env ]; then
    echo "   ✅ .env file exists"
    if grep -q "TELEGRAM_TOKEN" .env && grep -q "TELEGRAM_CHAT_ID" .env; then
        echo "   ✅ Telegram variables found in .env"
    else
        echo "   ⚠️  Telegram variables missing in .env"
    fi
else
    echo "   ❌ .env file missing!"
    echo "   Create it: cp .env.example .env"
    exit 1
fi

# Check 2: .env is gitignored
echo ""
echo "2. Checking .env is gitignored..."
if git check-ignore .env > /dev/null 2>&1; then
    echo "   ✅ .env is properly gitignored (safe!)"
else
    echo "   ⚠️  .env is NOT gitignored - add it to .gitignore!"
fi

# Check 3: Docker Compose can read .env
echo ""
echo "3. Checking Docker Compose configuration..."
if docker compose config 2>/dev/null | grep -q "TELEGRAM_TOKEN"; then
    echo "   ✅ Docker Compose can read environment variables"
else
    echo "   ⚠️  Docker Compose might not be reading .env correctly"
fi

# Check 4: Containers status
echo ""
echo "4. Checking container status..."
if docker ps --filter "name=staatsoper-scraper" --format "{{.Names}}" | grep -q "staatsoper-scraper"; then
    echo "   ✅ Container is running"
    echo ""
    echo "   Recent logs:"
    docker logs staatsoper-scraper --tail 5 2>&1 | grep -i staatsoper || echo "   (No recent scraper activity)"
else
    echo "   ℹ️  Container is not running"
    echo "   Start it with: docker compose up -d"
fi

# Check 5: Environment variables in container (if running)
echo ""
echo "5. Checking environment variables in container..."
if docker ps --filter "name=staatsoper-scraper" --format "{{.Names}}" | grep -q "staatsoper-scraper"; then
    if docker exec staatsoper-scraper env 2>/dev/null | grep -q "TELEGRAM_TOKEN="; then
        TOKEN_SET=$(docker exec staatsoper-scraper env 2>/dev/null | grep "TELEGRAM_TOKEN=" | cut -d= -f2)
        if [ -n "$TOKEN_SET" ] && [ "$TOKEN_SET" != "" ]; then
            echo "   ✅ TELEGRAM_TOKEN is set in container"
        else
            echo "   ⚠️  TELEGRAM_TOKEN is empty in container"
        fi
    else
        echo "   ⚠️  TELEGRAM_TOKEN not found in container environment"
    fi
else
    echo "   ℹ️  Container not running - cannot check environment variables"
fi

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
echo "Your local setup should work if:"
echo "  ✅ .env file exists with your tokens"
echo "  ✅ .env is gitignored"
echo "  ✅ Docker Compose can read .env"
echo ""
echo "To test the scraper:"
echo "  1. Start containers: docker compose up -d"
echo "  2. Check logs: docker logs staatsoper-scraper -f | grep -i staatsoper"
echo "  3. Wait for 09:30 AM Austria time, or modify the schedule for testing"
echo ""
echo "Your tokens are safe because .env is gitignored!"
echo ""
