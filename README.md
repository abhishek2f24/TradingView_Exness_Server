# TradingView to Exness Bridge

Webhook bridge that receives TradingView alerts and executes trades on Exness via MT4/MT5.

## Features
- Receives TradingView webhook alerts
- Stores signals for MT4 EA to process
- Simple web interface for monitoring

## Endpoints
- `POST /webhook` - Receive TradingView alerts
- `GET /signals` - Get pending signals for MT4
- `POST /test` - Create test signal

## Setup
1. Deploy to Render/Heroku
2. Set up TradingView alerts to point to your webhook URL
3. Install MT4 Expert Advisor to process signals
