from flask import Flask, request, jsonify
import re
import requests
import os

app = Flask(__name__)

# ⚠️ REMPLACER PAR VOS VRAIS JETONS FACEBOOK
FACEBOOK_TOKEN = "VOTRE_JETON_ACCES_FACEBOOK"
VERIFY_TOKEN = "hotel_tour_khalef_2025"

# Données basées sur votre Excel
TARIFS = {
    "LPD": [130, 120, 140, 120, 130, 120, 130, 140],
    "HB": [195, 180, 220, 180, 195, 180, 195, 220],
    "All in soft": [270, 255, 295, 255, 270, 255, 270, 295],
    "All in": [300, 285, 325, 285, 300, 285, 300, 325]
}

PERIODES = [
    "01.11.2025-22.11.2025", "23.11.2025-17.12.2025", "18.12.2025-03.01.2026",
    "04.01.2026-29.01.2026", "30.01.2026-14.02.2026", "15.02.2026-18.03.2026",
    "19.03.2026-04.04.2026", "05.04.2026-30.04.2026"
]

def analyser_devis(message_texte):
    """Analyse le message et calcule le devis"""
    print(f"🔍 Analyse du message: {message_texte}")
    
    # Détection de la durée
    duree_sejour = 7
    pattern_dates = r'du\s*(\d{1,2})\s*au\s*(\d{1,2})\s*(\w+)'
    match_dates = re.search(pattern_dates, message_texte.lower())
    
    if match_dates:
        date_debut = int(match_dates.group(1))
        date_fin = int(match_dates.group(2))
        duree_sejour = date_fin - date_debut
    else:
        pattern_nuits = r'(\d+)\s*(?:nuit|jour)'
        match_nuits = re.search(pattern_nuits, message_texte)
        if match_nuits:
            duree_sejour = int(match_nuits.group(1))

    # Détection formule
    formule = "LPD"
    if "demi-pension" in message_texte.lower() or "hb" in message_texte.lower():
        formule = "HB"
    elif "all in soft" in message_texte.lower():
        formule = "All in soft" 
    elif "all in" in message_texte.lower():
        formule = "All in"

    # Détection période
    periode_index = 2
    if "novembre" in message_texte.lower(): periode_index = 0
    elif "décembre" in message_texte.lower() or "dec" in message_texte.lower(): periode_index = 2
    elif "janvier" in message_texte.lower(): periode_index = 3
    elif "février" in message_texte.lower() or "fevrier" in message_texte.lower(): periode_index = 4
    elif "mars" in message_texte.lower(): periode_index = 6
    elif "avril" in message_texte.lower(): periode_index = 7

    # Détection personnes
    personnes = re.search(r'(\d+)\s*(?:personne|adulte|voyageur)', message_texte)
    nb_personnes = int(personnes.group(1)) if personnes else 2

    # Calcul
    prix_par_personne = TARIFS[formule][periode_index]
    prix_total = prix_par_personne * nb_personnes * duree_sejour

    # Préparation réponse
    reponse = f"""🏨 **HOTEL TOUR KHALEF** ⭐⭐⭐⭐⭐

📋 Formule : {formule}
📅 Période : {PERIODES[periode_index]}
👥 Personnes : {nb_personnes}
🌙 Nuits : {duree_sejour}

💰 **DEVIS : {prix_total}€**

📞 Notre équipe vous contacte sous 30 minutes pour confirmation !

ℹ️ _Tarifs selon grille Winter 2025-2026_"""
    
    return reponse

# ROUTE POUR LA VÉRIFICATION FACEBOOK
@app.route('/webhook', methods=['GET'])
def verifier_webhook():
    hub_verify_token = request.args.get('hub.verify_token')
    hub_challenge = request.args.get('hub.challenge')
    
    if hub_verify_token == VERIFY_TOKEN:
        print("✅ Webhook Facebook vérifié!")
        return hub_challenge
    return 'Token invalide', 403

# ROUTE POUR RECEVOIR LES MESSAGES FACEBOOK
@app.route('/webhook', methods=['POST'])
def recevoir_messages():
    data = request.json
    
    if data.get('object') == 'page':
        for entry in data['entry']:
            for messaging_event in entry.get('messaging', []):
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text', '')
                    
                    print(f"📩 Message de {sender_id}: {message_text}")
                    
                    # Analyser le message et calculer devis
                    reponse_bot = analyser_devis(message_text)
                    
                    # Envoyer la réponse sur Facebook
                    envoyer_reponse_facebook(sender_id, reponse_bot)
    
    return 'OK', 200

def envoyer_reponse_facebook(recipient_id, message_texte):
    """Envoie la réponse vers Facebook Messenger"""
    url = f"https://graph.facebook.com/v17.0/me/messages?access_token={FACEBOOK_TOKEN}"
    
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_texte}
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"📤 Réponse envoyée à Facebook - Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur envoi Facebook: {e}")

# PAGE D'ACCUEIL POUR TEST
@app.route('/')
def accueil():
    return """
    <h1>🤖 Bot Facebook - Hotel Tour Khalef</h1>
    <p><strong>✅ Prêt pour Facebook Messenger!</strong></p>
    <p>URL Webhook: <code>https://votre-url.com/webhook</code></p>
    <p>Testez l'analyse: <a href="/test?message=du 15 au 22 décembre pour 2 personnes">Exemple de test</a></p>
    """

# ROUTE DE TEST
@app.route('/test')
def tester_analyse():
    message = request.args.get('message', 'du 15 au 22 décembre pour 2 personnes')
    reponse = analyser_devis(message)
    return f"<pre>{reponse}</pre>"

if __name__ == '__main__':
    print("🚀 Bot Facebook Hotel Tour Khalef - Démarrage...")
    app.run(host='0.0.0.0', port=5000, debug=True)