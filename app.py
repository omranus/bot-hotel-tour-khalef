from flask import Flask, request, jsonify
import re
import os

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
    """Analyse le message et calcule le devis"""
    message_lower = message_texte.lower()
    
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
    concerne_devis = any(mot in message_lower for mot in mots_cles_devis)
    
    if not concerne_devis:
        return "❌ **Désolé, je suis un assistant spécialisé dans les devis.**\n\nJe peux vous aider à calculer le prix d'un séjour, mais je ne peux pas répondre à d'autres questions.\n\n💡 **Exemple de demande :** 'Devis pour 2 personnes du 15 au 20 décembre en demi-pension'"
    
    # Détection de la durée
    duree_sejour = 7
    pattern_dates = r'du\s*(\d{1,2})\s*au\s*(\d{1,2})\s*(\w+)'
    match_dates = re.search(pattern_dates, message_lower)
    
    if match_dates:
        date_debut = int(match_dates.group(1))
        date_fin = int(match_dates.group(2))
        duree_sejour = date_fin - date_debut

    # Détection formule
    formule = "LPD"
    if "demi-pension" in message_lower or "hb" in message_lower:
        formule = "HB"
    elif "all in soft" in message_lower:
        formule = "All in soft" 
    elif "all in" in message_lower:
        formule = "All in"
    elif "petit déjeuner" in message_lower or "pd" in message_lower:
        formule = "LPD"

    # Détection période
    periode_index = 2
    if "novembre" in message_lower: periodo_index = 0
    elif "décembre" in message_lower or "dec" in message_lower: periodo_index = 2
    elif "janvier" in message_lower: periodo_index = 3
    elif "février" in message_lower or "fevrier" in message_lower: periodo_index = 4
    elif "mars" in message_lower: periodo_index = 6
    elif "avril" in message_lower: periodo_index = 7

    # Calcul du prix
    prix_par_personne = TARIFS[formule][periode_index]

    # Compter les personnes
    personnes = re.search(r'(\d+)\s*(?:personne|adulte|voyageur)', message_lower)
    nb_personnes = int(personnes.group(1)) if personnes else 2

    prix_total = prix_par_personne * nb_personnes * duree_sejour

    # Préparation réponse
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

# Page d'accueil simplifiée mais fonctionnelle
@app.route('/')
def accueil():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Assistant Devis - Hotel Tour Khalef</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f0f8ff;
        }
        .chat-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chat-header {
            background: #40E0D0;
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
            background: #40E0D0;
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
            background: #40E0D0;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 20px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>🤖 Hotel Tour Khalef - Assistant Devis</h2>
            <p>Je calcule automatiquement vos devis en TND</p>
        </div>
        
        <div class="chat-messages" id="chat-messages">
            <div class="message bot-message">
                👋 Bonjour ! Je suis l'assistant devis de l'Hotel Tour Khalef.
                Dites-moi votre demande et je calculerai le prix automatiquement.
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="user-input" placeholder="Ex: Devis pour 2 personnes du 15 au 20 décembre..." autofocus>
            <button onclick="sendMessage()">Envoyer</button>
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (message === '') return;
            
            addMessage(message, 'user');
            input.value = '';
            
            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
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
            messageDiv.className = 'message ' + sender + '-message';
            messageDiv.innerHTML = text.replace(/\\n/g, '<br>');
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
    '''

# Route pour le chat
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message_utilisateur = data.get('message', '')
    reponse_bot = analyser_devis(message_utilisateur)
    return jsonify({'reponse': reponse_bot, 'status': 'success'})

# Route de test
@app.route('/test')
def tester_analyse():
    message = request.args.get('message', 'devis pour 2 personnes du 15 au 22 décembre')
    reponse = analyser_devis(message)
    return f"<pre>{reponse}</pre>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


