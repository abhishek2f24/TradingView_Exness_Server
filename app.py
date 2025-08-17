from flask import Flask, request, jsonify
import json
import os
from datetime import datetime
import requests

app = Flask(__name__)

# Store signals in memory (for free hosting without database)
signals = []

@app.route('/', methods=['GET'])
def home():
    return "TradingView to Exness Bridge is Running!"

@app.route('/webhook', methods=['POST'])
def trading_webhook():
    try:
        # Get the JSON data from TradingView
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['action', 'symbol', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create signal object
        signal = {
            "timestamp": datetime.now().isoformat(),
            "action": data['action'],  # "buy" or "sell"
            "symbol": data['symbol'],  # "EURUSD", "GBPUSD", etc.
            "price": data['price'],
            "quantity": data.get('quantity', 0.01),  # Default lot size
            "stop_loss": data.get('stop_loss'),
            "take_profit": data.get('take_profit'),
            "processed": False
        }
        
        # Store signal (in production, use database)
        signals.append(signal)
        
        # Keep only last 100 signals to prevent memory issues
        if len(signals) > 100:
            signals.pop(0)
        
        print(f"Signal received: {signal}")
        
        return jsonify({
            "status": "success",
            "message": "Signal received",
            "signal": signal
        }), 200
        
    except Exception as e:
        print(f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/signals', methods=['GET'])
def get_signals():
    """Endpoint for MT4 EA to check for new signals"""
    try:
        # Return unprocessed signals
        unprocessed = [s for s in signals if not s['processed']]
        return jsonify({"signals": unprocessed}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mark_processed', methods=['POST'])
def mark_processed():
    """Mark signal as processed by MT4 EA"""
    try:
        data = request.get_json()
        timestamp = data.get('timestamp')
        
        # Find and mark signal as processed
        for signal in signals:
            if signal['timestamp'] == timestamp:
                signal['processed'] = True
                break
        
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['POST'])
def test_signal():
    """Test endpoint to manually send a signal"""
    test_signal = {
        "action": "buy",
        "symbol": "EURUSD",
        "price": 1.0850,
        "quantity": 0.01
    }
    
    # Simulate webhook call
    return trading_webhook_internal(test_signal)

def trading_webhook_internal(data):
    signal = {
        "timestamp": datetime.now().isoformat(),
        "action": data['action'],
        "symbol": data['symbol'],
        "price": data['price'],
        "quantity": data.get('quantity', 0.01),
        "stop_loss": data.get('stop_loss'),
        "take_profit": data.get('take_profit'),
        "processed": False
    }
    
    signals.append(signal)
    return jsonify({"status": "success", "signal": signal}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
