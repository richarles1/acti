from datetime import datetime
from io import BytesIO
import sqlite3
from collections import defaultdict
import pandas as pd
import streamlit as st
from PIL import Image as PILImage
from PIL import Image
import easyocr
import numpy as np
import os
import cv2
import re
from pyzbar.pyzbar import decode as decode_qr
from pdf417decoder import PDF417Decoder

#python -m streamlit run main.py




donnees = {
                       "Artibonite": { "Gonaïves": ["gonaïves", "Pont Tamarin", "Bassin", "Petite Rivière de Bayonnais", "Poteaux", "Labranle"], "Ennery": ["Ennery", "Savane Carrée", "Passe-Reine ou Bas d'Ennery","Chemin Neuf", "Puilboreau"], "L'Estère":["L'Estère", "La Croix Perisse", "Petite Desdunes"], "Gros Morne": ["Gros Morne", "Boucan Richard", "Rivière Mancelle", "Rivière Blanche", "L'Acul", "Pendu", "Savane Carrée", "Moulin", "Ravine Gros Morne"], "Terre Neuve": ["Terre Neuve", "Doland", "Bois Neuf", "Lagon"], "L'Anse Rouge": ["L'Anse Rouge", "Sources Chaudes", "L'Arbre"], "Saint-Marc": ["Saint-Marc", "Délugé", "Bois Neuf", "Goyavier", "Lalouère", "Bocozelle", " Charrette"], "Verrettes": ["Verrettes", "Liancourt", "Belanger", "Guillaume Mogé", "Desarmes", "Bastien", "Terre Natte"], "La Chapelle": ["La Chapelle", "Martineau", "Bossous"], "Dessalines": ["Dessalines", "Villars", "Fosse Naboth ou Duvallon", "Ogé", "Poste Pierrot", "Fiéfé ou Petit Cahos", " La Croix ou Grand Cahos"], "Petite Rivière de L'Artibonite": ["Petite Rivière de L'Artibonite", "Bas Coursin I", "Bas Coursin II", "Labady", "Savane à Roche", "Pérodin", "Médor"], "Grande Saline": ["Grande Saline", "Poteneau"], "Desdunes": ["Desdunes"], "Saint-Michel de L'Attalaye": ["Saint-Michel de L'Attalaye", "Platana", "Camathe", "Bas de Sault", "Lalomas", "L'Ermite", "Lacedras", "Marmont", "L'Attalaye"], "Marmelade": ["Marmelade", "Crête à Pins", "Bassin ou Billier", "Platon"] }, 
                       "Centre": { "Hinche": ["hinche", "Juanaria", "Marmont", " Aguahédionde (Rive Droite)", "Aguahédionde (Rive Gauche)"], "Maïssade": ["Maïssade", "Savane Grande", "Narang", "Hatty"], "Thomonde": ["Thomonde", "Cabral", "Tierra Muscady", "Baille Tourrible", " La Hoye"], "Cerca Carvajal": ["Cerca Carvajal", "Rang"]," Mirebalais": ["Mirebalais", "Gascogne", "Sarazin", "Grand Boucan", "Crête Brûlée"], "Saut d'Eau": ["Saut d'Eau", "Canot ou Rivière Canot", "La Selle", "Coupe Mardi Gras", "Montagne Terrible"], "Boucan Carré": ["Boucan Carré", "Petite Montagne", "des Bayes"], "Lascahobas": ["Lascahobas", "Petit Fond", "Juampas"], "Belladère": ["Belladère", "Renthe Mathe", "Roye-Sec", "Riaribes"], "Savanette": ["Savanette", "La Haye"], "Cerca La Source": ["Cerca La Source", "Acajou Brûlé No.1", "Acajou Brûlé No.2", "Lamielle"], "Thomassique": ["Thomassique", "Matelgate", "Lociane"] },
                       "Grand-Anse": { "Abricots": ["abricots","Anse-du-Clerc","Balisiers","Danglise", "La Seringue"], "Anse-d'hainault": ["Anse d'Hainault", "Grandoit", "Boudon","Îlet-à-Pierre-Joseph", "Mandou"], "Bonbon": ["Bonbon", "Desormeau"], "Beaumont": ["Beaumont","Chardonnette", "Mouline"], "Corail": [ "Corail", "Duquillon", "Fonds-d'Icaque", "Champy ( Patte-large)"], "Chambelan": ["Chambellan", "Dejean", "Boucan"], "Dame-Marie": ["Dame Marie", "Baliverne","Bariadelle","Dallier","Desormeau","Lesson", "Petite Rivière"], "Irois": ["Irois", "Belair"," Matador (ou Jorgue)", "Garcasse (dont le quartier « Carcasse »)"], "Jérémie": ["Basse-Guinaudée","Basse-Voldrogue","Haute-Guinaudée","Haute-Voldrogue (dont le quartier « Léon ») ","Fond Rouge Dahere", "Fond Rouge Torbeck", "Ravine à Charles", "Iles Blanches"], "Les Îles Cayemites": ["L'Anse à Maçon", "Pointe Sable", "l'Anse du Nord"], "Marfranc": ["Marfranc", " Grande Rivière"], "Moron": ["Moron", "Anote ou 1re Tapion", "Sources Chaudes", "L'Assise ou Chameau"], "Pestel": ["Pestel", "Bernagousse","Espère","Jean Bellune","Tozia","Duchity"], "Roseaux": ["Carrefour Charles (ou Jacquet)", "Grand Vincent", "Les Gommiers", "Fond Cochon (ou Lopineau)"] },   
                       "Nippes": { "Anse-à-Veau": ["anse-à-Veau", "Baconnois-Grand-Fond","Grande-Rivière-Joly", "Saut du Baril" ], "Arnaud": ["Arnaud", "Baconnois-Barreau", "Baquet", "Morcou"], "Barradères": ["Baradères", "Gérin ou Mouton","Tête-d'Eau ", "Fond-Tortue", "La Plaine ", "Rivière-Salée" ], "Fonds-des-Nègres": [" Fonds des Nègres", "Bouzi", "Morne Brice", "Pemerle", "Cocoyers-Ducheine"], "Grand-Boucan": ["Grandes Boucan", "Eaux-Basses"], "L'Asile": ["L'Asile", "Nan Paul", "Changeux", "Tournade","Morisseau"], "Miragoâne": ["Miragoâne", "Chalon", "Belle Rivière", "Dessources", " Saint-Michel"], "Paillant": ["Paillant", "Salagnac", " Bezin II"], "Petite-Rivière-de-Nippes": ["petite Rivière de Nippes", " Fond des Lianes", "Cholette", "Silègue", " Bezin"], "Petit-Trou-de-Nippes": ["Petit-Trou-de-Nippes", "Raymond", "Tiby", "Lièvre ou Vigny" ], "Plaisance-du-Sud": ["Plaisance-du-Sud", "ti François", "Anse aux Pins", "Vassal Labiche"] },
                       "Nord": { "Acul-du-Nord": ["Camp-Louise", "Bas de l'Acul", "Mornet", "Grande Ravine", "Coupe à David", "La Soufrière"], "Plaine-du-Nord": ["Morne Rouge", "Basse Plaine", "Grand Boucan (Robillard)", "Bassin Diamant"], "Port-Margot": ["Grande Plaine", "Bas Petit Borgne", "Corail", "Haut Petit Borgne", "Bas Quartier (Bayeux)", "Bras Gauche (Petit-Bourg)"], "Milot": ["Perches-de-Bonnet", "Bonnet à l'Évêque", "Genipailler (Pères)"], "Borgne":["Petit Bourg de Borgne", "Margot", "Boucan Michel", "Trou d'Enfer", "Champagne", "Molas", "Côte de Fer", "Fond Lagrange"], "Cap-Haïtien": ["Bande du Nord", "Haut du Cap", "Petit Anse"], "Limonade": ["Basse Plaine (Bord-de-Mer de Limonade) ", "Bois de Lance", "Roucou"], "Quartier-Morin": ["Basse Plaine", "Morne Pelé"], "Grande-Rivière-du-Nord": ["Grand Gilles", "Solon", "Caracol", "Gambade", "Jolitrou", "Cormiers"], "Limbé": ["Tanmas", "Haut-Limbé", "Soufrière", "Ravine-des-Roches", "Simalo", "Camp-Coq"], "Bahon": ["Bois Pin", "Bailly (ou Bailla) (Ou Nan bay)", "Montagne Noire"], "Bas-Limbé": ["Garde-Champêtre (ou Bas-Limbé)", "Petit-Howars (ou La Frange)"], "Plaisance": ["Gobert (ou Colline Gobert)", "Champagne", "Haut Martineau", "Mapou", "La Trouble", "La Ville", "Bassin", "Grande Rivière" ], "Pilate": ["Ballon", "Baudin", "Ravine-Trompette", "Joly", "Dubourg", "Piment", "Rivière-Laporte", "Margot"], "Saint-Raphaël": ["Bois-Neuf", "Mathurin", "Bouyaha", "San-Yago"], "Dondon": ["Brostage", "Bassin Caïman", "Matador", "Laguille", "Haut du Trou"], "Ranquitte": ["Bac-à-Soude", "Bois-de-Lance", "Cracaraille"], "Pignon": ["Savannette", "La Belle-Mère"], "La Victoire": ["la victoire"] },
                       "Nord-est": { "Fort-Liberté": ["Dumas", "Bayaha", "Loiseau (Acul-Sammedi)", "Haut-Madeleine"], "Perches": ["Haut-des-Perches", "Bas-des-Perches"], "Ferrier": ["Maribahoux"], "Ouanaminthe": ["Haut Maribahoux", "Acul des Pins", "Savane Longue", "Savane au Lait", "Gens de Nantes"], "Capotille": ["capotille", "Lamine", "weche"], "Mont-Organisé": ["Savanette", "Bois-Poux"], "Trou-du-Nord": ["Garcin", "Roucou", "Roche-Plate", "Pilette", "Bassin Tournent", "Monsignac", "Frache", "Caracol", "Tantasyon (Démosthène Lochard)", "Devarin", "Ti roche"], "Caracol": ["Champin", "Glodine"], "Sainte-Suzanne": ["Foulon", "Bois-Blanc", "Cotelette", "Sarazin", "Moka-Neuf", "Fond-Bleu (Dupity)"], "Terrier-Rouge": ["Fond-Blanc", "Grand-Bassin"], "Vallières": ["Trois-Palmistes", "Écrevisse (Grosse-Roche)", "Corosse"], "Carice": ["Bois-Gamelle", "Rose-Bonite"], "Mombin-Crochu": ["Sans-Souci", "Bois-Laurence "] },
                       "Nord-ouest": { "Baie de Henne": ["Item A1.1", "Item A1.2"], "Bombardopolis": ["Plate-Forme ", "Des Forges", "Plaine-d'Oranges"], "Jean-Rabel": ["Lacoma", "Guinaudée", "Vielle Hatte", "La Montagne", "Dessources", "Grande Source", "Diondion"], "Môle Saint Nicholas": ["Côte-de-Fer", "Mare-Rouge", "Damé"], "Port-de-Paix": ["Baudin", "Aubert", "Paulin/Lacorne", "Mahotière", "Bas des Moustiques"], "Bassin-Bleu": ["La Plate", "Carreau-Datty", "Haut-des-Moustiques"], "Chansolme": ["Chansolme","Bion", "La visite"], "île de la Tortue": ["Pointe des Oiseaux", "Mare Rouge"], "La pointe des Palmistes": ["A1"],"Saint-Louis-du-Nord": ["Rivière-des-Nègres (Guichard)"], "Derouvray": ["Des Granges"], "Rivières-des-Barres":["Bonneau", "Lafague (ou Chamoise)"], "Anse-à-Foleur": ["Bas-de-Ste-Anne", "Mayance", "Côte-de-Fer"] },
                       "Ouest": { "Arcahaie": ["Boucassin", "Fonds Baptiste", "Des Vases (Saintard)", "Délices", "Matheux"], "Cabaret": ["Boucassin 1", "Boucassin 2", "Fonds-des-Blancs (ou Cazale)", "Source-Matelas"], "Croix-des-Bouquets":["Les Varreux 1", "Les Varreux 2", "Petit Bois 3", "Petit Bois 4", "Petit Bois 5", "Belle Fontaine 6", "Belle Fontaine 7", "Belle Fontaine 8", "Les Crochus", "Les Orangers"], "Ganthier": ["Galette Chambon", "Balan", "Fonds-Parisien", "Mare Roseaux"], "Thomazeau": ["Grande Plaine 1", "Grande Plaine 2", "Trou d'Eau", "Les Crochus"], "Cornillon": ["Plaine Céleste 1", "Plaine Céleste 2", "Boucan Bois pin 1", "Boucan Bois Pin 2", "Génipailler"], "Fonds-Verrettes": ["fonds-Verrettes"], "Anse-à-Galets": ["Palma", "Petite Source (formant le bourg)", "Grande Source", "Grand Lagon", "Picmy", "Petite Anse"], "Pointe-à-Raquette": ["La Source", "Grand Vide", "Trou Louis", "Pointe-à-Raquette", "Gros Mangle"],"Léogâne": ["Dessources", "Petite Rivière", "Grande Rivière", "Fond de Boudin (Trouin)", "Palmiste à Vin", "Orangers", "Parques", "Beauséjour", "Citronniers", "Fond d'Oie", "Gros Morne", "Cormiers", "Petit Harpon"], "Petit-Goâve": ["Première Plaine (Bino et village de « Vialet »)", "Deuxième Plaine (Étang de Miragoâne et la ville précolombienne Arnoux)", "Trou Chouchou", "Fond-Arabie (dont les grands quartiers historiques Lebrun, Poulard et Hyacinthe)", "Trou Canaries-Ve", "Trou Canaries-VIe", "Les Platons-VIIe (village Délatte)", "Les Platons-VIIIe", "Les Palmes-IXe", "Les Palmes-Xe", "Ravine Sèche", "Les Fourques"], "Grand-Goâve": ["Tête-à-Bœuf 1", "Tête-à-Bœuf 2", "Moussambé 3", "Moussambé 4", "Grande Colline 5", "Grande Colline 6", "Gérard 7"], "Port-au-Prince": ["Turgeau", "Morne l'Hôpital", "Martissant"], "Carrefour": ["Morne Chandelle", "Platon Dufréné", "Taïfer", "Procy", "Coupeau", "Bouvier", "Lavalle", "Berly", "Bizoton", "Thor", "Rivière Froide", "Malanga", "Corail Thor"], "Delmas": ["Saint-Martin"], "Pétion-Ville": ["Montagne-Noire (Thomassin)", "Étang-du-Jonc", "Bellevue-Lamontagne", "Aux-Cadets", "Bellevue-Charbonnière", "Soisson-la-Montagne"], "Kenscoff": ["Nouvelle Touraine", "Bongard", "Sourçailles", "Belle Fontaine", "Grand Fond"], "Cité Soleil": ["Varreux 1", "Varreux 2"], "Gressier": ["Gressier", "Morne à Bateau", "Morne Chandelle", "Petit Boucan"], "Tabarre": ["La ville de Tabarre", "Bellevue 1 (Croix-des-Missions)", "Bellevue 2 (Caradeux)"] },
                       "Sud": { "Cayes": ["cayes", "Bourdet", "Fonfrède", "Laborde", "Laurent", "Mercy", "Boulmier"], "Torbeck": ["Torbeck", "Boury", "Bérault", "Solon", "Moreau"], "Chantal": ["Chantal", "Fonds Palmiste", "Melonière", "Carrefour Canon"], "Camp-Perrin": ["Camp-Perrin", "Levy Mersan", "Champlois", "Tibi Davezac"], "Maniche": ["Maniche", "Dory", "Melon"], "L'Ile à Vache": ["L'Ile à Vache"], "Port-Salut": ["Port-Salut", "Barbois", "Dumont"], "Saint Jean du Sud": ["Saint Jean du Sud", "Tapion", "Débouchette", "Trichet"], "Arniquet": ["Arniquet", "Lazarre", "Anse à Drick"], "Aquin": ["Aquin", "Macéan (Quartier de Vieux Bourg d'Aquin)", "Bellevue (Quartier de Vieux Bourg d'Aquin)", "Brodequin", "Flamands", "Mare à Coiffe", "La Colline", "Frangipane", "Colline à Mongons", "Fond des Blancs", "Guirand"], "Saint Louis du Sud": ["Saint Louis du Sud", "Grand Fonds", "Baie Dumesle", "Grenodière", "Zanglais", "Sucrerie Henri", "Solon", "Cherette", "Corail-Henri"], "Cavaillon": ["Cavaillon", "Boileau", "Martineau", "Gros Marin", "Mare Henri", "Laroque"], "Côteaux": ["Côteaux", "Condé", "Despas", "Quentin"], "Port-à-Piment": ["Port-à-Piment", "Paricot", "Balais"], "Roche à Bâteau": ["Roche à Bâteau", "Beaulieu", "Renaudin", "Beauclos"], "Chardonnières": ["Chardonnières", "Randel", "Dejoie", "Bony"], "Les Anglais": ["Les Anglais", "Vérone", "Edelin", "Cosse"], "Tiburon": ["Tiburon", "Blactote", "Nan Sevré", "Loby", "Dalmette"]},
                       "Sud-est": { "Bainet": ["Brésilienne", "Trou Mahot", "La Vallée de Bainet", "Haut Gandou", "Bas de Gandou", "Bas de Lacroix", "Bras Gauche", "Oranger", "Bas des Gris Gris"], "Côtes-de-Fer": ["Gris Gris", "Labiche", "Bras Gauche", "Amazone", "Boucan Bélier", "Jamais Vu"], "Belle-Anse":["Bais d'Orange", "Mabriole", "Calumette", "Corail", "Lamothe", "Bel-Air", "Pichon", "Mapou"], "Anse-à-Pitres": ["Boucan-Guillaume (Banane)", "Bois-d'Ormes"], "Grand-Gosier": [" Colline des Chênes (Bodarie ou homonyme)"], "Thiotte": ["Pot-de-Chambre", "Colombier"], "Jacmel": ["Bas Cap Rouge (Orangers)", "Fond Melon (Selles)", "Cochon Gras", "La Gosseline", "Marbial", "Montagne La Voûte", "Grande Rivière de jacmel", "Bas Coq Chante", "Haut Coq Chante", "La Vanneau", "La Montagne", "la Vallée de Jacmel"], "Cayes-Jacmel": ["Ravine-Normande", "Gaillard", "Haut-Cap-Rouge", "La Selle de Fond-Melon"], "Marigot": ["Corail Soult", "Grande Rivière Fesles", "Macary", "Fond Jean Noël (Seguin)", "Savane Dubois"], "La Vallée-de-Jacmel": ["Muzac", "Ternier", "Morne-à-Brûler"] },

                    }








