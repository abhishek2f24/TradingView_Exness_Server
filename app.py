from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage for signals (works for free hosting)
signals = []

@app.route('/', methods=['GET'])
def home():
    return """
    <h1>TradingView to Exness Bridge</h1>
    <p>Status: Running ✅</p>
    <h2>Endpoints:</h2>
    <ul>
        <li><strong>POST /webhook</strong> - Receive TradingView alerts</li>
        <li><strong>GET /signals</strong> - Check pending signals</li>
        <li><strong>POST /test</strong> - Send test signal</li>
    </ul>
    <h2>Recent Signals:</h2>
    <div id="signals">
    """ + str(len(signals)) + " signals received" + """
    </div>
    """

@app.route('/webhook', methods=['POST'])
def trading_webhook():
    try:
        # Get JSON data from TradingView
        data = request.get_json()
        
        print(f"Received webhook data: {data}")
        
        # Validate data
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Extract trading information
        action = data.get('action', '').lower()
        symbol = data.get('symbol', '')
        price = data.get('price', 0)
        quantity = data.get('quantity', 0.01)
        
        # Validate required fields
        if not action or not symbol:
            return jsonify({"error": "Missing action or symbol"}), 400
            
        if action not in ['buy', 'sell']:
            return jsonify({"error": "Action must be 'buy' or 'sell'"}), 400
        
        # Create signal object
        signal = {
            "id": len(signals) + 1,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "symbol": symbol.upper(),
            "price": float(price),
            "quantity": float(quantity),
            "stop_loss": data.get('stop_loss'),
            "take_profit": data.get('take_profit'),
            "processed": False,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Store signal
        signals.append(signal)
        
        # Keep only last 50 signals to prevent memory issues
        if len(signals) > 50:
            signals.pop(0)
        
        print(f"✅ Signal stored: {signal}")
        
        return jsonify({
            "status": "success",
            "message": "Signal received and stored",
            "signal_id": signal["id"],
            "action": signal["action"],
            "symbol": signal["symbol"]
        }), 200
        
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route('/signals', methods=['GET'])
def get_signals():
    """Get unprocessed signals for MT4 EA"""
    try:
        # Return only unprocessed signals
        unprocessed = [s for s in signals if not s['processed']]
        
        return jsonify({
            "status": "success",
            "count": len(unprocessed),
            "signals": unprocessed
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/signals/all', methods=['GET'])
def get_all_signals():
    """Get all signals (for debugging)"""
    return jsonify({
        "status": "success",
        "total_signals": len(signals),
        "signals": signals
    }), 200

@app.route('/mark_processed', methods=['POST'])
def mark_processed():
    """Mark signal as processed by MT4 EA"""
    try:
        data = request.get_json()
        signal_id = data.get('signal_id')
        
        if not signal_id:
            return jsonify({"error": "signal_id required"}), 400
        
        # Find and mark signal as processed
        for signal in signals:
            if signal['id'] == signal_id:
                signal['processed'] = True
                signal['processed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"✅ Signal {signal_id} marked as processed")
                return jsonify({"status": "success", "message": f"Signal {signal_id} processed"}), 200
        
        return jsonify({"error": "Signal not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['POST'])
def test_signal():
    """Test endpoint - send a sample signal"""
    test_data = {
        "action": "buy",
        "symbol": "EURUSD",
        "price": 1.0850,
        "quantity": 0.01
    }
    
    # Create test signal
    signal = {
        "id": len(signals) + 1,
        "timestamp": datetime.now().isoformat(),
        "action": "buy",
        "symbol": "EURUSD",
        "price": 1.0850,
        "quantity": 0.01,
        "processed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "note": "Test signal"
    }
    
    signals.append(signal)
    
    return jsonify({
        "status": "success",
        "message": "Test signal created",
        "signal": signal
    }), 200

@app.route('/clear', methods=['POST'])
def clear_signals():
    """Clear all signals (for testing)"""
    global signals
    signals = []
    return jsonify({"status": "success", "message": "All signals cleared"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
