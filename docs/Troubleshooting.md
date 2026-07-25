# Troubleshooting Guide

## 1. Backend Issues

### AI Provider Errors
- **Error**: `AI Provider Rate Limit Reached`
- **Solution**: The system should automatically switch to a fallback. If all fail, check your API keys or wait for the cooldown.
- **Error**: `Timeout connecting to Groq`
- **Solution**: Check your internet connection or verify if Groq's status page reports an outage.

### Database Errors
- **Error**: `OperationalError: no such table`
- **Solution**: Run migrations: `alembic upgrade head`.

## 2. Frontend Issues

### White Screen on Load
- **Cause**: Usually a failed API fetch or a JavaScript error.
- **Check**: Open Browser DevTools (F12) and check the "Console" tab. Verify if `npm run dev` is running and the backend is up.

### Styles Not Loading
- **Solution**: Ensure `tailwind.config.js` is correct and run `npm run build` or `npm run dev`.

## 3. Scraper Issues
- **Problem**: No jobs found for a valid query.
- **Solution**: Scrapers are sensitive to IP blocks. If using Apify, ensure you have sufficient credits. If using local scrapers, check if the target site (e.g., LinkedIn) has changed its layout.
