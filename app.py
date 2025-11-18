from flask import Flask, request, jsonify, render_template
import re
import requests
import os
from datetime import datetime

app = Flask(__name__)

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
    elif "petit déjeuner" in message_texte.lower() or "pd" in message_texte.lower():
        formule = "LPD"

    # Détection période
    periode_index = 2  # Décembre par défaut
    if "novembre" in message_texte.lower(): periodo_index = 0
    elif "décembre" in message_texte.lower() or "dec" in message_texte.lower(): periodo_index = 2
    elif "janvier" in message_texte.lower(): periodo_index = 3
    elif "février" in message_texte.lower() or "fevrier" in message_texte.lower(): periodo_index = 4
    elif "mars" in message_texte.lower(): periodo_index = 6
    elif "avril" in message_texte.lower(): periodo_index = 7

    # Détection personnes
    personnes = re.search(r'(\d+)\s*(?:personne|adulte|voyageur)', message_texte)
    nb_personnes = int(personnes.group(1)) if personnes else 2

    # Calcul
    prix_par_personne = TARIFS[formule][periode_index]
    prix_total = prix_par_personne * nb_personnes * duree_sejour

    # Préparation réponse
    reponse = f"""🏨 **HOTEL TOUR KHALEF** ⭐⭐⭐⭐⭐

📋 **Formule :** {formule}
📅 **Période :** {PERIODES[periode_index]}
👥 **Personnes :** {nb_personnes}
🌙 **Nuits :** {duree_sejour}

💰 **DEVIS : {prix_total}€**

📞 Notre équipe vous contacte sous 30 minutes pour confirmation !

ℹ️ _Tarifs selon grille Winter 2025-2026_"""
    
    return reponse

# PAGE PRINCIPALE AVEC CHAT
@app.route('/')
def accueil():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Chat Bot - Hotel Tour Khalef</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chat-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chat-header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 10px;
            max-width: 80%;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background: white;
            border: 1px solid #ddd;
        }
        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #ddd;
        }
        #user-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 20px;
            margin-right: 10px;
        }
        button {
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 20px;
            cursor: pointer;
        }
        button:hover {
            background: #218838;
        }
        .examples {
            background: #e9ecef;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
        }
        .example-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>🤖 Hotel Tour Khalef - Assistant Devis</h2>
            <p>Je vous aide à calculer votre devis automatiquement</p>
        </div>
        
        <div class="chat-messages" id="chat-messages">
            <div class="message bot-message">
                👋 Bonjour ! Je suis l'assistant de l'Hotel Tour Khalef.<br>
                Dites-moi votre demande de séjour et je vous préparerai un devis immédiatement !
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="user-input" placeholder="Ex: Je veux réserver du 15 au 20 décembre pour 2 personnes..." autofocus>
            <button onclick="sendMessage()">Envoyer</button>
        </div>
    </div>

    <div class="examples">
        <p><strong>Exemples rapides :</strong></p>
        <button class="example-btn" onclick="setExample('du 15 au 22 décembre pour 2 personnes avec petit déjeuner')">Décembre - 2 pers - PD</button>
        <button class="example-btn" onclick="setExample('demi-pension pour 3 personnes en février 7 nuits')">Février - 3 pers - DP</button>
        <button class="example-btn" onclick="setExample('all in soft pour 4 personnes en avril')">Avril - 4 pers - All in</button>
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
                addMessage(data.reponse, 'bot');
            })
            .catch(error => {
                addMessage('Désolé, une erreur est survenue.', 'bot');
            });
        }

        function addMessage(text, sender) {
            const messagesDiv = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = text.replace(/\\n/g, '<br>');
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // Enter key support
        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
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
    message = request.args.get('message', 'du 15 au 22 décembre pour 2 personnes')
    reponse = analyser_devis(message)
    return f"<pre>{reponse}</pre>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Bot Chat Hotel Tour Khalef - Démarrage...")
    app.run(host='0.0.0.0', port=port, debug=False)
