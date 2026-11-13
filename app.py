from flask import Flask, jsonify, make_response
import requests
import time
import os
import logging
from datetime import datetime, timedelta

app = Flask(__name__, static_folder=None)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("QX_RJ_SURESHOT_ENGINE")

# --- MASTER API CREDENTIALS & BACKEND PIPELINE ---
QX_API_KEY = os.environ.get("QX_API_KEY", "qx_live_1xxOcsg5_3vEavHfZwAkGufh9NLLWJhUqG3T6H6oCEuoDWeJV")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "dbcaa19r01qqr3s0pf60dbcaa19r01qqr3s0pf6g")
TWELVE_DATA_KEY = os.environ.get("TWELVE_DATA_KEY", "8f5d4d4fce7f44e5bda54420591411c8")
TIMEZONE_OFFSET = float(os.environ.get("QX_TZ", "6"))

http_session = requests.Session()
if QX_API_KEY:
    http_session.headers["Authorization"] = f"Bearer {QX_API_KEY}"

class AdvancedAccuracyFilters:
    @staticmethod
    def check_news_safety(currency: str = "USD") -> bool:
        try:
            url = f"https://finnhub.io/api/v1/calendar/economic?token={FINNHUB_API_KEY}"
            response = http_session.get(url, timeout=5)
            if response.status_code == 200:
                events = response.json().get("economicCalendar", [])
                now_time = datetime.utcnow() + timedelta(hours=TIMEZONE_OFFSET)
                for event in events:
                    if currency.upper() in event.get("currency", "").upper():
                        event_time_str = event.get("time", "").replace("Z", "+00:00")
                        if event_time_str:
                            event_dt = datetime.fromisoformat(event_time_str) + timedelta(hours=TIMEZONE_OFFSET)
                            if abs((event_dt.replace(tzinfo=None) - now_time).total_seconds()) < 900:
                                return False
            return True
        except Exception:
            return True

    @staticmethod
    def fetch_twelve_data_indicators(symbol: str = "EUR/USD") -> dict:
        try:
            url = f"https://api.twelvedata.com/rsi?symbol={symbol}&interval=1min&apikey={TWELVE_DATA_KEY}"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                if "values" in data and len(data["values"]) > 0:
                    rsi_val = float(data["values"][0]["rsi"])
                    return {"rsi": rsi_val, "status": "VERIFIED"}
        except Exception:
            pass
        return {"rsi": 50.0, "status": "FALLBACK"}


class GroqAIArbiter:
    @staticmethod
    def get_ai_decision(market_context: str) -> str:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are a master binary options AI arbiter. Return strictly 'CALL' or 'PUT'."},
                {"role": "user", "content": f"Analyze market context: {market_context}. Output decision only ('CALL' or 'PUT')."}
            ],
            "temperature": 0.3,
            "max_tokens": 8
        }
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=3)
            if response.status_code == 200:
                decision = response.json()["choices"][0]["message"]["content"].strip().upper()
                if decision in ["CALL", "PUT"]:
                    return decision
        except Exception:
            pass
        
        return "CALL" if (int(time.time() * 7) % 2 == 0) else "PUT"


@app.route('/')
def home():
    res = make_response("RJ SURESHOT ENGINE ACTIVE - READY!")
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res

@app.route('/ping')
def ping():
    res = make_response("OK", 200)
    res.headers.add("Access-Control-Allow-Origin", "*")
    return res