# --- DATABASE SETUP ---
current_db_path = "A.ev"



#current_db_path = "I.ev"


def init_db():
    """Creates a local database and a sample table if they don't exist."""
    conn = sqlite3.connect(current_db_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS document (
           id INTEGER  PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            image_backup BLOB
        )
    """
    )
    # Insert a dummy record for demonstration purposes if table is empty
    cursor.execute("SELECT COUNT(*) FROM document")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO document (titre, image_backup) VALUES (?, ?)",
            ("Le Registre Globale", " "),
        )
    conn.commit()
    create_table_0()
    #conn.close()
###############################################################################3333
def create_table_0():

        if current_db_path:
           conn = sqlite3.connect(current_db_path)
           table_create_query = '''CREATE TABLE IF NOT EXISTS circonscription 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, Nom TEXT, Departement TEXT, Commune1 TEXT, commune2 TEXT)
           '''
           conn.execute(table_create_query)
           create_table_cv()

def create_table_cv():

        if current_db_path:
           conn = sqlite3.connect(current_db_path)
           table_create_query = '''CREATE TABLE IF NOT EXISTS CV 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, Nom TEXT, Departement TEXT, Commune TEXT, Section TEXT)
           '''
           conn.execute(table_create_query)
           create_table_bv()
def create_table_bv():

        if current_db_path:
           conn = sqlite3.connect(current_db_path)
           table_create_query = '''CREATE TABLE IF NOT EXISTS BV 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, Nom TEXT, Departement TEXT, Commune TEXT, Section TEXT, CV TEXT)
           '''
           conn.execute(table_create_query)
           create_table_base()

def create_table_base():

        if current_db_path:
           conn = sqlite3.connect(current_db_path)
           table_create_query = '''CREATE TABLE IF NOT EXISTS base 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, Nom TEXT, Localité TEXT, Departement TEXT, Commune TEXT, Section TEXT)
           '''
           conn.execute(table_create_query)
           create_table_membre()

def create_table_membre():

        if current_db_path:
           conn = sqlite3.connect(current_db_path)
           table_create_query = '''CREATE TABLE IF NOT EXISTS membre 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, image_data BLOB, Nom TEXT, Prénom TEXT, Addresse TEXT, Phone TEXT, Sexe TEXT, Nin TEXT, Base TEXT)
           '''
           conn.execute(table_create_query)
           create_table_hide_membre()

def create_table_hide_membre():

        if current_db_path:
           conn = sqlite3.connect(current_db_path)
           table_create_query = '''CREATE TABLE IF NOT EXISTS hide_membre 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, image_data BLOB, Nom TEXT, Prénom TEXT, Addresse TEXT, Phone TEXT, Naissance TEXT, Sexe INT, Nin TEXT, CV TEXT, BV TEXT, Asec TEXT, Casec TEXT, Délégué TEXT, Maire TEXT, Député TEXT, Sénateur TEXT, Président TEXT, Departement TEXT, Commune TEXT, Section TEXT, Base TEXT)
           '''
           conn.execute(table_create_query)
           create_table()

def create_table():

        if current_db_path:
           conn = sqlite3.connect(current_db_path)
           table_create_query = '''CREATE TABLE IF NOT EXISTS electeur 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, image_data BLOB, filename TEXT, Nom TEXT, Prénom TEXT, Addresse TEXT, Phone TEXT, Naissance TEXT, Sexe INT, Nin TEXT, CV TEXT, BV TEXT, Asec TEXT, Casec TEXT, Délégué TEXT, Maire TEXT, Député TEXT, Sénateur TEXT, Président TEXT, Departement TEXT, Commune TEXT, Section TEXT)
           '''
           conn.execute(table_create_query)
           create_table_2()

def create_table_2():

        if current_db_path:
           conn = sqlite3.connect(current_db_path)
           table_create_query = '''CREATE TABLE IF NOT EXISTS candidat 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, image_data BLOB, filename TEXT, nom TEXT, prenom TEXT, sexe INT, parti TEXT, poste TEXT, departement TEXT, commune1 TEXT, commune2 TEXT, section TEXT)
            '''
           conn.execute(table_create_query)
           conn.execute("INSERT OR IGNORE INTO candidat (id, image_data, filename, nom, prenom) VALUES (0, '','', 'Aucun', 'Candidat')")
           conn.commit()


           create_table3()

def create_table3():

        if current_db_path:
           conn = sqlite3.connect(current_db_path)
           table_create_query = '''CREATE TABLE IF NOT EXISTS parti 
                    (id INTEGER PRIMARY KEY AUTOINCREMENT, image_data BLOB, filename TEXT,  nom TEXT, sigle TEXT, nin TEXT )
            '''
           conn.execute(table_create_query)
           conn.execute("INSERT OR IGNORE INTO parti (id, image_data, filename,  nom, sigle) VALUES (0, '','', '', 'independant')")
           conn.commit()
           conn.close()





def check_record_exists(voteur_id):

    """Checks if a voteur exists in the SQLite database."""
    conn = sqlite3.connect(current_db_path)
    cursor = conn.cursor()
    # Safely query using the passed argument
    cursor.execute("SELECT 1 FROM electeur WHERE Nin = ?", (voteur_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# Initialize the database when the app starts
init_db()

# --- STREAMLIT APP ---
#st.title("Qui sera élu ?")
# --- STREAMLIT APP ---
# Header Image Banner
# Replace the URL with your local file path (e.g., "assets/banner.png") or your own image link
st.image("https://github.com/richarles1/acti/raw/refs/heads/main/logo.jpg", width='stretch')

st.markdown(
    """
    <style>
    [data-testid="stImage"] img {
        max-height: 120px;
        object-fit: cover; /* Prevents stretching by cropping edges instead */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Initialize session state variables to track workflow
if "step" not in st.session_state:
    st.session_state.step = "input_stage"
if "username_input" not in st.session_state:
    st.session_state.username_input = ""

# --- STAGE 0: USER INPUT ---
if st.session_state.step == "input_stage":

    st.markdown("<h2 style='text-align: center;'>Qui sera élu ?</h2>", unsafe_allow_html=True)
   
    st.markdown("<h4 style='text-align: center;'>Connaitre à l'avance votre prochain représentant</h4>", unsafe_allow_html=True)

    #st.subheader("Connaitre à l'avance votre prochain représentant")
    #st.write("Entrer les 10 chiffres de votre carte électorale pour afficher les résultats")

    # Wrap input in a form to control execution timing
    with st.form(key="search_form"):
        voteur_raw = st.text_input("Entrer les 10 chiffres de votre carte électorale pour afficher les résultats:", key="form_username", max_chars=10, placeholder="Ex: 1234567890" ).strip()
        submit_button = st.form_submit_button(label="Check Record")

    # Registration button (placed safely outside the form)
    # Create columns to push the registration button to the right side
    # [4, 1] means the left side takes 80% space, right side takes 20%
    col1, col2 = st.columns([4, 1])
    
    with col2:
        if st.button("S'enregistrer", width='stretch'):        
            st.session_state.step = "step_3" 
            st.rerun()

    # Form Submission Logic
    if submit_button:
        if voteur_raw == "":
            st.error("Veuillez entrer un numéro de carte.")
        # Check if the string contains anything other than numbers
        elif not voteur_raw.isdigit():
            st.error("Erreur : La carte ne doit contenir que des chiffres.")
        # Check the exact length constraint
        elif len(voteur_raw) != 10:
            st.error("Erreur : Le numéro doit comporter exactement 10 chiffres.")
        else:
            # Everything is clean, assign it safely
            st.session_state.username_input = voteur_raw
            
            # Database evaluation logic
            if check_record_exists(voteur_raw):
                st.session_state.step = "step_1"
            else:
                st.session_state.step = "step_2"
                
            st.rerun()

 










# --- STAGE 1: RECORD EXISTS ---




######################  Step 1  #########################3



# --- STAGE 1: RECORD EXISTS ---
elif st.session_state.step == "step_1":
  st.success(
      f"✅ Record Found ! " "Selectionnez une option dans l'onglet Navigation." )

  # 1. Define your callback functions
  def show_resultat():
    st.write("### Résultats: Président")
    #st.info("📊 Affichage des graphiques et des statistiques pour la Présidentielle...")
    #def resultat_par_candidat():
    # 1. Database Connection & Fetching data
    conn = sqlite3.connect(current_db_path)
    cursor = conn.cursor()

    cursor.execute("select Président from electeur")
    all_colors = cursor.fetchall()
    conn.close()

    # 2. Data Processing
    color_counts = defaultdict(int)
    for row in all_colors:
        if row and row[0] is not None:
            color = str(row[0]).strip().capitalize()
            color_counts[color] += 1

    # 3. Displaying the UI
    show_resultat_par_candidat_on_screen(color_counts)


  def show_resultat_par_candidat_on_screen(counts):
    # Streamlit updates dynamically; no need to manually .destroy() old frames

    # Set up a title or header widget
    #st.markdown("### Résultat prévu")

    total_votes = sum(counts.values())

    if total_votes == 0:
        st.warning("Aucun vote enregistré pour le moment.")
        return

    # Prepare data for a clean display using a Pandas DataFrame
    data_list = []
    for candidat, count in counts.items():
        percentage = (count / total_votes) * 100
        data_list.append(
            {
                "Candidat": candidat,
                "Votes": count,
                "Pourcentage": f"{percentage:.2f}%",
            }
        )

    df = pd.DataFrame(data_list)

    # Display data in an interactive table (replaces Treeview + scrollbars)
    st.dataframe(df, width='stretch', hide_index=True)  







  def check_resultat_senateur():
    #st.write("### Résultats: Sénateur")
    #st.info("📊 Affichage des graphiques et des statistiques pour les Sénatoriales...")
    

     

    #def resultat_senateur():
    st.title("🗳️ Résultats: Sénateur")

    # 1. Sélection du département (Remplace la Combobox)
    # Note : 'liste_departements' doit contenir vos données (ex: ["Paris", "Lyon"])
    #liste_departements = ["", "Grand-Anse", "Département B", "Département C"]
    #departement = st.selectbox("Sélectionnez un département", options=liste_departements)
   
    # 1. Sélection dynamique du Département (Texte issu des clés principales)
    liste_departements = sorted(list(donnees.keys()))
    departement = st.selectbox(
        "Sélectionnez le Département :", 
        options=liste_departements
    )
    





    # 2. Bouton pour lancer la vérification (Remplace le mécanisme Toplevel/Bouton)
    if st.button("Afficher les résultats"):
        # Équivalent de check_departement()
        if departement and departement.strip() != "":
            
            # Équivalent de check_if_exist()
            try:
                # 'current_db_path' doit être défini dans votre code global
                conn = sqlite3.connect(current_db_path) 
                cursor = conn.cursor()

                # Récupération des votes
                query_votes = """ SELECT Sénateur FROM electeur WHERE Departement = ? """
                cursor.execute(query_votes, (departement.strip(),))
                all_votes = cursor.fetchall()
                conn.close()

                # Comptage des voix par candidat
                color_counts = defaultdict(int)
                for row in all_votes:
                    if row and row[0] is not None:
                        color = str(row[0]).strip().capitalize()
                        color_counts[color] += 1

                # Affichage des résultats
                show_resultat_par_candidat_on_screen(color_counts)

            except Exception as e:
                st.error(f"Erreur lors de la connexion à la base de données : {e}")
        
        else:
            # Remplace tkinter.messagebox.showwarning
            st.error("⚠️ Erreur : Département est requis.")







  def check_resultat_depute():
    st.write("### 🗳️ Résultats: Député")
    #def resultat_depute(donnees):
    #st.title("🗳️ Analyse des Résultats par Circonscription")

    # Obtenir la liste triée de tous les départements disponibles
    departements_disponibles = sorted(list(donnees.keys()))

    # Utilisation de colonnes pour afficher le choix de la Commune 1 et de la Commune 2 côte à côte
    col1, col2 = st.columns(2)

    with col1:
        #st.subheader("📍 Première Commune")
        dept_1 = st.selectbox(
            " Sélectionnez le Département :",
            options=departements_disponibles,
            key="dept_1",
        )
        communes_1_disponibles = sorted(list(donnees[dept_1].keys()))
        commune1 = st.selectbox(
            "Sélectionnez la Commune 1 :",
            options=communes_1_disponibles,
            key="commune_1",
        )

    with col2:
        #st.subheader("📍 Deuxième Commune")
        #dept_2 = st.selectbox(
        #    "Département (Commune 2) :",
        #    options=departements_disponibles,
        #    key="dept_2",
        #)
        communes_2_disponibles = sorted(list(donnees[dept_1].keys()))
        commune2 = st.selectbox(
            "Sélectionnez la Commune 2 :",
            options=communes_2_disponibles,
            key="commune_2",
        )

    # Nettoyage des chaînes
    commune1 = commune1.strip() if commune1 else ""
    commune2 = commune2.strip() if commune2 else ""

    st.markdown("---")

    # Bouton de validation pour lancer le calcul
    if st.button("Afficher les Résultats", type="primary"):
        if not commune1 or not commune2:
            st.error("Veuillez sélectionner deux communes.")
            return

        conn = sqlite3.connect(current_db_path)
        cursor = conn.cursor()

        # 3. Vérification de l'existence de la circonscription
        query = """ 
            SELECT EXISTS(
                SELECT 1 FROM circonscription  
                WHERE commune1 = ? AND commune2 = ?
            ) 
        """
        cursor.execute(query, (commune1, commune2))
        (exists,) = cursor.fetchone()

        if exists:
            # 4. Récupération des votes
            query_votes = """
                SELECT Député FROM electeur 
                WHERE Commune = ? OR Commune = ?
            """
            cursor.execute(query_votes, (commune1, commune2))
            all_votes = cursor.fetchall()
            conn.close()

            # 5. Comptage des voix par candidat / parti
            color_counts = defaultdict(int)
            for row in all_votes:
                if row and row[0] is not None:
                    color = str(row[0]).strip().capitalize()
                    color_counts[color] += 1

            # Affichage des résultats à l'écran
            show_resultat_par_candidat_on_screen(color_counts)

        else:
            conn.close()
            st.warning(
                "⚠️ **Erreur de circonscription** : Les deux communes choisies ne partagent pas la même circonscription."
            )





  ################################################################################
  def get_votes_delegue_from_db(departement, commune):
    """Fetches votes from the SQLite database."""
    try:
        conn = sqlite3.connect(current_db_path)
        cursor = conn.cursor()

        query_votes = """ SELECT Délégué FROM electeur WHERE Departement = ? AND Commune = ? """
        cursor.execute(query_votes, (departement, commune))
        all_votes = cursor.fetchall()
        conn.close()
        return all_votes
    except sqlite3.OperationalError:
        st.error(
            "Impossible de se connecter à la base de données. Vérifiez le chemin."
        )
        return []
  ################################################################################
  def get_votes_maire_from_db(departement, commune):
    """Fetches votes from the SQLite database."""
    try:
        conn = sqlite3.connect(current_db_path)
        cursor = conn.cursor()

        query_votes = """ 
            SELECT Maire FROM electeur 
            WHERE Departement = ? AND Commune = ? 
        """
        cursor.execute(query_votes, (departement, commune))
        all_votes = cursor.fetchall()
        conn.close()
        return all_votes
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données : {e}")
        return []
  ##############################################################################
  def check_resultat_maire():
    st.write("### Résultats: Maire")
    #def resultat_maire():
    #st.title("🗳️ Résultats Élection Maire")

    # 1. Department Selection
    departements_disponibles = list(donnees.keys())
    selected_departement = st.selectbox(
        "Sélectionnez un Département :",
        options=[""] + departements_disponibles,
        index=0,
    )

    # 2. Conditional Commune Selection
    if selected_departement:
        communes_disponibles = list(donnees[selected_departement].keys())
        selected_commune = st.selectbox(
            "Sélectionnez une Commune :",
            options=[""] + communes_disponibles,
            index=0,
        )
    else:
        st.info("Veuillez d'abord sélectionner un département.")
        return

    # 3. Validation & Action Button
    if st.button("Afficher les résultats"):
        if not selected_departement:
            st.error("Le Département est requis.")
        elif not selected_commune:
            st.error("La Commune est requise.")
        else:
            # Fetch and process data
            all_votes = get_votes_maire_from_db(selected_departement, selected_commune)

            color_counts = defaultdict(int)
            for row in all_votes:
                if row and row[0] is not None:
                    color = str(row[0]).strip().capitalize()
                    color_counts[color] += 1

            # Display results
            show_resultat_par_candidat_on_screen(color_counts)
 



 ###########################################################################################################
 

  def check_resultat_delegue():
    st.write("### Résultats: Délégué")
    #def resultat_delegue():
    #st.title("Résultats des Délégués")

    # 1. Sélection du Département
    liste_departements = list(donnees.keys())
    selected_departement = st.selectbox(
        "Sélectionnez un Département",
        options=[""] + liste_departements,
        index=0,
    )

    # 2. Mise à jour dynamique de la Commune (Équivalent de update_commune_cb)
    liste_communes = []
    if selected_departement and selected_departement in donnees:
        liste_communes = list(donnees[selected_departement].keys())

    selected_commune = st.selectbox(
        "Sélectionnez une Commune", options=[""] + liste_communes, index=0
    )

    # 3. Bouton pour lancer la vérification (Équivalent des fonctions check_departement / check_commune)
    if st.button("Afficher les résultats"):
        # Validation des champs requis (Équivalent de tkinter.messagebox.showwarning)
        if not selected_departement:
            st.warning("Le Département est requis.")
        elif not selected_commune:
            st.warning("La Commune est requise.")
        else:
            # Traitement si tout est valide (Équivalent de check_if_exist)
            with st.spinner("Chargement des données..."):
                all_votes = get_votes_delegue_from_db(
                    selected_departement.strip(), selected_commune.strip()
                )

                # Comptage des voix par candidat
                color_counts = defaultdict(int)
                for row in all_votes:
                    if row and row[0] is not None:
                        color = str(row[0]).strip().capitalize()
                        color_counts[color] += 1

                # Affichage des résultats
                show_resultat_par_candidat_on_screen(color_counts)









  #################################################################################
  def check_resultat_casec():
    st.write("### Résultats: Casec")
    #def resultat_casec():
    #st.title("Résultats CASEC")

    # 1. Department Selection
    departements = list(donnees.keys()) if "donnees" in globals() else []
    selected_departement = st.selectbox(
        "Sélectionnez le Département",
        options=[""] + departements,
        index=0,
    )

    if not selected_departement:
        st.warning("⚠️ Le Département est requis.")
        return

    # 2. Commune Selection (Updates dynamically based on Department)
    communes = list(donnees[selected_departement].keys())
    selected_commune = st.selectbox(
        "Sélectionnez la Commune", options=[""] + communes, index=0
    )

    if not selected_commune:
        st.warning("⚠️ La Commune est requise.")
        return

    # 3. Section Selection (Updates dynamically based on Commune)
    sections = donnees[selected_departement][selected_commune]
    selected_section = st.selectbox(
        "Sélectionnez la Section", options=[""] + sections, index=0
    )

    if not selected_section:
        st.warning("⚠️ La Section est requise.")
        return

    # 4. Process and Display Results automatically when all fields are valid
    if st.button("Afficher les résultats"):
        with st.spinner("Chargement des données..."):
            try:
                # Database connection (Ensure current_db_path is defined)
                conn = sqlite3.connect(current_db_path)
                cursor = conn.cursor()

                query_votes = """ SELECT Casec FROM electeur WHERE Section = ? """
                cursor.execute(query_votes, (selected_section,))
                all_votes = cursor.fetchall()
                conn.close()

                # Count votes
                color_counts = defaultdict(int)
                for row in all_votes:
                    if row and row[0] is not None:
                        color = str(row[0]).strip().capitalize()
                        color_counts[color] += 1

                # Display results
                show_resultat_par_candidat_on_screen(color_counts)

            except Exception as e:
                st.error(f"Erreur de base de données : {e}")







  def check_resultat_asec():
    st.write("### Résultats: Asec")
    #def resultat_asec():
    #st.write("### Résultats: Asec")

    # 1. Department Selection
    departements = list(donnees.keys()) if "donnees" in globals() else []
    selected_departement = st.selectbox(
        "Sélectionnez le Département",
        options=[""] + departements,
        index=0,
    )

    if not selected_departement:
        st.warning("⚠️ Le Département est requis.")
        return

    # 2. Commune Selection (Updates dynamically based on Department)
    communes = list(donnees[selected_departement].keys())
    selected_commune = st.selectbox(
        "Sélectionnez la Commune", options=[""] + communes, index=0
    )

    if not selected_commune:
        st.warning("⚠️ La Commune est requise.")
        return

    # 3. Section Selection (Updates dynamically based on Commune)
    sections = donnees[selected_departement][selected_commune]
    selected_section = st.selectbox(
        "Sélectionnez la Section", options=[""] + sections, index=0
    )

    if not selected_section:
        st.warning("⚠️ La Section est requise.")
        return

    # 4. Process and Display Results automatically when all fields are valid
    if st.button("Afficher les résultats"):
        with st.spinner("Chargement des données..."):
            try:
                # Database connection
                conn = sqlite3.connect(current_db_path)
                cursor = conn.cursor()

                # Targets the 'Asec' column as per your original logic
                query_votes = """ SELECT Asec FROM electeur WHERE Section = ? """
                cursor.execute(query_votes, (selected_section,))
                all_votes = cursor.fetchall()
                conn.close()

                # Count votes
                color_counts = defaultdict(int)
                for row in all_votes:
                    if row and row[0] is not None:
                        color = str(row[0]).strip().capitalize()
                        color_counts[color] += 1

                # Display results using your original function
                show_resultat_par_candidat_on_screen(color_counts)

            except Exception as e:
                st.error(f"Erreur de base de données : {e}")






  # 2. Create the menu structure in the sidebar
  st.sidebar.title("Navigation")

  menu_options = [
      "",
      "Président",
      "Sénateur",
      "Député",
      "Maire",
      "Délégué",
      "Casec",
      "Asec",
  ]

  selected_page = st.sidebar.selectbox("Sélectionnez un Résultat", menu_options)

  # Bouton pour revenir à la recherche (placé en bas du menu latéral)
  st.sidebar.divider()
  if st.sidebar.button("⬅️ Retour "):
    st.session_state.step = "input_stage"
    st.rerun()

  # 3. Route the selection to the correct function in the main area
  if selected_page == "Président":
    show_resultat()
  elif selected_page == "Sénateur":
    check_resultat_senateur()
  elif selected_page == "Député":
    check_resultat_depute()
  elif selected_page == "Maire":
    check_resultat_maire()
  elif selected_page == "Délégué":
    check_resultat_delegue()
  elif selected_page == "Casec":
    check_resultat_casec()
  elif selected_page == "Asec":
    check_resultat_asec()



























##################  Step 2 #####################3




# --- STAGE 2: RECORD DOES NOT EXIST ---
elif st.session_state.step == "step_2":
    st.error(f"❌  Utilisateur introuvable ")
    #st.header("Step 2 View")
    st.write("Il semblerait que vous êtes nouveau ici. Pour continuer Veuillez d'abord vous inscrire.")

    
    # Go back button
    if st.button("s'inscrire"):
        st.session_state.step = "step_3"
        st.rerun()

    # Registration button (placed safely outside the form)
    # Create columns to push the registration button to the right side
    # [4, 1] means the left side takes 80% space, right side takes 20%
    col1, col2 = st.columns([4, 1])
    
    with col2:
        if st.button("⬅️ Retour", width='stretch'):        
            st.session_state.step = "input_stage" 
            st.rerun()
























###############  Step 3  #####################













# --- STAGE 2: RECORD DOES NOT EXIST ---
elif st.session_state.step == "step_3":

    st.markdown("<h3 style='text-align: center;' title='Pour utiliser ce service vous devez avoir 18 ans accompli.'>Vérifier votre identité</h3>", unsafe_allow_html=True )
    st.write("« Scanner le **recto** de votre **carte électorale** ou en importer une photo »")

    

    # Initialize cached OCR Reader
    #@st.cache_resource
    #def load_ocr_reader():
    #    return easyocr.Reader(['fr', 'en'], gpu=False, recog_network='standard', detector='dbnet18')
    #reader = load_ocr_reader()
    ###@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # Define the absolute or relative path to your pre-loaded models folder
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
    @st.cache_resource
    def load_ocr_model():
        return easyocr.Reader(
            ['en'], 
            gpu=False, 
            model_storage_directory=MODEL_DIR, # Point to your folder
            download_enabled=False             # Block automatic web downloads
        )


    # Safely check if models exist before running the reader initialization
    if not os.path.exists(os.path.join(MODEL_DIR, "english_g2.pth")):
        st.error(f"Required model files missing in `{MODEL_DIR}/`. Please make sure to download them.")
    else:
        reader = load_ocr_model()

    ####@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


    ###########################################################################
    def check_image_usability(img_np):
        """Checks basic visual heuristics before letting OCR execute to prevent crashing or false data."""
        # Convert to grayscale
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    
        # 1. Blur Detection using Laplacian Variance
        variance_of_laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance_of_laplacian < 70.0:  # Threshold can be adjusted based on camera test runs
            return False, "The image is too blurry. Please take a steadier, well-focused photo."
        
        # 2. Minimum Resolution Check 
        h, w, _ = img_np.shape
        if h < 400 or w < 400:
            return False, "The image resolution is too low. Please upload a higher-quality file."
        
        return True, "Valid"

    #########################################################################    
    source_option = st.sidebar.radio("Choose image source:", ("Upload File", "Use Camera"))
    uploaded_file = None
    if source_option == "Upload File":
        uploaded_file = st.file_uploader(f"Upload  Image...", type=["jpg", "jpeg", "png"])
            
    else:
        #uploaded_file = st.camera_input(f"Snapshot of {card_side}")
        uploaded_file = st.camera_input(f"Snapshot of ")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        img_np = np.array(image)
    
        col1, col2 = st.columns([1, 1])
    
        with col1:
            #st.image(image, caption=f"Target {card_side}", use_container_width=True)
            st.image(image, caption=f"Target ", width='stretch')

        with col2:
            
            # Pre-execution structural image checking
            is_usable, message = check_image_usability(img_np)
            if not is_usable:
                st.error(f"❌ **Quality Error:** {message}")
                st.stop()

            # Create a unique key for this uploaded file to prevent re-processing the same image
            file_cache_key = f"processed_{uploaded_file.name}_{uploaded_file.size}"

            # Only analyze if we haven't processed this specific file yet
            if st.session_state.get("current_file_key") != file_cache_key:
                with st.spinner("Analyzing image assets..."):
                    # Execute Text OCR tracking 
                    ocr_results = reader.readtext(img_np)
                    extracted_lines = [res[1].strip() for res in ocr_results if res and len(res) > 1]
                
                    # Text Validation Layer
                    full_block = "\n".join(extracted_lines)
                    full_text_upper = full_block.upper()
                    required_anchors = ["REPIBLIK", "HAITI", "IDENTIFICATION", "IDANTIFIKASYON", "NATIONALE", "COMMUNE", "DEPARTEMENT", "CIN"]
                
                    # If completely irrelevant text is processed, halt layout generation
                    if not any(anchor in full_text_upper for anchor in required_anchors):
                        st.error("❌ **Invalid Card Type.** The document text does not closely match a standard Haitian National ID Card pattern. Please align your card clearly.")
                        st.stop()
                
                    # Parse Data Fields
                    u_id = re.search(r'\b\d{10}\b', full_block)
                    gender_match = re.search(r'\b([MF])\b', full_block)
                    date_match = re.search(
                        r'(?:)[\s:]*((?:0[1-9]|[12]\d|3[01])-(?:0[1-9]|1[0-2])-\d{4})', 
                        full_block, 
                        re.IGNORECASE
                    )
               
                    lines = [line.strip() for line in full_block.split('\n') if line.strip()] 
                    target_words = ["DAYITI", "REPIBLIK", "D'HAITI", "RÉPUBLIQUE","KAT IDANTIFIKASYON NASYONAL", "CARTE D'IDENTIFICATION NATIONALE", "F", "M", "HTI"]
                    
                    nom = ""
                    prenom = ""
                    unwanted_chars = ["/", "\\", "-", "_"]
                    valid_matches = []
                    current_index = 7

                    while current_index <= 18: 
                        if len(lines) > current_index:
                            original_line = lines[current_index]
                            current_line = original_line
                            for char in unwanted_chars:
                                current_line = current_line.replace(char, "")
                            current_line = current_line.strip()

                            if not current_line or any(char.isdigit() for char in current_line) or any(char.islower() for char in current_line):
                                current_index += 1
                                continue
            
                            line_words = current_line.split()
                            if any(word in target_words for word in line_words) or current_line in target_words:
                                current_index += 1
                                continue

                            valid_matches.append((current_index, original_line))
                            current_index += 1
                        else:
                            break

                    if len(valid_matches) >= 2:
                        valid_matches.sort(key=lambda x: x[0]) 
                        nom = valid_matches[-1][1]    
                        prenom = " ".join([match[1] for match in valid_matches[:-1]])   
                    elif len(valid_matches) == 1:
                        prenom = valid_matches[0][1]
                        nom = ""

                    # Save parsed results strictly to session state
                    st.session_state["extracted_nom"] = nom
                    st.session_state["extracted_prenom"] = prenom
                    st.session_state["extracted_sexe"] = gender_match.group(0).upper() if gender_match else ""
                    st.session_state["extracted_nin"] = u_id.group(0) if u_id else ""
                    st.session_state["image_data"] = uploaded_file.getvalue()
                    st.session_state["image_filename"] = uploaded_file.name
                    
                    if date_match:
                        try:
                            st.session_state["extracted_dob"] = datetime.strptime(date_match.group(1), "%d-%m-%Y")
                        except ValueError:
                            st.session_state["extracted_dob"] = datetime(2000, 1, 1)
                    else:
                        st.session_state["extracted_dob"] = datetime(2000, 1, 1)

                    # Mark this specific file layout configuration as successfully cached
                    st.session_state["current_file_key"] = file_cache_key

            # --- UI Display Layer (Reads from frozen state to avoid re-running calculations) ---
            #st.subheader("📋 Parsed Front Identification Details")
            st.markdown(" #### 📋 Identification Details", help="Ces informations ont été automatiquement extraites de l'image. Elles peuvent être erronnées si l'image est de mauvaise qualité.")

            st.write(f"**Nom:** `{st.session_state['extracted_nom'] if st.session_state['extracted_nom'] else 'Non Détecté'}`")
            st.write(f"**Prénom:** `{st.session_state['extracted_prenom'] if st.session_state['extracted_prenom'] else 'Non Détecté'}`")
            st.write(f"**Sexe:** `{st.session_state['extracted_sexe'] if st.session_state['extracted_sexe'] else 'Non Détecté'}`")
            
            dob_string = st.session_state['extracted_dob'].strftime('%d-%m-%Y') if st.session_state['extracted_dob'] != datetime(2000, 1, 1) else 'Non Détecté'
            st.write(f"**Date de Naissance:** `{dob_string}`")
            st.write(f"**Nin:** `{st.session_state['extracted_nin'] if st.session_state['extracted_nin'] else 'Non Détecté'}`")
            # 💡 ADDED INFO BULB BANNER HERE
            st.info("ℹ️Les informations ci-dessus ont été extraites de votre image. Veuillez vérifier que le **nom**, le **prénom** et le **NIN** sont corrects, puis cliquez sur « **Suivant** » pour valider et finaliser votre inscription.")
                              
            # Define an atomic callback to instantly push state to Step 4 on button press
            def move_to_step_4():
                st.session_state.step = "step_4"

            st.button("Suivant", on_click=move_to_step_4)







    #def run_voter_registration():
    #st.title("Ajout d'électeur")
    # Go back button
    if st.sidebar.button("⬅️ Retour"):
        st.session_state.step = "input_stage"
        st.rerun()

    








###########################   Step  4 ################









        

# --- STAGE 2: RECORD DOES NOT EXIST ---

elif st.session_state.step == "step_4":
    st.markdown("<h3 style='text-align: center;'>Formulaire d'inscription</h3>", unsafe_allow_html=True)

    # Fallbacks for safer extraction bindings
    sc_nom = st.session_state.get("extracted_nom", "")
    sc_prenom = st.session_state.get("extracted_prenom", "")
    sc_sexe = st.session_state.get("extracted_sexe", "")
    sc_dob = st.session_state.get("extracted_dob", datetime(2000, 1, 1))
    sc_nin = st.session_state.get("extracted_nin", "")
    image_filename = st.session_state.get("image_filename", "scanned_id.png")
    
    # --- 1. Initialize a success flag at the top of step_4 if it doesn't exist ---
    if "registration_success" not in st.session_state:
        st.session_state["registration_success"] = False
    # --- 1. Session State Initialization ---
    if "image_data" not in st.session_state:
        st.session_state.image_data = None

    # Default backup image generation
    img_backup = PILImage.new("RGB", (25, 25), color="blue")
    output = BytesIO()
    img_backup.save(output, format="PNG")
    image_backup = output.getvalue()

    # --- 2. Database & Reactive Dropdowns (MUST STAY OUTSIDE THE FORM) ---
    conn = sqlite3.connect(current_db_path)
    cursor = conn.cursor()

    # Fetch Departements
    cursor.execute("SELECT DISTINCT departement FROM candidat")
    dept_values = [row[0] for row in cursor.fetchall() if row[0]]
    
    # Cascading Dropdown States
    geo_col1, geo_col2, geo_col3 = st.columns(3)
    with geo_col1:
        combo1 = st.selectbox("Departement *", options=[""] + dept_values)

    commune_values = []
    if combo1:
        cursor.execute("SELECT DISTINCT commune1 FROM candidat WHERE departement = ?", (combo1,))
        commune_values = [row[0] for row in cursor.fetchall() if row[0]]
    
    with geo_col2:
        combo2 = st.selectbox("Commune *", options=[""] + commune_values)

    section_values = []
    if combo2:
        cursor.execute("SELECT DISTINCT section FROM candidat WHERE departement = ? AND commune1 = ?", (combo1, combo2))
        section_values = [row[0] for row in cursor.fetchall() if row[0]]
    
    with geo_col3:
        combo3 = st.selectbox("Section *", options=[""] + section_values)
    
    vote_col1, vote_col2, _ = st.columns(3)
    cv_values = []
    if combo3:
        cursor.execute("SELECT Nom FROM CV WHERE Section = ?", (combo3,))
        cv_values = [row[0] for row in cursor.fetchall() if row[0]]
        
    with vote_col1:
        CV_combobox = st.selectbox("Centre de Vote (CV)", options=[""] + cv_values)

    bv_values = []
    if CV_combobox:
        cursor.execute("SELECT Nom FROM BV WHERE CV = ?", (CV_combobox,))
        bv_values = [row[0] for row in cursor.fetchall() if row[0]]
        
    with vote_col2:
        BV_combobox = st.selectbox("Bureau de Vote (BV)", options=[""] + bv_values)

    # Fetch Dynamic Candidates based on layout locations
    presidents = [row[0] for row in cursor.execute("SELECT nom FROM candidat WHERE poste = 'Président'").fetchall()]
    senateurs = []
    if combo1:
        cursor.execute("SELECT nom FROM candidat WHERE departement = ? AND poste = 'Sénateur'", (combo1,))
        senateurs = [row[0] for row in cursor.fetchall()]

    deputes = []
    if combo2:
        cursor.execute("SELECT nom FROM candidat WHERE (commune1 = ? OR commune2 = ?) AND poste = 'Député'", (combo2, combo2))
        deputes = [row[0] for row in cursor.fetchall()]

    maires = []
    delegues = []
    if combo2:
        maires = [row[0] for row in cursor.execute("SELECT nom FROM candidat WHERE commune1 = ? AND poste = 'Maire'", (combo2,)).fetchall()]
        delegues = [row[0] for row in cursor.execute("SELECT nom FROM candidat WHERE commune1 = ? AND poste = 'Délégué'", (combo2,)).fetchall()]

    casecs = []
    asecs = []
    if combo3:
        casecs = [row[0] for row in cursor.execute("SELECT nom FROM candidat WHERE section = ? AND poste = 'Casec'", (combo3,)).fetchall()]
        asecs = [row[0] for row in cursor.execute("SELECT nom FROM candidat WHERE section = ? AND poste = 'Asec'", (combo3,)).fetchall()]


    # --- 3. SINGLE UNIFIED FORM BLOCK ---
    with st.form("unified_electeur_form", clear_on_submit=False):
        st.markdown(
            "<h4 style='text-align: center;' title='Verifier votre identité'>Informations Personnelles</h4>", 
            unsafe_allow_html=True
        )

        #st.subheader("Informations Personnelles")
        row1_col1, row1_col2, row1_col3 = st.columns(3)
        with row1_col1:
            nom_entry = st.text_input("Nom *", value=sc_nom, disabled=True).strip()
        with row1_col2:
             prenom_entry = st.text_input("Prénom *", value=sc_prenom, disabled=True).strip()
        with row1_col3:
            sexe_opts = ["", "M", "F"]
            sexe_index = sexe_opts.index(sc_sexe) if sc_sexe in sexe_opts else 0
            sexe_combobox = st.selectbox("Sexe *", options=sexe_opts, index=sexe_index)

        row2_col1, row2_col2, row2_col3 = st.columns(3)
        with row2_col1:            
            dn_entry = st.date_input("Date de naissance *", value=sc_dob)
        with row2_col2:
            addresse_entry = st.text_input("Adresse *").strip()
        with row2_col3:
            tel_entry = st.text_input("Téléphone").strip()               
       
        # Hidden or restricted layout calculations
        nin_entry = sc_nin.strip()

        # Candidates Section inside the exact same form block
        #st.subheader("Sélectionnez vos Candidats")
        st.markdown(
            "<h4 style='text-align: center;' title='Je vote'>Sélectionnez vos Candidats</h4>", 
            unsafe_allow_html=True
        )

        cand_row1_col1, cand_row1_col2, cand_row1_col3 = st.columns(3)
        with cand_row1_col1:
            combo_president = st.selectbox("Président", options=["Aucun Candidat"] + presidents)
        with cand_row1_col2:
            combo_senateur = st.selectbox("Sénateur", options=["Aucun Candidat"] + senateurs)
        with cand_row1_col3:
            combo_depute = st.selectbox("Député", options=["Aucun Candidat"] + deputes)
            
        cand_row2_col1, cand_row2_col2, cand_row2_col3 = st.columns(3)
        with cand_row2_col1:
            combo_maire = st.selectbox("Maire", options=["Aucun Candidat"] + maires)
        with cand_row2_col2:
            combo_delegue = st.selectbox("Délégué", options=["Aucun Candidat"] + delegues)
        with cand_row2_col3:
            combo_casec = st.selectbox("Casec", options=["Aucun Candidat"] + casecs)

        cand_row3_col1, _, _ = st.columns(3)
        with cand_row3_col1:
            combo_asec = st.selectbox("Asec", options=["Aucun Candidat"] + asecs)

        # The single form submission trigger
        # --- Form submission trigger (Conditionally Hidden on Success) ---
        if not st.session_state.get("registration_success", False):
            # Show the active button if they haven't successfully registered yet
            submit_button = st.form_submit_button("Enregistrer", type="primary")
        else:
            # Hide the submit button and provide a visual lock indicator inside the form
            #st.form_submit_button("Formulaire Verrouillé 🔒", disabled=True)
            submit_button = False  # Safe structural fallback flag

    # --- 4. Database Actions Execution (After form submission) ---
    if submit_button:
        current_year = datetime.now().year
        age = current_year - dn_entry.year

        # Multi-point Validation Checks
        if not nom_entry:
            st.error("Erreur: Le Nom est requis.")
        elif not prenom_entry:
            st.error("Erreur: Le Prénom est requis.")
        elif len(tel_entry) != 11 and len(tel_entry) != 0:
            st.error("Erreur: Le numéro du téléphone est incorrect (doit être de 11 chiffres ou vide).")
        elif age < 18:
            st.error("Erreur: L'électeur doit être majeur (18 ans minimum).")
        elif not sexe_combobox:
            st.error("Erreur: Veuillez choisir le sexe.")
        elif len(nin_entry) != 10:
            st.error("Erreur: Le Numero d'identité doit avoir exactement 10 chiffres.")
        elif not (combo1 and combo2 and combo3):
            st.error("Erreur: Les champs Géographiques (Département, Commune, Section) sont requis.")
        elif not addresse_entry:
            st.error("Erreur: L'adresse est requise.")
        else:
            # Query constraints verification
            cursor.execute("SELECT COUNT(*) FROM electeur WHERE Nin = ?", (nin_entry,))
            if cursor.fetchone()[0] > 0:
                st.error(f"Erreur de doublon: Ce Numero d'identité '{nin_entry}' existe déjà.")
            else:
                if st.session_state.image_data:
                    final_image = st.session_state.image_data
                else:
                    final_image = image_backup

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS electeur (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, image_data BLOB, filename TEXT, 
                        Nom TEXT, Prénom TEXT, Addresse TEXT, Phone TEXT, Naissance TEXT, 
                        Sexe TEXT, Nin TEXT, CV TEXT, BV TEXT, Asec TEXT, Casec TEXT, 
                        Délégué TEXT, Maire TEXT, Député TEXT, Sénateur TEXT, Président TEXT, 
                        Departement TEXT, Commune TEXT, Section TEXT
                    )
                """)

                data_insert_query = """
                    INSERT INTO electeur (
                        image_data, filename, Nom, Prénom, Addresse, Phone, Naissance, Sexe, Nin, 
                        CV, BV, Asec, Casec, Délégué, Maire, Député, Sénateur, Président, Departement, Commune, Section
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

                data_insert_tuple = (
                    final_image, image_filename, nom_entry, prenom_entry, addresse_entry, tel_entry,
                    str(dn_entry), sexe_combobox, nin_entry, CV_combobox, BV_combobox, combo_asec,
                    combo_casec, combo_delegue, combo_maire, combo_depute, combo_senateur, combo_president,
                    combo1, combo2, combo3
                )

                cursor.execute(data_insert_query, data_insert_tuple)
                conn.commit()
                # Clear structural state hooks
                st.session_state.image_data = None
                
                # Save the voter's name to session state for the persistent message
                st.session_state["success_message"] = f"Félicitations ! L'électeur {prenom_entry} {nom_entry} a été enregistré avec succès."
                
                # Set our persistent flag to True and force a rerun to update the UI
                st.session_state["registration_success"] = True
                st.rerun()

    conn.close()

    # --- 6. Persistent Post-Registration UI Layer (OUTSIDE the form and submit blocks) ---
    # --- 6. Persistent Post-Registration UI Layer ---
    if st.session_state.get("registration_success", False):
        st.success(st.session_state["success_message"])
        
        # Inject standard style targets using a strict macro class definition
        st.html("""
            <style>
                #green_action_block button {
                    background-color: #28a745 !important;
                    color: white !important;
                    border: 1px solid #28a745 !important;
                }
                #green_action_block button:hover {
                    background-color: #218838 !important;
                    color: white !important;
                    border: 1px solid #218838 !important;
                }
            </style>
        """)
        
        # Open an explicit HTML ID anchor wrapper
        st.markdown('<div id="green_action_block">', unsafe_allow_html=True)
        
        if st.button("Afficher les Résultats"):
            st.session_state["registration_success"] = False  
            st.session_state.step = "step_1"                  
            st.rerun()
            
        # Close the explicit anchor block
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 7. Global Back Navigation (Stays standard layout color) ---
    if st.button("⬅️ Retour"):
        st.session_state["registration_success"] = False      
        st.session_state.step = "input_stage"
        st.rerun()













