from flask import Flask, render_template, request, send_from_directory
from duckduckgo_search import DDGS
import os

app = Flask(__name__)

# YAPAY ZEKA SİTELERİ SÖZLÜĞÜ (Hızlı Erişim)
AI_SITES = {
    "chatgpt": {"title": "ChatGPT - OpenAI", "link": "https://chatgpt.com", "snippet": "Dünyanın en popüler yapay zeka asistanı."},
    "gemini": {"title": "Gemini - Google", "link": "https://gemini.google.com", "snippet": "Google'ın en gelişmiş yapay zeka modeli."},
    "claude": {"title": "Claude - Anthropic", "link": "https://claude.ai", "snippet": "Anthropic tarafından geliştirilen güvenli AI."},
    "copilot": {"title": "Microsoft Copilot", "link": "https://copilot.microsoft.com", "snippet": "Microsoft'un yapay zeka destekli yardımcısı."}
}

def get_smart_results(query):
    results = []
    query_lower = query.lower()

    # 1. ADIM: Eğer arama terimi bir AI ismiyse, onu en başa zorla ekle
    for key, info in AI_SITES.items():
        if key in query_lower:
            results.append(info)

    # 2. ADIM: İnternetten genel sonuçları çek
    try:
        with DDGS() as ddgs:
            # Safesearch kapalı ve bölge Türkiye olarak ayarlandı
            ddg_gen = ddgs.text(query, region="tr-tr", safesearch="off")
            for r in ddg_gen:
                # Zaten manuel eklediysek tekrar ekleme
                if not any(r['href'] == res['link'] for res in results):
                    results.append({
                        "title": r['title'],
                        "link": r['href'],
                        "snippet": r['body']
                    })
                if len(results) >= 12: break
        return results
    except:
        return results

@app.route('/logo.jpg')
def get_logo():
    return send_from_directory(os.getcwd(), 'logo.jpg')

@app.route('/')
def home():
    return '''
    <body style="font-family:sans-serif; display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; margin:0; background:#fff;">
        <img src="/logo.jpg" style="width:280px; margin-bottom:25px;">
        <form action="/results">
            <input type="text" name="q" placeholder="Querya: ChatGPT, Gemini ve daha fazlasını bul..." required autofocus
                   style="width:550px; padding:16px 25px; border-radius:30px; border:1px solid #ddd; outline:none; font-size:16px;">
            <br><center><button type="submit" style="margin-top:20px; padding:12px 35px; background:#0056b3; color:white; border:none; border-radius:25px; cursor:pointer; font-weight:bold;">Sorgula</button></center>
        </form>
    </body>
    '''

@app.route('/results')
def results():
    query = request.args.get('q')
    data = get_smart_results(query)
    
    res_html = f'''
    <body style="font-family:sans-serif; margin:0; background:#f8f9fa;">
        <div style="padding:15px 50px; border-bottom:1px solid #ddd; display:flex; align-items:center; position:sticky; top:0; background:white; z-index:100;">
            <a href="/"><img src="/logo.jpg" style="height:40px; margin-right:20px;"></a>
            <form action="/results"><input type="text" name="q" value="{query}" style="width:400px; padding:10px 20px; border-radius:25px; border:1px solid #ddd; outline:none;"></form>
        </div>
        <div style="max-width:850px; margin:25px auto; padding:0 20px;">
            <p style="color:#70757a;">'{query}' için Querya sonuçları:</p>
    '''
    
    for d in data:
        # Eğer bu bir AI sitesiyse ona özel bir "Önerilen" etiketi koyalım
        is_ai = any(key in d['title'].lower() for key in AI_SITES.keys())
        border_style = "border-left: 5px solid #0056b3;" if is_ai else "border: 1px solid #eee;"
        
        res_html += f'''
        <div style="background:white; padding:20px; margin-bottom:15px; border-radius:10px; box-shadow:0 1px 4px rgba(0,0,0,0.05); {border_style}">
            { '<span style="color:#0056b3; font-size:12px; font-weight:bold;">ÖNERİLEN SONUÇ</span><br>' if is_ai else '' }
            <small style="color:#006621; display:block; margin-bottom:4px;">{d['link']}</small>
            <a href="{d['link']}" target="_blank" style="color:#1a0dab; text-decoration:none; font-size:20px; font-weight:500;">{d['title']}</a>
            <p style="color:#4d5156; font-size:14px; margin-top:8px;">{d['snippet']}</p>
        </div>
        '''
    
    res_html += "</div></body>"
    return res_html

if __name__ == '__main__':
    app.run(debug=True)