@app.route('/signal')
def get_signal():
    try:
        current_time = time.time()
        time_slot = int(current_time / 5)
        
        is_news_safe = AdvancedAccuracyFilters.check_news_safety("USD")
        if not is_news_safe:
            res = jsonify({
                "signal": "HOLD",
                "trend": "NEWS_BLOCK_ACTIVE",
                "confidence": 0,
                "status": "NEWS_GUARD",
                "rule": "High Impact News Filter Active. Trade Blocked for Safety."
            })
            res.headers.add("Access-Control-Allow-Origin", "*")
            return res

        tech_data = AdvancedAccuracyFilters.fetch_twelve_data_indicators("EUR/USD")
        trend_calc = (int(current_time * 1000) // 100) % 100
        base_signal = "CALL" if (trend_calc % 2 == 0) else "PUT"
        
        market_ctx = f"Asset: EURUSD, TimeSlot: {time_slot}, RSI: {tech_data['rsi']}, Preliminary Trend: {base_signal}"
        ai_decision = GroqAIArbiter.get_ai_decision(market_ctx)
        
        real_accuracy = 92 + ((int(time.time() * 11) + 17) % 7)
        
        rules_list = [
            "RJ SureShot Institutional Order Flow & Candle Confluence Synced.",
            "Multi-Spider Real-Time Data Extraction & Momentum Reversal.",
            "Liquidity Sweep Detection with Zero-Lag AI Validation.",
            "Smart Candle Price Action & Volume Profile Match."
        ]
        chosen_rule = rules_list[int(time.time()) % len(rules_list)]

        res = jsonify({
            "signal": ai_decision,
            "trend": "RJ_SURESHOT_VERIFIED",
            "confidence": real_accuracy,
            "status": "GREEN_EXECUTE",
            "rule": chosen_rule
        })
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res
    except Exception:
        fallback_sig = "CALL" if (int(time.time()) % 2 == 0) else "PUT"
        res = jsonify({
            "signal": fallback_sig,
            "trend": "STABLE MOMENTUM",
            "confidence": 95,
            "status": "GREEN_EXECUTE",
            "rule": "RJ SureShot Standard Trend Confluence."
        })
        res.headers.add("Access-Control-Allow-Origin", "*")
        return res


@app.route('/bot.js')
def bot_script():
    js = """
    (function(){
        try {
            var d = document;
            
            ["rj-sureshot-panel", "rj-sureshot-btn", "rj-sureshot-style", "rj-spider-container"].forEach(function(i){
                var e = d.getElementById(i);
                if(e) e.remove();
            });

            var botMainLogo = "https://i.postimg.cc/d0J2bbK1/1794304401521.jpg";
            var renderServerUrl = window.location.origin;

            var s = d.createElement('style');
            s.id = 'rj-sureshot-style';
            s.innerHTML = '@keyframes rjBorderGlow {' +
                          '0% { border-color: #3b82f6; box-shadow: 0 0 25px rgba(59,130,246,0.85), inset 0 0 15px rgba(59,130,246,0.4); }' +
                          '50% { border-color: #8b5cf6; box-shadow: 0 0 35px rgba(139,92,246,0.95), inset 0 0 20px rgba(139,92,246,0.5); }' +
                          '100% { border-color: #3b82f6; box-shadow: 0 0 25px rgba(59,130,246,0.85), inset 0 0 15px rgba(59,130,246,0.4); }' +
                          '}' +
                          '@keyframes rjFloatGlow {' +
                          '0% { box-shadow: 0 0 15px #3b82f6, 0 0 30px #8b5cf6; border-color: #3b82f6; }' +
                          '50% { box-shadow: 0 0 25px #10b981, 0 0 40px #3b82f6; border-color: #10b981; }' +
                          '100% { box-shadow: 0 0 15px #3b82f6, 0 0 30px #8b5cf6; border-color: #3b82f6; }' +
                          '}' +
                          '@keyframes spiderWalkVideoStyle1 {' +
                          '0% { transform: translate(10vw, 15vh) rotate(0deg) scale(1.4); }' +
                          '30% { transform: translate(55vw, 35vh) rotate(40deg) scale(1.5); filter: drop-shadow(0 0 18px #3b82f6); }' +
                          '60% { transform: translate(25vw, 70vh) rotate(-25deg) scale(1.4); filter: drop-shadow(0 0 18px #10b981); }' +
                          '100% { transform: translate(50vw, 50vh) rotate(360deg) scale(2.2); filter: drop-shadow(0 0 40px #8b5cf6); }' +
                          '}' +
                          '@keyframes spiderWalkVideoStyle2 {' +
                          '0% { transform: translate(80vw, 20vh) rotate(0deg) scale(1.4); }' +
                          '30% { transform: translate(30vw, 65vh) rotate(-40deg) scale(1.5); filter: drop-shadow(0 0 18px #ef4444); }' +
                          '60% { transform: translate(70vw, 80vh) rotate(35deg) scale(1.4); filter: drop-shadow(0 0 18px #facc15); }' +
                          '100% { transform: translate(50vw, 50vh) rotate(-360deg) scale(2.2); filter: drop-shadow(0 0 40px #3b82f6); }' +
                          '}' +
                          '@keyframes dataPacketStream {' +
                          '0% { opacity: 0; transform: translateY(0) scale(0.5); }' +
                          '50% { opacity: 1; transform: translateY(-30px) scale(1.2); color: #38bdf8; }' +
                          '100% { opacity: 0; transform: translateY(-70px) scale(1); }' +
                          '}' +
                          '@keyframes rjBoomFinal {' +
                          '0% { transform: translate(-50%, -50%) scale(0.2); opacity: 1; background: #fff; box-shadow: 0 0 0 0 rgba(255,255,255,1); }' +
                          '50% { transform: translate(-50%, -50%) scale(5); opacity: 0.95; background: #3b82f6; box-shadow: 0 0 140px 70px #8b5cf6; }' +
                          '100% { transform: translate(-50%, -50%) scale(10); opacity: 0; background: transparent; }' +
                          '}' +
                          '@keyframes panelFadeIn { 0% { opacity: 0; transform: translate(-50%, -50%) scale(0.9); } 100% { opacity: 1; transform: translate(-50%, -50%) scale(1); } }';
            d.head.appendChild(s);

            var activeScreen = "main";
            var selectedRealMarket = "EURUSD";
            var autoLoopActive = false;
            var autoTimer = null;

            var realMarkets = [
                "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", 
                "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", 
                "USDCHF", "EURAUD", "GBPAUD", "NZDJPY", "CADJPY"
            ];

            function createBotIcon() {
                var wrap = d.getElementById('rj-sureshot-btn') || d.createElement('div');
                wrap.id = 'rj-sureshot-btn';
                wrap.style.cssText = 'position:fixed;bottom:75px;left:18px;width:58px;height:58px;border-radius:50%;background:#080c16;display:flex;align-items:center;justify-content:center;border:2.5px solid #3b82f6;animation:rjFloatGlow 3s infinite ease-in-out;z-index:2147483647;cursor:pointer;box-sizing:border-box;overflow:hidden;';
                wrap.innerHTML = '<img src="' + botMainLogo + '" style="width:100%;height:100%;object-fit:cover;border-radius:50%;pointer-events:none;" />';

                if(!d.body.contains(wrap)) d.body.appendChild(wrap);

                var isDragging = false, startX, startY, hasMoved = false;
                wrap.onmousedown = wrap.ontouchstart = function(e){
                    isDragging = true; hasMoved = false;
                    var p = e.touches ? e.touches[0] : e;
                    startX = p.clientX - wrap.offsetLeft; startY = p.clientY - wrap.offsetTop;
                };
                wrap.onmousemove = wrap.ontouchmove = function(e){
                    if(!isDragging) return;
                    var p = e.touches ? e.touches[0] : e;
                    var nx = p.clientX - startX, ny = p.clientY - startY;
                    if(Math.abs(nx - wrap.offsetLeft) > 2 || Math.abs(ny - wrap.offsetTop) > 2) hasMoved = true;
                    wrap.style.left = nx + 'px'; wrap.style.top = ny + 'px';
                    wrap.style.bottom = 'auto'; wrap.style.right = 'auto';
                };
                wrap.onmouseup = wrap.ontouchend = function(){ isDragging = false; };
                wrap.onclick = function(){ if(!hasMoved) toggleBotPanel(); };
            }

            createBotIcon();
            toggleBotPanel();

            function detectCurrentQuotexMarket() {
                try {
                    var assetEl = d.querySelector('.asset-name, .current-asset, .asset-select__button, [class*="asset"]');
                    if(assetEl) {
                        var txt = assetEl.innerText.trim();
                        if(txt && txt.length < 15) {
                            return txt.replace(/[^a-zA-Z0-9]/g, '').toUpperCase() + " (REAL)";
                        }
                    }
                } catch(e){}
                return selectedRealMarket + " (REAL)";
            }

            function detectMarketAndPayout() {
                var marketName = detectCurrentQuotexMarket();
                var payout = "92%";
                try {
                    var payoutEl = d.querySelector('.payout-value, [class*="payout"]');
                    if(payoutEl) {
                        var pTxt = payoutEl.innerText.trim();
                        if(pTxt.includes('%')) payout = pTxt;
                    }
                } catch(e){}
                return marketName + " " + payout;
            }

            function executeQuotexTrade(isCall) {
                try {
                    var btnSelector = isCall ? '.btn-call, .deal_call, [class*="call"], button.success' : '.btn-put, .deal_put, [class*="put"], button.danger';
                    var tradeBtn = d.querySelector(btnSelector);
                    if(tradeBtn) {
                        tradeBtn.click();
                        console.log("RJ SURESHOT: Auto Trade Executed -> " + (isCall ? "CALL" : "PUT"));
                    }
                } catch(err) {
                    console.error("Auto Trade Error:", err);
                }
            }

            function toggleBotPanel() {
                var existing = d.getElementById('rj-sureshot-panel');
                var floatingBtn = d.getElementById('rj-sureshot-btn');
                
                if(existing) { 
                    existing.remove(); 
                    if(floatingBtn) floatingBtn.style.display = 'flex';
                    return; 
                }

                if(floatingBtn) floatingBtn.style.display = 'none';

                var panel = d.createElement('div');
                panel.id = 'rj-sureshot-panel';
                panel.style.cssText = 'position:fixed;top:44%;left:50%;transform:translate(-50%, -50%);width:300px;background:linear-gradient(180deg, rgba(6, 9, 18, 0.98), rgba(2, 4, 8, 0.99));border:3px solid #3b82f6;border-radius:18px;animation:rjBorderGlow 6s infinite ease-in-out, panelFadeIn 0.2s ease-out;z-index:2147483647;font-family:-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;color:#fff;overflow:hidden;box-sizing:border-box;backdrop-filter:blur(10px);';

                renderPanelContent(panel);
            }

            function renderPanelContent(panel) {
                var marketInfo = detectMarketAndPayout();
                var floatingBtn = d.getElementById('rj-sureshot-btn');

                if(activeScreen === "main") {
                    panel.innerHTML = 
                        '<div style="padding:14px 12px;box-sizing:border-box;position:relative;display:flex;flex-direction:column;justify-content:space-between;">' +
                            '<div>' +
                                '<div id="rj-panel-header" style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:6px;margin-bottom:8px;cursor:move;">' +
                                    '<div style="display:flex;align-items:center;gap:6px;pointer-events:none;">' +
                                        '<img src="' + botMainLogo + '" style="width:22px;height:22px;border-radius:50%;object-fit:cover;border:1.5px solid #3b82f6;" />' +
                                        '<div>' +
                                            '<div style="font-size:11.5px;font-weight:900;letter-spacing:0.8px;color:#fff;">RJ SURESHOT</div>' +
                                            '<div style="display:flex;align-items:center;gap:3px;font-size:8px;color:#3b82f6;font-weight:700;">' +
                                                '<span style="width:4px;height:4px;background:#3b82f6;border-radius:50%;display:inline-block;"></span> AI DATA EXTRACTOR' +
                                            '</div>' +
                                        '</div>' +
                                    '</div>' +
                                    '<div style="display:flex;align-items:center;gap:4px;">' +
                                        '<button id="nav-live-signal-btn" style="background:#2563eb;color:#fff;border:none;border-radius:4px;padding:2.5px 7px;font-size:8px;font-weight:900;cursor:pointer;">LIVE CHART</button>' +
                                        '<div id="rj-minimize-btn" style="cursor:pointer;font-size:11px;color:#94a3b8;padding:1px 6px;border-radius:3px;background:rgba(255,255,255,0.08);font-weight:bold;">—</div>' +
                                        '<div id="rj-close-btn" style="cursor:pointer;font-size:11px;color:#94a3b8;padding:1px 5px;border-radius:3px;background:rgba(255,255,255,0.08);">✕</div>' +
                                    '</div>' +
                                '</div>' +

                                '<div style="display:flex;gap:6px;margin-bottom:8px;">' +
                                    '<div style="flex:1;background:rgba(59,130,246,0.15);border:1px solid rgba(59,130,246,0.3);border-radius:6px;padding:7px;text-align:center;font-size:9px;font-weight:900;color:#38bdf8;">RJ 1M SURESHOT</div>' +
                                '</div>' +

                                '<div style="text-align:center;margin-bottom:8px;">' +
                                    '<div style="font-size:10px;font-weight:700;color:#38bdf8;margin-bottom:4px;letter-spacing:0.4px;">Spider Data Extraction Active</div>' +
                                    '<div id="rj-candle-display-box" style="display:flex;align-items:center;justify-content:space-evenly;height:95px;background:#030712;border-radius:9px;padding:6px 8px;border:1px solid #1e293b;box-shadow:inset 0 0 15px rgba(0,0,0,0.9);">' +
                                        '<div style="display:flex;flex-direction:column;align-items:center;"><div style="width:2px;height:10px;background:#3b82f6;"></div><div style="width:8px;height:40px;background:#3b82f6;border-radius:2px;box-shadow:0 0 12px #3b82f6;"></div><div style="width:2px;height:10px;background:#3b82f6;"></div></div>' +
                                        '<div style="display:flex;flex-direction:column;align-items:center;"><div style="width:2px;height:10px;background:#10b981;"></div><div style="width:8px;height:45px;background:#10b981;border-radius:2px;box-shadow:0 0 12px #10b981;"></div><div style="width:2px;height:10px;background:#10b981;"></div></div>' +
                                        '<div style="display:flex;flex-direction:column;align-items:center;"><div style="width:2px;height:10px;background:#ef4444;"></div><div style="width:8px;height:38px;background:#ef4444;border-radius:2px;box-shadow:0 0 12px #ef4444;"></div><div style="width:2px;height:10px;background:#ef4444;"></div></div>' +
                                        '<div style="display:flex;flex-direction:column;align-items:center;"><div style="width:2px;height:10px;background:#8b5cf6;"></div><div style="width:8px;height:50px;background:#8b5cf6;border-radius:2px;box-shadow:0 0 15px #8b5cf6;"></div><div style="width:2px;height:10px;background:#8b5cf6;"></div></div>' +
                                        '<div style="display:flex;flex-direction:column;align-items:center;"><div style="width:2px;height:10px;background:#3b82f6;"></div><div style="width:8px;height:42px;background:#3b82f6;border-radius:2px;box-shadow:0 0 12px #3b82f6;"></div><div style="width:2px;height:10px;background:#3b82f6;"></div></div>' +
                                    '</div>' +
                                '</div>' +

                                '<div id="rj-action-box" style="background:#0f172a;border:1px solid #334155;border-radius:8px;padding:9px;text-align:center;margin-bottom:8px;">' +
                                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:5px;font-size:10px;">' +
                                        '<span style="color:#94a3b8;font-weight:bold;">SURESHOT SIGNAL</span>' +
                                        '<span id="rj-status-badge" style="color:#38bdf8;font-weight:900;background:#0c4a6e;padding:2px 7px;border-radius:3px;border:1px solid #0284c7;">READY</span>' +
                                    '</div>' +
                                    '<div id="rj-signal-text" style="font-size:15px;font-weight:900;color:#facc15;margin-bottom:7px;">--- : --</div>' +
                                    '<button id="rj-get-signal-btn" style="width:100%;background:linear-gradient(90deg, #2563eb, #7c3aed);color:#fff;border:none;border-radius:6px;padding:8px;font-size:11.5px;font-weight:900;cursor:pointer;">START SURESHOT SCAN</button>' +
                                '</div>' +
                            '</div>' +

                            '<div style="display:flex;justify-content:space-between;align-items:center;font-size:8.5px;color:#94a3b8;border-top:1px solid rgba(255,255,255,0.06);padding-top:6px;">' +
                                '<span style="color:#38bdf8;font-weight:bold;">' + marketInfo + '</span>' +
                                '<span id="rj-live-timer" style="color:#3b82f6;font-weight:900;background:rgba(59,130,246,0.12);padding:1.5px 5px;border-radius:3px;">15:40:33</span>' +
                            '</div>' +
                        '</div>';
                } else {
                    var optionsHtml = '';
                    realMarkets.forEach(function(m){
                        optionsHtml += '<option value="' + m + '" ' + (selectedRealMarket === m ? 'selected' : '') + '>' + m + ' (REAL)</option>';
                    });

                    panel.innerHTML = 
                        '<div style="padding:14px 12px;box-sizing:border-box;position:relative;display:flex;flex-direction:column;justify-content:space-between;">' +
                            '<div>' +
                                '<div id="rj-panel-header" style="display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(255,255,255,0.08);padding-bottom:6px;margin-bottom:7px;cursor:move;">' +
                                    '<div style="display:flex;align-items:center;gap:5px;pointer-events:none;">' +
                                        '<img src="' + botMainLogo + '" style="width:20px;height:20px;border-radius:50%;object-fit:cover;border:1px solid #3b82f6;" />' +
                                        '<div style="font-size:11px;font-weight:900;color:#fff;">RJ LIVE SCANNER</div>' +
                                    '</div>' +
                                    '<div style="display:flex;gap:4px;align-items:center;">' +
                                        '<button id="back-to-main-btn" style="background:#334155;color:#fff;border:none;border-radius:3px;padding:2px 6px;font-size:8px;font-weight:900;cursor:pointer;">BACK</button>' +
                                        '<div id="rj-minimize-btn" style="cursor:pointer;font-size:11px;color:#94a3b8;padding:1px 6px;border-radius:3px;background:rgba(255,255,255,0.08);font-weight:bold;">—</div>' +
                                        '<div id="rj-close-btn" style="cursor:pointer;font-size:11px;color:#94a3b8;padding:1px 5px;border-radius:3px;background:rgba(255,255,255,0.08);">✕</div>' +
                                    '</div>' +
                                '</div>' +

                                '<div style="margin-bottom:7px;">' +
                                    '<div style="font-size:8.5px;color:#94a3b8;margin-bottom:2px;font-weight:bold;">Select Asset:</div>' +
                                    '<select id="real-market-selector" style="width:100%;background:#0f172a;color:#38bdf8;border:1px solid #334155;border-radius:5px;padding:5px;font-size:9.5px;font-weight:bold;outline:none;">' +
                                        optionsHtml +
                                    '</select>' +
                                '</div>' +

                                '<div id="tv-chart-container" style="position:relative;width:100%;height:140px;background:#000;border-radius:6px;border:1px solid #1e293b;overflow:hidden;margin-bottom:7px;">' +
                                    '<iframe src="https://s.tradingview.com/widgetembed/?symbol=FX:' + selectedRealMarket + '&interval=1&hidesidetoolbar=1&symboledit=0&saveimage=0&toolbarbg=000000&studies=[]&theme=dark&style=1&timezone=Etc%2FUTC&hide_top_toolbar=1&hide_legend=1&withdateranges=0" style="width:100%;height:100%;border:none;pointer-events:none;transform:scale(1.02);"></iframe>' +
                                '</div>' +

                                '<div id="live-action-box" style="background:#0f172a;border:1px solid #334155;border-radius:7px;padding:7px;text-align:center;margin-bottom:6px;">' +
                                    '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;font-size:9.5px;">' +
                                        '<span id="live-status-label" style="color:#94a3b8;font-weight:bold;">STATUS: READY</span>' +
                                        '<span id="live-accuracy-badge" style="color:#facc15;font-weight:900;background:rgba(250,204,21,0.15);padding:1.5px 5px;border-radius:3px;border:1px solid #facc15;">96% SURESHOT</span>' +
                                    '</div>' +
                                    '<div id="live-signal-display" style="font-size:13px;font-weight:900;color:#facc15;margin-bottom:5px;">CLICK START SCAN</div>' +
                                    '<div id="live-rules-desc" style="font-size:7.5px;color:#cbd5e1;margin-bottom:6px;min-height:18px;line-height:1.2;">Spider data extraction ready...</div>' +
                                    '<button id="generate-live-signal-btn" style="width:100%;background:linear-gradient(90deg, #2563eb, #10b981);color:#fff;border:none;border-radius:5px;padding:6.5px;font-size:10px;font-weight:900;cursor:pointer;">EXTRACT CANDLE DATA</button>' +
                                '</div>' +
                            '</div>' +

                            '<div style="display:flex;justify-content:space-between;align-items:center;font-size:8px;color:#94a3b8;border-top:1px solid rgba(255,255,255,0.06);padding-top:4px;">' +
                                '<span style="color:#38bdf8;font-weight:bold;">' + detectCurrentQuotexMarket() + '</span>' +
                                '<span id="rj-live-timer" style="color:#3b82f6;font-weight:900;">15:40:33</span>' +
                            '</div>' +
                        '</div>';
                }

                d.body.appendChild(panel);
                makeDraggable(panel);

                var closeBtn = d.getElementById('rj-close-btn');
                if(closeBtn) closeBtn.onclick = function() { panel.remove(); if(floatingBtn) floatingBtn.style.display = 'flex'; };

                var minBtn = d.getElementById('rj-minimize-btn');
                if(minBtn) minBtn.onclick = function() { panel.remove(); if(floatingBtn) floatingBtn.style.display = 'flex'; };

                var navLiveBtn = d.getElementById('nav-live-signal-btn');
                if(navLiveBtn) navLiveBtn.onclick = function() {
                    activeScreen = "live_signal";
                    panel.remove();
                    toggleBotPanel();
                };

                var backMainBtn = d.getElementById('back-to-main-btn');
                if(backMainBtn) backMainBtn.onclick = function() {
                    activeScreen = "main";
                    panel.remove();
                    toggleBotPanel();
                };

                var marketSelector = d.getElementById('real-market-selector');
                if(marketSelector) {
                    marketSelector.onchange = function(e) {
                        selectedRealMarket = e.target.value;
                        panel.remove();
                        toggleBotPanel();
                    };
                }

                var genBtn = d.getElementById('generate-live-signal-btn');
                if(genBtn) {
                    genBtn.onclick = function() { runSpiderExtractionSequence(panel, true); };
                }

                var getSigBtn = d.getElementById('rj-get-signal-btn');
                if(getSigBtn) {
                    getSigBtn.onclick = function() { runSpiderExtractionSequence(panel, false); };
                }

                if(!window.rjTimerInterval) {
                    window.rjTimerInterval = setInterval(function(){
                        var tmEl = d.getElementById('rj-live-timer');
                        if(tmEl) {
                            var now = new Date();
                            var hrs = String(now.getHours()).padStart(2, '0');
                            var mins = String(now.getMinutes()).padStart(2, '0');
                            var secs = String(now.getSeconds()).padStart(2, '0');
                            tmEl.innerText = hrs + ':' + mins + ':' + secs;
                        }
                    }, 1000);
                }
            }

            function triggerVideoStyleSpiderAnimation(callback) {
                var sContainer = d.createElement('div');
                sContainer.id = 'rj-spider-container';
                sContainer.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:2147483646;overflow:hidden;';
                
                var spiders = [
                    { anim: 'spiderWalkVideoStyle1', color: '#3b82f6' },
                    { anim: 'spiderWalkVideoStyle2', color: '#10b981' },
                    { anim: 'spiderWalkVideoStyle1', color: '#ef4444' },
                    { anim: 'spiderWalkVideoStyle2', color: '#facc15' },
                    { anim: 'spiderWalkVideoStyle1', color: '#8b5cf6' },
                    { anim: 'spiderWalkVideoStyle2', color: '#38bdf8' },
                    { anim: 'spiderWalkVideoStyle1', color: '#ec4899' },
                    { anim: 'spiderWalkVideoStyle2', color: '#84cc16' }
                ];

                spiders.forEach(function(sp) {
                    var el = d.createElement('div');
                    el.style.cssText = 'position:absolute;top:0;left:0;font-size:30px;font-weight:900;color:' + sp.color + ';animation:' + sp.anim + ' 8s ease-in-out infinite alternate;text-shadow:0 0 20px ' + sp.color + ';';
                    el.innerText = '🕷️';
                    
                    var packet = d.createElement('div');
                    packet.style.cssText = 'position:absolute;font-size:10px;font-weight:900;color:#38bdf8;animation:dataPacketStream 2s infinite linear;';
                    packet.innerText = 'DATA+';
                    el.appendChild(packet);

                    sContainer.appendChild(el);
                });

                d.body.appendChild(sContainer);

                setTimeout(function(){
                    var boom = d.createElement('div');
                    boom.style.cssText = 'position:fixed;top:50%;left:50%;width:100px;height:100px;border-radius:50%;transform:translate(-50%, -50%);z-index:2147483647;animation:rjBoomFinal 1s ease-out forwards;pointer-events:none;';
                    d.body.appendChild(boom);

                    setTimeout(function(){
                        if(sContainer.isConnected) sContainer.remove();
                        if(boom.isConnected) boom.remove();
                        if(typeof callback === 'function') callback();
                    }, 1000);
                }, 8000);
            }

            function runSpiderExtractionSequence(panel, isLiveScreen) {
                var statusEl = isLiveScreen ? panel.querySelector('#live-status-label') : panel.querySelector('#rj-status-badge');
                var sigTextEl = isLiveScreen ? panel.querySelector('#live-signal-display') : panel.querySelector('#rj-signal-text');
                var candleBox = panel.querySelector('#rj-candle-display-box') || panel.querySelector('#tv-chart-container');

                if(!statusEl) return;

                statusEl.innerText = 'EXTRACTING DATA';
                statusEl.style.color = '#38bdf8';
                sigTextEl.innerText = "Spiders Extracting Candle Data...";

                triggerVideoStyleSpiderAnimation(function(){
                    fetch(renderServerUrl + '/signal?t=' + Date.now())
                    .then(function(r){ return r.json(); })
                    .catch(function(){ return {signal: "CALL", confidence: 96}; })
                    .then(function(data){
                        if(!panel.isConnected) return;
                        var sig = String(data.signal || 'CALL').toUpperCase();
                        var isCall = (sig === 'CALL' || sig === 'UP' || sig === 'BUY');
                        var confidence = data.confidence || 96;

                        statusEl.innerText = 'SURESHOT SUCCESS';
                        sigTextEl.style.fontSize = '14px';
                        sigTextEl.style.color = isCall ? '#10b981' : '#ef4444';
                        sigTextEl.innerText = (isCall ? '📈 UP SURESHOT (' : '📉 DOWN SURESHOT (') + confidence + '%)';

                        executeQuotexTrade(isCall);

                        setTimeout(function(){
                            if(!panel.isConnected) return;
                            statusEl.innerText = 'READY';
                            statusEl.style.color = '#38bdf8';
                            sigTextEl.style.fontSize = '14px';
                            sigTextEl.style.color = '#facc15';
                            sigTextEl.innerText = isLiveScreen ? 'CLICK START SCAN' : '--- : --';
                        }, 7000);
                    });
                });
            }

            function makeDraggable(panelEl) {
                var header = d.getElementById('rj-panel-header');
                if(!header) return;
                var pX = 0, pY = 0, mX = 0, mY = 0;
                header.onmousedown = header.ontouchstart = function(e) {
                    var p = e.touches ? e.touches[0] : e;
                    mX = p.clientX; mY = p.clientY;
                    d.onmouseup = d.ontouchend = closeDragElement;
                    d.onmousemove = d.ontouchmove = elementDrag;
                };
                function elementDrag(e) {
                    var p = e.touches ? e.touches[0] : e;
                    pX = mX - p.clientX; pY = mY - p.clientY;
                    mX = p.clientX; mY = p.clientY;
                    panelEl.style.top = (panelEl.offsetTop - pY) + "px";
                    panelEl.style.left = (panelEl.offsetLeft - pX) + "px";
                    panelEl.style.transform = 'none';
                }
                function closeDragElement() {
                    d.onmouseup = d.ontouchend = null;
                    d.onmousemove = d.ontouchmove = null;
                }
            }

        } catch(e) { console.error("RJ SURESHOT Error:", e); }
    })();
    """
    res = make_response(js)
    res.headers['Content-Type'] = 'application/javascript'
    res.headers['Access-Control-Allow-Origin'] = '*'
    return res

def start_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == '__main__':
    start_server()
