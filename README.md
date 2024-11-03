
# Générateur de Rapport de Ventes

Ce projet permet de générer et d'envoyer automatiquement des rapports de ventes par email au format PDF.

## 📋 Prérequis

- Python 3.13
- Les bibliothèques Python suivantes :
  - pandas
  - reportlab
  - smtplib
  - logging

## 🛠️ Installation

1. Clonez le repository
2. Installez les dépendances :
```bash
pip install pandas reportlab
```

## ⚙️ Configuration

1. Configurez le fichier `config.json` avec vos informations :
   - `email_from` : Votre adresse email d'expédition
   - `email_password` : Votre mot de passe email
   - `recipients` : Liste des destinataires

2. Assurez-vous que le fichier `sales_data.csv` est présent avec les données de ventes.

## 📝 Utilisation

### Ajouter un nouveau destinataire
```bash
python rapport_ventes.py --add-receiver email@example.com
```

### Modifier l'expéditeur
```bash
python rapport_ventes.py --set-sender nouveau@email.com mot_de_passe
```

### Générer et envoyer le rapport
```bash
python rapport_ventes.py --generate-report
```

## 📊 Format des Données

Le fichier `sales_data.csv` doit contenir les colonnes suivantes :
- category
- product
- revenue
- cost
- margin

## 📁 Structure du Projet

- `rapport_ventes.py` : Script principal
- `config.json` : Configuration des emails
- `sales_data.csv` : Données des ventes
- `rapport_ventes.log` : Fichier de logs

## 📄 Logs

Les logs sont enregistrés dans :
- Le fichier `rapport_ventes.log`
- La console (stdout)

## 🔒 Sécurité

- Les informations sensibles sont stockées dans `config.json`
- Utilisez un mot de passe d'application pour Gmail
- Ne partagez jamais vos identifiants

## 📧 Format du Rapport

Le rapport PDF généré inclut :
- Un titre avec la date
- Un tableau des ventes avec :
  - Revenu Total
  - Nombre de Ventes
  - Moyenne par Vente
