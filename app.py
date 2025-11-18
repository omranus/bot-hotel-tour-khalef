from flask import Flask, request, jsonify, render_template
import re
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Données basées sur votre Excel - Prix en TND
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
    """Analyse le message et calcule le devis - Version focus devis uniquement"""
    print(f"🔍 Analyse du message: {message_texte}")
    
    # Liste des mots-clés liés aux devis
    mots_cles_devis = [
        'devis', 'tarif', 'prix', 'réservation', 'réserver', 'séjour', 
        'nuit', 'nuits', 'personne', 'personnes', 'adulte', 'adultes',
        'enfant', 'enfants', 'chambre', 'double', 'triple', 'formule',
        'lpd', 'hb', 'all in', 'demi-pension', 'petit déjeuner',
        'janvier', 'février', 'mars', 'avril', 'novembre', 'décembre',
        'du', 'au', 'pour'
    ]
    
    # Vérifier si le message concerne un devis
    message_lower = message_texte.lower()
    concerne_devis = any(mot in message_lower for mot in mots_cles_devis)
    
    if not concerne_devis:
        return "❌ **Désolé, je suis un assistant spécialisé dans les devis.**\n\nJe peux vous aider à calculer le prix d'un séjour, mais je ne peux pas répondre à d'autres questions.\n\n💡 **Exemple de demande :** 'Devis pour 2 personnes du 15 au 20 décembre en demi-pension'"
    
    # === DÉTECTION DE LA DURÉE ===
    duree_sejour = 7
    pattern_dates = r'du\s*(\d{1,2})\s*au\s*(\d{1,2})\s*(\w+)'
    match_dates = re.search(pattern_dates, message_lower)
    
    if match_dates:
        date_debut = int(match_dates.group(1))
        date_fin = int(match_dates.group(2))
        duree_sejour = date_fin - date_debut
        print(f"📅 Durée détectée : {duree_sejour} nuits")
    else:
        pattern_nuits = r'(\d+)\s*(?:nuit|jour)'
        match_nuits = re.search(pattern_nuits, message_lower)
        if match_nuits:
            duree_sejour = int(match_nuits.group(1))
            print(f"📅 Durée détectée : {duree_sejour} nuits")

    # === DÉTECTION FORMULE ===
    formule = "LPD"
    if "demi-pension" in message_lower or "hb" in message_lower:
        formule = "HB"
    elif "all in soft" in message_lower:
        formule = "All in soft" 
    elif "all in" in message_lower:
        formule = "All in"
    elif "petit déjeuner" in message_lower or "pd" in message_lower:
        formule = "LPD"

    print(f"📋 Formule détectée : {formule}")

    # === DÉTECTION PÉRIODE ===
    periode_index = 2
    if "novembre" in message_lower: periodo_index = 0
    elif "décembre" in message_lower or "dec" in message_lower: periodo_index = 2
    elif "janvier" in message_lower: periodo_index = 3
    elif "février" in message_lower or "fevrier" in message_lower: periodo_index = 4
    elif "mars" in message_lower: periodo_index = 6
    elif "avril" in message_lower: periodo_index = 7

    print(f"📅 Période : {PERIODES[periode_index]}")
    print(f"💰 Prix par personne : {TARIFS[formule][periode_index]} TND")

    # === CALCUL DU PRIX ===
    prix_par_personne = TARIFS[formule][periode_index]

    # Compter les personnes
    personnes = re.search(r'(\d+)\s*(?:personne|adulte|voyageur)', message_lower)
    nb_personnes = int(personnes.group(1)) if personnes else 2

    prix_total = prix_par_personne * nb_personnes * duree_sejour

    # === PRÉPARATION RÉPONSE ===
    reponse = f"""🏨 **HOTEL TOUR KHALEF** ⭐⭐⭐⭐⭐
*Assistant Devis Automatique*

📋 **Formule :** {formule}
📅 **Période :** {PERIODES[periode_index]}
👥 **Personnes :** {nb_personnes}
🌙 **Nuits :** {duree_sejour}

💰 **DEVIS ESTIMÉ : {prix_total} TND**

📧 **Réservations :** marouane.tefifha@tour-khalef.com
🌐 **Site :** www.tour-khalef.com
📞 **Notre équipe vous contacte sous 30 minutes !**

_⚠️ Estimation basée sur nos tarifs Winter 2025-2026_"""

    return reponse

