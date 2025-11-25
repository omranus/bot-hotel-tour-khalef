from flask import Flask, request, jsonify
import re
import os

app = Flask(__name__)

# ==================== BASE DE CONNAISSANCES TOUR KHALEF ====================

BASE_CONNAISSANCES = {
    # INFORMATIONS GÉNÉRALES
    "presentation": {
        "questions": ["présentation", "description", "historique", "qui êtes-vous", "hotel"],
        "reponse": """🏨 **HÔTEL TOUR KHALEF - LUXE & SÉRÉNITÉ**

Luxe, sérénité et expérience unique au cœur de la Méditerranée.

🌟 **Description :**
Resort moderne en front de mer alliant modernité occidentale et élégance orientale.

📍 **Situation :**
• Zone touristique de Sousse
• 30 min des aéroports Enfidha/Monastir
• 5 min de la Médina (classée UNESCO)
• 10 min du Port El Kantaoui et golfs

🏛️ **Culture :**
Médina, Grande Mosquée, Ribat, Musée archéologique, Catacombes"""
    },
    
    # CHAMBRES ET SUITES
    "chambres": {
        "questions": ["chambre", "suite", "hébergement", "logement", "chambres"],
        "reponse": """🛏️ **CHAMBRES & SUITES - 490 UNITÉS**

• 379 Chambres Standard (26m²)
• 40 Chambres Luxe (26m²) 
• 45 Chambres Familiales (32m²)
• 12 Suites Junior (36m²)
• 14 Suites Senior Prestige (52m²)

🎯 **Équipements :**
Balcon/terrasse • Climatisation • Salle de bain italienne • Mini-bar gratuit • Coffre-fort gratuit • Bouilloire/Machine à café • TV satellite • WiFi gratuit • Sèche-cheveux • Fer à repasser (sur demande)"""
    },
    
    # RESTAURANTS
    "restaurants": {
        "questions": ["restaurant", "manger", "dîner", "diner", "repas", "buffet"],
        "reponse": """🍽️ **RESTAURANTS TOUR KHALEF**

**Le Grand Restaurant** 🏛️
• Cuisine internationale en buffet

**La Palmeraie** 🌴  
• Petit-déjeuner tardif, déjeuner, collation

**L'Oliveraie** 🇮🇹🇹🇳
• Cuisine italienne & tunisienne • Terrasse jardin

**Le Pêcheur** 🐟 
• Restaurant à thème (haute saison)

⏰ **Horaires :**
Petit-déjeuner : 7h-10h • Déjeuner : 12h30-14h • Dîner : 19h-21h"""
    },
    
    # BARS
    "bars": {
        "questions": ["bar", "boisson", "boire", "cocktail", "vin"],
        "reponse": """🍹 **BARS TOUR KHALEF**

**Bar Salon** 🛋️
• Boissons locales & internationales

**Lobby Bar** ☕  
• Boissons + station de café

**Bar Terrasse** 🌅
• Ambiance soirée

**Pool Bar** 🏊
• Piscine

**Beach Bar** 🏖️
• Plage

🕙 **Service : 10h à minuit**"""
    },
    
    # FORMULE TOUT INCLUS
    "formule": {
        "questions": ["tout inclus", "all inclusive", "formule", "inclus", "compris"],
        "reponse": """🎫 **FORMULE TOUT INCLUS**

✅ **Inclus :**
• Petit-déjeuner 7h-10h
• Déjeuner 12h30-14h  
• Dîner 19h-21h
• Petit-déjeuner tardif
• Goûter/Intersnacks
• Boissons à table (eau, bière, vin, sodas)

🌟 **Bonus :**
• Dîner à thème offert pour séjour ≥ 7 nuits (sur réservation)

🍷 **Boissons :**
Restaurants & bars : eau, bière locale, vins locaux, liqueurs locales, sodas, infusions, café"""
    },
    
    # SPA & BIEN-ÊTRE
    "spa": {
        "questions": ["spa", "massage", "bien-être", "détente", "thalasso", "relaxation"],
        "reponse": """💆 **SPA & THALASSO - 4700m²**

**Soins :**
Massages • Enveloppements • Hydrothérapie • Thalassothérapie

**Installations :**
• Piscine eau de mer chauffée
• Hammams & Saunas  
• Salle fitness 92m² (dernière génération)
• Espace repos & tisanerie
• Boutique bien-être"""
    },
    
    # SPORTS & LOISIRS
    "sports": {
        "questions": ["sport", "piscine", "loisir", "activité", "animation", "gym"],
        "reponse": """🏊 **SPORTS & LOISIRS**

**Piscines :**
• Piscine extérieure eau douce + toboggans
• Piscine extérieure eau de mer  
• Piscine intérieure (hiver)
• Piscine couverte eau de mer (chauffée hiver)

**Sports Gratuits :**
Tennis • Padel (3 courts) • Pickleball (4 courts) • Football • Volley • Water-polo • Tennis de table • Aérobic • Aquagym

**Famille :**
2 piscines enfants • Aire jeux • Mini-club (4-12 ans) • Buffet enfants • Lits/chaises bébé"""
    },
    
    # SERVICES
    "services": {
        "questions": ["service", "réception", "wifi", "parking", "blanchisserie", "change"],
        "reponse": """🛎️ **SERVICES**

**Gratuits :**
• WiFi dans tout l'hôtel
• Parking 
• Serviettes piscine/plage
• Coffre-fort
• Club enfants
• Station café 24/7

**Disponibles :**
• Réception 24/7
• Distributeur billets
• Cartes crédit (Visa/Mastercard)
• Salle conférence (300 pers.)
• Service change
• Blanchisserie
• Boutique souvenirs
• Personnes mobilité réduite"""
    },
    
    # PRATIQUE
    "pratique": {
        "questions": ["check-in", "check-out", "horaire", "heure", "arrivée", "départ"],
        "reponse": """📋 **INFORMATIONS PRATIQUES**

**Horaires :**
• Check-in : À partir de 14h
• Check-out : Jusqu'à 11h
• Early check-in / Late check-out : Selon disponibilité

**Services :**
• Petit-déjeuner prématuré
• Dîner tardif
• Chaises roulantes sur demande"""
    }
}

