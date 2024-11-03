import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
import json
import sys
import argparse

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rapport_ventes.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def charger_configuration():
    """Charge la configuration depuis config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            required_fields = ['email_from', 'email_password', 'recipients']
            if not all(field in config for field in required_fields):
                raise ValueError("Configuration incomplète")
            return config
    except FileNotFoundError:
        logger.error("Fichier config.json non trouvé")
        raise
    except json.JSONDecodeError:
        logger.error("Erreur de format dans config.json")
        raise
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {str(e)}")
        raise

def generer_rapport_ventes():
    """Génère le rapport PDF des ventes"""
    try:
        if not os.path.exists('sales_data.csv'):
            logger.error("Fichier sales_data.csv non trouvé")
            raise FileNotFoundError("Fichier de données des ventes non trouvé")

        # Lecture des données
        logger.info("Lecture des données de ventes...")
        df = pd.read_csv('sales_data.csv')

        # Analyse des données
        logger.info("Analyse des données...")
        rapport = df.groupby('product').agg({
            'revenue': ['sum', 'count', 'mean']
        }).round(2)

        rapport.columns = ['Revenu Total', 'Nombre de Ventes', 'Moyenne par Vente']
        rapport = rapport.reset_index().sort_values('Revenu Total', ascending=False)

        # Création du PDF
        logger.info("Génération du rapport PDF...")
        doc = SimpleDocTemplate(
            'rapport_ventes.pdf',
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

        elements = []
        styles = getSampleStyleSheet()

        # Titre
        title = Paragraph(
            f"Rapport des Ventes - {datetime.now().strftime('%d/%m/%Y')}",
            styles['Title']
        )
        elements.append(title)
        elements.append(Spacer(1, 20))

        # Table
        data = [rapport.columns.tolist()] + rapport.values.tolist()
        table = Table(data, colWidths=[150, 100, 100, 100])
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -1), 10)
        ])
        
        table.setStyle(style)
        elements.append(table)

        # Génération du PDF
        doc.build(elements)
        logger.info("Rapport PDF généré avec succès")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport: {str(e)}")
        raise

def envoyer_rapport(config):
    """Envoie le rapport par email"""
    try:
        if not os.path.exists('rapport_ventes.pdf'):
            raise FileNotFoundError("Rapport PDF non trouvé")

        logger.info("Préparation de l'email...")
        msg = MIMEMultipart()
        msg['Subject'] = 'Rapport des Ventes'
        msg['From'] = config['email_from']
        msg['To'] = ', '.join(config['recipients'])

        # Corps du message
        corps_message = """
        Bonjour,

        Veuillez trouver ci-joint le rapport des ventes.

        Cordialement,
        Service Commercial
        """
        msg.attach(MIMEText(corps_message, 'plain'))

        # Pièce jointe
        logger.info("Ajout de la pièce jointe...")
        with open('rapport_ventes.pdf', 'rb') as f:
            pdf = MIMEApplication(f.read(), _subtype='pdf')
            pdf.add_header('Content-Disposition', 'attachment', 
                         filename='rapport_ventes.pdf')
            msg.attach(pdf)

        # Envoi de l'email
        logger.info("Connexion au serveur SMTP...")
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(config['email_from'], config['email_password'])
            logger.info("Envoi de l'email...")
            server.send_message(msg)

        logger.info("Email envoyé avec succès")
        return True

    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        raise

def ajouter_destinataire(email):
    """Ajoute un nouveau destinataire à la configuration"""
    try:
        config = charger_configuration()
        if email not in config['recipients']:
            config['recipients'].append(email)
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Destinataire {email} ajouté avec succès")
        else:
            logger.info(f"Le destinataire {email} existe déjà")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout du destinataire: {str(e)}")
        raise

def modifier_expediteur(email, password):
    """Modifie l'expéditeur dans la configuration"""
    try:
        config = charger_configuration()
        config['email_from'] = email
        config['email_password'] = password
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        logger.info(f"Expéditeur modifié avec succès: {email}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la modification de l'expéditeur: {str(e)}")
        raise
# ... existing code ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Script de rapport de ventes')
    
    # Création des groupes d'options mutuellement exclusifs
    group = parser.add_mutually_exclusive_group(required=True)
    
    group.add_argument('--add-receiver', 
                      type=str,
                      help='Ajouter une nouvelle adresse email de destinataire')
    
    group.add_argument('--set-sender',
                      nargs=2,
                      metavar=('EMAIL', 'PASSWORD'),
                      help='Modifier l\'email et le mot de passe de l\'expéditeur')
    
    group.add_argument('--generate-report',
                      action='store_true',
                      help='Générer et envoyer le rapport')
    
    args = parser.parse_args()
    
    try:
        if args.add_receiver:
            ajouter_destinataire(args.add_receiver)
            sys.exit(0)
        elif args.set_sender:
            email, password = args.set_sender
            modifier_expediteur(email, password)
            sys.exit(0)
        elif args.generate_report:
            sys.exit(main())
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        sys.exit(1)