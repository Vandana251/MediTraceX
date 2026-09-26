"""
MediTraceX Database Seeder
Generates realistic, fictional pharmaceutical dataset for 22+ pharmacies, 105+ medicines,
inventory across pharmacies, and 8+ months of daily sales history for ML/DSA testing.
"""

import sys
import os
from datetime import date, datetime, time, timedelta
import random
import math

# Ensure project root is on PYTHONPATH
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database.db_config import Base, engine, SessionLocal
from database.models import (
    User, Pharmacy, Medicine, Inventory, SalesHistory,
    MedicineRequest, Watchlist, Notification
)

def create_tables(drop_existing: bool = False):
    """Create all tables in the configured database."""
    if drop_existing:
        print("[1/5] Dropping and recreating database tables...")
        Base.metadata.drop_all(bind=engine)
    else:
        print("[1/5] Verifying and creating missing database tables...")
    Base.metadata.create_all(bind=engine)
    print("      Database tables verified/created successfully.")

# ---------------------------------------------------------------------
# Fictional Master Data Catalogs
# ---------------------------------------------------------------------

PHARMACIES_DATA = [
    {"name": "MediCare Plus Pharmacy - Jubilee Hills", "license": "TS-HYD-2023-1001", "address": "Road No. 36, Jubilee Hills", "city": "Hyderabad", "pincode": "500033", "lat": 17.4325, "lon": 78.4071, "phone": "+91-9848011221", "email": "jubilee@medicareplus.com", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "HealthPoint Super Pharmacy - Madhapur", "license": "TS-HYD-2023-1002", "address": "Near Cyber Towers, Hitec City Main Rd", "city": "Hyderabad", "pincode": "500081", "lat": 17.4483, "lon": 78.3742, "phone": "+91-9848011222", "email": "hitec@healthpoint.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "CityMed 24/7 Chemists - Gachibowli", "license": "TS-HYD-2023-1003", "address": "Plot 14, Financial District, Gachibowli", "city": "Hyderabad", "pincode": "500032", "lat": 17.4401, "lon": 78.3489, "phone": "+91-9848011223", "email": "gachibowli@citymed.com", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Care & Cure Pharmacy - Banjara Hills", "license": "TS-HYD-2023-1004", "address": "Road No. 12, Banjara Hills", "city": "Hyderabad", "pincode": "500034", "lat": 17.4156, "lon": 78.4350, "phone": "+91-9848011224", "email": "banjara@carecure.org", "open": time(7, 30), "close": time(22, 30), "is_24_7": False},
    {"name": "Apollo Care Center - Kondapur", "license": "TS-HYD-2023-1005", "address": "Botanical Garden Rd, Kondapur", "city": "Hyderabad", "pincode": "500084", "lat": 17.4612, "lon": 78.3587, "phone": "+91-9848011225", "email": "kondapur@apollocare.in", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "Lifeline Drug House - Ameerpet", "license": "TS-HYD-2023-1006", "address": "Near Metro Station Pillar 1042, Ameerpet", "city": "Hyderabad", "pincode": "500016", "lat": 17.4375, "lon": 78.4483, "phone": "+91-9848011226", "email": "ameerpet@lifelinedrugs.com", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Guardian Lifecare - Begumpet", "license": "TS-HYD-2023-1007", "address": "Prakash Nagar, Begumpet", "city": "Hyderabad", "pincode": "500016", "lat": 17.4442, "lon": 78.4682, "phone": "+91-9848011227", "email": "begumpet@guardianlife.in", "open": time(8, 30), "close": time(22, 30), "is_24_7": False},
    {"name": "Noble Chemists - Kukatpally", "license": "TS-HYD-2023-1008", "address": "KPHB Phase 1, Kukatpally", "city": "Hyderabad", "pincode": "500072", "lat": 17.4934, "lon": 78.3989, "phone": "+91-9848011228", "email": "kphb@noblechemists.com", "open": time(7, 0), "close": time(23, 30), "is_24_7": False},
    {"name": "Fortis MediStore - Secunderabad", "license": "TS-HYD-2023-1009", "address": "RP Road, Near Clock Tower", "city": "Secunderabad", "pincode": "500003", "lat": 17.4399, "lon": 78.4983, "phone": "+91-9848011229", "email": "rp_road@fortismed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Wellness Forever - Manikonda", "license": "TS-HYD-2023-1010", "address": "Puppalaguda Main Road, Manikonda", "city": "Hyderabad", "pincode": "500089", "lat": 17.4012, "lon": 78.3842, "phone": "+91-9848011230", "email": "manikonda@wellnessforever.com", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Sanjeevani Medicals - Miyapur", "license": "TS-HYD-2023-1011", "address": "Allwyn X Road, Miyapur", "city": "Hyderabad", "pincode": "500049", "lat": 17.4968, "lon": 78.3614, "phone": "+91-9848011231", "email": "miyapur@sanjeevani.com", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "TrueMed Pharmacy - Dilsukhnagar", "license": "TS-HYD-2023-1012", "address": "Main Road, Opp Bus Stand, Dilsukhnagar", "city": "Hyderabad", "pincode": "500060", "lat": 17.3688, "lon": 78.5247, "phone": "+91-9848011232", "email": "dilsukhnagar@truemed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Aster Pharmacy - LB Nagar", "license": "TS-HYD-2023-1013", "address": "Sagar Ring Road, LB Nagar", "city": "Hyderabad", "pincode": "500074", "lat": 17.3457, "lon": 78.5522, "phone": "+91-9848011233", "email": "lbnagar@asterpharma.com", "open": time(8, 30), "close": time(22, 30), "is_24_7": False},
    {"name": "Relief Pharmacy - Tolichowki", "license": "TS-HYD-2023-1014", "address": "Paramount Colony, Tolichowki", "city": "Hyderabad", "pincode": "500008", "lat": 17.3982, "lon": 78.4112, "phone": "+91-9848011234", "email": "tolichowki@reliefpharma.com", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "PrimeCare Pharma - Kothapet", "license": "TS-HYD-2023-1015", "address": "Victoria Memorial Metro Station, Kothapet", "city": "Hyderabad", "pincode": "500035", "lat": 17.3621, "lon": 78.5411, "phone": "+91-9848011235", "email": "kothapet@primecare.in", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "Pulse Pharmacy - Nizampet", "license": "TS-HYD-2023-1016", "address": "Nizampet Village Road", "city": "Hyderabad", "pincode": "500090", "lat": 17.5142, "lon": 78.3812, "phone": "+91-9848011236", "email": "nizampet@pulsepharma.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Universal Chemist - Alwal", "license": "TS-HYD-2023-1017", "address": "IG Statue, Old Alwal", "city": "Secunderabad", "pincode": "500010", "lat": 17.5023, "lon": 78.5089, "phone": "+91-9848011237", "email": "alwal@universalchem.com", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "Healwell Pharma - Malkajgiri", "license": "TS-HYD-2023-1018", "address": "Geeta Nagar, Malkajgiri", "city": "Hyderabad", "pincode": "500047", "lat": 17.4491, "lon": 78.5298, "phone": "+91-9848011238", "email": "malkajgiri@healwell.in", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "Global Pharmacy - Somajiguda", "license": "TS-HYD-2023-1019", "address": "Raj Bhavan Road, Somajiguda", "city": "Hyderabad", "pincode": "500082", "lat": 17.4261, "lon": 78.4578, "phone": "+91-9848011239", "email": "somajiguda@globalpharma.in", "open": time(7, 30), "close": time(23, 0), "is_24_7": False},
    {"name": "Evergreen Chemists - Mehdipatnam", "license": "TS-HYD-2023-1020", "address": "Opp Rythu Bazar, Mehdipatnam", "city": "Hyderabad", "pincode": "500028", "lat": 17.3916, "lon": 78.4418, "phone": "+91-9848011240", "email": "mehdipatnam@evergreenchem.com", "open": time(8, 0), "close": time(23, 30), "is_24_7": False},
    {"name": "Apex Health Pharmacy - Attapur", "license": "TS-HYD-2023-1021", "address": "Pillar 143, PVNR Expressway, Attapur", "city": "Hyderabad", "pincode": "500048", "lat": 17.3712, "lon": 78.4289, "phone": "+91-9848011241", "email": "attapur@apexhealth.in", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "Himalaya Chemist - Chandanagar", "license": "TS-HYD-2023-1022", "address": "Chandanagar Main Road", "city": "Hyderabad", "pincode": "500050", "lat": 17.4921, "lon": 78.3312, "phone": "+91-9848011242", "email": "chandanagar@himalayachem.com", "open": time(8, 0), "close": time(22, 30), "is_24_7": False}
]

MEDICINES_DATA = [
    # Analgesics & Antipyretics
    ("Paracetamol 500mg", "Paracetamol", "Calpol 500", "500mg", "Tablet", "GSK Consumer", "Analgesic & Antipyretic", False, 18.50),
    ("Paracetamol 650mg", "Paracetamol", "Dolo 650", "650mg", "Tablet", "Micro Labs", "Analgesic & Antipyretic", False, 32.00),
    ("Paracetamol 650mg ER", "Paracetamol", "Pacimol 650", "650mg", "Tablet", "Ipca Labs", "Analgesic & Antipyretic", False, 30.50),
    ("Paracetamol Syrup 120mg/5ml", "Paracetamol", "Calpol Pead Syrup", "120mg/5ml", "Syrup", "GSK Consumer", "Analgesic & Antipyretic", False, 45.00),
    ("Paracetamol Syrup 250mg/5ml", "Paracetamol", "Dolo Suspension", "250mg/5ml", "Syrup", "Micro Labs", "Analgesic & Antipyretic", False, 52.00),
    ("Ibuprofen 400mg", "Ibuprofen", "Brufen 400", "400mg", "Tablet", "Abbott", "Analgesic & Antipyretic", False, 22.00),
    ("Ibuprofen 200mg + Paracetamol 325mg", "Ibuprofen + Paracetamol", "Combiflam", "200mg/325mg", "Tablet", "Sanofi", "Analgesic & Antipyretic", False, 42.00),
    ("Aceclofenac 100mg + Paracetamol 325mg", "Aceclofenac + Paracetamol", "Zerodol-P", "100mg/325mg", "Tablet", "Ipca Labs", "Analgesic & Antipyretic", True, 68.00),
    ("Aceclofenac 100mg + Serratiopeptidase 15mg", "Aceclofenac + Serratiopeptidase", "Zerodol-SP", "100mg/15mg", "Tablet", "Ipca Labs", "Analgesic & Antipyretic", True, 115.00),
    ("Diclofenac Sodium 50mg", "Diclofenac Sodium", "Voveran 50", "50mg", "Tablet", "Novartis", "Analgesic & Antipyretic", True, 55.00),
    ("Diclofenac Topical Gel 30g", "Diclofenac Diethylamine", "Volini Gel", "1.16% w/w", "Ointment", "Sun Pharma", "Analgesic & Antipyretic", False, 135.00),
    ("Tramadol 50mg", "Tramadol HCl", "Tramazac 50", "50mg", "Capsule", "Zydus Cadila", "Analgesic & Antipyretic", True, 90.00),
    ("Mefenamic Acid 500mg", "Mefenamic Acid", "Meftal 500", "500mg", "Tablet", "Blue Cross", "Analgesic & Antipyretic", True, 48.00),
    ("Mefenamic Acid + Dicyclomine", "Mefenamic Acid + Dicyclomine", "Meftal-Spas", "250mg/10mg", "Tablet", "Blue Cross", "Analgesic & Antipyretic", True, 54.00),

    # Antibiotics & Antimicrobials
    ("Amoxicillin 500mg", "Amoxicillin", "Novamox 500", "500mg", "Capsule", "Cipla", "Antibiotic", True, 78.50),
    ("Amoxicillin 250mg", "Amoxicillin", "Mox 250", "250mg", "Capsule", "Ranbaxy", "Antibiotic", True, 45.00),
    ("Amoxicillin 500mg + Clavulanic Acid 125mg", "Amoxicillin + Clavulanic Acid", "Augmentin 625 Duo", "625mg", "Tablet", "GSK Consumer", "Antibiotic", True, 204.00),
    ("Amoxicillin 500mg + Clavulanate 125mg (Clavam)", "Amoxicillin + Clavulanic Acid", "Clavam 625", "625mg", "Tablet", "Alkem Labs", "Antibiotic", True, 198.00),
    ("Azithromycin 500mg", "Azithromycin", "Azithral 500", "500mg", "Tablet", "Alembic Pharma", "Antibiotic", True, 132.00),
    ("Azithromycin 250mg", "Azithromycin", "Azee 250", "250mg", "Tablet", "Cipla", "Antibiotic", True, 85.00),
    ("Azithromycin Liquid 200mg/5ml", "Azithromycin", "Azithral Liquid", "200mg/5ml", "Syrup", "Alembic Pharma", "Antibiotic", True, 120.00),
    ("Cefixime 200mg", "Cefixime", "Taxim-O 200", "200mg", "Tablet", "Alkem Labs", "Antibiotic", True, 175.00),
    ("Cefixime 100mg DT", "Cefixime", "Zifi 100 DT", "100mg", "Tablet", "FDC Ltd", "Antibiotic", True, 95.00),
    ("Ciprofloxacin 500mg", "Ciprofloxacin", "Ciplox 500", "500mg", "Tablet", "Cipla", "Antibiotic", True, 42.00),
    ("Ciprofloxacin Eye/Ear Drops", "Ciprofloxacin", "Ciplox Eye Drops", "0.3% w/v", "Drops", "Cipla", "Antibiotic", True, 22.50),
    ("Ofloxacin 200mg", "Ofloxacin", "Zenflox 200", "200mg", "Tablet", "Mankind Pharma", "Antibiotic", True, 65.00),
    ("Ofloxacin + Ornidazole", "Ofloxacin + Ornidazole", "O2 Tablet", "200mg/500mg", "Tablet", "Medley Pharma", "Antibiotic", True, 125.00),
    ("Doxycycline 100mg", "Doxycycline Hyclate", "Doxicip 100", "100mg", "Capsule", "Cipla", "Antibiotic", True, 80.00),
    ("Metronidazole 400mg", "Metronidazole", "Flagyl 400", "400mg", "Tablet", "Abbott", "Antibiotic", True, 24.50),
    ("Levofloxacin 500mg", "Levofloxacin", "Levomac 500", "500mg", "Tablet", "Macleods", "Antibiotic", True, 98.00),

    # Antihistamines & Allergy
    ("Cetirizine 10mg", "Cetirizine HCl", "Cetzine 10", "10mg", "Tablet", "Dr. Reddy's", "Antihistamine", False, 24.00),
    ("Cetirizine Syrup 5mg/5ml", "Cetirizine HCl", "Zyrtec Syrup", "5mg/5ml", "Syrup", "Dr. Reddy's", "Antihistamine", False, 42.00),
    ("Levocetirizine 5mg", "Levocetirizine", "Vozet 5", "5mg", "Tablet", "Glenmark", "Antihistamine", False, 56.00),
    ("Levocetirizine 5mg + Montelukast 10mg", "Levocetirizine + Montelukast", "Montair-LC", "5mg/10mg", "Tablet", "Cipla", "Antihistamine", True, 185.00),
    ("Levocetirizine + Montelukast (Telekast-L)", "Levocetirizine + Montelukast", "Telekast-L", "5mg/10mg", "Tablet", "Lupin", "Antihistamine", True, 178.00),
    ("Montelukast 10mg", "Montelukast", "Montair 10", "10mg", "Tablet", "Cipla", "Antihistamine", True, 140.00),
    ("Fexofenadine 120mg", "Fexofenadine HCl", "Allegra 120", "120mg", "Tablet", "Sanofi", "Antihistamine", False, 198.00),
    ("Fexofenadine 180mg", "Fexofenadine HCl", "Allegra 180", "180mg", "Tablet", "Sanofi", "Antihistamine", False, 245.00),
    ("Chlorpheniramine Maleate 4mg", "Chlorpheniramine", "Avil 25", "25mg", "Tablet", "Sanofi", "Antihistamine", False, 12.00),
    ("Loratadine 10mg", "Loratadine", "Claritin 10", "10mg", "Tablet", "Bayer", "Antihistamine", False, 88.00),
    ("Bilastine 20mg", "Bilastine", "Bilaxten 20", "20mg", "Tablet", "Dr. Reddy's", "Antihistamine", True, 160.00),

    # Cardiovascular & Antihypertensives
    ("Amlodipine 5mg", "Amlodipine Besylate", "Amlong 5", "5mg", "Tablet", "Micro Labs", "Cardiovascular", True, 34.00),
    ("Amlodipine 10mg", "Amlodipine Besylate", "Amlong 10", "10mg", "Tablet", "Micro Labs", "Cardiovascular", True, 58.00),
    ("Amlodipine 5mg + Atenolol 50mg", "Amlodipine + Atenolol", "Amlokind-AT", "5mg/50mg", "Tablet", "Mankind Pharma", "Cardiovascular", True, 45.00),
    ("Telmisartan 40mg", "Telmisartan", "Telma 40", "40mg", "Tablet", "Glenmark", "Cardiovascular", True, 118.00),
    ("Telmisartan 80mg", "Telmisartan", "Telma 80", "80mg", "Tablet", "Glenmark", "Cardiovascular", True, 190.00),
    ("Telmisartan 40mg + Hydrochlorothiazide 12.5mg", "Telmisartan + HCTZ", "Telma-H", "40mg/12.5mg", "Tablet", "Glenmark", "Cardiovascular", True, 142.00),
    ("Telmisartan 40mg + Amlodipine 5mg", "Telmisartan + Amlodipine", "Telma-AM", "40mg/5mg", "Tablet", "Glenmark", "Cardiovascular", True, 155.00),
    ("Losartan Potassium 50mg", "Losartan", "Repace 50", "50mg", "Tablet", "Sun Pharma", "Cardiovascular", True, 92.00),
    ("Atorvastatin 10mg", "Atorvastatin Calcium", "Atorva 10", "10mg", "Tablet", "Zydus Cadila", "Cardiovascular", True, 95.00),
    ("Atorvastatin 20mg", "Atorvastatin Calcium", "Atorva 20", "20mg", "Tablet", "Zydus Cadila", "Cardiovascular", True, 165.00),
    ("Rosuvastatin 10mg", "Rosuvastatin", "Rosuvas 10", "10mg", "Tablet", "Sun Pharma", "Cardiovascular", True, 180.00),
    ("Rosuvastatin 20mg", "Rosuvastatin", "Rosuvas 20", "20mg", "Tablet", "Sun Pharma", "Cardiovascular", True, 290.00),
    ("Clopidogrel 75mg", "Clopidogrel", "Clopilet 75", "75mg", "Tablet", "Sun Pharma", "Cardiovascular", True, 110.00),
    ("Aspirin 75mg Gastro-resistant", "Aspirin", "Ecosprin 75", "75mg", "Tablet", "USV Ltd", "Cardiovascular", False, 10.50),
    ("Aspirin 150mg Gastro-resistant", "Aspirin", "Ecosprin 150", "150mg", "Tablet", "USV Ltd", "Cardiovascular", False, 14.00),
    ("Metoprolol Succinate 25mg ER", "Metoprolol", "Metolar XR 25", "25mg", "Tablet", "Cipla", "Cardiovascular", True, 78.00),

    # Antidiabetics
    ("Metformin 500mg SR", "Metformin HCl", "Glycomet 500 SR", "500mg", "Tablet", "USV Ltd", "Antidiabetic", True, 32.00),
    ("Metformin 1000mg SR", "Metformin HCl", "Glycomet 1000 SR", "1000mg", "Tablet", "USV Ltd", "Antidiabetic", True, 60.00),
    ("Glimepiride 1mg", "Glimepiride", "Amaryl 1", "1mg", "Tablet", "Sanofi", "Antidiabetic", True, 85.00),
    ("Glimepiride 2mg", "Glimepiride", "Amaryl 2", "2mg", "Tablet", "Sanofi", "Antidiabetic", True, 142.00),
    ("Glimepiride 2mg + Metformin 500mg SR", "Glimepiride + Metformin", "Glycomet-GP 2", "2mg/500mg", "Tablet", "USV Ltd", "Antidiabetic", True, 112.00),
    ("Sitagliptin 100mg", "Sitagliptin", "Januvia 100", "100mg", "Tablet", "MSD Pharma", "Antidiabetic", True, 410.00),
    ("Sitagliptin 50mg + Metformin 500mg", "Sitagliptin + Metformin", "Janumet 50/500", "50mg/500mg", "Tablet", "MSD Pharma", "Antidiabetic", True, 360.00),
    ("Dapagliflozin 10mg", "Dapagliflozin", "Forxiga 10", "10mg", "Tablet", "AstraZeneca", "Antidiabetic", True, 520.00),
    ("Empagliflozin 10mg", "Empagliflozin", "Jardiance 10", "10mg", "Tablet", "Boehringer Ingelheim", "Antidiabetic", True, 545.00),
    ("Voglibose 0.2mg", "Voglibose", "Volibo 0.2", "0.2mg", "Tablet", "Sun Pharma", "Antidiabetic", True, 88.00),
    ("Voglibose 0.3mg", "Voglibose", "Volibo 0.3", "0.3mg", "Tablet", "Sun Pharma", "Antidiabetic", True, 120.00),
    ("Insulin Glargine 100IU/ml Cartridge", "Insulin Glargine", "Lantus SoloStar", "100IU/ml", "Injection", "Sanofi", "Antidiabetic", True, 680.00),

    # Gastrointestinal & Antacids
    ("Pantoprazole 40mg", "Pantoprazole Sodium", "Pan 40", "40mg", "Tablet", "Alkem Labs", "Gastrointestinal", False, 115.00),
    ("Pantoprazole 40mg + Domperidone 30mg SR", "Pantoprazole + Domperidone", "Pan-D", "40mg/30mg", "Capsule", "Alkem Labs", "Gastrointestinal", True, 195.00),
    ("Omeprazole 20mg", "Omeprazole", "Omez 20", "20mg", "Capsule", "Dr. Reddy's", "Gastrointestinal", False, 62.00),
    ("Omeprazole 20mg + Domperidone 10mg", "Omeprazole + Domperidone", "Omez-D", "20mg/10mg", "Capsule", "Dr. Reddy's", "Gastrointestinal", True, 145.00),
    ("Rabeprazole 20mg", "Rabeprazole Sodium", "Razo 20", "20mg", "Tablet", "Dr. Reddy's", "Gastrointestinal", False, 130.00),
    ("Rabeprazole 20mg + Domperidone 30mg SR", "Rabeprazole + Domperidone", "Razo-D", "20mg/30mg", "Capsule", "Dr. Reddy's", "Gastrointestinal", True, 210.00),
    ("Ondansetron 4mg MD", "Ondansetron", "Emeset 4 MD", "4mg", "Tablet", "Cipla", "Gastrointestinal", True, 45.00),
    ("Ondansetron Syrup 2mg/5ml", "Ondansetron", "Emeset Syrup", "2mg/5ml", "Syrup", "Cipla", "Gastrointestinal", True, 38.00),
    ("Sucralfate + Oxetacaine Suspension", "Sucralfate + Oxetacaine", "Sucrafil O Gel", "1000mg/20mg", "Syrup", "Fourrts India", "Gastrointestinal", True, 185.00),
    ("Antacid Liquid Mint 200ml", "Magnesium Hydroxide + Aluminium Hydroxide", "Digene Gel Mint", "200ml", "Syrup", "Abbott", "Gastrointestinal", False, 140.00),
    ("Loperamide 2mg", "Loperamide HCl", "Imodium 2", "2mg", "Capsule", "Johnson & Johnson", "Gastrointestinal", False, 28.00),
    ("Probiotics Multi-Strain Capsule", "Lactic Acid Bacillus + Probiotics", "Darolac", "1.25B CFU", "Capsule", "Aristo Pharma", "Gastrointestinal", False, 110.00),

    # Respiratory & Cough
    ("Salbutamol Inhaler 100mcg (200 MDI)", "Salbutamol", "Asthalin Inhaler", "100mcg", "Inhaler", "Cipla", "Respiratory", True, 165.00),
    ("Budesonide 200mcg Inhaler", "Budesonide", "Budecort 200", "200mcg", "Inhaler", "Cipla", "Respiratory", True, 340.00),
    ("Formoterol + Budesonide Inhaler", "Formoterol + Budesonide", "Foracort 200 Synchrobreathe", "6mcg/200mcg", "Inhaler", "Cipla", "Respiratory", True, 480.00),
    ("Ambroxol + Levosalbutamol + Guaifenesin", "Ambroxol + Levosalbutamol + Guaifenesin", "Ascoril LS Syrup", "100ml", "Syrup", "Glenmark", "Respiratory", False, 118.00),
    ("Dextromethorphan + Chlorpheniramine", "Dextromethorphan + CPM", "Ascoril D Plus", "100ml", "Syrup", "Glenmark", "Respiratory", False, 112.00),
    ("Benadryl Cough Formula Syrup 100ml", "Diphenhydramine + Ammonium Chloride", "Benadryl Cough Formula", "100ml", "Syrup", "Johnson & Johnson", "Respiratory", False, 125.00),
    ("Acetylcysteine 600mg Effervescent", "Acetylcysteine", "Mucosef 600", "600mg", "Tablet", "Mankind Pharma", "Respiratory", True, 280.00),

    # Dermatology & Topicals
    ("Clotrimazole Cream 1% 20g", "Clotrimazole", "Candid Cream", "1% w/w", "Ointment", "Glenmark", "Dermatology", False, 95.00),
    ("Clotrimazole Dusting Powder 100g", "Clotrimazole", "Candid Dusting Powder", "1% w/w", "Powder", "Glenmark", "Dermatology", False, 145.00),
    ("Mupirocin 2% Ointment 5g", "Mupirocin", "T-Bact 2% Ointment", "2% w/w", "Ointment", "GSK Consumer", "Dermatology", True, 135.00),
    ("Betamethasone Dipropionate 0.05%", "Betamethasone", "Betnovate-C", "20g", "Ointment", "GSK Consumer", "Dermatology", True, 62.00),
    ("Ketoconazole 2% Shampoo 100ml", "Ketoconazole", "Scalpe Pro Shampoo", "2% w/v", "Drops", "Glenmark", "Dermatology", False, 280.00),
    ("Permethrin 5% Lotion 60ml", "Permethrin", "Scaboma Lotion", "5% w/v", "Drops", "Glenmark", "Dermatology", True, 85.00),

    # Vitamins, Minerals & Supplements
    ("Vitamin D3 60000 IU Capsule", "Cholecalciferol", "Calcirol 60K", "60,000 IU", "Capsule", "Cadila Pharma", "Supplements & Vitamins", False, 140.00),
    ("Vitamin D3 Oral Drops 800 IU/ml", "Cholecalciferol", "D3 Must Drops", "800 IU/ml", "Drops", "Mankind Pharma", "Supplements & Vitamins", False, 95.00),
    ("Vitamin C 500mg Chewable", "Ascorbic Acid + Sodium Ascorbate", "Limcee 500", "500mg", "Tablet", "Abbott", "Supplements & Vitamins", False, 25.00),
    ("Multivitamin + Minerals + Zinc", "Multivitamin & Zinc", "Zincovit Tablet", "15 Tablets", "Tablet", "Apex Labs", "Supplements & Vitamins", False, 105.00),
    ("Zincovit Syrup 200ml", "Multivitamin & Zinc", "Zincovit Syrup", "200ml", "Syrup", "Apex Labs", "Supplements & Vitamins", False, 145.00),
    ("Vitamin B-Complex + B12", "B-Complex + Cyanocobalamin", "Becosules Capsule", "20 Capsules", "Capsule", "Pfizer", "Supplements & Vitamins", False, 48.00),
    ("Neurobion Forte Vitamin B12", "Vitamin B1, B6, B12", "Neurobion Forte", "30 Tablets", "Tablet", "Procter & Gamble", "Supplements & Vitamins", False, 38.00),
    ("Calcium 500mg + Vitamin D3", "Calcium Carbonate + Vit D3", "Shelcal 500", "500mg/250IU", "Tablet", "Torrent Pharma", "Supplements & Vitamins", False, 118.00),
    ("Iron + Folic Acid + Zinc", "Ferrous Ascorbate + Folic Acid", "Orofer-XT", "100mg/1.5mg", "Tablet", "Emcure Pharma", "Supplements & Vitamins", False, 185.00),
    ("Folic Acid 5mg", "Folic Acid", "Folvite 5mg", "5mg", "Tablet", "Pfizer", "Supplements & Vitamins", False, 75.00),

    # Neurological & Psychiatric
    ("Alprazolam 0.25mg", "Alprazolam", "Alprax 0.25", "0.25mg", "Tablet", "Torrent Pharma", "Neurological", True, 28.00),
    ("Alprazolam 0.5mg", "Alprazolam", "Alprax 0.5", "0.5mg", "Tablet", "Torrent Pharma", "Neurological", True, 45.00),
    ("Clonazepam 0.5mg", "Clonazepam", "ClonaFit 0.5", "0.5mg", "Tablet", "Mankind Pharma", "Neurological", True, 52.00),
    ("Sertraline 50mg", "Sertraline HCl", "Sertima 50", "50mg", "Tablet", "Intas Pharma", "Neurological", True, 125.00),
    ("Escitalopram 10mg", "Escitalopram Oxalate", "Nexito 10", "10mg", "Tablet", "Sun Pharma", "Neurological", True, 110.00),
    ("Gabapentin 300mg", "Gabapentin", "Gabapin 300", "300mg", "Capsule", "Intas Pharma", "Neurological", True, 195.00),
    ("Pregabalin 75mg", "Pregabalin", "Prebaxe 75", "75mg", "Capsule", "Sun Pharma", "Neurological", True, 160.00),
    ("Methylcobalamin 1500mcg", "Mecobalamin", "Nurokind-OD", "1500mcg", "Tablet", "Mankind Pharma", "Neurological", False, 98.00)
]

# ---------------------------------------------------------------------
# Seeder Logic
# ---------------------------------------------------------------------

def seed_core_catalog(session=None, drop_existing: bool = False):
    """
    Fast, essential catalog seeding routine (under 1 second).
    Seeds Pharmacies, Medicines, Users, Inventory across pharmacies,
    and minimal sample requests/watchlist/notifications.
    Does NOT seed the heavy 100k+ historical sales simulation.
    """
    random.seed(42)
    owns_session = False
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        pharmacy_count = session.query(Pharmacy).count()
        medicine_count = session.query(Medicine).count()

        if not drop_existing and pharmacy_count > 0 and medicine_count > 0:
            print(f"      [Skip] Core catalog already populated ({pharmacy_count} Pharmacies | {medicine_count} Medicines).")
            return

        print("[2/4] Seeding Pharmacies and Medicines catalog...")
        
        # 1. Pharmacies
        pharmacies = []
        for p in PHARMACIES_DATA:
            pharm = Pharmacy(
                name=p["name"],
                license_number=p["license"],
                address=p["address"],
                city=p["city"],
                pincode=p["pincode"],
                latitude=p["lat"],
                longitude=p["lon"],
                contact_phone=p["phone"],
                contact_email=p["email"],
                opening_time=p["open"],
                closing_time=p["close"],
                is_24_7=p["is_24_7"],
                is_active=True
            )
            pharmacies.append(pharm)
        session.add_all(pharmacies)
        session.flush()

        # 2. Medicines
        medicines = []
        for item in MEDICINES_DATA:
            name, gen, brand, dos, form, mfr, cat, rx, price = item
            med = Medicine(
                name=name,
                generic_name=gen,
                brand_name=brand,
                dosage=dos,
                dosage_form=form,
                manufacturer=mfr,
                category=cat,
                is_prescription_required=rx,
                unit_price=price
            )
            medicines.append(med)
        session.add_all(medicines)
        session.flush()

        print(f"      Seeded {len(pharmacies)} Pharmacies and {len(medicines)} Medicines.")

        # 3. Users
        print("[3/4] Seeding System Users & Customer Accounts...")
        users = [
            User(name="Rahul Sharma", email="rahul.sharma@example.com", phone="+91-9876543210", password_hash="hashed_pw_user_1", role="customer", latitude=17.4370, longitude=78.3950),
            User(name="Priya Patel", email="priya.patel@example.com", phone="+91-9876543211", password_hash="hashed_pw_user_2", role="customer", latitude=17.4420, longitude=78.3800),
            User(name="Vikram Reddy", email="vikram.reddy@example.com", phone="+91-9876543212", password_hash="hashed_pw_user_3", role="customer", latitude=17.4100, longitude=78.4300),
            User(name="Dr. Ananya Rao", email="ananya.rao@example.com", phone="+91-9876543213", password_hash="hashed_pw_user_4", role="customer", latitude=17.4600, longitude=78.3600),
            User(name="MediCare Admin", email="admin@medicareplus.com", phone="+91-9876543214", password_hash="hashed_pw_admin_1", role="pharmacy_admin", latitude=17.4325, longitude=78.4071),
            User(name="HealthPoint Admin", email="admin@healthpoint.in", phone="+91-9876543215", password_hash="hashed_pw_admin_2", role="pharmacy_admin", latitude=17.4483, longitude=78.3742),
            User(name="System Administrator", email="admin@meditracex.io", phone="+91-9876543219", password_hash="hashed_pw_sys_1", role="system_admin", latitude=17.4399, longitude=78.3820)
        ]
        session.add_all(users)
        session.flush()

        # 4. Inventory Across All Pharmacies
        print("[4/4] Generating Pharmacy Inventory (In Stock, Low Stock, Out of Stock)...")
        inventory_records = []
        batch_counter = 1000

        for pharm in pharmacies:
            for med in medicines:
                batch_counter += 1
                batch_no = f"BT{date.today().year}-{batch_counter:05d}"
                exp_days = random.randint(180, 720) # 6 to 24 months in future
                expiry_dt = date.today() + timedelta(days=exp_days)
                
                # Distribution of availability:
                # 65% In Stock, 22% Low Stock, 13% Out of Stock
                roll = random.random()
                safety_threshold = 15

                if roll < 0.13:
                    qty = 0
                    status = "Out of Stock"
                elif roll < 0.35:
                    qty = random.randint(1, safety_threshold - 1)
                    status = "Low Stock"
                else:
                    if "Paracetamol" in med.name or "Pantoprazole" in med.name or "Cetirizine" in med.name:
                        qty = random.randint(45, 220)
                    else:
                        qty = random.randint(16, 120)
                    status = "In Stock"

                inv = Inventory(
                    pharmacy_id=pharm.id,
                    medicine_id=med.id,
                    stock_quantity=qty,
                    safety_stock_threshold=safety_threshold,
                    reorder_quantity=50 if qty < safety_threshold else 0,
                    batch_number=batch_no,
                    expiry_date=expiry_dt,
                    stock_status=status,
                    last_restocked_at=datetime.now() - timedelta(days=random.randint(1, 45))
                )
                inventory_records.append(inv)

        session.add_all(inventory_records)
        session.flush()
        print(f"      Seeded {len(inventory_records)} Inventory item records across all pharmacies.")

        # Sample Requests, Watchlist, Notifications
        sample_requests = [
            MedicineRequest(user_id=1, pharmacy_id=1, medicine_id=2, quantity_requested=2, status="FULFILLED", notes="Urgent for fever treatment"),
            MedicineRequest(user_id=2, pharmacy_id=2, medicine_id=18, quantity_requested=1, status="PENDING", notes="Prescription uploaded for Azithral 500"),
            MedicineRequest(user_id=3, pharmacy_id=3, medicine_id=82, quantity_requested=1, status="ACCEPTED", notes="Asthalin Inhaler needed"),
        ]
        session.add_all(sample_requests)

        sample_watchlist = [
            Watchlist(user_id=1, medicine_id=82, target_pharmacy_id=1, notify_on_restock=True, is_active=True),
            Watchlist(user_id=2, medicine_id=18, target_pharmacy_id=2, notify_on_restock=True, is_active=True),
        ]
        session.add_all(sample_watchlist)

        sample_notifs = [
            Notification(user_id=1, title="Stock Restocked Alert", message="Paracetamol 650mg is now back in stock at MediCare Plus!", type="RESTOCK_ALERT", is_read=False),
            Notification(user_id=5, title="Low Stock Warning", message="Inventory for Dolo 650 reached 8 units (below threshold 15). Reorder recommended.", type="LOW_STOCK_WARNING", is_read=False),
        ]
        session.add_all(sample_notifs)

        if owns_session:
            session.commit()
            print("\n[SUCCESS] Essential catalog and inventory seeded successfully!")

    except Exception as e:
        if owns_session:
            session.rollback()
        print(f"[ERROR] Essential catalog seeding failed: {e}")
        raise
    finally:
        if owns_session:
            session.close()

def seed_historical_sales(session=None, days_history: int = 240, batch_size: int = 5000):
    """
    Heavy historical sales simulation (Past 240 days / ~8 months).
    Generates 100,800+ granular time series records for ML training/simulation.
    Run separately on demand via CLI; never blocks normal web service startup.
    """
    random.seed(42)
    owns_session = False
    if session is None:
        session = SessionLocal()
        owns_session = True

    try:
        print(f"\n[Optional] Generating {days_history} Days of Granular Daily Sales History for ML simulation...")
        medicines = session.query(Medicine).all()
        pharmacies = session.query(Pharmacy).all()

        if not medicines or not pharmacies:
            print("      [Warning] No medicines or pharmacies found. Seeding core catalog first...")
            seed_core_catalog(session)
            medicines = session.query(Medicine).all()
            pharmacies = session.query(Pharmacy).all()

        start_date = date.today() - timedelta(days=days_history)
        sales_records = []

        popular_med_ids = [m.id for m in medicines[:35]]
        key_pharm_ids = [p.id for p in pharmacies[:12]]
        med_dict = {m.id: m for m in medicines}
        
        total_sales_count = 0

        for day_idx in range(days_history):
            cur_date = start_date + timedelta(days=day_idx)
            day_name = cur_date.strftime("%A")
            is_weekend_val = cur_date.weekday() >= 5
            
            dow_factor = 1.25 if cur_date.weekday() in (0, 5, 6) else 0.95
            season_factor = 1.0 + 0.3 * math.sin(2 * math.pi * day_idx / 180.0)

            for pharm_id in key_pharm_ids:
                for med_id in popular_med_ids:
                    med = med_dict[med_id]
                    
                    if "Paracetamol 650mg" in med.name or "Dolo 650" in med.name:
                        base = 45.0
                    elif "Paracetamol" in med.name or "Pantoprazole" in med.name:
                        base = 28.0
                    elif "Azithromycin" in med.name or "Augmentin" in med.name:
                        base = 16.0
                    elif "Cetirizine" in med.name or "Montair" in med.name:
                        base = 20.0
                    else:
                        base = 10.0

                    mean_demand = base * dow_factor * season_factor
                    noise = random.gauss(0, max(2.0, mean_demand * 0.15))
                    qty_sold = max(0, int(round(mean_demand + noise)))

                    if qty_sold > 0:
                        total_amt = round(float(med.unit_price) * qty_sold, 2)
                        sale = SalesHistory(
                            pharmacy_id=pharm_id,
                            medicine_id=med_id,
                            sale_date=cur_date,
                            quantity_sold=qty_sold,
                            unit_price=med.unit_price,
                            total_amount=total_amt,
                            day_of_week=day_name,
                            is_weekend=is_weekend_val
                        )
                        sales_records.append(sale)
                        total_sales_count += 1

                        if len(sales_records) >= batch_size:
                            session.add_all(sales_records)
                            session.flush()
                            sales_records.clear()

        if sales_records:
            session.add_all(sales_records)
            session.flush()
            sales_records.clear()

        if owns_session:
            session.commit()
        print(f"      Seeded {total_sales_count} Historical Daily Sales Transactions.")

    except Exception as e:
        if owns_session:
            session.rollback()
        print(f"[ERROR] Historical sales generation failed: {e}")
        raise
    finally:
        if owns_session:
            session.close()

def seed_database(include_sales_history: bool = False, drop_existing: bool = False, days_history: int = 240):
    """Main database seeding routine."""
    create_tables(drop_existing=drop_existing)

    session = SessionLocal()
    try:
        seed_core_catalog(session, drop_existing=drop_existing)
        if include_sales_history:
            seed_historical_sales(session, days_history=days_history)
        session.commit()
        print("\n[SUCCESS] MediTraceX Database seeding completed successfully!")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Database seeding failed: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MediTraceX Database Seeder")
    parser.add_argument("--full-history", "--with-sales", action="store_true", dest="full_history", help="Generate full 240-day historical sales records for ML training")
    parser.add_argument("--reset", "--drop-existing", action="store_true", dest="reset", help="Drop and recreate existing tables before seeding")
    parser.add_argument("--days", type=int, default=240, help="Days of historical sales simulation (default: 240)")
    args = parser.parse_args()

    seed_database(include_sales_history=args.full_history, drop_existing=args.reset, days_history=args.days)
