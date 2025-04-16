# BI Analysis - Application Streamlit pour l'Analyse BI

Cette application Streamlit permet de réaliser plusieurs analyses BI issues d'un modèle en étoile. Elle propose notamment :

- **Trend Analysis par Client** : Visualisation de l'évolution des volumes selon différents scénarios.
- **Bridge Analysis** : Analyse du passage du Forecast Base vers le Forecast Revised, avec des vues dynamiques (filtrées par client et catégorie) et statiques (regroupées par client et par catégorie).
- **Revenue & Gross Profit Impact** : Calcul et visualisation de l'impact sur le chiffre d'affaires et sur la marge brute suite à la réallocation.

## Organisation du Projet

```
BI_analysis/
│
├── Home.py                      # Fichier d'accueil principal de l'application Streamlit
├── requirements.txt             # Liste des dépendances Python nécessaires
├── README.md                    # Ce fichier
├── Data/                        # Dossier contenant les fichiers de données
│   ├── DimCustomer.xlsx
│   ├── DimPrice.xlsx
│   ├── DimCateg.xlsx
│   └── FactVolumes.xlsx
└── pages/                       # Dossier des pages de l'application
    ├── 1_Trend_Analysis.py      # Trend Analysis par Client
    ├── 2_Bridge_Analysis.py     # Bridge Analysis dynamique (filtré par client, Base -> Revised)
    ├── 3_Impact_Analysis.py     # Revenue & Gross Profit Impact Analysis
    └── 4_Static_Bridge_Analysis.py  # Bridge Analysis statique (par Client & par Catégorie)
```

## Installation

1. **Cloner le dépôt depuis GitHub :**

   ```bash
   git clone https://github.com/stevenroman91/BI_analysis.git
   cd BI_analysis
   ```

2. **Installer les dépendances :**

   Assurez-vous d'avoir Python installé, puis exécutez :

   ```bash
   pip install -r requirements.txt
   ```

   Un exemple de contenu pour `requirements.txt` :

   ```
   streamlit
   pandas
   plotly
   openpyxl
   ```

## Lancer l'Application en Local

Pour démarrer l'application en local, utilisez la commande suivante dans le répertoire du projet :

```bash
streamlit run Home.py
```

Cela ouvrira l'application dans votre navigateur par défaut à l'adresse [http://localhost:8501](http://localhost:8501).

## Déploiement sur Render

Pour déployer l'application sur Render, suivez ces étapes :

1. **Poussez votre code sur GitHub :**

   ```bash
   git add .
   git commit -m "Déploiement initial de l'application Streamlit BI Analysis"
   git push origin main
   ```

2. **Créer un nouveau service Web sur Render :**

   - Connectez-vous sur [Render](https://render.com) avec votre compte GitHub.
   - Cliquez sur **New > Web Service**.
   - Sélectionnez votre dépôt `BI_analysis`.
   - **Build Command :**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command :**
     ```bash
     streamlit run Home.py --server.port $PORT --server.enableCORS true
     ```

## Contribution

Les contributions sont les bienvenues ! Ouvrez une issue ou soumettez une pull request.

## Licence

Ce projet est sous licence [MIT](LICENSE).
