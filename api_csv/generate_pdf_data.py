import random
from datetime import datetime
from faker import Faker
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Initialiser faker pour générer des données fictives
fake = Faker('fr_FR')

# Exemple de données fictives pour 50 fichiers
data = []
for _ in range(50):
    patient = {
        'nom': fake.name(),
        'date_naissance': fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%d.%m.%Y'),
        'sexe': random.choice(['M', 'F']),
        'type_examen': random.choice(['IRM', 'Scanner', 'Radiographie', 'Echographie']),
        'date_examen': datetime.now().strftime('%d.%m.%Y'),
        'indication': fake.sentence(nb_words=8),
        'description': fake.paragraph(nb_sentences=5),
        'conclusion': fake.paragraph(nb_sentences=2)
    }
    data.append(patient)

# Générer les PDF avec les données
def generate_pdf(patient, file_path):
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Informations de l'hôpital
    c.drawString(100, height - 50, "Hôpital du Valais - Centre Hospitalier du Valais Romand")
    c.drawString(100, height - 70, "Hôpital de Sion, Avenue du Grand-Champsec 80, CH-1950 Sion")
    c.drawString(100, height - 90, "CHVR, Hôpital de Sion, Case Postale 736, CH-1951 Sion")

    # Informations sur le patient et l'examen
    c.drawString(100, height - 130, f"Patient: {patient['nom']}")
    c.drawString(100, height - 150, f"Date de naissance: {patient['date_naissance']}, Sexe: {patient['sexe']}")
    c.drawString(100, height - 170, f"Type d'examen: {patient['type_examen']}")
    c.drawString(100, height - 190, f"Date de l'examen: {patient['date_examen']}")
    c.drawString(100, height - 210, f"Indication: {patient['indication']}")

    # Description et conclusion
    c.drawString(100, height - 250, "Description:")
    c.drawString(100, height - 270, patient['description'])

    c.drawString(100, height - 370, "Conclusion:")
    c.drawString(100, height - 390, patient['conclusion'])

    # Informations du médecin
    c.drawString(100, height - 430, "Avec nos cordiales salutations,")
    c.drawString(100, height - 450, "Dr. XYZ, Médecin")

    c.save()

# Générer les 50 fichiers PDF
for i, patient in enumerate(data):
    file_path = f"/mnt/data/report_{i+1}.pdf"
    generate_pdf(patient, file_path)

import ace_tools as tools; tools.display_dataframe_to_user(name="Sample Patient Data", dataframe=pd.DataFrame(data))
