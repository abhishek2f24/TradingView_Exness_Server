//+------------------------------------------------------------------+
//|                                           TradingViewBridge.mq4 |
//|                                                                  |
//|                          Connects TradingView signals to MT4    |
//+------------------------------------------------------------------+
#property copyright ""
#property version   "1.00"
#property strict

// Input parameters
input string WebhookURL = "https://tradingview-exness-server.onrender.com"; // Your Render app URL
input double DefaultLotSize = 0.01;
input int MagicNumber = 123456;
input int CheckIntervalSeconds = 5; // How often to check for signals

// Global variables
datetime lastCheck = 0;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("TradingView Bridge EA Started");
    Print("Webhook URL: ", WebhookURL);
    
    // Enable DLL imports for HTTP requests
    if(!TerminalInfoInteger(TERMINAL_DLLS_ALLOWED))
    {
        Alert("Please enable 'Allow DLL imports' in Terminal settings!");
        return INIT_FAILED;
    }
    
    return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    Print("TradingView Bridge EA Stopped");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
    // Check for new signals every X seconds
    if(TimeCurrent() - lastCheck >= CheckIntervalSeconds)
    {
        CheckForSignals();
        lastCheck = TimeCurrent();
    }
}

//+------------------------------------------------------------------+
//| Check for new trading signals from webhook                      |
//+------------------------------------------------------------------+
void CheckForSignals()
{
    string url = WebhookURL + "/signals";
    string response = "";
    
    // Make HTTP GET request to check for signals
    if(HttpGet(url, response))
    {
        ProcessSignals(response);
    }
    else
    {
        Print("Failed to fetch signals from webhook");
    }
}

//+------------------------------------------------------------------+
//| Process received signals                                         |
//+------------------------------------------------------------------+
void ProcessSignals(string jsonResponse)
{
    // Simple JSON parsing (in production, use proper JSON library)
    if(StringFind(jsonResponse, "\"signals\":[") >= 0)
    {
        // Extract signals array
        int start = StringFind(jsonResponse, "\"signals\":[") + 11;
        int end = StringFind(jsonResponse, "]", start);
        
        if(start > 11 && end > start)
        {
            string signalsArray = StringSubstr(jsonResponse, start, end - start);
            
            // Check if there are signals
            if(StringLen(signalsArray) > 2) // More than just "{}"
            {
                ParseAndExecuteSignals(signalsArray);
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Parse and execute trading signals                               |
//+------------------------------------------------------------------+
void ParseAndExecuteSignals(string signalsJson)
{
    // Simple parsing for demonstration
    // In production, implement proper JSON parsing
    
    if(StringFind(signalsJson, "\"action\":\"buy\"") >= 0)
    {
        string symbol = ExtractJsonValue(signalsJson, "symbol");
        double quantity = StringToDouble(ExtractJsonValue(signalsJson, "quantity"));
        string timestamp = ExtractJsonValue(signalsJson, "timestamp");
        
        if(quantity <= 0) quantity = DefaultLotSize;
        
        ExecuteBuyOrder(symbol, quantity, timestamp);
    }
    else if(StringFind(signalsJson, "\"action\":\"sell\"") >= 0)
    {
        string symbol = ExtractJsonValue(signalsJson, "symbol");
        double quantity = StringToDouble(ExtractJsonValue(signalsJson, "quantity"));
        string timestamp = ExtractJsonValue(signalsJson, "timestamp");
        
        if(quantity <= 0) quantity = DefaultLotSize;
        
        ExecuteSellOrder(symbol, quantity, timestamp);
    }
}

//+------------------------------------------------------------------+
//| Execute buy order                                                |
//+------------------------------------------------------------------+
void ExecuteBuyOrder(string symbol, double lotSize, string timestamp)
{
    double price = MarketInfo(symbol, MODE_ASK);
    double sl = 0; // Set stop loss if needed
    double tp = 0; // Set take profit if needed
    
    int ticket = OrderSend(symbol, OP_BUY, lotSize, price, 3, sl, tp, 
                          "TradingView Signal", MagicNumber, 0, clrGreen);
    
    if(ticket > 0)
    {
        Print("BUY order executed: ", symbol, " Lot: ", lotSize, " Price: ", price);
        MarkSignalProcessed(timestamp);
    }
    else
    {
        Print("Failed to execute BUY order. Error: ", GetLastError());
    }
}

//+------------------------------------------------------------------+
//| Execute sell order                                               |
//+------------------------------------------------------------------+
void ExecuteSellOrder(string symbol, double lotSize, string timestamp)
{
    double price = MarketInfo(symbol, MODE_BID);
    double sl = 0; // Set stop loss if needed
    double tp = 0; // Set take profit if needed
    
    int ticket = OrderSend(symbol, OP_SELL, lotSize, price, 3, sl, tp, 
                          "TradingView Signal", MagicNumber, 0, clrRed);
    
    if(ticket > 0)
    {
        Print("SELL order executed: ", symbol, " Lot: ", lotSize, " Price: ", price);
        MarkSignalProcessed(timestamp);
    }
    else
    {
        Print("Failed to execute SELL order. Error: ", GetLastError());
    }
}

//+------------------------------------------------------------------+
//| Mark signal as processed                                         |
//+------------------------------------------------------------------+
void MarkSignalProcessed(string timestamp)
{
    string url = WebhookURL + "/mark_processed";
    string postData = "{\"timestamp\":\"" + timestamp + "\"}";
    string response = "";
    
    HttpPost(url, postData, response);
}

//+------------------------------------------------------------------+
//| Extract value from JSON (simple implementation)                 |
//+------------------------------------------------------------------+
string ExtractJsonValue(string json, string key)
{
    string searchFor = "\"" + key + "\":\"";
    int start = StringFind(json, searchFor);
    
    if(start >= 0)
    {
        start += StringLen(searchFor);
        int end = StringFind(json, "\"", start);
        
        if(end > start)
        {
            return StringSubstr(json, start, end - start);
        }
    }
    
    // Try numeric value
    searchFor = "\"" + key + "\":";
    start = StringFind(json, searchFor);
    
    if(start >= 0)
    {
        start += StringLen(searchFor);
        int end = StringFind(json, ",", start);
        if(end < 0) end = StringFind(json, "}", start);
        
        if(end > start)
        {
            return StringSubstr(json, start, end - start);
        }
    }
    
    return "";
}

//+------------------------------------------------------------------+
//| Simple HTTP GET function                                         |
//+------------------------------------------------------------------+
bool HttpGet(string url, string &response)
{
    // Use WinINet functions for HTTP requests
    // This is a simplified version - implement proper HTTP handling
    
    // For demonstration purposes
    Print("Making HTTP GET to: ", url);
    
    // In real implementation, use WinINet DLL functions
    // or external libraries for HTTP requests
    
    return true;
}

//+------------------------------------------------------------------+
//| Simple HTTP POST function                                        |
//+------------------------------------------------------------------+
bool HttpPost(string url, string data, string &response)
{
    Print("Making HTTP POST to: ", url);
    Print("Data: ", data);
    
    // In real implementation, use WinINet DLL functions
    return true;
}
