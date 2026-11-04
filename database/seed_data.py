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
    # --- 1. ANDHRA PRADESH ---
    # Vijayawada
    {"name": "Krishna Valley Chemists - Benz Circle", "license": "AP-VJA-2023-1001", "address": "Benz Circle Main Rd, Near Jyothi Mahal", "city": "Vijayawada", "pincode": "520010", "lat": 16.5012, "lon": 80.6485, "phone": "+91-8662481001", "email": "benzcircle@krishnamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Amaravati Care Pharmacy - Governorpet", "license": "AP-VJA-2023-1002", "address": "Prakasam Rd, Governorpet", "city": "Vijayawada", "pincode": "520002", "lat": 16.5144, "lon": 80.6288, "phone": "+91-8662481002", "email": "governorpet@amaravaticare.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "CityMed Chemists - MG Road", "license": "AP-VJA-2023-1003", "address": "Bandar Road, Opposite PVP Square", "city": "Vijayawada", "pincode": "520010", "lat": 16.5055, "lon": 80.6420, "phone": "+91-8662481003", "email": "mgroad@citymed.in", "open": time(7, 30), "close": time(23, 30), "is_24_7": False},
    {"name": "Sanjeevani Drug House - One Town", "license": "AP-VJA-2023-1004", "address": "Brahmin St, Near Kanaka Durga Temple", "city": "Vijayawada", "pincode": "520001", "lat": 16.5188, "lon": 80.6122, "phone": "+91-8662481004", "email": "onetown@sanjeevaniap.in", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "Apollo Care Center - Gunadala", "license": "AP-VJA-2023-1005", "address": "Eluru Rd, Near ESI Hospital", "city": "Vijayawada", "pincode": "520004", "lat": 16.5290, "lon": 80.6650, "phone": "+91-8662481005", "email": "gunadala@apollocare.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},

    # Visakhapatnam
    {"name": "Vizag MedPlus Chemist - Dwaraka Nagar", "license": "AP-VSKP-2023-1011", "address": "Diamond Park Rd, 3rd Lane, Dwaraka Nagar", "city": "Visakhapatnam", "pincode": "530016", "lat": 17.7285, "lon": 83.3088, "phone": "+91-8912751011", "email": "dwarakanagar@vizagmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Coastal Health Pharmacy - MVP Colony", "license": "AP-VSKP-2023-1012", "address": "Sector 4, MVP Double Road", "city": "Visakhapatnam", "pincode": "530017", "lat": 17.7410, "lon": 83.3365, "phone": "+91-8912751012", "email": "mvpcolony@coastalhealth.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Steel City Pharmacy - Gajuwaka", "license": "AP-VSKP-2023-1013", "address": "High School Rd, Old Gajuwaka", "city": "Visakhapatnam", "pincode": "530026", "lat": 17.6912, "lon": 83.2145, "phone": "+91-8912751013", "email": "gajuwaka@steelcitymed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Dolphin Chemists - Siripuram", "license": "AP-VSKP-2023-1014", "address": "VIP Road, Siripuram Junction", "city": "Visakhapatnam", "pincode": "530003", "lat": 17.7215, "lon": 83.3198, "phone": "+91-8912751014", "email": "siripuram@dolphinmed.in", "open": time(7, 30), "close": time(23, 0), "is_24_7": False},
    {"name": "Port City Pharma - Jagadamba Junction", "license": "AP-VSKP-2023-1015", "address": "Cinema Road, Jagadamba Centre", "city": "Visakhapatnam", "pincode": "530020", "lat": 17.7120, "lon": 83.3012, "phone": "+91-8912751015", "email": "jagadamba@portcitypharma.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},

    # Guntur & Tirupati
    {"name": "Chaitanya Medicals - Arundelpet", "license": "AP-GNT-2023-1021", "address": "Main Road, 6/2 Arundelpet", "city": "Guntur", "pincode": "522002", "lat": 16.3045, "lon": 80.4420, "phone": "+91-8632231021", "email": "arundelpet@chaitanyamed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Guntur 24/7 Drug Store - Brodipet", "license": "AP-GNT-2023-1022", "address": "4th Line, Brodipet", "city": "Guntur", "pincode": "522002", "lat": 16.3112, "lon": 80.4365, "phone": "+91-8632231022", "email": "brodipet@gunturmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Balaji Health Pharmacy - KT Road", "license": "AP-TPT-2023-1023", "address": "Opposite RTC Bus Stand, KT Road", "city": "Tirupati", "pincode": "517501", "lat": 13.6325, "lon": 79.4215, "phone": "+91-8772241023", "email": "ktroad@balajipharma.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Seven Hills Chemists - Alipiri", "license": "AP-TPT-2023-1024", "address": "Bypass Road, Near Alipiri Gate", "city": "Tirupati", "pincode": "517507", "lat": 13.6510, "lon": 79.4055, "phone": "+91-8772241024", "email": "alipiri@sevenhillsmed.in", "open": time(6, 0), "close": time(23, 0), "is_24_7": False},

    # --- 2. TELANGANA ---
    # Hyderabad & Secunderabad
    {"name": "MediCare Plus Pharmacy - Jubilee Hills", "license": "TS-HYD-2023-1001", "address": "Road No. 36, Jubilee Hills", "city": "Hyderabad", "pincode": "500033", "lat": 17.4325, "lon": 78.4071, "phone": "+91-9848011221", "email": "jubilee@medicareplus.com", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "HealthPoint Super Pharmacy - Madhapur", "license": "TS-HYD-2023-1002", "address": "Near Cyber Towers, Hitec City Main Rd", "city": "Hyderabad", "pincode": "500081", "lat": 17.4483, "lon": 78.3742, "phone": "+91-9848011222", "email": "hitec@healthpoint.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "CityMed 24/7 Chemists - Gachibowli", "license": "TS-HYD-2023-1003", "address": "Plot 14, Financial District, Gachibowli", "city": "Hyderabad", "pincode": "500032", "lat": 17.4401, "lon": 78.3489, "phone": "+91-9848011223", "email": "gachibowli@citymed.com", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Care & Cure Pharmacy - Banjara Hills", "license": "TS-HYD-2023-1004", "address": "Road No. 12, Banjara Hills", "city": "Hyderabad", "pincode": "500034", "lat": 17.4156, "lon": 78.4350, "phone": "+91-9848011224", "email": "banjara@carecure.org", "open": time(7, 30), "close": time(22, 30), "is_24_7": False},
    {"name": "Apollo Care Center - Kondapur", "license": "TS-HYD-2023-1005", "address": "Botanical Garden Rd, Kondapur", "city": "Hyderabad", "pincode": "500084", "lat": 17.4612, "lon": 78.3587, "phone": "+91-9848011225", "email": "kondapur@apollocare.in", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "Lifeline Drug House - Ameerpet", "license": "TS-HYD-2023-1006", "address": "Near Metro Station Pillar 1042, Ameerpet", "city": "Hyderabad", "pincode": "500016", "lat": 17.4375, "lon": 78.4483, "phone": "+91-9848011226", "email": "ameerpet@lifelinedrugs.com", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Noble Chemists - Kukatpally", "license": "TS-HYD-2023-1008", "address": "KPHB Phase 1, Kukatpally", "city": "Hyderabad", "pincode": "500072", "lat": 17.4934, "lon": 78.3989, "phone": "+91-9848011228", "email": "kphb@noblechemists.com", "open": time(7, 0), "close": time(23, 30), "is_24_7": False},
    {"name": "Fortis MediStore - Secunderabad", "license": "TS-HYD-2023-1009", "address": "RP Road, Near Clock Tower", "city": "Secunderabad", "pincode": "500003", "lat": 17.4399, "lon": 78.4983, "phone": "+91-9848011229", "email": "rp_road@fortismed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Wellness Forever - Manikonda", "license": "TS-HYD-2023-1010", "address": "Puppalaguda Main Road, Manikonda", "city": "Hyderabad", "pincode": "500089", "lat": 17.4012, "lon": 78.3842, "phone": "+91-9848011230", "email": "manikonda@wellnessforever.com", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Sanjeevani Medicals - Miyapur", "license": "TS-HYD-2023-1011", "address": "Allwyn X Road, Miyapur", "city": "Hyderabad", "pincode": "500049", "lat": 17.4968, "lon": 78.3614, "phone": "+91-9848011231", "email": "miyapur@sanjeevani.com", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "Aster Pharmacy - LB Nagar", "license": "TS-HYD-2023-1013", "address": "Sagar Ring Road, LB Nagar", "city": "Hyderabad", "pincode": "500074", "lat": 17.3457, "lon": 78.5522, "phone": "+91-9848011233", "email": "lbnagar@asterpharma.com", "open": time(8, 30), "close": time(22, 30), "is_24_7": False},
    {"name": "Relief Pharmacy - Tolichowki", "license": "TS-HYD-2023-1014", "address": "Paramount Colony, Tolichowki", "city": "Hyderabad", "pincode": "500008", "lat": 17.3982, "lon": 78.4112, "phone": "+91-9848011234", "email": "tolichowki@reliefpharma.com", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Kakatiya Health Store - Hanamkonda", "license": "TS-WGL-2023-1025", "address": "Nayeemnagar, Hanamkonda Main Road", "city": "Warangal", "pincode": "506001", "lat": 17.9942, "lon": 79.5788, "phone": "+91-8702441025", "email": "hanamkonda@kakatiyamed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Warangal City Chemists - Kazipet", "license": "TS-WGL-2023-1026", "address": "Station Road, Kazipet", "city": "Warangal", "pincode": "506003", "lat": 17.9785, "lon": 79.5120, "phone": "+91-8702441026", "email": "kazipet@warangalmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},

    # --- 3. KARNATAKA ---
    # Bengaluru
    {"name": "Bengaluru MedTrust - Indiranagar", "license": "KA-BLR-2023-1031", "address": "100 Feet Rd, 12th Main, Indiranagar", "city": "Bengaluru", "pincode": "560038", "lat": 12.9719, "lon": 77.6412, "phone": "+91-8041511031", "email": "indiranagar@medtrust.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Silicon Care Pharmacy - Koramangala", "license": "KA-BLR-2023-1032", "address": "80 Feet Rd, 4th Block, Koramangala", "city": "Bengaluru", "pincode": "560034", "lat": 12.9352, "lon": 77.6245, "phone": "+91-8041511032", "email": "koramangala@siliconcare.in", "open": time(7, 30), "close": time(23, 30), "is_24_7": False},
    {"name": "Whitefield 24/7 Drug Store", "license": "KA-BLR-2023-1033", "address": "ITPL Main Rd, Opp Forum Shantiniketan", "city": "Bengaluru", "pincode": "560066", "lat": 12.9868, "lon": 77.7382, "phone": "+91-8041511033", "email": "whitefield@bengalurumed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Garden City Chemists - Jayanagar", "license": "KA-BLR-2023-1034", "address": "11th Main, 4th Block, Jayanagar", "city": "Bengaluru", "pincode": "560011", "lat": 12.9250, "lon": 77.5838, "phone": "+91-8041511034", "email": "jayanagar@gardencitymed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Heritage Pharmacy - Malleshwaram", "license": "KA-BLR-2023-1035", "address": "Sampige Rd, Near 8th Cross, Malleshwaram", "city": "Bengaluru", "pincode": "560003", "lat": 13.0035, "lon": 77.5702, "phone": "+91-8041511035", "email": "malleshwaram@heritagmed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "HSR Super Chemist - Sector 2", "license": "KA-BLR-2023-1036", "address": "27th Main Rd, HSR Layout Sector 2", "city": "Bengaluru", "pincode": "560102", "lat": 12.9115, "lon": 77.6520, "phone": "+91-8041511036", "email": "hsr@bengalurumed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Electronic City MediStore", "license": "KA-BLR-2023-1037", "address": "Neeladri Rd, Electronic City Phase 1", "city": "Bengaluru", "pincode": "560100", "lat": 12.8398, "lon": 77.6775, "phone": "+91-8041511037", "email": "ecity@medtrust.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "North Bengaluru Chemists - Yelahanka", "license": "KA-BLR-2023-1038", "address": "BB Road, Yelahanka New Town", "city": "Bengaluru", "pincode": "560064", "lat": 13.1008, "lon": 77.5963, "phone": "+91-8041511038", "email": "yelahanka@gardencitymed.in", "open": time(8, 30), "close": time(22, 30), "is_24_7": False},

    # Mysuru, Mangaluru, Hubballi
    {"name": "Royal City Pharma - Saraswathipuram", "license": "KA-MYS-2023-1041", "address": "Kantharaj Urs Rd, Saraswathipuram", "city": "Mysuru", "pincode": "570009", "lat": 12.3025, "lon": 76.6340, "phone": "+91-8212451041", "email": "saraswathi@royalcitymed.in", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "Chamundi 24/7 Chemists - Gokulam", "license": "KA-MYS-2023-1042", "address": "3rd Stage, Contour Road, Gokulam", "city": "Mysuru", "pincode": "570002", "lat": 12.3298, "lon": 76.6212, "phone": "+91-8212451042", "email": "gokulam@chamundimed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Coastal Drug Store - Hampankatta", "license": "KA-MNG-2023-1043", "address": "KS Rao Road, Hampankatta", "city": "Mangaluru", "pincode": "575001", "lat": 12.8702, "lon": 74.8435, "phone": "+91-8242441043", "email": "hampankatta@coastalmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Hubballi Central Pharma - Vidyanagar", "license": "KA-HUB-2023-1044", "address": "PB Road, Vidyanagar", "city": "Hubballi", "pincode": "580021", "lat": 15.3645, "lon": 75.1245, "phone": "+91-8362371044", "email": "vidyanagar@hubballimed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},

    # --- 4. TAMIL NADU ---
    # Chennai
    {"name": "Madras Health Hub - T Nagar", "license": "TN-CHE-2023-1051", "address": "Pondy Bazaar, Sir Thyagaraya Rd, T Nagar", "city": "Chennai", "pincode": "600017", "lat": 13.0418, "lon": 80.2341, "phone": "+91-4428151051", "email": "tnagar@madrashealth.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Tower City Pharmacy - Anna Nagar", "license": "TN-CHE-2023-1052", "address": "2nd Avenue, Near Anna Nagar Roundtana", "city": "Chennai", "pincode": "600040", "lat": 13.0850, "lon": 80.2105, "phone": "+91-4428151052", "email": "annanagar@towercitymed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "South Coast Chemists - Adyar", "license": "TN-CHE-2023-1053", "address": "LB Road, Near Adyar Signal", "city": "Chennai", "pincode": "600020", "lat": 13.0062, "lon": 80.2568, "phone": "+91-4428151053", "email": "adyar@southcoastmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Velachery Express Pharma", "license": "TN-CHE-2023-1054", "address": "Velachery Bypass Rd, Opp Phoenix Marketcity", "city": "Chennai", "pincode": "600042", "lat": 12.9812, "lon": 80.2185, "phone": "+91-4428151054", "email": "velachery@madrashealth.in", "open": time(7, 30), "close": time(23, 0), "is_24_7": False},
    {"name": "Mylapore Traditional Chemists", "license": "TN-CHE-2023-1055", "address": "Luz Church Rd, Near Kapaleeshwarar Temple", "city": "Chennai", "pincode": "600004", "lat": 13.0335, "lon": 80.2675, "phone": "+91-4428151055", "email": "mylapore@mylaporemed.in", "open": time(7, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Kilpauk Medical Store - EVR Periyar Salai", "license": "TN-CHE-2023-1056", "address": "Poonamallee High Rd, Kilpauk", "city": "Chennai", "pincode": "600010", "lat": 13.0825, "lon": 80.2412, "phone": "+91-4428151056", "email": "kilpauk@madrashealth.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Tambaram Super Pharmacy", "license": "TN-CHE-2023-1057", "address": "GST Road, Tambaram West", "city": "Chennai", "pincode": "600045", "lat": 12.9255, "lon": 80.1175, "phone": "+91-4428151057", "email": "tambaram@southcoastmed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},

    # Coimbatore, Madurai, Salem
    {"name": "Kovai Care Chemists - RS Puram", "license": "TN-CBE-2023-1061", "address": "DB Road, RS Puram", "city": "Coimbatore", "pincode": "641002", "lat": 11.0085, "lon": 76.9512, "phone": "+91-4222471061", "email": "rspuram@kovaicare.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Gandhipuram 24/7 Pharma", "license": "TN-CBE-2023-1062", "address": "Cross Cut Rd, Gandhipuram", "city": "Coimbatore", "pincode": "641012", "lat": 11.0182, "lon": 76.9685, "phone": "+91-4222471062", "email": "gandhipuram@kovaicare.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Temple City Pharma - KK Nagar", "license": "TN-MDU-2023-1063", "address": "80 Feet Rd, KK Nagar", "city": "Madurai", "pincode": "625020", "lat": 9.9288, "lon": 78.1485, "phone": "+91-4522531063", "email": "kknagar@templecitymed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Salem Steel Drug House - Fairlands", "license": "TN-SLM-2023-1064", "address": "Brindavan Rd, Fairlands", "city": "Salem", "pincode": "636016", "lat": 11.6745, "lon": 78.1412, "phone": "+91-4272441064", "email": "fairlands@salemmed.in", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},

    # --- 5. MAHARASHTRA ---
    # Mumbai, Navi Mumbai, Thane
    {"name": "Bombay Central Pharmacy - Andheri West", "license": "MH-MUM-2023-1071", "address": "Link Road, Near Infinity Mall, Andheri West", "city": "Mumbai", "pincode": "400053", "lat": 19.1365, "lon": 72.8315, "phone": "+91-2226341071", "email": "andheri@bombaypharma.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Bandra Coast Chemists - Bandra West", "license": "MH-MUM-2023-1072", "address": "Hill Road, Near Mehboob Studio, Bandra", "city": "Mumbai", "pincode": "400050", "lat": 19.0545, "lon": 72.8290, "phone": "+91-2226341072", "email": "bandra@bombaypharma.in", "open": time(8, 0), "close": time(23, 30), "is_24_7": False},
    {"name": "Dadar Central Drug House - Dadar TT", "license": "MH-MUM-2023-1073", "address": "Dr. Ambedkar Rd, Dadar TT Circle", "city": "Mumbai", "pincode": "400014", "lat": 19.0182, "lon": 72.8435, "phone": "+91-2226341073", "email": "dadar@mumbaimed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Borivali Care Pharmacy - Borivali West", "license": "MH-MUM-2023-1074", "address": "SV Road, Near Borivali Station", "city": "Mumbai", "pincode": "400092", "lat": 19.2312, "lon": 72.8568, "phone": "+91-2226341074", "email": "borivali@mumbaimed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Powai Lake Chemists - Hiranandani", "license": "MH-MUM-2023-1075", "address": "Central Ave, Hiranandani Gardens, Powai", "city": "Mumbai", "pincode": "400076", "lat": 19.1198, "lon": 72.9055, "phone": "+91-2226341075", "email": "powai@bombaypharma.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Colaba Heritage Pharma - South Mumbai", "license": "MH-MUM-2023-1076", "address": "Colaba Causeway, Near Gateway of India", "city": "Mumbai", "pincode": "400005", "lat": 18.9185, "lon": 72.8298, "phone": "+91-2226341076", "email": "colaba@mumbaimed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Vashi 24/7 Medicals - Sector 17", "license": "MH-NVM-2023-1077", "address": "Sector 17, Opp Vashi Bus Depot", "city": "Navi Mumbai", "pincode": "400703", "lat": 19.0768, "lon": 72.9985, "phone": "+91-2227891077", "email": "vashi@navimumbaimed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Thane City Chemists - Ghodbunder Road", "license": "MH-THN-2023-1078", "address": "Ghodbunder Rd, Near Majiwada Junction", "city": "Thane", "pincode": "400601", "lat": 19.2185, "lon": 72.9782, "phone": "+91-2225431078", "email": "thane@thanemed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},

    # Pune, Nagpur, Nashik
    {"name": "Punya City Pharma - Kothrud", "license": "MH-PUN-2023-1081", "address": "Paud Road, Near Vanaz Metro, Kothrud", "city": "Pune", "pincode": "411038", "lat": 18.5075, "lon": 73.8078, "phone": "+91-2025441081", "email": "kothrud@punemed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Viman Nagar 24/7 Chemists", "license": "MH-PUN-2023-1082", "address": "Symbiosis Rd, Viman Nagar", "city": "Pune", "pincode": "411014", "lat": 18.5678, "lon": 73.9145, "phone": "+91-2025441082", "email": "vimannagar@punemed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Hinjewadi Tech Pharma - Phase 1", "license": "MH-PUN-2023-1083", "address": "Rajiv Gandhi Infotech Park, Hinjewadi", "city": "Pune", "pincode": "411057", "lat": 18.5912, "lon": 73.7388, "phone": "+91-2025441083", "email": "hinjewadi@techcare.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Shivaji Nagar Central Drug Store", "license": "MH-PUN-2023-1084", "address": "FC Road, Shivaji Nagar", "city": "Pune", "pincode": "411005", "lat": 18.5312, "lon": 73.8445, "phone": "+91-2025441084", "email": "shivajinagar@punemed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Nagpur Orange City Pharma - Dharampeth", "license": "MH-NGP-2023-1085", "address": "West High Court Rd, Dharampeth", "city": "Nagpur", "pincode": "440010", "lat": 21.1445, "lon": 79.0612, "phone": "+91-7122551085", "email": "dharampeth@nagpurmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Ramdaspeth Health Chemist", "license": "MH-NGP-2023-1086", "address": "Central Bazar Rd, Ramdaspeth", "city": "Nagpur", "pincode": "440010", "lat": 21.1350, "lon": 79.0745, "phone": "+91-7122551086", "email": "ramdaspeth@nagpurmed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Godavari Care Chemists - College Road", "license": "MH-NSK-2023-1087", "address": "College Road, Near Thatte Nagar", "city": "Nashik", "pincode": "422005", "lat": 20.0065, "lon": 73.7650, "phone": "+91-2532311087", "email": "collegerd@nashikmed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},

    # --- 6. DELHI NCR ---
    # New Delhi
    {"name": "Capital Health Chemists - Connaught Place", "license": "DL-NDLS-2023-1091", "address": "Block E, Inner Circle, Connaught Place", "city": "New Delhi", "pincode": "110001", "lat": 28.6328, "lon": 77.2195, "phone": "+91-1123411091", "email": "cp@capitalhealth.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "South Ext 24/7 Pharmacy - Part 1", "license": "DL-NDLS-2023-1092", "address": "Ring Road, South Extension Part 1", "city": "New Delhi", "pincode": "110049", "lat": 28.5725, "lon": 77.2210, "phone": "+91-1123411092", "email": "southext@capitalhealth.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Lajpat Nagar Central Drug Store", "license": "DL-NDLS-2023-1093", "address": "Central Market, Lajpat Nagar II", "city": "New Delhi", "pincode": "110024", "lat": 28.5695, "lon": 77.2415, "phone": "+91-1123411093", "email": "lajpat@delhimed.in", "open": time(8, 30), "close": time(23, 0), "is_24_7": False},
    {"name": "Dwarka Subcity Pharma - Sector 12", "license": "DL-NDLS-2023-1094", "address": "Sector 12 City Centre, Dwarka", "city": "New Delhi", "pincode": "110078", "lat": 28.5925, "lon": 77.0425, "phone": "+91-1123411094", "email": "dwarka@capitalhealth.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "North Delhi Chemists - Rohini Sector 9", "license": "DL-NDLS-2023-1095", "address": "DC Chowk, Sector 9, Rohini", "city": "New Delhi", "pincode": "110085", "lat": 28.7115, "lon": 77.1215, "phone": "+91-1123411095", "email": "rohini@delhimed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Karol Bagh Medicals - Arya Samaj Road", "license": "DL-NDLS-2023-1096", "address": "Arya Samaj Rd, Karol Bagh", "city": "New Delhi", "pincode": "110005", "lat": 28.6515, "lon": 77.1912, "phone": "+91-1123411096", "email": "karolbagh@delhimed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},

    # Gurgaon / Gurugram, Noida, Ghaziabad
    {"name": "Cyber City 24/7 Chemists - DLF Phase 2", "license": "HR-GGN-2023-1101", "address": "Cyber Hub, DLF Cyber City, Sector 24", "city": "Gurgaon", "pincode": "122002", "lat": 28.4950, "lon": 77.0895, "phone": "+91-1244101101", "email": "cybercity@gurgaonmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Golf Course Road Pharma - Sector 54", "license": "HR-GGN-2023-1102", "address": "Suncity, Golf Course Road, Sector 54", "city": "Gurgaon", "pincode": "122011", "lat": 28.4412, "lon": 77.1085, "phone": "+91-1244101102", "email": "golfcourse@gurgaonmed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Noida City Centre Pharma - Sector 18", "license": "UP-NOI-2023-1103", "address": "Atta Market, Sector 18", "city": "Noida", "pincode": "201301", "lat": 28.5705, "lon": 77.3245, "phone": "+91-1204201103", "email": "sector18@noidamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Electronic City Chemists - Noida Sector 62", "license": "UP-NOI-2023-1104", "address": "C-Block, Institutional Area, Sector 62", "city": "Noida", "pincode": "201309", "lat": 28.6255, "lon": 77.3688, "phone": "+91-1204201104", "email": "sector62@noidamed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Indirapuram 24/7 Medicals", "license": "UP-GZB-2023-1105", "address": "Kala Patthar Rd, Vaibhav Khand, Indirapuram", "city": "Ghaziabad", "pincode": "201014", "lat": 28.6385, "lon": 77.3712, "phone": "+91-1204251105", "email": "indirapuram@ghaziabadmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},

    # --- 7. WEST BENGAL ---
    # Kolkata & Siliguri
    {"name": "Calcutta Medical Hub - Park Street", "license": "WB-KOL-2023-1111", "address": "Park Street, Near Camac Street Crossing", "city": "Kolkata", "pincode": "700016", "lat": 22.5512, "lon": 88.3535, "phone": "+91-3322291111", "email": "parkstreet@calcuttamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Salt Lake IT Pharma - Sector V", "license": "WB-KOL-2023-1112", "address": "College More, Sector V, Salt Lake", "city": "Kolkata", "pincode": "700091", "lat": 22.5765, "lon": 88.4345, "phone": "+91-3322291112", "email": "sector5@saltlakemed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "New Town Eco Chemists - Action Area 1", "license": "WB-KOL-2023-1113", "address": "Major Arterial Rd, Action Area 1, New Town", "city": "Kolkata", "pincode": "700156", "lat": 22.5898, "lon": 88.4625, "phone": "+91-3322291113", "email": "newtown@calcuttamed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Gariahat South Chemists - Gariahat Road", "license": "WB-KOL-2023-1114", "address": "Gariahat Crossing, Ballygunge", "city": "Kolkata", "pincode": "700019", "lat": 22.5195, "lon": 88.3685, "phone": "+91-3322291114", "email": "gariahat@calcuttamed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Howrah Central Drug Store - Mandirtala", "license": "WB-KOL-2023-1115", "address": "Kona Expressway, Mandirtala", "city": "Kolkata", "pincode": "711102", "lat": 22.5625, "lon": 88.3215, "phone": "+91-3322291115", "email": "howrah@calcuttamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Behala Care Pharmacy - Diamond Harbour Rd", "license": "WB-KOL-2023-1116", "address": "DH Road, Behala Chowrasta", "city": "Kolkata", "pincode": "700034", "lat": 22.4985, "lon": 88.3145, "phone": "+91-3322291116", "email": "behala@calcuttamed.in", "open": time(8, 0), "close": time(22, 0), "is_24_7": False},
    {"name": "North Bengal Chemists - Sevoke Road", "license": "WB-SLG-2023-1117", "address": "Sevoke Rd, 2nd Mile, Near Vega Circle", "city": "Siliguri", "pincode": "734001", "lat": 26.7315, "lon": 88.4312, "phone": "+91-3532541117", "email": "sevokerd@siligurimed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},

    # --- 8. GUJARAT ---
    # Ahmedabad, Surat, Vadodara, Rajkot
    {"name": "Ahmedabad Health Trust - Navrangpura", "license": "GJ-AHD-2023-1121", "address": "CG Road, Near Municipal Market, Navrangpura", "city": "Ahmedabad", "pincode": "380009", "lat": 23.0365, "lon": 72.5612, "phone": "+91-7926441121", "email": "navrangpura@ahdhealth.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "SG Highway 24/7 Pharma - Bodakdev", "license": "GJ-AHD-2023-1122", "address": "SG Highway, Opp Iscon Mega Mall", "city": "Ahmedabad", "pincode": "380054", "lat": 23.0298, "lon": 72.5085, "phone": "+91-7926441122", "email": "sghighway@ahdhealth.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Maninagar Central Drug Store", "license": "GJ-AHD-2023-1123", "address": "Rambaug Rd, Maninagar", "city": "Ahmedabad", "pincode": "380008", "lat": 22.9985, "lon": 72.6045, "phone": "+91-7926441123", "email": "maninagar@ahdhealth.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Satellite Care Pharmacy - Shivranjani", "license": "GJ-AHD-2023-1124", "address": "132 Ft Ring Rd, Shivranjani Cross Roads", "city": "Ahmedabad", "pincode": "380015", "lat": 23.0185, "lon": 72.5295, "phone": "+91-7926441124", "email": "satellite@ahdhealth.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Diamond City Chemists - Athwa Lines", "license": "GJ-SRT-2023-1125", "address": "Ghod Dod Rd, Athwa", "city": "Surat", "pincode": "395007", "lat": 21.1715, "lon": 72.8012, "phone": "+91-2612451125", "email": "athwalines@suratmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Adajan 24/7 Pharma - LP Savani Rd", "license": "GJ-SRT-2023-1126", "address": "LP Savani Rd, Adajan", "city": "Surat", "pincode": "395009", "lat": 21.1985, "lon": 72.7895, "phone": "+91-2612451126", "email": "adajan@suratmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Sayaji Health Store - Alkapuri", "license": "GJ-BDQ-2023-1127", "address": "RC Dutt Rd, Alkapuri", "city": "Vadodara", "pincode": "390007", "lat": 22.3125, "lon": 73.1785, "phone": "+91-2652331127", "email": "alkapuri@sayajimed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Saurashtra Medicals - Kalawad Road", "license": "GJ-RJT-2023-1128", "address": "Kalawad Rd, Near Kotecha Chowk", "city": "Rajkot", "pincode": "360005", "lat": 22.2855, "lon": 70.7745, "phone": "+91-2812471128", "email": "kalawad@saurashtramed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},

    # --- 9. RAJASTHAN ---
    # Jaipur, Jodhpur, Udaipur
    {"name": "Pink City Care Pharma - C-Scheme", "license": "RJ-JPR-2023-1131", "address": "MI Road, Near Panch Batti, C-Scheme", "city": "Jaipur", "pincode": "302001", "lat": 26.9155, "lon": 75.8012, "phone": "+91-1412371131", "email": "cscheme@pinkcitymed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Malviya Nagar 24/7 Medicals - Calgiri Marg", "license": "RJ-JPR-2023-1132", "address": "Calgiri Marg, Malviya Nagar", "city": "Jaipur", "pincode": "302017", "lat": 26.8545, "lon": 75.8195, "phone": "+91-1412371132", "email": "malviyanagar@pinkcitymed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Vaishali Care Chemists - National Handloom", "license": "RJ-JPR-2023-1133", "address": "Amrapali Marg, Vaishali Nagar", "city": "Jaipur", "pincode": "302021", "lat": 26.9015, "lon": 75.7412, "phone": "+91-1412371133", "email": "vaishali@jaipurmed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Sun City Pharmacy - Shastri Nagar", "license": "RJ-JDH-2023-1134", "address": "Residency Rd, Shastri Nagar", "city": "Jodhpur", "pincode": "342003", "lat": 26.2715, "lon": 73.0185, "phone": "+91-2912641134", "email": "shastrinagar@jodhpurmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Lake City Chemists - Panchwati", "license": "RJ-UDR-2023-1135", "address": "Saheli Marg, Panchwati", "city": "Udaipur", "pincode": "313001", "lat": 24.5985, "lon": 73.6895, "phone": "+91-2942421135", "email": "panchwati@udaipurmed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},

    # --- 10. KERALA ---
    # Kochi, Thiruvananthapuram, Kozhikode
    {"name": "Cochin Health Hub - MG Road", "license": "KL-COK-2023-1141", "address": "MG Road, Near Shenoys Junction, Ernakulam", "city": "Kochi", "pincode": "682016", "lat": 9.9715, "lon": 76.2812, "phone": "+91-4842381141", "email": "mgroad@cochinhealth.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Edappally 24/7 Chemists - Toll Junction", "license": "KL-COK-2023-1142", "address": "NH 66, Near LuLu Mall, Edappally", "city": "Kochi", "pincode": "682024", "lat": 10.0245, "lon": 76.3085, "phone": "+91-4842381142", "email": "edappally@cochinhealth.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Kakkanad Info Pharma - Seaport-Airport Rd", "license": "KL-COK-2023-1143", "address": "Infopark Expressway, Kakkanad", "city": "Kochi", "pincode": "682030", "lat": 10.0125, "lon": 76.3455, "phone": "+91-4842381143", "email": "kakkanad@kochimed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Travancore Care Pharma - Pattom", "license": "KL-TVM-2023-1144", "address": "Medical College Rd, Pattom", "city": "Thiruvananthapuram", "pincode": "695004", "lat": 8.5285, "lon": 76.9412, "phone": "+91-4712441144", "email": "pattom@travancoremed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Malabar Coast Drug Store - Mavoor Road", "license": "KL-CCJ-2023-1145", "address": "Mavoor Rd, Near Calicut Medical College", "city": "Kozhikode", "pincode": "673004", "lat": 11.2612, "lon": 75.7945, "phone": "+91-4952721145", "email": "mavoorrd@malabarmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},

    # --- 11. ODISHA ---
    # Bhubaneswar & Cuttack
    {"name": "Kalinga Health Store - Saheed Nagar", "license": "OD-BBI-2023-1151", "address": "Janpath Road, Saheed Nagar", "city": "Bhubaneswar", "pincode": "751007", "lat": 20.2885, "lon": 85.8445, "phone": "+91-6742541151", "email": "saheednagar@kalingamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Patia Infocity Pharma - KIIT Square", "license": "OD-BBI-2023-1152", "address": "Nandan Kanan Rd, Patia", "city": "Bhubaneswar", "pincode": "751024", "lat": 20.3545, "lon": 85.8195, "phone": "+91-6742541152", "email": "patia@kalingamed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Silver City Chemists - Badambadi", "license": "OD-CTC-2023-1153", "address": "Ring Road, Badambadi Junction", "city": "Cuttack", "pincode": "753012", "lat": 20.4512, "lon": 85.8745, "phone": "+91-6712321153", "email": "badambadi@cuttackmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},

    # --- 12. UTTAR PRADESH ---
    # Lucknow, Kanpur, Varanasi, Agra
    {"name": "Awadh Care Chemists - Hazratganj", "license": "UP-LKO-2023-1161", "address": "MG Marg, Hazratganj Market", "city": "Lucknow", "pincode": "226001", "lat": 26.8485, "lon": 80.9412, "phone": "+91-5222281161", "email": "hazratganj@awadhmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Gomti Nagar 24/7 Pharma - Patrakarpuram", "license": "UP-LKO-2023-1162", "address": "Vikas Khand, Gomti Nagar", "city": "Lucknow", "pincode": "226010", "lat": 26.8595, "lon": 80.9985, "phone": "+91-5222281162", "email": "gomtinagar@awadhmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Alambagh City Medicals", "license": "UP-LKO-2023-1163", "address": "Kanpur Rd, Alambagh Chauraha", "city": "Lucknow", "pincode": "226005", "lat": 26.8125, "lon": 80.9015, "phone": "+91-5222281163", "email": "alambagh@lucknowmed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Kanpur Central Drug Store - Civil Lines", "license": "UP-KNP-2023-1164", "address": "Mall Road, Civil Lines", "city": "Kanpur", "pincode": "208001", "lat": 26.4685, "lon": 80.3412, "phone": "+91-5122301164", "email": "civillines@kanpurmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Kashi Vishwanath Pharma - Sigra", "license": "UP-VNS-2023-1165", "address": "Sigra-Mahmoorganj Rd, Sigra", "city": "Varanasi", "pincode": "221010", "lat": 25.3195, "lon": 82.9812, "phone": "+91-5422221165", "email": "sigra@kashimed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Taj City Chemists - Sanjay Place", "license": "UP-AGR-2023-1166", "address": "Commercial Complex, Sanjay Place", "city": "Agra", "pincode": "282002", "lat": 27.2015, "lon": 78.0045, "phone": "+91-5622521166", "email": "sanjayplace@agramed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},

    # --- 13. MADHYA PRADESH ---
    # Indore, Bhopal, Gwalior
    {"name": "Malwa Health Hub - Vijay Nagar", "license": "MP-IDR-2023-1171", "address": "AB Road, Vijay Nagar Square", "city": "Indore", "pincode": "452010", "lat": 22.7545, "lon": 75.8912, "phone": "+91-7312571171", "email": "vijaynagar@malwamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Palasia 24/7 Pharma - Old Palasia", "license": "MP-IDR-2023-1172", "address": "Manorama Ganj, Palasia", "city": "Indore", "pincode": "452001", "lat": 22.7215, "lon": 75.8825, "phone": "+91-7312571172", "email": "palasia@malwamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Bhopal Lake Care Pharma - MP Nagar", "license": "MP-BPL-2023-1173", "address": "Zone II, MP Nagar", "city": "Bhopal", "pincode": "462011", "lat": 23.2325, "lon": 77.4312, "phone": "+91-7552551173", "email": "mpnagar@bhopalmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Arera Colony Chemists - E-3", "license": "MP-BPL-2023-1174", "address": "Main Market, E-3 Arera Colony", "city": "Bhopal", "pincode": "462016", "lat": 23.2085, "lon": 77.4245, "phone": "+91-7552551174", "email": "arera@bhopalmed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},
    {"name": "Gwalior Fort City Medicals - City Centre", "license": "MP-GWL-2023-1175", "address": "Lalitpur Colony, City Centre", "city": "Gwalior", "pincode": "474011", "lat": 26.2085, "lon": 78.1895, "phone": "+91-7512441175", "email": "citycentre@gwaliormed.in", "open": time(8, 0), "close": time(22, 30), "is_24_7": False},

    # --- 14. PUNJAB & CHANDIGARH ---
    # Chandigarh, Ludhiana, Amritsar
    {"name": "City Beautiful Pharma - Sector 17", "license": "CH-CHD-2023-1181", "address": "Bank Square, Sector 17B", "city": "Chandigarh", "pincode": "160017", "lat": 30.7412, "lon": 76.7785, "phone": "+91-1722701181", "email": "sector17@chandigarhmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Sector 35 Care Chemists - Sector 35C", "license": "CH-CHD-2023-1182", "address": "Inner Market, Sector 35C", "city": "Chandigarh", "pincode": "160035", "lat": 30.7225, "lon": 76.7625, "phone": "+91-1722701182", "email": "sector35@chandigarhmed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Ludhiana Grand Pharma - Model Town", "license": "PB-LDH-2023-1183", "address": "Tuition Market Rd, Model Town", "city": "Ludhiana", "pincode": "141002", "lat": 30.8915, "lon": 75.8345, "phone": "+91-1612401183", "email": "modeltown@ludhianamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Amritsar Golden City Pharma - Mall Road", "license": "PB-ASR-2023-1184", "address": "Lawrence Rd Crossing, Mall Road", "city": "Amritsar", "pincode": "143001", "lat": 31.6395, "lon": 74.8712, "phone": "+91-1832561184", "email": "mallroad@amritsarmed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},

    # --- 15. BIHAR ---
    # Patna & Gaya
    {"name": "Pataliputra Care Pharma - Boring Road", "license": "BR-PAT-2023-1191", "address": "Boring Road Chauraha, Opposite Alankar Place", "city": "Patna", "pincode": "800001", "lat": 25.6145, "lon": 85.1215, "phone": "+91-6122531191", "email": "boringroad@patnamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Kankarbagh 24/7 Medicals - Colony More", "license": "BR-PAT-2023-1192", "address": "Main Rd, Near Doctor's Colony, Kankarbagh", "city": "Patna", "pincode": "800020", "lat": 25.5945, "lon": 85.1545, "phone": "+91-6122531192", "email": "kankarbagh@patnamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
    {"name": "Bailey Road Super Chemists - Raja Bazar", "license": "BR-PAT-2023-1193", "address": "Bailey Rd, Near IGIMS, Raja Bazar", "city": "Patna", "pincode": "800014", "lat": 25.6125, "lon": 85.0845, "phone": "+91-6122531193", "email": "rajabazar@patnamed.in", "open": time(8, 0), "close": time(23, 0), "is_24_7": False},
    {"name": "Fraser Road Central Drug Store", "license": "BR-PAT-2023-1194", "address": "Dak Bungalow Crossing, Fraser Road", "city": "Patna", "pincode": "800001", "lat": 25.6075, "lon": 85.1375, "phone": "+91-6122531194", "email": "fraserroad@patnamed.in", "open": time(7, 30), "close": time(22, 30), "is_24_7": False},
    {"name": "Bodhgaya Care Pharma - Rampur", "license": "BR-GAY-2023-1195", "address": "Station Rd, Near Gandhi Maidan, Rampur", "city": "Gaya", "pincode": "823001", "lat": 24.7955, "lon": 85.0012, "phone": "+91-6312221195", "email": "rampur@gayamed.in", "open": time(0, 0), "close": time(23, 59), "is_24_7": True},
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