# PAGE PRINCIPALE AVEC CHAT - DESIGN TOUR KHALEF
@app.route('/')
def accueil():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Assistant Devis - Hotel Tour Khalef</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --turquoise: #40E0D0;
            --turquoise-fonce: #20B2AA;
            --turquoise-clair: #AFEEEE;
            --blanc: #FFFFFF;
            --noir: #2C3E50;
            --gris-clair: #F8F9FA;
            --gris: #E9ECEF;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, var(--turquoise-clair) 0%, var(--blanc) 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
        }
        
        .logo {
            font-size: 2.5em;
            font-weight: bold;
            color: var(--noir);
            margin-bottom: 10px;
        }
        
        .logo-turquoise {
            color: var(--turquoise-fonce);
        }
        
        .slogan {
            color: var(--noir);
            font-size: 1.1em;
            opacity: 0.8;
        }
        
        .chat-container {
            background: var(--blanc);
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(64, 224, 208, 0.2);
            overflow: hidden;
            margin-bottom: 20px;
        }
        
        .chat-header {
            background: linear-gradient(135deg, var(--turquoise) 0%, var(--turquoise-fonce) 100%);
            color: var(--blanc);
            padding: 25px;
            text-align: center;
        }
        
        .chat-header h2 {
            margin-bottom: 8px;
            font-size: 1.5em;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 1em;
        }
        
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 25px;
            background: var(--gris-clair);
        }
        
        .message {
            margin-bottom: 20px;
            padding: 15px 20px;
            border-radius: 18px;
            max-width: 85%;
            line-height: 1.5;
            animation: fadeIn 0.3s ease-in;
        }
        
        .user-message {
            background: linear-gradient(135deg, var(--turquoise) 0%, var(--turquoise-fonce) 100%);
            color: var(--blanc);
            margin-left: auto;
            text-align: right;
            box-shadow: 0 4px 15px rgba(64, 224, 208, 0.3);
        }
        
        .bot-message {
            background: var(--blanc);
            border: 2px solid var(--turquoise-clair);
            color: var(--noir);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        }
        
        .chat-input-container {
            padding: 20px;
            background: var(--blanc);
            border-top: 2px solid var(--gris);
        }
        
        .chat-input {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        #user-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid var(--turquoise-clair);
            border-radius: 25px;
            font-size: 1em;
            outline: none;
            transition: all 0.3s ease;
        }
        
        #user-input:focus {
            border-color: var(--turquoise);
            box-shadow: 0 0 0 3px rgba(64, 224, 208, 0.1);
        }
        
        .send-btn {
            background: linear-gradient(135deg, var(--turquoise) 0%, var(--turquoise-fonce) 100%);
            color: var(--blanc);
            border: none;
            padding: 15px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(64, 224, 208, 0.3);
        }
        
        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(64, 224, 208, 0.4);
        }
        
        .examples {
            background: var(--blanc);
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
        }
        
        .examples h3 {
            color: var(--noir);
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .example-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .example-btn {
            background: var(--gris-clair);
            color: var(--noir);
            border: 2px solid var(--turquoise-clair);
            padding: 10px 18px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }
        
        .example-btn:hover {
            background: var(--turquoise);
            color: var(--blanc);
            border-color: var(--turquoise);
        }
        
        .contact-info {
            background: linear-gradient(135deg, var(--turquoise-clair) 0%, var(--blanc) 100%);
            padding: 25px;
            border-radius: 20px;
            text-align: center;
            border: 2px solid var(--turquoise);
            box-shadow: 0 5px 20px rgba(64, 224, 208, 0.2);
        }
        
        .contact-info h3 {
            color: var(--noir);
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .contact-details {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
        }
        
        .contact-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--noir);
            font-weight: 500;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .chat-messages {
                height: 350px;
                padding: 15px;
            }
            
            .message {
                max-width: 90%;
                padding: 12px 15px;
            }
            
            .contact-details {
                flex-direction: column;
                gap: 15px;
            }
            
            .example-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- En-tête avec logo -->
        <div class="header">
            <div class="logo">
                TOUR <span class="logo-turquoise">KHALEF</span>
            </div>
            <div class="slogan">Hôtel de Charme & Spa ⭐⭐⭐⭐⭐</div>
        </div>
        
        <!-- Interface de chat -->
        <div class="chat-container">
            <div class="chat-header">
                <h2>🤖 Assistant Devis Intelligent</h2>
                <p>Calcul automatique de vos devis en TND</p>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message bot-message">
                    🌟 <strong>Bienvenue à l'Hôtel Tour Khalef !</strong><br><br>
                    Je suis votre assistant devis personnel. Je peux calculer instantanément le prix de votre séjour en TND.<br><br>
                    
                    💡 <strong>Comment utiliser :</strong><br>
                    • "Devis 2 personnes du 15 au 20 décembre"<br>
                    • "Prix pour 3 nuits en demi-pension"<br>
                    • "Tarif all in soft pour 4 personnes"
                </div>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input">
                    <input type="text" id="user-input" 
                           placeholder="Ex: Devis pour 2 personnes du 15 au 20 décembre en demi-pension..." 
                           autofocus>
                    <button class="send-btn" onclick="sendMessage()">
                        Envoyer →
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Exemples rapides -->
        <div class="examples">
            <h3>🚀 Exemples rapides :</h3>
            <div class="example-buttons">
                <button class="example-btn" onclick="setExample('devis pour 2 personnes du 15 au 22 décembre avec petit déjeuner')">
                    Décembre - 2 pers - PD
                </button>
                <button class="example-btn" onclick="setExample('demi-pension pour 3 personnes en février 7 nuits')">
                    Février - 3 pers - DP
                </button>
                <button class="example-btn" onclick="setExample('all in soft pour 4 personnes en avril')">
                    Avril - 4 pers - All in
                </button>
                <button class="example-btn" onclick="setExample('tarif pour chambre double 5 nuits en mars')">
                    Mars - Double - 5 nuits
                </button>
            </div>
        </div>
        
        <!-- Informations de contact -->
        <div class="contact-info">
            <h3>📞 Contactez-nous</h3>
            <div class="contact-details">
                <div class="contact-item">
                    📧 <span>marouane.tefifha@tour-khalef.com</span>
                </div>
                <div class="contact-item">
                    🌐 <span>www.tour-khalef.com</span>
                </div>
                <div class="contact-item">
                    🏨 <span>Hôtel Tour Khalef ⭐⭐⭐⭐⭐</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        function setExample(text) {
            document.getElementById('user-input').value = text;
        }

        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (message === '') return;
            
            // Ajouter le message de l'utilisateur
            addMessage(message, 'user');
            input.value = '';
            
            // Afficher indicateur de frappe
            showTypingIndicator();
            
            // Envoyer au serveur
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                removeTypingIndicator();
                addMessage(data.reponse, 'bot');
            })
            .catch(error => {
                removeTypingIndicator();
                addMessage('Désolé, une erreur est survenue. Veuillez réessayer.', 'bot');
            });
        }

        function addMessage(text, sender) {
            const messagesDiv = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = text.replace(/\n/g, '<br>');
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function showTypingIndicator() {
            const messagesDiv = document.getElementById('chat-messages');
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typing-indicator';
            typingDiv.className = 'message bot-message';
            typingDiv.innerHTML = '💭 Calcul du devis en cours...';
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function removeTypingIndicator() {
            const typingDiv = document.getElementById('typing-indicator');
            if (typingDiv) {
                typingDiv.remove();
            }
        }

        // Support touche Entrée
        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Focus automatique
        document.getElementById('user-input').focus();
    </script>
</body>
</html>
    """

# ROUTE POUR LE CHAT
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message_utilisateur = data.get('message', '')
    
    reponse_bot = analyser_devis(message_utilisateur)
    
    return jsonify({
        'reponse': reponse_bot,
        'status': 'success'
    })

# Route de test existante
@app.route('/test')
def tester_analyse():
    message = request.args.get('message', 'devis pour 2 personnes du 15 au 22 décembre')
    reponse = analyser_devis(message)
    return f"<pre>{reponse}</pre>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Assistant Devis Hotel Tour Khalef - Démarrage...")
    app.run(host='0.0.0.0', port=port, debug=False)