# ==================== SYSTÈME DE DEVIS (EXISTANT) ====================

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
    
    mots_cles_devis = ['devis', 'tarif', 'prix', 'réservation', 'réserver', 'coût']
    concerne_devis = any(mot in message_lower for mot in mots_cles_devis)
    
    if not concerne_devis:
        return None  # Pas une demande de devis
    
    # Logique de calcul existante
    duree_sejour = 7
    pattern_dates = r'du\s*(\d{1,2})\s*au\s*(\d{1,2})\s*(\w+)'
    match_dates = re.search(pattern_dates, message_lower)
    
    if match_dates:
        date_debut = int(match_dates.group(1))
        date_fin = int(match_dates.group(2))
        duree_sejour = date_fin - date_debut

    formule = "LPD"
    if "demi-pension" in message_lower or "hb" in message_lower:
        formule = "HB"
    elif "all in soft" in message_lower:
        formule = "All in soft" 
    elif "all in" in message_lower:
        formule = "All in"

    periode_index = 2
    if "novembre" in message_lower: periodo_index = 0
    elif "décembre" in message_lower or "dec" in message_lower: periodo_index = 2
    elif "janvier" in message_lower: periodo_index = 3
    elif "février" in message_lower or "fevrier" in message_lower: periodo_index = 4
    elif "mars" in message_lower: periodo_index = 6
    elif "avril" in message_lower: periodo_index = 7

    prix_par_personne = TARIFS[formule][periode_index]
    personnes = re.search(r'(\d+)\s*(?:personne|adulte|voyageur)', message_lower)
    nb_personnes = int(personnes.group(1)) if personnes else 2
    prix_total = prix_par_personne * nb_personnes * duree_sejour

    reponse = f"""🏨 **HOTEL TOUR KHALEF** ⭐⭐⭐⭐⭐
*Devis Automatique*

📋 **Formule :** {formule}
📅 **Période :** {PERIODES[periode_index]}
👥 **Personnes :** {nb_personnes}
🌙 **Nuits :** {duree_sejour}

💰 **ESTIMATION : {prix_total} TND**

📧 **Réservations :** marouane.tefifha@tour-khalef.com
🌐 **Site :** www.tour-khalef.com
📞 **Contact sous 30 minutes !**

_Estimation basée sur tarifs Winter 2025-2026_"""
    
    return reponse

def trouver_reponse_infos(message_texte):
    """Trouve la réponse dans la base de connaissances"""
    message_lower = message_texte.lower()
    
    # Cherche dans chaque catégorie
    for categorie, infos in BASE_CONNAISSANCES.items():
        for mot_cle in infos["questions"]:
            if mot_cle in message_lower:
                return infos["reponse"]
    
    # Si aucune correspondance
    return """🤖 **ASSISTANT TOUR KHALEF**

Je peux vous aider sur :

💰 **Devis & Tarifs** 
🏨 **Chambres & Suites**
🍽️ **Restaurants & Bars**
💆 **SPA & Bien-être** 
🏊 **Sports & Loisirs**
🛎️ **Services & Informations pratiques**

💡 **Exemples :** 
• "Devis pour 2 personnes en décembre"
• "Horaires du restaurant"
• "Vos équipements spa"
• "Check-in/check-out"

Quelle information souhaitez-vous ?"""

# ==================== APPLICATION FLASK ====================

