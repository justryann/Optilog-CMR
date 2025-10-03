import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import time
import math
from io import StringIO
import requests
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
import warnings
warnings.filterwarnings('ignore')
import traceback

# Configuration de la page
st.set_page_config(
    page_title="OptiLog Cameroun - Optimisation Logistique",
    page_icon="🇨🇲",
    layout="wide"
)

# CSS personnalisé - Thème professionnel et dynamique
st.markdown("""
<style>
    /* Réinitialisation et polices */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Montserrat', sans-serif;
    }
    
    /* Variables CSS modernes */
    :root {
        --primary: #0056b3; /* Bleu professionnel */
        --secondary: #003366; /* Bleu marine */
        --accent: #FF7D00; /* Orange vif */
        --success: #28a745;
        --warning: #ffc107;
        --danger: #dc3545;
        --dark: #212529;
        --light: #f8f9fa;
        --white: #ffffff;
        --gray: #6c757d;
        --border-radius: 12px;
        --box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        --transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    /* Fond d'application avec dégradé subtil */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
    }
    
    /* En-tête principal */
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        margin: 1rem 0;
        box-shadow: var(--box-shadow);
        position: relative;
        overflow: hidden;
        text-align: center;
        animation: fadeIn 0.8s ease-out;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
                    rgba(255,255,255,0.1) 0%, 
                    rgba(255,255,255,0.3) 50%, 
                    rgba(255,255,255,0.1) 100%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        100% { transform: translateX(100%); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    
    /* Styles unifiés pour les en-têtes de toutes les pages */
    .page-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        position: relative;
        overflow: hidden;
        text-align: center;
    }
    
    .page-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
                    rgba(255,255,255,0.1) 0%, 
                    rgba(255,255,255,0.3) 50%, 
                    rgba(255,255,255,0.1) 100%);
        transform: translateX(-100%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        100% { transform: translateX(100%); }
    }
    
    /* Styles pour les cartes de statistiques */
    .stats-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        text-align: center;
        margin-bottom: 1rem;
        border-top: 4px solid;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .stats-card.in-progress { border-color: #3498db; }
    .stats-card.delivered { border-color: #27ae60; }
    .stats-card.delayed { border-color: #f39c12; }
    .stats-card.pending { border-color: #e74c3c; }
    
    .stats-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: #2c3e50;
    }
    
    .stats-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin-bottom: 0.5rem;
    }
    
    .stats-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    /* Animation pour les cartes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stats-card {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .page-header {
            padding: 1.2rem;
        }
        
        .stats-value {
            font-size: 2rem;
        }
    }
      
            
    /* Sidebar stylisée */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--secondary) 0%, var(--primary) 100%) !important;
        box-shadow: 5px 0 15px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="stSidebar"] .stRadio > div {
        flex-direction: column;
        gap: 0.5rem;
    }
    
    [data-testid="stSidebar"] label {
        color: white !important;
        padding: 0.75rem 1rem;
        border-radius: var(--border-radius);
        transition: var(--transition);
        margin: 0.25rem 0;
        background: rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] label:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(5px);
    }
    
    [data-testid="stSidebar"] label > div:first-child {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Boutons modernes */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: var(--transition);
        box-shadow: var(--box-shadow);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(0, 86, 179, 0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stButton > button::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
                    transparent, 
                    rgba(255,255,255,0.3), 
                    transparent);
        transform: translateX(-100%);
        transition: 0.6s;
    }
    
    .stButton > button:hover::after {
        transform: translateX(100%);
    }
    
    /* Cartes métriques */
    [data-testid="metric-container"] {
        background: white;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--box-shadow);
        transition: var(--transition);
        border-left: 5px solid var(--accent);
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
    }
    
    [data-testid="metric-container"] > div {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    [data-testid="metric-container"] label {
        font-size: 1rem;
        color: var(--gray);
        font-weight: 500;
    }
    
    [data-testid="metric-container"] div[class*="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--dark);
    }
    
    /* Onglets stylisés */
    [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem !important;
        border-radius: var(--border-radius) !important;
        transition: var(--transition) !important;
        background: rgba(0, 86, 179, 0.1) !important;
    }
    
    [data-baseweb="tab"]:hover {
        background: rgba(0, 86, 179, 0.2) !important;
    }
    
    [data-baseweb="tab"][aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
        font-weight: 600;
    }
    
    /* Inputs et sélecteurs */
    [data-baseweb="input"], 
    [data-baseweb="select"] > div,
    .stSelectbox > div > div,
    .stTextInput > div > div {
        border-radius: var(--border-radius) !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        transition: var(--transition);
    }
    
    [data-baseweb="input"]:focus-within, 
    [data-baseweb="select"] > div:focus-within,
    .stSelectbox > div > div:focus-within,
    .stTextInput > div > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 2px rgba(0, 86, 179, 0.2) !important;
    }
    
    /* Graphiques encadrés */
    .element-container .plotly-graph-div {
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow);
        overflow: hidden;
        transition: var(--transition);
    }
    
    .element-container .plotly-graph-div:hover {
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
    }
    
    /* Tableaux modernes */
    .stDataFrame {
        border-radius: var(--border-radius) !important;
        box-shadow: var(--box-shadow) !important;
    }
    
    .stDataFrame thead tr {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: white !important;
    }
    
    .stDataFrame th {
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        letter-spacing: 0.5px;
    }
    
    .stDataFrame tr:hover {
        background: rgba(0, 86, 179, 0.05) !important;
    }
    
    /* Messages d'alerte */
    .stAlert {
        border-radius: var(--border-radius) !important;
        box-shadow: var(--box-shadow) !important;
        border-left: 5px solid;
    }
    
    .stAlert[data-status="success"] {
        border-left-color: var(--success) !important;
        background: rgba(40, 167, 69, 0.1) !important;
    }
    
    .stAlert[data-status="warning"] {
        border-left-color: var(--warning) !important;
        background: rgba(255, 193, 7, 0.1) !important;
    }
    
    .stAlert[data-status="error"] {
        border-left-color: var(--danger) !important;
        background: rgba(220, 53, 69, 0.1) !important;
    }
    
    .stAlert[data-status="info"] {
        border-left-color: var(--primary) !important;
        background: rgba(0, 86, 179, 0.1) !important;
    }
    
    /* Expandeurs */
    .stExpander {
        border-radius: var(--border-radius) !important;
        box-shadow: var(--box-shadow) !important;
    }
    
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        color: var(--primary) !important;
    }
    
    /* Pied de page */
    footer {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 2rem;
        border-radius: var(--border-radius);
        margin-top: 3rem;
        text-align: center;
        box-shadow: var(--box-shadow);
    }
    
    footer p {
        margin: 0.5rem 0;
        opacity: 0.9;
    }
    
    /* Effets spéciaux */
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.03); }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            padding: 1.5rem;
        }
        
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        [data-testid="metric-container"] {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.title("OptiLog Cameroun 🇨🇲")
menu_options = [
    ("📊 Tableau de Bord", "Dashboard"),
    ("📁 Gestion des Données", "DataManagement"),
    ("🌍 Suivi des Livraisons", "Tracking"),
    ("🔮 Prévisions Logistiques", "Prediction"),
    ("🗺 Optimisation des Itinéraires", "Routes"),
    ("📈 Performance", "Performance"),
    ("🔔 Alertes", "Alertes")
]

selected = st.sidebar.radio(
    "Navigation",
    [option[1] for option in menu_options],
    format_func=lambda x: [option[0] for option in menu_options if option[1] == x][0]
)

# Données géographiques réelles du Cameroun avec coordonnées précises
CAMEROON_CITIES = {
    'Yaoundé': {'lat': 3.8480, 'lon': 11.5021, 'region': 'Centre', 'population': 4100000},
    'Douala': {'lat': 4.0511, 'lon': 9.7679, 'region': 'Littoral', 'population': 3663000},
    'Garoua': {'lat': 9.3014, 'lon': 13.3937, 'region': 'Nord', 'population': 436899},
    'Bamenda': {'lat': 5.9614, 'lon': 10.1517, 'region': 'Nord-Ouest', 'population': 2500000},
    'Maroua': {'lat': 10.5956, 'lon': 14.3247, 'region': 'Extrême-Nord', 'population': 383000},
    'Ngaoundéré': {'lat': 7.3167, 'lon': 13.5833, 'region': 'Adamaoua', 'population': 385000},
    'Bafoussam': {'lat': 5.4667, 'lon': 10.5167, 'region': 'Ouest', 'population': 400000},
    'Bertoua': {'lat': 4.5833, 'lon': 13.6833, 'region': 'Est', 'population': 218000},
    'Ebolowa': {'lat': 2.9000, 'lon': 11.1500, 'region': 'Sud', 'population': 87000},
    'Limbe': {'lat': 4.0167, 'lon': 9.2167, 'region': 'Sud-Ouest', 'population': 84000},
    'Kribi': {'lat': 2.9333, 'lon': 9.9167, 'region': 'Sud', 'population': 58000},
    'Kumba': {'lat': 4.6333, 'lon': 9.4167, 'region': 'Sud-Ouest', 'population': 144000}
}

# Matrice des distances réelles entre villes (en km)
DISTANCE_MATRIX = {
    ('Yaoundé', 'Douala'): 243,
    ('Yaoundé', 'Garoua'): 621,
    ('Yaoundé', 'Bamenda'): 371,
    ('Yaoundé', 'Maroua'): 733,
    ('Yaoundé', 'Ngaoundéré'): 438,
    ('Yaoundé', 'Bafoussam'): 292,
    ('Yaoundé', 'Bertoua'): 306,
    ('Yaoundé', 'Ebolowa'): 178,
    ('Douala', 'Garoua'): 697,
    ('Douala', 'Bamenda'): 371,
    ('Douala', 'Bafoussam'): 273,
    ('Douala', 'Limbe'): 75,
    ('Douala', 'Kribi'): 158,
    ('Bamenda', 'Bafoussam'): 81,
    ('Garoua', 'Maroua'): 184,
    ('Garoua', 'Ngaoundéré'): 260,
}

# État des routes réelles au Cameroun
ROAD_CONDITIONS = {
    ('Yaoundé', 'Douala'): {'condition': 'Excellente', 'type': 'Autoroute', 'pedagage': 2},
    ('Yaoundé', 'Bafoussam'): {'condition': 'Bonne', 'type': 'Nationale', 'pedagage': 1},
    ('Yaoundé', 'Ebolowa'): {'condition': 'Moyenne', 'type': 'Nationale', 'pedagage': 1},
    ('Douala', 'Bamenda'): {'condition': 'Bonne', 'type': 'Nationale', 'pedagage': 2},
    ('Douala', 'Limbe'): {'condition': 'Excellente', 'type': 'Nationale', 'pedagage': 0},
    ('Bamenda', 'Bafoussam'): {'condition': 'Moyenne', 'type': 'Régionale', 'pedagage': 0},
    ('Garoua', 'Maroua'): {'condition': 'Bonne', 'type': 'Nationale', 'pedagage': 1},
    ('Yaoundé', 'Bertoua'): {'condition': 'Dégradée', 'type': 'Nationale', 'pedagage': 1},
}

def get_real_distance(city1, city2):
    """Obtient la distance réelle entre deux villes"""
    key1 = (city1, city2)
    key2 = (city2, city1)
    
    if key1 in DISTANCE_MATRIX:
        return DISTANCE_MATRIX[key1]
    elif key2 in DISTANCE_MATRIX:
        return DISTANCE_MATRIX[key2]
    else:
        # Calcul approximatif avec Haversine si pas dans la matrice
        coord1 = (CAMEROON_CITIES[city1]['lat'], CAMEROON_CITIES[city1]['lon'])
        coord2 = (CAMEROON_CITIES[city2]['lat'], CAMEROON_CITIES[city2]['lon'])
        return haversine_distance(coord1, coord2)

def haversine_distance(coord1, coord2):
    """Calcule la distance Haversine entre deux coordonnées"""
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Rayon de la Terre en km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def load_default_data():
    """Charge les données par défaut"""
    dates = pd.date_range(start='2023-01-01', end='2024-01-31', freq='D')
    
    transport_data = pd.DataFrame({
        'Date': dates,
        'Ville_Origine': np.random.choice(list(CAMEROON_CITIES.keys()), len(dates)),
        'Ville_Destination': np.random.choice(list(CAMEROON_CITIES.keys()), len(dates)),
        'Colis_Livres': np.random.poisson(150, len(dates)),
        'Retards_Minutes': np.random.exponential(45, len(dates)),
        'Cout_Transport': np.random.normal(350000, 80000, len(dates)),
        'Distance_km': np.random.normal(400, 150, len(dates)),
        'Type_Vehicule': np.random.choice(['Camion 10T', 'Camion 5T', 'Véhicule léger'], len(dates)),
        'Chauffeur': [f'Chauffeur_{i%50}' for i in range(len(dates))],
        'Carburant_Litres': np.random.normal(80, 25, len(dates))
    })
    
    # Assurer que les valeurs sont positives
    transport_data['Cout_Transport'] = np.abs(transport_data['Cout_Transport'])
    transport_data['Distance_km'] = np.abs(transport_data['Distance_km'])
    transport_data['Carburant_Litres'] = np.abs(transport_data['Carburant_Litres'])
    
    return transport_data

 #Initialisation des données dans session_state
if 'transport_data' not in st.session_state:
    st.session_state.transport_data = pd.DataFrame()  # DataFrame vide initial
    st.session_state.use_real_data = False
    st.session_state.file_uploaded = False

def get_current_data():
    """Retourne les données actuellement utilisées (réelles ou simulées)"""
    if st.session_state.use_real_data and not st.session_state.transport_data.empty:
        return st.session_state.transport_data
    else:
        return load_default_data()
# Page Gestion des Données
if selected == "DataManagement":
    st.markdown('<div class="page-header"><h1>📁 Gestion des Données</h1></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("📤 Charger vos données")
        
        uploaded_file = st.file_uploader(
            "Choisissez un fichier CSV",
            type=['csv'],
            help="Le fichier doit contenir au minimum les colonnes: Date, Ville_Origine, Ville_Destination, Colis_Livres",
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Validation des colonnes requises
                required_cols = ['Date', 'Ville_Origine', 'Ville_Destination', 'Colis_Livres']
                missing_cols = [col for col in required_cols if col not in df.columns]
                
                if missing_cols:
                    st.error(f"❌ Colonnes manquantes: {', '.join(missing_cols)}")
                    st.info("Colonnes disponibles: " + ", ".join(df.columns.tolist()))
                else:
                    # Conversion robuste des dates
                    try:
                        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                        # Suppression des lignes avec dates invalides
                        df = df.dropna(subset=['Date'])
                        
                        if df.empty:
                            raise ValueError("Aucune date valide trouvée après conversion")
                    except Exception as date_error:
                        st.error(f"Erreur de conversion des dates: {str(date_error)}")
                        df['Date'] = datetime.now()  # Valeur par défaut
                    
                    # Ajout des colonnes manquantes avec des valeurs par défaut si nécessaire
                    if 'Retards_Minutes' not in df.columns:
                        df['Retards_Minutes'] = np.random.exponential(45, len(df)).round(1)
                    if 'Cout_Transport' not in df.columns:
                        df['Cout_Transport'] = np.abs(np.random.normal(350000, 80000, len(df))).round(2)
                    if 'Distance_km' not in df.columns:
                        df['Distance_km'] = df.apply(
                            lambda row: get_real_distance(row['Ville_Origine'], row['Ville_Destination']) 
                            if row['Ville_Origine'] in CAMEROON_CITIES and row['Ville_Destination'] in CAMEROON_CITIES 
                            else np.random.randint(200, 800), 
                            axis=1
                        )
                    
                    # Vérification finale des données
                    if df['Date'].isnull().any():
                        st.warning("Certaines dates n'ont pas pu être converties et ont été remplacées")
                        df['Date'] = df['Date'].fillna(datetime.now())
                    
                    # Mise à jour des données dans session_state
                    st.session_state.transport_data = df
                    st.session_state.use_real_data = True
                    st.session_state.file_uploaded = True
                    
                    st.success("🎉 Données chargées avec succès!")
                    
                    # Aperçu des données
                    st.subheader("📋 Aperçu des données")
                    st.dataframe(df.head(10), use_container_width=True)
                    
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement: {str(e)}")
                st.session_state.file_uploaded = False
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.subheader("📊 État actuel")
        
        if st.session_state.get('file_uploaded', False) and 'transport_data' in st.session_state:
            data = st.session_state.transport_data
            
            # Vérification que les dates sont valides avant affichage
            try:
                min_date = data['Date'].min()
                max_date = data['Date'].max()
                
                st.metric("Données chargées", f"{len(data)} lignes")
                st.metric("Période couverte", 
                         f"{min_date.strftime('%Y-%m-%d')} au {max_date.strftime('%Y-%m-%d')}")
                st.metric("Villes uniques", data['Ville_Destination'].nunique())
            except Exception as e:
                st.error(f"Erreur lors de l'affichage des métriques: {str(e)}")
                st.metric("Données chargées", f"{len(data)} lignes")
        else:
            st.warning("Aucun fichier chargé")
            st.info("Utilisation des données de simulation")
        
        st.subheader("📋 Format requis")
        st.code("""
Colonnes requises:
- Date: Format YYYY-MM-DD ou JJ/MM/AAAA
- Ville_Origine: Nom de la ville
- Ville_Destination: Nom de la ville  
- Colis_Livres: Nombre entier
Colonnes optionnelles:
- Retards_Minutes: Nombre décimal
- Cout_Transport: Montant numérique
- Distance_km: Nombre entier
        """)
        
        if st.button("Réinitialiser les données"):
            st.session_state.transport_data = pd.DataFrame()
            st.session_state.use_real_data = False
            st.session_state.file_uploaded = False
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Dashboard":
    st.markdown('<div class="page-header"><h1>📊 Tableau de Bord Logistique - Cameroun</h1></div>', unsafe_allow_html=True)
    
    data = get_current_data()
    
    if not st.session_state.file_uploaded:
        st.warning("Vous utilisez des données de simulation. Chargez vos données dans l'onglet 'Gestion des Données'", icon="⚠️")
    
    # Conversion robuste des dates
    if 'Date' in data.columns:
        try:
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce').dt.date
            data = data.dropna(subset=['Date'])
        except Exception as e:
            st.error(f"Erreur de conversion des dates : {str(e)}")
            data['Date'] = datetime.now().date()
    
    # Calcul des dates pour les comparaisons
    current_date = datetime.now().date()
    last_month_date = (current_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    
    # KPI dynamiques
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        try:
            total_colis = data['Colis_Livres'].sum()
            prev_month_data = data[(data['Date'] >= last_month_date) & 
                                 (data['Date'] < current_date.replace(day=1))]
            prev_month = prev_month_data['Colis_Livres'].sum()
            growth = ((total_colis - prev_month) / prev_month * 100) if prev_month > 0 else 0
            trend_class = "trend-up" if growth > 0 else "trend-down" if growth < 0 else "trend-neutral"
        except:
            total_colis = 0
            growth = 0
            trend_class = "trend-neutral"
            
        st.markdown(f"""
        <div class="stats-card primary">
            <div class="stats-icon">📦</div>
            <div class="stats-value">{total_colis:,}</div>
            <div class="stats-label">Colis Livrés</div>
            <div class="metric-trend {trend_class}">
                <span>{"↑" if growth >= 0 else "↓"} {abs(growth):.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        try:
            avg_delay = data['Retards_Minutes'].mean()
            if pd.isna(avg_delay):
                avg_delay = 0
        except:
            avg_delay = 0
            
        st.markdown(f"""
        <div class="stats-card warning">
            <div class="stats-icon">⏱️</div>
            <div class="stats-value">{avg_delay:.0f} min</div>
            <div class="stats-label">Retard Moyen</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        try:
            avg_cost = data['Cout_Transport'].mean()
        except:
            avg_cost = 0
            
        st.markdown(f"""
        <div class="stats-card danger">
            <div class="stats-icon">💰</div>
            <div class="stats-value">{avg_cost:,.0f} FCFA</div>
            <div class="stats-label">Coût Moyen</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        try:
            efficiency = data['Distance_km'].sum() / data['Cout_Transport'].sum() * 1000
            if pd.isna(efficiency) or np.isinf(efficiency):
                efficiency = 0
        except:
            efficiency = 0
            
        st.markdown(f"""
        <div class="stats-card success">
            <div class="stats-icon">🚚</div>
            <div class="stats-value">{efficiency:.2f}</div>
            <div class="stats-label">Efficacité (km/1000F)</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Graphiques dynamiques
    col5, col6 = st.columns(2)
    
    with col5:
        try:
            # Évolution temporelle
            daily_data = data.groupby('Date').agg({
                'Colis_Livres': 'sum',
                'Retards_Minutes': 'mean'
            }).reset_index()
            
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=daily_data['Date'],
                y=daily_data['Colis_Livres'],
                mode='lines+markers',
                name='Colis Livrés',
                line=dict(color='#2a5298')
            ))
            fig1.update_layout(
                title='Évolution des Livraisons',
                xaxis_title='Date',
                yaxis_title='Nombre de Colis'
            )
            st.plotly_chart(fig1, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur lors de la création du graphique d'évolution : {str(e)}")
    
    with col6:
        try:
            # Top destinations
            top_destinations = data.groupby('Ville_Destination')['Colis_Livres'].sum().nlargest(8)
            fig2 = px.pie(
                values=top_destinations.values,
                names=top_destinations.index,
                title='Top 8 Destinations',
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            st.plotly_chart(fig2, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur lors de la création du graphique des destinations : {str(e)}")
# Page de tracking
elif selected == "Tracking":
    st.markdown('<div class="page-header"><h1>🌍 Suivi des Livraisons en Temps Réel</h1></div>', unsafe_allow_html=True)
    
    # Chargement des données
    data = get_current_data()
    
    # Avertissement si données simulées
    if not st.session_state.get('file_uploaded', False):
        st.warning("Vous utilisez des données de simulation. Chargez vos données dans l'onglet 'Gestion des Données'", icon="⚠️")
    
    # Conversion robuste du type de date
    if 'Date' in data.columns:
        try:
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce').dt.date
            # Suppression des lignes avec dates invalides
            data = data.dropna(subset=['Date'])
        except Exception as e:
            st.error(f"Erreur lors de la conversion des dates : {str(e)}")
            data['Date'] = datetime.now().date()
    
    # Traitement des données réelles ou simulation
    if st.session_state.get('file_uploaded', False) and not data.empty:
        current_deliveries = data.copy()
        
        # Calcul du statut basé sur les données réelles
        current_deliveries['Statut'] = np.where(
            current_deliveries['Retards_Minutes'] > 60, 'Retardé',
            np.where(pd.isna(current_deliveries['Retards_Minutes']), 'En attente',
                   'Livré')
        )
        
        current_deliveries['Progression'] = np.where(
            current_deliveries['Statut'] == 'Livré', 100,
            np.where(current_deliveries['Statut'] == 'Retardé', 
                   np.random.randint(50, 90),
                   np.random.randint(10, 50))
        )
    else:
        # Simulation si pas de données réelles
        current_deliveries = data.tail(20).copy() if not data.empty else pd.DataFrame()
        if not current_deliveries.empty:
            current_deliveries['Statut'] = np.random.choice(
                ['En cours', 'Livré', 'Retardé', 'En attente'], 
                size=len(current_deliveries),
                p=[0.4, 0.3, 0.2, 0.1]
            )
            current_deliveries['Progression'] = np.random.randint(10, 100, len(current_deliveries))
    
    # Métriques de suivi
    st.subheader("📊 Statistiques des Livraisons")
    col1, col2, col3, col4 = st.columns(4)
    
    if not current_deliveries.empty:
        status_counts = current_deliveries['Statut'].value_counts()
    else:
        status_counts = pd.Series()
    
    with col1:
        en_cours = status_counts.get('En cours', 0)
        st.markdown(f"""
        <div class="stats-card in-progress">
            <div class="stats-icon">📦</div>
            <div class="stats-value">{en_cours}</div>
            <div class="stats-label">En cours</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        livres = status_counts.get('Livré', 0)
        st.markdown(f"""
        <div class="stats-card delivered">
            <div class="stats-icon">✅</div>
            <div class="stats-value">{livres}</div>
            <div class="stats-label">Livrés</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        retardes = status_counts.get('Retardé', 0)
        st.markdown(f"""
        <div class="stats-card delayed">
            <div class="stats-icon">⚠️</div>
            <div class="stats-value">{retardes}</div>
            <div class="stats-label">Retardés</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        en_attente = status_counts.get('En attente', 0)
        st.markdown(f"""
        <div class="stats-card pending">
            <div class="stats-icon">⏳</div>
            <div class="stats-value">{en_attente}</div>
            <div class="stats-label">En attente</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Carte interactive améliorée
    st.subheader("🗺️ Carte des Livraisons en Temps Réel")
    
    if not current_deliveries.empty:
        m = folium.Map(
            location=[5.6919, 10.2223],  # Centré sur le Cameroun
            zoom_start=6,
            tiles="cartodbpositron"
        )
        
        # Cluster pour mieux gérer les nombreux marqueurs
        marker_cluster = MarkerCluster().add_to(m)
        
        # Ajout des marqueurs avec des popups enrichis
        for idx, row in current_deliveries.iterrows():
            if row['Ville_Destination'] in CAMEROON_CITIES:
                city_info = CAMEROON_CITIES[row['Ville_Destination']]
                
                # Icônes personnalisées selon le statut
                icon_color = {
                    'En cours': 'blue',
                    'Livré': 'green',
                    'Retardé': 'red',
                    'En attente': 'orange'
                }.get(row['Statut'], 'gray')
                
                custom_icon = folium.Icon(
                    color=icon_color,
                    icon='truck' if row['Statut'] == 'En cours' else 'check' if row['Statut'] == 'Livré' else 'exclamation',
                    prefix='fa'
                )
                
                popup_content = f"""
                <b>{row['Ville_Origine']} → {row['Ville_Destination']}</b><br>
                Statut: <b>{row['Statut']}</b><br>
                Colis: {row.get('Colis_Livres', 'N/A')}<br>
                Progression: {row['Progression']}%<br>
                {f"Retard: {row.get('Retards_Minutes', 'N/A')} min" if row['Statut'] == 'Retardé' else ''}
                """
                
                folium.Marker(
                    location=[city_info['lat'], city_info['lon']],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=custom_icon
                ).add_to(marker_cluster)
        
        folium_static(m, width=1200, height=600)
    else:
        st.warning("Aucune donnée de livraison disponible pour afficher la carte.")
    
    # Tableau détaillé avec filtres améliorés
    st.subheader("📋 Détail des Livraisons")
    
    if not current_deliveries.empty:
        col_filter1, col_filter2, col_filter3 = st.columns(3)
        
        with col_filter1:
            statut_filter = st.multiselect(
                "Filtrer par statut",
                options=current_deliveries['Statut'].unique(),
                default=current_deliveries['Statut'].unique()
            )
        
        with col_filter2:
            ville_filter = st.multiselect(
                "Filtrer par destination",
                options=current_deliveries['Ville_Destination'].unique(),
                default=current_deliveries['Ville_Destination'].unique()
            )
        
        with col_filter3:
            min_date = current_deliveries['Date'].min()
            max_date = current_deliveries['Date'].max()
            date_filter = st.date_input(
                "Filtrer par date",
                value=[min_date, max_date],
                min_value=min_date,
                max_value=max_date
            )
        
        # Application des filtres
        filtered_data = current_deliveries[
            (current_deliveries['Statut'].isin(statut_filter)) &
            (current_deliveries['Ville_Destination'].isin(ville_filter))
        ]
        
        # Filtre de date seulement si deux dates sont sélectionnées
        if len(date_filter) == 2:
            filtered_data = filtered_data[
                (filtered_data['Date'] >= date_filter[0]) & 
                (filtered_data['Date'] <= date_filter[1])
            ]
        
        # Affichage du tableau avec colonnes pertinentes
        cols_to_show = ['Date', 'Ville_Origine', 'Ville_Destination', 'Colis_Livres', 
                       'Statut', 'Progression', 'Retards_Minutes', 'Cout_Transport']
        cols_to_show = [col for col in cols_to_show if col in filtered_data.columns]
        
        if not filtered_data.empty:
            st.dataframe(
                filtered_data[cols_to_show],
                use_container_width=True,
                height=400
            )
        else:
            st.warning("Aucune donnée ne correspond aux filtres sélectionnés.")
    else:
        st.warning("Aucune donnée de livraison disponible.")
# Page Prévisions Logistiques
elif selected == "Prediction":
    st.markdown('<div class="page-header"><h1>🔮 Prévisions Logistiques Avancées</h1></div>', unsafe_allow_html=True)
    
    data = get_current_data()
    
    if not st.session_state.file_uploaded:
        st.warning("Vous utilisez des données de simulation. Chargez vos données dans l'onglet 'Gestion des Données'", icon="⚠️")

    # Vérification des données minimales
    if len(data) < 30:
        st.error("⚠️ Besoin d'au moins 30 jours de données historiques pour des prévisions fiables")
        st.stop()

    # Nettoyage et préparation avancée des données
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values('Date').drop_duplicates('Date')
    
    # Agrégation quotidienne
    daily_data = data.groupby('Date').agg({
        'Colis_Livres': 'sum',
        'Retards_Minutes': 'mean',
        'Cout_Transport': 'sum',
        'Distance_km': 'mean'
    }).reset_index()
    
    # Remplissage des valeurs manquantes
    for col in ['Distance_km', 'Cout_Transport', 'Retards_Minutes']:
        if col in daily_data.columns:
            daily_data[col] = daily_data[col].fillna(daily_data[col].median())

    # Interface de configuration
    st.subheader("Configuration du modèle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_variable = st.selectbox(
            "Variable à prédire",
            ['Colis_Livres', 'Retards_Minutes', 'Cout_Transport'],
            key='pred_target'
        )
        
        prediction_days = st.slider(
            "Jours à prédire", 
            min_value=7, 
            max_value=90, 
            value=30,
            key='pred_days'
        )
    
    with col2:
        model_type = st.selectbox(
            "Type de modèle",
            ['Random Forest', 'Régression Linéaire', 'Moyenne Mobile'],
            key='model_type'
        )
        
        advanced_settings = st.expander("Paramètres avancés")
        with advanced_settings:
            include_seasonality = st.checkbox(
                "Inclure saisonnalité", 
                True,
                key='seasonality'
            )
            
            if model_type == 'Random Forest':
                n_estimators = st.slider(
                    "Nombre d'arbres",
                    min_value=50,
                    max_value=500,
                    value=200,
                    key='n_estimators'
                )
                max_depth = st.slider(
                    "Profondeur maximale",
                    min_value=3,
                    max_value=20,
                    value=7,
                    key='max_depth'
                )

    if st.button("🚀 Générer Prédictions", use_container_width=True, key='run_prediction'):
        with st.spinner("Entraînement du modèle en cours..."):
            try:
                # Features temporelles
                daily_data['Jour_Annee'] = daily_data['Date'].dt.dayofyear
                daily_data['Semaine_Annee'] = daily_data['Date'].dt.isocalendar().week
                daily_data['Jour_Semaine'] = daily_data['Date'].dt.dayofweek
                daily_data['Mois'] = daily_data['Date'].dt.month
                
                # Features cycliques
                if include_seasonality:
                    daily_data['Mois_Sin'] = np.sin(2 * np.pi * daily_data['Mois']/12)
                    daily_data['Mois_Cos'] = np.cos(2 * np.pi * daily_data['Mois']/12)
                
                # Lag features
                for lag in [1, 7, 14]:
                    daily_data[f'Lag_{lag}'] = daily_data[target_variable].shift(lag)
                
                # Features supplémentaires
                features = ['Jour_Annee', 'Semaine_Annee', 'Jour_Semaine']
                if include_seasonality:
                    features.extend(['Mois_Sin', 'Mois_Cos'])
                
                # Ajout des lags pertinents
                features.extend([f'Lag_{lag}' for lag in [1, 7] if f'Lag_{lag}' in daily_data.columns])
                
                # Suppression des lignes avec valeurs manquantes
                train_data = daily_data.dropna(subset=[target_variable] + features)
                
                if len(train_data) < 30:
                    raise ValueError(f"Seulement {len(train_data)} jours de données disponibles après nettoyage")
                
                X = train_data[features]
                y = train_data[target_variable]
                
                # Sélection et entraînement du modèle
                if model_type == 'Random Forest':
                    model = RandomForestRegressor(
                        n_estimators=n_estimators,
                        max_depth=max_depth,
                        min_samples_split=10,
                        random_state=42,
                        n_jobs=-1
                    )
                elif model_type == 'Régression Linéaire':
                    model = LinearRegression()
                else:  # Moyenne Mobile
                    model = None
                
                if model is not None:
                    # Validation croisée temporelle
                    tscv = TimeSeriesSplit(n_splits=5)
                    mae_scores = []
                    
                    for train_idx, test_idx in tscv.split(X):
                        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
                        
                        model.fit(X_train, y_train)
                        preds = model.predict(X_test)
                        mae_scores.append(mean_absolute_error(y_test, preds))
                    
                    # Entraînement final
                    model.fit(X, y)
                    
                    # Prédictions futures
                    last_date = daily_data['Date'].max()
                    future_dates = pd.date_range(
                        start=last_date + timedelta(days=1),
                        periods=prediction_days,
                        freq='D'
                    )
                    
                    future_df = pd.DataFrame({'Date': future_dates})
                    future_df['Jour_Annee'] = future_df['Date'].dt.dayofyear
                    future_df['Semaine_Annee'] = future_df['Date'].dt.isocalendar().week
                    future_df['Jour_Semaine'] = future_df['Date'].dt.dayofweek
                    future_df['Mois'] = future_df['Date'].dt.month
                    
                    if include_seasonality:
                        future_df['Mois_Sin'] = np.sin(2 * np.pi * future_df['Mois']/12)
                        future_df['Mois_Cos'] = np.cos(2 * np.pi * future_df['Mois']/12)
                    
                    # Ajout des lag features pour les prédictions
                    for lag in [1, 7]:
                        if f'Lag_{lag}' in features:
                            last_value = daily_data[target_variable].iloc[-lag]
                            future_df[f'Lag_{lag}'] = [last_value] + [None]*(len(future_df)-1)
                            future_df[f'Lag_{lag}'] = future_df[f'Lag_{lag}'].fillna(method='ffill')
                    
                    # Prédictions
                    predictions = model.predict(future_df[features])
                    future_df['Prediction'] = predictions
                    
                    # Calcul de l'intervalle de confiance
                    future_df['Upper'] = future_df['Prediction'] * 1.2
                    future_df['Lower'] = future_df['Prediction'] * 0.8
                    
                    # Visualisation améliorée
                    fig = go.Figure()
                    
                    # Historique
                    fig.add_trace(go.Scatter(
                        x=train_data['Date'],
                        y=train_data[target_variable],
                        mode='lines',
                        name='Historique',
                        line=dict(color='#3498db', width=2)
                    ))
                    
                    # Prédictions
                    fig.add_trace(go.Scatter(
                        x=future_df['Date'],
                        y=future_df['Prediction'],
                        mode='lines+markers',
                        name='Prédictions',
                        line=dict(color='#e74c3c', width=2)
                    ))
                    
                    # Intervalle de confiance
                    fig.add_trace(go.Scatter(
                        x=future_df['Date'],
                        y=future_df['Upper'],
                        fill=None,
                        mode='lines',
                        line=dict(width=0),
                        showlegend=False,
                        name='Intervalle supérieur'
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=future_df['Date'],
                        y=future_df['Lower'],
                        fill='tonexty',
                        mode='lines',
                        line=dict(width=0),
                        fillcolor='rgba(231, 76, 60, 0.2)',
                        name='Intervalle de confiance'
                    ))
                    
                    fig.update_layout(
                        title=f'Prévisions des {target_variable} avec Intervalle de Confiance',
                        xaxis_title='Date',
                        yaxis_title=target_variable,
                        hovermode='x unified',
                        xaxis=dict(
                            tickmode='auto',
                            nticks=min(20, len(future_df)),
                            tickformat='%d %b %Y',
                            rangeslider=dict(visible=True)
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        margin=dict(l=20, r=20, t=60, b=20)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Métriques de performance
                    st.subheader("📊 Performance du modèle")
                    
                    preds = model.predict(X)
                    mae = mean_absolute_error(y, preds)
                    mae_cv = np.mean(mae_scores)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("MAE (Validation Croisée)", f"{mae_cv:.2f}")
                    with col2:
                        st.metric("MAE (Ensemble d'entraînement)", f"{mae:.2f}")
                    with col3:
                        trend = "↗️ Hausse" if future_df['Prediction'].iloc[-1] > future_df['Prediction'].iloc[0] else "↘️ Baisse"
                        st.metric("Tendance générale", trend)
                    
                    # Importance des variables (pour Random Forest)
                    if model_type == 'Random Forest':
                        st.subheader("📌 Importance des Variables")
                        
                        feature_importance = pd.DataFrame({
                            'Feature': features,
                            'Importance': model.feature_importances_
                        }).sort_values('Importance', ascending=False)
                        
                        fig_imp = px.bar(
                            feature_importance,
                            x='Importance',
                            y='Feature',
                            orientation='h',
                            title='Importance Relative des Variables',
                            color='Importance',
                            color_continuous_scale='Blues'
                        )
                        
                        st.plotly_chart(fig_imp, use_container_width=True)
                    
                    # Téléchargement des prédictions
                    st.subheader("💾 Export des Prévisions")
                    
                    csv = future_df[['Date', 'Prediction', 'Upper', 'Lower']].to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="📥 Télécharger les prévisions (CSV)",
                        data=csv,
                        file_name=f"previsions_{target_variable}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime='text/csv'
                    )
                
                else:  # Moyenne Mobile
                    window_size = st.select_slider(
                        "Fenêtre de la moyenne mobile",
                        options=[7, 14, 21, 30],
                        value=14
                    )
                    
                    rolling_avg = daily_data[target_variable].rolling(window=window_size).mean().iloc[-1]
                    st.info(f"La moyenne mobile sur {window_size} jours est: {rolling_avg:.2f}")
                    
                    # Visualisation de la moyenne mobile
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=daily_data['Date'],
                        y=daily_data[target_variable],
                        mode='lines',
                        name='Données réelles',
                        line=dict(color='#3498db')
                    ))
                    fig.add_trace(go.Scatter(
                        x=daily_data['Date'],
                        y=daily_data[target_variable].rolling(window=window_size).mean(),
                        mode='lines',
                        name=f'Moyenne mobile ({window_size}j)',
                        line=dict(color='#e74c3c', dash='dash')
                    ))
                    fig.update_layout(
                        title=f'Moyenne Mobile des {target_variable}',
                        xaxis_title='Date',
                        yaxis_title=target_variable
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
            except Exception as e:
                st.error(f"Erreur lors de la prédiction: {str(e)}")
                st.error("Détails techniques (pour débogage):")
                st.error(traceback.format_exc())

# Page Optimisation des Itinéraires
elif selected == "Routes":
    st.markdown('<div class="page-header"><h1>🗺 Optimisation des Itinéraires</h1></div>', unsafe_allow_html=True)
    
    # Constantes pour les calculs
    COST_FACTORS = {
        "Camion 10T": 450,
        "Camion 5T": 350,
        "Véhicule léger": 200,
        "Moto": 100
    }
    
    SPEED_FACTORS = {
        "Camion 10T": 45,
        "Camion 5T": 55,
        "Véhicule léger": 65,
        "Moto": 70
    }
    
    SAFETY_FACTORS = {
        "Excellente": 0.8,
        "Bonne": 1.0,
        "Moyenne": 1.2,
        "Dégradée": 1.5
    }
    
    # Fonction pour trouver le meilleur itinéraire
    def find_best_route(start, end, vehicle_type, priority):
        cities = list(CAMEROON_CITIES.keys())
        distances = {city: float('inf') for city in cities}
        previous = {city: None for city in cities}
        distances[start] = 0
        unvisited = set(cities)
        
        while unvisited:
            current = min(unvisited, key=lambda city: distances[city])
            if current == end:
                break
            unvisited.remove(current)
            
            for neighbor in unvisited:
                if neighbor == current:
                    continue
                    
                # Calcul de la distance réelle
                distance = get_real_distance(current, neighbor)
                
                # Information sur la route
                route_info = ROAD_CONDITIONS.get((current, neighbor), ROAD_CONDITIONS.get((neighbor, current), {}))
                condition = route_info.get('condition', 'Moyenne')
                road_type = route_info.get('type', 'Nationale')
                peages = route_info.get('pedagage', 0)
                
                # Calcul du poids selon la priorité
                if priority == "Coût minimum":
                    weight = distance * COST_FACTORS[vehicle_type] + peages * 2000
                elif priority == "Temps minimum":
                    weight = distance / SPEED_FACTORS[vehicle_type] * (1.5 if condition == "Dégradée" else 1.0)
                else:  # Route la plus sûre
                    weight = SAFETY_FACTORS.get(condition, 1) * distance
                
                if distances[neighbor] > distances[current] + weight:
                    distances[neighbor] = distances[current] + weight
                    previous[neighbor] = current
        
        # Reconstruction du chemin
        path = []
        current = end
        while current:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return path, distances[end]

    # Interface utilisateur
    with st.expander("⚙️ Paramètres de l'itinéraire", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ville_depart = st.selectbox(
                "Ville de départ",
                options=list(CAMEROON_CITIES.keys()),
                index=0,
                key='route_start'
            )
            
            type_vehicule = st.selectbox(
                "Type de véhicule",
                options=["Camion 10T", "Camion 5T", "Véhicule léger", "Moto"],
                key='vehicle_type'
            )
        
        with col2:
            ville_arrivee = st.selectbox(
                "Ville d'arrivée",
                options=list(CAMEROON_CITIES.keys()),
                index=1,
                key='route_end'
            )
            
            saison = st.selectbox(
                "Saison",
                options=["Saison sèche", "Petite saison des pluies", "Grande saison des pluies"],
                key='season'
            )
        
        with col3:
            priorite = st.selectbox(
                "Critère d'optimisation",
                options=["Coût minimum", "Temps minimum", "Route la plus sûre"],
                key='priority'
            )
            
            charge_kg = st.number_input(
                "Charge (kg)", 
                min_value=0, 
                max_value=10000, 
                value=5000,
                key='load_weight'
            )
    
    if st.button("🔍 Calculer l'itinéraire optimal", key='calculate_route'):
        if ville_depart == ville_arrivee:
            st.error("Les villes de départ et d'arrivée doivent être différentes!")
        else:
            with st.spinner("Calcul en cours..."):
                try:
                    # Calcul du meilleur itinéraire
                    best_path, total_weight = find_best_route(ville_depart, ville_arrivee, type_vehicule, priorite)
                    
                    # Calcul des indicateurs pour l'itinéraire
                    total_distance = 0
                    total_peages = 0
                    conditions = []
                    
                    for i in range(len(best_path)-1):
                        city1, city2 = best_path[i], best_path[i+1]
                        segment_distance = get_real_distance(city1, city2)
                        total_distance += segment_distance
                        
                        route_info = ROAD_CONDITIONS.get((city1, city2), ROAD_CONDITIONS.get((city2, city1), {}))
                        total_peages += route_info.get('pedagage', 0)
                        conditions.append(route_info.get('condition', 'Moyenne'))
                    
                    # Calcul du temps estimé
                    vitesse = SPEED_FACTORS[type_vehicule]
                    facteur_saison = 1.0 if saison == "Saison sèche" else 1.2 if saison == "Petite saison des pluies" else 1.5
                    temps_estime = (total_distance / vitesse) * facteur_saison
                    
                    # Calcul du coût
                    cout_transport = total_distance * COST_FACTORS[type_vehicule]
                    cout_peages = total_peages * 2000  # 2000 FCFA par péage
                    cout_total = cout_transport + cout_peages
                    
                    # Condition moyenne de la route
                    condition_moyenne = max(set(conditions), key=conditions.count)
                    
                    # Estimation du risque de retard
                    retard_risk = {
                        "Excellente": 10,
                        "Bonne": 25,
                        "Moyenne": 50,
                        "Dégradée": 75
                    }.get(condition_moyenne, 50)
                    
                    if saison != "Saison sèche":
                        retard_risk += 20
                    
                    # Affichage des résultats
                    st.success("Itinéraire optimisé avec succès!")
                    
                    # Métriques clés
                    st.subheader("📊 Indicateurs clés")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Distance totale", f"{total_distance:.1f} km")
                    with col2:
                        st.metric("Temps estimé", f"{temps_estime:.1f} heures")
                    with col3:
                        st.metric("Coût total", f"{cout_total:,.0f} FCFA")
                    with col4:
                        st.metric("Risque de retard", f"{retard_risk}%")
                    
                    # Carte interactive
                    st.subheader("🗺 Carte de l'itinéraire optimal")
                    
                    # Coordonnées des villes sur le parcours
                    path_coords = []
                    for city in best_path:
                        if city in CAMEROON_CITIES:
                            city_info = CAMEROON_CITIES[city]
                            path_coords.append([city_info['lat'], city_info['lon']])
                    
                    # Création de la carte
                    m = folium.Map(
                        location=path_coords[len(path_coords)//2],
                        zoom_start=7,
                        tiles="cartodbpositron"
                    )
                    
                    # Ajout des marqueurs
                    for i, city in enumerate(best_path):
                        if city in CAMEROON_CITIES:
                            city_info = CAMEROON_CITIES[city]
                            icon_color = 'green' if i == 0 else 'red' if i == len(best_path)-1 else 'blue'
                            
                            folium.Marker(
                                location=[city_info['lat'], city_info['lon']],
                                popup=f"{city} ({'Départ' if i == 0 else 'Arrivée' if i == len(best_path)-1 else f'Étape {i}'})",
                                icon=folium.Icon(color=icon_color)
                            ).add_to(m)
                    
                    # Ajout du tracé
                    folium.PolyLine(
                        path_coords,
                        color='#0056b3',
                        weight=3,
                        opacity=0.8,
                        tooltip="Itinéraire optimal"
                    ).add_to(m)
                    
                    folium_static(m, width=1000, height=600)
                    
                    # Détails techniques
                    st.subheader("📋 Détails Techniques")
                    
                    details_data = []
                    for i in range(len(best_path)-1):
                        city1, city2 = best_path[i], best_path[i+1]
                        segment_distance = get_real_distance(city1, city2)
                        
                        route_info = ROAD_CONDITIONS.get((city1, city2), ROAD_CONDITIONS.get((city2, city1), {}))
                        details_data.append({
                            'Étape': f"{i+1}. {city1} → {city2}",
                            'Distance (km)': segment_distance,
                            'Condition': route_info.get('condition', 'Moyenne'),
                            'Type de route': route_info.get('type', 'Nationale'),
                            'Péages': route_info.get('pedagage', 0)
                        })
                    
                    details_df = pd.DataFrame(details_data)
                    
                    # Affichage stylisé
                    st.dataframe(
                        details_df.style
                            .set_properties(**{'background-color': '#f8f9fa'})
                            .highlight_max(subset=['Distance (km)'], color='#fff3cd')
                            .highlight_min(subset=['Distance (km)'], color='#d4edda'),
                        use_container_width=True
                    )
                    
                    # Alertes importantes
                    st.subheader("⚠️ Alertes Importantes")
                    
                    if condition_moyenne == "Dégradée":
                        st.warning("""
                        **Route en mauvais état**  
                        Cet itinéraire comprend des tronçons en mauvais état.  
                        Prévoir un temps supplémentaire et vérifier l'état du véhicule.
                        """)
                    
                    if total_peages > 3:
                        st.warning(f"""
                        **Nombre élevé de péages ({total_peages})**  
                        Cet itinéraire comporte plusieurs postes de péage.  
                        Coût estimé des péages: {total_peages * 2000:,} FCFA
                        """)
                    
                    if saison != "Saison sèche":
                        st.info("""
                        **Conditions météo défavorables**  
                        En saison des pluies, prévoir des retards possibles  
                        et adapter la conduite aux conditions routières.
                        """)
                    
                    if type_vehicule == "Camion 10T" and charge_kg > 8000:
                        st.error("""
                        **Charge lourde détectée**  
                        Vérifier les restrictions de poids sur les ponts  
                        et l'état des routes pour ce type de chargement.
                        """)
                    
                except Exception as e:
                    st.error(f"Erreur lors du calcul d'itinéraire: {str(e)}")
                    st.error(traceback.format_exc())
# Page Performance
elif selected == "Performance":
    st.markdown('<div class="page-header"><h1>📈 Analyse des Performances</h1></div>', unsafe_allow_html=True)
    
    data = get_current_data()
    
    if not st.session_state.file_uploaded:
        st.warning("Vous utilisez des données de simulation. Chargez vos données dans l'onglet 'Gestion des Données'", icon="⚠️")

    # KPI principaux
    st.subheader("🎯 Indicateurs Clés de Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        taux_livraison = (data['Colis_Livres'] > 0).mean() * 100
        st.markdown(f"""
        <div class="stats-card success">
            <div class="stats-icon">📦</div>
            <div class="stats-value">{taux_livraison:.1f}%</div>
            <div class="stats-label">Taux de livraison</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        efficacite_cout = data['Distance_km'].sum() / data['Cout_Transport'].sum() * 1000
        st.markdown(f"""
        <div class="stats-card primary">
            <div class="stats-icon">💰</div>
            <div class="stats-value">{efficacite_cout:.2f}</div>
            <div class="stats-label">Efficacité coût (km/1000F)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ponctualite = 100 - (data['Retards_Minutes'] > 60).mean() * 100
        st.markdown(f"""
        <div class="stats-card warning">
            <div class="stats-icon">⏱️</div>
            <div class="stats-value">{ponctualite:.1f}%</div>
            <div class="stats-label">Ponctualité</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        satisfaction = np.random.uniform(75, 95)  # Simulation
        st.markdown(f"""
        <div class="stats-card info">
            <div class="stats-icon">😊</div>
            <div class="stats-value">{satisfaction:.1f}%</div>
            <div class="stats-label">Satisfaction client</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Analyses détaillées
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("📊 Analyse par Destination")
    
    # Performance par ville
    perf_ville = data.groupby('Ville_Destination').agg({
        'Colis_Livres': 'sum',
        'Retards_Minutes': 'mean',
        'Cout_Transport': 'mean'
    }).reset_index()
    
    fig1 = px.scatter(
        perf_ville,
        x='Cout_Transport',
        y='Colis_Livres',
        size='Retards_Minutes',
        color='Ville_Destination',
        title='Performance par Destination',
        labels={
            'Cout_Transport': 'Coût Moyen (FCFA)',
            'Colis_Livres': 'Nombre de Colis Livrés',
            'Retards_Minutes': 'Retard Moyen (minutes)'
        }
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Évolution temporelle
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("📅 Évolution Temporelle")
    
    # Agrégation par mois
    data['Mois'] = data['Date'].dt.to_period('M').astype(str)
    monthly_data = data.groupby('Mois').agg({
        'Colis_Livres': 'sum',
        'Retards_Minutes': 'mean',
        'Cout_Transport': 'sum'
    }).reset_index()
    
    fig2 = go.Figure()
    
    # Ajout des barres pour les colis livrés
    fig2.add_trace(go.Bar(
        x=monthly_data['Mois'],
        y=monthly_data['Colis_Livres'],
        name='Colis Livrés',
        yaxis='y',
        marker_color='#3498db'
    ))
    
    # Ajout de la ligne pour les retards
    fig2.add_trace(go.Scatter(
        x=monthly_data['Mois'],
        y=monthly_data['Retards_Minutes'],
        name='Retard Moyen (min)',
        yaxis='y2',
        line=dict(color='#e74c3c')
    ))
    
    # Mise en forme
    fig2.update_layout(
        title='Performance Mensuelle',
        xaxis_title='Mois',
        yaxis=dict(
            title='Nombre de Colis',
            side='left'
        ),
        yaxis2=dict(
            title='Retard Moyen (minutes)',
            side='right',
            overlaying='y',
            showgrid=False
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Page Alertes
elif selected == "Alertes":
    st.markdown('<div class="page-header"><h1>🔔 Système d\'Alertes</h1></div>', unsafe_allow_html=True)
    
    data = get_current_data()
    
    if not st.session_state.file_uploaded:
        st.warning("Vous utilisez des données de simulation. Chargez vos données dans l'onglet 'Gestion des Données'", icon="⚠️")

    # Configuration des alertes
    st.subheader("⚙️ Paramètres des Alertes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        seuil_retard = st.slider(
            "Seuil d'alerte retard (minutes)",
            min_value=15,
            max_value=120,
            value=60,
            step=5,
            key='delay_threshold'
        )
        
        seuil_cout = st.slider(
            "Seuil d'alerte coût (% au-dessus de la moyenne)",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
            key='cost_threshold'
        )
    
    with col2:
        alert_meteo = st.checkbox(
            "Activer les alertes météo",
            True,
            key='weather_alerts'
        )
        
        alert_stock = st.checkbox(
            "Activer les alertes de stock",
            True,
            key='stock_alerts'
        )
    
    # Génération des alertes
    st.subheader("🚨 Alertes Actives")
    
    alertes = []
    
    # 1. Alertes basées sur les retards
    if 'Retards_Minutes' in data.columns:
        severe_delays = data[data['Retards_Minutes'] > seuil_retard]
        if len(severe_delays) > 0:
            top_delayed = severe_delays.nlargest(3, 'Retards_Minutes')
            destinations = ', '.join(top_delayed['Ville_Destination'].unique())
            
            alertes.append({
                'type': 'danger',
                'titre': f'{len(severe_delays)} Livraisons en Retard (> {seuil_retard} min)',
                'message': f"Destinations concernées: {destinations}",
                'details': f"Retard maximum: {severe_delays['Retards_Minutes'].max():.0f} min"
            })
    
    # 2. Alertes de coût anormal
    if 'Cout_Transport' in data.columns:
        cost_mean = data['Cout_Transport'].mean()
        cost_threshold = cost_mean * (1 + seuil_cout/100)
        high_cost = data[data['Cout_Transport'] > cost_threshold]
        
        if len(high_cost) > 0:
            avg_high_cost = high_cost['Cout_Transport'].mean()
            
            alertes.append({
                'type': 'warning',
                'titre': f'{len(high_cost)} Coûts Anormalement Élevés',
                'message': f"Coût moyen: {avg_high_cost:,.0f} FCFA (+{seuil_cout}% vs moyenne)",
                'details': "Vérifier les itinéraires et véhicules utilisés"
            })
    
    # 3. Alertes de routes problématiques
    if 'Ville_Origine' in data.columns and 'Ville_Destination' in data.columns and 'Retards_Minutes' in data.columns:
        route_delays = data.groupby(['Ville_Origine', 'Ville_Destination'])['Retards_Minutes'].mean().nlargest(3)
        
        for (origin, dest), delay in route_delays.items():
            condition = ROAD_CONDITIONS.get((origin, dest), {}).get('condition', 'Inconnue')
            
            alertes.append({
                'type': 'info',
                'titre': f'Route à risque: {origin} → {dest}',
                'message': f"Retard moyen: {delay:.1f} min | Condition: {condition}",
                'details': f"Type: {ROAD_CONDITIONS.get((origin, dest), {}).get('type', 'Inconnu')}"
            })
    
    # 4. Alertes météo (simulées)
    if alert_meteo:
        current_month = datetime.now().month
        if 5 <= current_month <= 10:  # Saison des pluies
            alertes.append({
                'type': 'info',
                'titre': 'Alerte Météo - Saison des Pluies',
                'message': "Prévoir des retards sur les routes non goudronnées",
                'details': "Régions concernées: Sud-Ouest, Littoral, Ouest"
            })
    
    # 5. Alertes de stock (simulées)
    if alert_stock:
        alertes.append({
            'type': 'warning',
            'titre': 'Stock Carburant Critique',
            'message': "3 véhicules avec niveau de carburant < 20%",
            'details': "Véhicules: CAM-7894, CAM-6541, CAM-3210"
        })
    
    # Affichage des alertes
    if alertes:
        for alerte in alertes:
            if alerte['type'] == 'danger':
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="background-color: #f8d7da; padding: 15px; border-radius: 10px; border-left: 5px solid #dc3545;">
                        <h4 style="color: #dc3545; margin-top: 0;">🚨 {alerte['titre']}</h4>
                        <p>{alerte['message']}</p>
                        <small style="color: #6c757d;">{alerte.get('details', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            elif alerte['type'] == 'warning':
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="background-color: #fff3cd; padding: 15px; border-radius: 10px; border-left: 5px solid #ffc107;">
                        <h4 style="color: #856404; margin-top: 0;">⚠️ {alerte['titre']}</h4>
                        <p>{alerte['message']}</p>
                        <small style="color: #6c757d;">{alerte.get('details', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="background-color: #d1ecf1; padding: 15px; border-radius: 10px; border-left: 5px solid #17a2b8;">
                        <h4 style="color: #0c5460; margin-top: 0;">ℹ️ {alerte['titre']}</h4>
                        <p>{alerte['message']}</p>
                        <small style="color: #6c757d;">{alerte.get('details', '')}</small>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.success("✅ Aucune alerte critique détectée")
    
    # Historique des alertes
    st.subheader("📊 Historique des Alertes (30 derniers jours)")
    
    # Simulation d'historique
    dates = pd.date_range(end=datetime.now(), periods=30).tolist()
    alert_history = pd.DataFrame({
        'Date': dates,
        'Type': np.random.choice(['Retard', 'Coût', 'Route', 'Météo', 'Stock'], 30),
        'Niveau': np.random.choice(['Critique', 'Élevé', 'Moyen', 'Faible'], 30, p=[0.1, 0.3, 0.4, 0.2]),
        'Statut': np.random.choice(['Non résolu', 'En cours', 'Résolu'], 30, p=[0.2, 0.3, 0.5]),
        'Description': np.random.choice([
            'Retard livraison Bamenda',
            'Coût transport élevé Douala-Yaoundé',
            'Route dégradée Maroua-Garoua',
            'Alerte pluies intenses',
            'Stock carburant faible'
        ], 30)
    })
    
    # Graphique des alertes par type
    fig1 = px.histogram(
        alert_history,
        x='Date',
        color='Type',
        title='Répartition des Alertes par Type',
        labels={'count': 'Nombre d\'alertes'},
        color_discrete_map={
            'Retard': '#e74c3c',
            'Coût': '#f39c12',
            'Route': '#3498db',
            'Météo': '#17a2b8',
            'Stock': '#6c757d'
        }
    )
    st.plotly_chart(fig1, use_container_width=True)
    
    # Tableau détaillé
    st.dataframe(
        alert_history.sort_values('Date', ascending=False),
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "Type": "Type d'alerte",
            "Niveau": st.column_config.SelectboxColumn(
                "Niveau",
                options=["Critique", "Élevé", "Moyen", "Faible"]
            ),
            "Statut": st.column_config.SelectboxColumn(
                "Statut",
                options=["Non résolu", "En cours", "Résolu"]
            ),
            "Description": "Description"
        },
        hide_index=True,
        use_container_width=True
    )

# Pied de page
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <h4>OptiLog Cameroun - Plateforme d'Optimisation Logistique 🇨🇲</h4>
    <p>Solution intelligente adaptée au contexte camerounais</p>
    <p><strong>Fonctionnalités:</strong> Chargement CSV • Optimisation réelle • Prédictions ML • Suivi temps réel</p>
</div>
""", unsafe_allow_html=True)