@app.route('/')
def accueil():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Assistant Tour Khalef</title>
    <meta charset="UTF-8">
    <style>
        :root {
            --turquoise: #40E0D0;
            --turquoise-fonce: #20B2AA;
            --blanc: #FFFFFF;
            --noir: #2C3E50;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #AFEEEE 0%, #FFFFFF 100%);
            min-height: 100vh;
            padding: 20px;
            margin: 0;
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
        
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 25px;
            background: #f8f9fa;
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
        }
        
        .bot-message {
            background: white;
            border: 2px solid #AFEEEE;
            color: var(--noir);
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 2px solid #E9ECEF;
        }
        
        .chat-input {
            display: flex;
            gap: 12px;
            align-items: center;
        }
        
        #user-input {
            flex: 1;
            padding: 15px 20px;
            border: 2px solid #AFEEEE;
            border-radius: 25px;
            font-size: 1em;
            outline: none;
        }
        
        .send-btn {
            background: linear-gradient(135deg, var(--turquoise) 0%, var(--turquoise-fonce) 100%);
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
        }
        
        .categories {
            background: white;
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        }
        
        .categories h3 {
            color: var(--noir);
            margin-bottom: 15px;
        }
        
        .category-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .category-btn {
            background: #f8f9fa;
            color: var(--noir);
            border: 2px solid #AFEEEE;
            padding: 10px 18px;
            border-radius: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .category-btn:hover {
            background: var(--turquoise);
            color: white;
        }
        
        .contact-info {
            background: linear-gradient(135deg, #AFEEEE 0%, white 100%);
            padding: 25px;
            border-radius: 20px;
            text-align: center;
            border: 2px solid var(--turquoise);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">TOUR <span class="logo-turquoise">KHALEF</span></div>
            <div class="slogan">Luxe, sérénité et expérience unique ⭐⭐⭐⭐⭐</div>
        </div>
        
        <div class="chat-container">
            <div class="chat-header">
                <h2>🤖 Assistant Tour Khalef</h2>
                <p>Devis automatiques & Informations complètes</p>
            </div>
            
            <div class="chat-messages" id="chat-messages">
                <div class="message bot-message">
                    🌟 <strong>Bienvenue à l'Hôtel Tour Khalef !</strong><br><br>
                    Je suis votre assistant personnel. Je peux :<br>
                    • Calculer vos devis automatiquement<br>
                    • Répondre à toutes vos questions sur l'hôtel<br><br>
                    Que souhaitez-vous savoir ?
                </div>
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input">
                    <input type="text" id="user-input" placeholder="Ex: Devis 2 personnes décembre ou Horaires restaurant..." autofocus>
                    <button class="send-btn" onclick="sendMessage()">Envoyer →</button>
                </div>
            </div>
        </div>
        
        <div class="categories">
            <h3>📋 Catégories rapides :</h3>
            <div class="category-buttons">
                <button class="category-btn" onclick="setExample('devis pour 2 personnes en décembre')">💰 Devis</button>
                <button class="category-btn" onclick="setExample('types de chambres')">🏨 Chambres</button>
                <button class="category-btn" onclick="setExample('horaires restaurant')">🍽️ Restaurants</button>
                <button class="category-btn" onclick="setExample('équipements spa')">💆 SPA</button>
                <button class="category-btn" onclick="setExample('activités sportives')">🏊 Sports</button>
                <button class="category-btn" onclick="setExample('check in check out')">🛎️ Services</button>
            </div>
        </div>
        
        <div class="contact-info">
            <h3>📞 Contact</h3>
            <p>📧 marouane.tefifha@tour-khalef.com | 🌐 www.tour-khalef.com</p>
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
            
            addMessage(message, 'user');
            input.value = '';
            
            showTypingIndicator();
            
            fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                removeTypingIndicator();
                addMessage(data.reponse, 'bot');
            })
            .catch(error => {
                removeTypingIndicator();
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

        function showTypingIndicator() {
            const messagesDiv = document.getElementById('chat-messages');
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typing-indicator';
            typingDiv.className = 'message bot-message';
            typingDiv.innerHTML = '💭 Recherche en cours...';
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function removeTypingIndicator() {
            const typingDiv = document.getElementById('typing-indicator');
            if (typingDiv) typingDiv.remove();
        }

        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
    '''

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message_utilisateur = data.get('message', '')
    
    # Essaie d'abord le module devis
    reponse_devis = analyser_devis(message_utilisateur)
    if reponse_devis:
        return jsonify({'reponse': reponse_devis, 'status': 'success'})
    
    # Sinon cherche dans les informations
    reponse_infos = trouver_reponse_infos(message_utilisateur)
    return jsonify({'reponse': reponse_infos, 'status': 'success'})

@app.route('/test')
def tester():
    message = request.args.get('message', 'bonjour')
    reponse_devis = analyser_devis(message)
    if reponse_devis:
        return f"<pre>{reponse_devis}</pre>"
    reponse_infos = trouver_reponse_infos(message)
    return f"<pre>{reponse_infos}</pre>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Assistant Tour Khalef - Démarrage...")
    app.run(host='0.0.0.0', port=port, debug=False)


