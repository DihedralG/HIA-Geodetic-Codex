%pip install cartopy
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os



# Monte Carlo simulated sites (random scatter around the globe for demonstration)

np.random.seed(42)

monte_carlo_longitudes = np.random.uniform(-180, 180, 400)

monte_carlo_latitudes = np.random.uniform(-60, 60, 400)


# Create output directory
output_dir = "frames"
os.makedirs(output_dir, exist_ok=True)

# Generate 18 frames (20° per step)
for i in range(18):
    fig = plt.figure(figsize=(8, 8))
    ax = plt.axes(projection=ccrs.Orthographic(central_longitude=i*20, central_latitude=10))
    ax.set_global()
    ax.coastlines()
    ax.stock_img()
    ax.gridlines()

# Rotation loop for longitude sweep
longitudes = np.linspace(-180, 180, 36)  # 18 frames (~20° steps)

for i, lon in enumerate(longitudes):
    fig = plt.figure(figsize=(8, 8))
    ax = plt.axes(projection=ccrs.Orthographic(central_longitude=lon, central_latitude=0))
    ax.set_global()
    ax.coastlines()
    ax.stock_img()
    ax.gridlines(draw_labels=False, linewidth=0.5, linestyle='--')
    ax.scatter(monte_carlo_longitudes, monte_carlo_latitudes,
               color='gray', s=10, alpha=0.5, transform=ccrs.PlateCarree())

    # Optional: Add a corner glyph
    ax.text(-170, -80, 'ChiR CG21', fontsize=9, transform=ccrs.PlateCarree(), color='black')



# Initialize figure with orthographic (globe-like) projection

fig = plt.figure(figsize=(12, 12))

ax = plt.axes(projection=ccrs.Orthographic(central_longitude=30, central_latitude=20))

ax.set_global()

ax.coastlines()

ax.stock_img()

ax.gridlines(draw_labels=True)



# Monte Carlo simulated sites

ax.scatter(monte_carlo_longitudes, monte_carlo_latitudes, transform=ccrs.PlateCarree(),

           color='gray', s=10, alpha=0.5, label='Monte Carlo Sites')



# Updated nodes

nodes = {

    "Northern Magnetic Pole (current GNP)": (-72.66, 90),

    "Undisclosed Canadian Location (CO)": (-72.66, 61),

    "Undisclosed, Greenland (GO)": (-72.3, 76.4),

    "Meadow House Observatory (MHO), USA": (-72.66, 44.5),

    "Ciudad Perdida (CPO), Colombia": (-73.55, 11.2),

    "Citadelle Laferrière (CLO), Haiti": (-72.8, 18.5),

    "Sayacmarca, Peru (SO)": (-72.5, -13.2),

    "Monte Verde Observatory (MVO), Chile": (-72.67, -44.5),

    "Monte Verde II (MV ~14,500 BP)": (-73.2, -41.5),

    "Meadow House Inverse Fulcrum (MVO)": (-72.66, -44.3),

    "Great Serpent Effigy Mound" : (-83.43, 39.03),

    "Louisiana Mounds Dataset" : (-91.08, 32.32),

    "Teotihuacan Pyramid, Mexico" : (-98.5, 19.3),

    "Drake's Passage (DP)": (-70, -60),

    "Vinson Massif (VM)": (-78.31, -85.37),

    "Newgrange (Brú na Bóinne), Ireland" : (-6.26, 53.7),

    "Stonehenge, UK" : (1.83, 51.18),

    "Giza Plateau, Egypt (GZP)": (31.13, 29.98),

    "Göbekli Tepe, Türkiye (GTO)" : (38.92, 37.22),

    "Adams Calendar Observatory (ACO), South Africa": (30, -25),

    "Juukan Gorge, Australia": (120.88, -21.5554),

    "Murujuga, Burrup Peninsula, Australia (MJO)": (116.85,-20.53),

    "Gunung Padang, Karyamukti, Indonesia": (107.1, -6.90),

    "Đảo An Bang, Vietnam (Star Fort w/ Obelisk)": (112.98, 07.92),

    "Laschamp Excursursion": (2.5, 45),

    "Mono Lake Excursursion": (-119, 38),

    "North Atlantic Geomarker": (-40, 45),

    "South Atlantic Geomarker": (-20, -40),

    "Southern Magnetic Pole (current GSP)": (-72.66, -90)


}


pyramids = {
    # Africa – Egypt
    "Great Pyramid of Giza (Khufu), Egypt": (31.13417, 29.97917),  #  [oai_citation:0‡en.wikipedia.org](https://en.wikipedia.org/wiki/Great_Pyramid_of_Giza?utm_source=chatgpt.com)
    "Pyramid of Khafre, Egypt": (31.13428, 29.97670),  # approximation
    "Pyramid of Menkaure, Egypt": (31.13130, 29.97228),  # approximation

    # Africa – Sudan
    "Nubian Pyramids at Meroë, Sudan": (31.36611, 16.93333),  # general location

    # Americas – Mexico
    "Pyramid of the Sun, Teotihuacan, Mexico": (-98.84394, 19.69972),  #
    "Pyramid of the Moon, Teotihuacan, Mexico": (-98.84394, 19.69972),  # approximate same site
    "Temple of Kukulcán (Chichen Itza), Mexico": (-88.56778, 20.68111),  # typical coord

    # Asia – Indonesia
    "Borobudur, Indonesia": (110.20380, -7.60736),  #

    # Asia – Cambodia
    "Ko Ker Prang, Cambodia": (104.29139, 13.73778),  # approximate

    # Europe
    "Couhard Pyramid, France": (0.50194, 48.19583),  # near Le Man
    "Pyramid of Cestius, Rome, Italy": (12.47333, 41.88417),  # typical

    # Europe – UK
    "Stockport Pyramid, UK": (-2.1575, 53.4081),  # approximation

    # Americas – Belize
    "Caracol, Belize": (-88.47556, 16.75333),
}


# Updated forts

forts = {

"Forte Acqui Alessandria, Italy " :	(8.60,44.89)	,
"Fort Adams Newport, Rhode Island, USA " :	(-71.34,41.48)	,
"Aguada Fort Goa, India " :	(73.77,15.49)	,
"Citadelle d'Ajaccio Ajaccio, Corsica, France " :	(8.74,41.92)	,
"Alba Carolina Citadel Alba Iulia, Romania " :	(23.57,46.07)	,
"Fort Albert Alderney, Channel Islands, UK " :	(-2.18,49.73)	,
"Fort Alcatraz San Francisco Bay, California, USA " :	(-122.42,37.83)	,
"Rocco Aldobrandesca Monte Argentario, Italy " :	(11.12,42.43)	,
"Citadel of Alessandria Alessandria, Italy " :	(8.61,44.92)	,
"Fortress of Almeida Almeida, Portugal " :	(-8.22,39.40)	,
"Fort Amsterdam Willemstad, Curaçao " :	(-68.93,12.10)	,
"Fort Anahuac Anahuac, Texas, USA " :	(-94.68,29.76)	,
"Fort Anne Annapolis Royal, Nova Scotia, Canada " :	(-65.52,44.74)	,
"Fort Arnold West Point, New York, USA " :	(-73.95,41.39)	,
"Fort au Fer Champlain, New York, USA " :	(-73.35,44.94)	,
"Presidio La Bahía Goliad, Texas, USA " :	(-97.38,28.65)	,
"Fort Barrancas Pensacola, Florida, USA " :	(-87.30,30.35)	,
"Fortezza da Basso Florence, Italy " :	(11.25,43.78)	,
"Citadelle Bayonne Bayonne, France " :	(-1.48,43.49)	,
"Fort Beauséjour Aulac, New Brunswick, Canada " :	(-64.29,45.86)	,
"Fort Belgica Banda Neira, Moluccas, Indonesia " :	(129.90,-4.53)	,
"Fort Bellegarde Le Perthus, France " :	(2.86,42.46)	,
"Forte di Belvedere Florence, Italy " :	(11.25,43.76)	,
"Berwick Castle Berwick-Upon-Tweed, UK " :	(-2.00,55.77)	,
"Bihu Loukon Maklang, Manipur, India " :	(93.82,24.80)	,
"Citadelle de Bitche Bitche, Moselle, France " :	(7.43,49.05)	,
"Citadelle de Blaye Blaye, France " :	(-0.67,45.13)	,
"Fort Bregille Besançon, Franche-Compte, France " :	(6.04,47.23)	,
"Bohus Fortress Kungalv, Sweden " :	(12.00,57.86)	,
"Borj Nord Fez, Morocco " :	(-4.98,34.07)	,
"Forte Bormida Alessandria, Italy " :	(8.65,44.91)	,
"Fortress Bourtange Bourtange, Netherlands " :	(7.19,53.01)	,
"Fortress Boyen Gizycko, Poland " :	(21.75,54.03)	,
"Brest Fortress Brest, Belarus " :	(23.66,52.08)	,
"Fort Camden Crosshaven, County Cork, Ireland " :	(-8.28,51.81)	,
"Fort Carlisle Whitegate, County Cork, Ireland " :	(-8.26,51.82)	,
"Fort Caroline Jacksonville, Florida, USA " :	(-81.50,30.39)	,
"Fort Carré Antibes, France " :	(7.13,43.59)	,
"Fort Carroll; Baltimore, Maryland, USA " :	(-76.52,39.22)	,
"Cidadela de Cascais Cascais, Portugal " :	(-9.42,38.69)	,
"Fort Caswell Oak Island, North Carolina, USA " :	(-78.02,33.89)	,
"Castillo de Santa Catalina Cádiz, Spain " :	(-6.31,36.53)	,
"Fort Chaberton Montgenèvre Pass, Italy " :	(12.57,41.87)	,
"Fort Chambly Chambly, Quebec, Canada " :	(-73.28,45.45)	,
"Fort de la Charente Rochefort, France " :	(-0.96,45.94)	,
"Charles Fort Kinsale Harbor, Ireland " :	(-8.50,51.70)	,
"Fort Charlotte Lerwick, Shetland Islands, Scotland " :	(-1.14,60.16)	,
"Fort Chaudanne Besançon, Franche-Compte, France " :	(6.02,47.23)	,
"Cheremshan Fortress Cheremshan, Samarskaya Oblast, Russia " :	(50.47,53.42)	,
"Fort Christiansvaern Christiansted, St. Croix, US Virgin Islands " :	(-64.70,17.75)	,
"Fort Clinch Amelia Island, Florida, USA " :	(-81.45,30.70)	,
"Fort Clinton West Point, New York, USA " :	(-73.95,41.39)	,
"Fort Clonque Alderney, Channel Islands, UK " :	(-2.23,49.71)	,
"Real Fuerte de la Concepción Aldea del Obispo, Spain " :	(-6.80,40.70)	,
"Forte Conde de Lippe Elvas, Portugal " :	(-7.16,38.89)	,
"Fort Constitution New Castle, New Hampshire, USA " :	(-70.71,43.07)	,
"Fort Corblets Alderney, Channel Islands, UK " :	(-2.17,49.73)	,
"The Fortifications of Cork Cork, Ireland, UK " :	(-7.31,53.78)	,
"Fort Cornwallis Georgetown, Malaysia " :	(100.34,5.42)	,
"Fort at Coteau du Lac Coteau du Lac, Québec, Canada " :	(-74.18,45.30)	,
"Cove Fort Cobh, County Cork, Ireland " :	(-8.28,51.85)	,
"Fort Crown Point Crown Point, New York, USA " :	(-73.44,43.95)	,
"Fort Cumberland Portsmouth, UK " :	(-1.03,50.79)	,
"Fort Curtis Helena-West Helena, Arkansas, USA " :	(-90.59,34.53)	,
"Daugavgriva Fortress Riga, Latvia " :	(24.04,57.05)	,
"Daugavpils Fortress Daugavpils, Latvia " :	(26.50,55.89)	,
"Fort Dauphin Briançon, France " :	(6.66,44.90)	,
"Deal Castle Deal, Kent, UK " :	(1.40,51.22)	,
"Fort de Chartres Prairie du Rocher, Illinois, USA " :	(-90.16,38.08)	,
"Fort Delaware Pea Patch Island, Delaware, USA " :	(-75.59,39.58)	,
"Fort Delgrès Basse-Tere, Guadeloupe (France) " :	(-61.72,15.99)	,
"Fort de Roovere Halsteren, Netherlands " :	(4.30,51.53)	,
"Fort Desaix Fort-de-France, Martinique (France) " :	(-61.06,14.62)	,
"Fort Desaix Mundolsheim, France " :	(7.73,48.63)	,
"Fort Diamant Rémire-Montjoly, French Guiana " :	(-52.25,4.87)	,
"Dien Hai Citadel Da Nang, Vietnam " :	(108.22,16.08)	,
"Citadel Diest Diest, Belgium " :	(5.05,50.98)	,
"Diu Fort Diu, India " :	(71.00,20.71)	,
"Fortress Dömitz Dömitz, Germany " :	(11.27,53.14)	,
"Fort Dorchester Summerville, South Carolina, USA " :	(-80.11,32.93)	,
"Fort Doyle Alderney, Channel Islands, UK " :	(-2.21,49.72)	,
"Dresden Germany (Quondam Starfort) " :	(13.74,51.05)	,
"Drop Redoubt Dover, Kent, UK " :	(1.31,51.12)	,
"Drottningskärs Kastell Drottningskär, Sweden " :	(15.56,56.11)	,
"Fort Duquesne Pittsburgh, Pennsylvania, USA " :	(-80.01,40.44)	,
"Fort Edward Windsor, Nova Scotia, Canada " :	(-64.14,45.00)	,
"Festung Ehrenbreitstein Ehrenbreitstein, Germany " :	(7.62,50.36)	,
"Castle Elfsborg Gotherburg, Sweden " :	(11.88,57.67)	,
"Elizabeth Fort Cork, Ireland " :	(-8.48,51.89)	,
"Elvas Elvas, Portugal " :	(-7.16,38.88)	,
"Fort Erie Ontario, Canada " :	(-78.94,42.91)	,
"Castle Essex Alderney, Channel Islands, UK " :	(0.48,51.77)	,
"Estremoz Castle Estremoz, Portugal " :	(-7.59,38.84)	,
"Eternal Golden Castle Anping, Tainan, Taiwan " :	(120.16,22.99)	,
"Fort Château à l'Étoc Alderney, Channel Islands, UK " :	(-2.18,49.73)	,
"Forte Ferrovia Alessandria, Italy " :	(8.61,44.91)	,
"Forte Filippo Monte Argenatario, Italy " :	(11.21,42.40)	,
"Fort Fisher Petersburg, Virginia, USA " :	(-77.45,37.18)	,
"Fort Frederick Big Pool, Maryland, USA " :	(-78.01,39.61)	,
"Fort Frederick Kingston, Ontario, Canada " :	(-76.47,44.23)	,
"Fort Frederick Plaisance, Newfoundland and Labrador, Canada " :	(-53.96,47.25)	,
"Fredricksberg Fortress Bergen, Norway " :	(5.31,60.40)	,
"Fredrikstad Fortress Fredrikstad, Norway " :	(10.93,59.22)	,
"Fort Frontenac Kingston, Ontario, Canada " :	(-76.48,44.23)	,
"Fort Gadsden Wewahitchka, Florida, USA " :	(-85.01,29.94)	,
"Fort Gaines Mobile, Alabama, USA " :	(-88.08,30.25)	,
"Galle Fort Galle, Sri Lanka " :	(80.22,6.03)	,
"Geneva Switzerland (Quondam Starfort) " :	(6.14,46.20)	,
"Fort George Hillhead, Scotland " :	(-4.29,55.87)	,
"Fort George Niagra-on-the-Lake, Canada " :	(-79.06,43.25)	,
"Fort Glanville Adelaide, Australia " :	(138.48,-34.85)	,
"Castle of Good Hope Cape Town, South Africa " :	(18.43,-33.93)	,
"Fort Gorgast Gorgast, Germany " :	(14.55,52.56)	,
"Fort Gorges Hog Island Ledge, Portland, Maine, USA " :	(-70.22,43.66)	,
"Fort Goryokaku Hakodate, Japan " :	(140.76,41.80)	,
"Forte de Graca Elvas, Portugal " :	(-7.16,38.89)	,
"Fort Griswold Groton, Connecticut, USA " :	(-72.08,41.35)	,
"Fort Grosnez Alderney, Channel Islands, UK " :	(-2.20,49.72)	,
"Fuerte de Guadalupe Puebla, Mexico " :	(-98.29,19.08)	,
"Fortaleza de Hacho Ceuta, Spain " :	(-5.29,35.90)	,
"Halifax Citadel Halifax, Nova Scotia, Canada " :	(-63.58,44.65)	,
"Hame Castle Hameenlinna, Finland " :	(24.46,61.00)	,
"Handyside Fort Kohat, Pakistan " :	(71.44,33.59)	,
"Fort Henricus Steenbergen, Netherlands " :	(4.31,51.60)	,
"Fort Henry Kingston, Ontario, Canada " :	(-76.46,44.23)	,
"Fort Holmes Mackinac Island, Michigan, USA " :	(-84.62,45.86)	,
"Fort Hommeaux Florains Alderney, Channel Islands, UK " :	(-2.20,49.72)	,
"Fort Houmet Herbé Alderney, Channel Islands, UK " :	(-2.16,49.73)	,
"Hulst Hulst, Netherlands " :	(4.05,51.28)	,
"Fort de Huy Huy, Belgium " :	(5.24,50.52)	,
"Chateau d'If Marseilles, France " :	(5.33,43.28)	,
"Fort et des Îles Grand Île, Chausey, France " :	(-1.82,48.87)	,
"Fort Independence Boston, Massachusetts, USA " :	(-71.01,42.34)	,
"Fort Infernet Briançon, France " :	(6.69,44.89)	,
"Ivangorod Fortress Ivangorod, Leningrad Oblast, Russia " :	(28.21,59.37)	,
"Ciudadela de Jaca Jaca, Spain " :	(-0.55,42.57)	,
"Fort Jackson Plaquemines Parish, Louisiana, USA " :	(-89.46,29.36)	,
"Fort Jackson Wetumpka, Alabama, USA " :	(-86.25,32.51)	,
"Fort Jacques Port-au-Prince, Haiti " :	(-72.27,18.47)	,
"James' Fort Kinsale, Ireland " :	(-8.51,51.70)	,
"Fort James Jackson Savannah, Georgia, USA " :	(-81.04,32.08)	,
"Fort Jay Governor's Island, New York City, USA " :	(-74.02,40.69)	,
"Fort Jefferson Dry Tortugas, Florida, USA " :	(-82.87,24.63)	,
"Fort Jervois Lyttelton, New Zealand " :	(172.75,-43.62)	,
"Fort Jesus Mombasa, Kenya " :	(39.68,-4.06)	,
"Fortress Josefov Jaromer, Czech Republic " :	(15.93,50.34)	,
"Zitadelle Jülich Jülich, Germany " :	(6.36,50.92)	,
"Fort Julien Izbat Burj Rashid, Egypt " :	(30.39,31.44)	,
"Fort Al Kabibat Larache, Morocco " :	(-6.14,35.17)	,
"Kangla Fort Imphal, Manipur, India " :	(93.94,24.81)	,
"Karlovac Fortress Karlovac, Croatia " :	(15.56,45.49)	,
"Kastellet Copenhagen, Denmark " :	(12.59,55.69)	,
"The Keep Ireland Island, Bermuda " :	(-64.84,32.32)	,
"Kerroogarroo Fort Kerroogarroo, Isle of Man, UK " :	(-3.44,55.38)	,
"Kichuysky Redoubt Kichuy, Samarskaya Oblast, Russia " :	(50.47,53.42)	,
"Fort King George Darien, Georgia, USA " :	(-81.41,31.36)	,
"Fort Knox Prospect, Maine, USA " :	(-68.80,44.57)	,
"Komarno Komarno, Slovakia " :	(18.13,47.76)	,
"Kongsvinger Fortress Kongsvinger, Norway " :	(12.01,60.20)	,
"Kopgalis Fortress Klaipėda, Lithuania " :	(21.10,55.72)	,
"Fortress of Kondurca Kondurcha, Samarskaya Oblast, Russia " :	(50.35,53.52)	,
"Fortifications of Kostrzyn Kostrzyn, Poland " :	(17.22,52.39)	,
"Krasny Yar Fortress Krasny Yar, Samarskaya Oblast, Russia " :	(49.87,52.35)	,
"Kristiansten Fort Trondheim, Norway " :	(10.41,63.43)	,
"Kronborg Helsingor, Denmark " :	(12.62,56.04)	,
"Kronshlot Kronstadt, Russia " :	(29.75,59.98)	,
"Fort Kugelbake Cuxhaven, Germany " :	(8.68,53.89)	,
"Kungsholms Fort Tjurkö, Sweden " :	(15.59,56.11)	,
"Kuressaare Castle Saaremaa, Estonia " :	(22.48,58.25)	,
"Fort Lagarde Prats de Mollo, France " :	(2.48,42.41)	,
"Fort Lamalgue Toulon, France " :	(5.94,43.11)	,
"Landguard Fort Felixstowe, Suffolk, UK " :	(1.32,51.94)	,
"Landskrona Citadel Landskrona, Sweden " :	(12.82,55.87)	,
"Fort Lapointe Rochefort, France " :	(-1.08,45.96)	,
"Landskrona Citadel Landskrona, Sweden " :	(12.82,55.87)	,
"Forteresse Île du Large Îles Saint-Marcouf, Normandy, France " :	(-1.15,49.50)	,
"Fort Largs Adelaide, Australia " :	(138.50,-34.81)	,
"Fort Lennox Isle aux Noix, Quebec, Canada " :	(-73.27,45.12)	,
"Fort Leopold Diest, Belgium " :	(5.05,51.00)	,
"Leopoldov Leopoldov, Slovakia " :	(17.77,48.45)	,
"Fort Lernoult Detroit, Michigan, USA " :	(-83.05,42.33)	,
"Fort Liefkenshoek Antwerp, Belgium " :	(4.29,51.29)	,
"Fort Ligonier Ligonier, Pennsylvania, USA " :	(-79.24,40.24)	,
"Fort Livingston Isle Grand Terre, Louisiana, USA " :	(-89.95,29.27)	,
"Fort Lillo Antwerp, Belgium " :	(4.29,51.30)	,
"Citadelle de Lille Lille, France " :	(3.04,50.64)	,
"Fuerte de Loreto Puebla, Mexico " :	(-97.44,18.49)	,
"Fort Loudoun Vonore, Tennessee, USA " :	(-84.21,35.60)	,
"Fort Loyal North Hero, Vermont, USA " :	(-73.27,44.83)	,
"Fort Lupin Rochefort, France " :	(-1.03,45.96)	,
"Fortress Luxembourg Luxembourg City, Luxembourg " :	(6.13,49.61)	,
"Fort Mackinac Mackinac Island, Michigan, USA " :	(-84.62,45.85)	,
"Fort Macomb New Orleans, Louisiana, USA " :	(-89.80,30.06)	,
"Fort Macon Atlantic Beach, North Carolina, USA " :	(-76.69,34.70)	,
"Magazine Fort Dublin, Ireland " :	(-6.32,53.35)	,
"Manjarabad Fort Sakleshpur, India " :	(75.76,12.92)	,
"Fort Manoel Valetta, Malta " :	(14.51,35.90)	,
"Forte Marghera Venice, Italy " :	(12.26,45.48)	,
"Festung Marienberg Würzburg, Germany " :	(9.92,49.79)	,
"Fortress of Mazagan Al-Jadida, Morocco " :	(-8.50,33.23)	,
"Fort Marion Saint Augustine, Florida, USA " :	(-81.31,29.90)	,
"Fort Massac Metropolis, Illinois, USA " :	(-88.71,37.14)	,
"Fort Massachusetts Ship Island, Mississippi, USA " :	(-88.97,30.21)	,
"Fort McClary Kittery Point, Maine, USA " :	(-70.71,43.08)	,
"Fort McHenry Baltimore, Maryland, USA " :	(-76.58,39.26)	,
"Fort Médoc Cussac, France " :	(-0.70,45.11)	,
"Fort Meigs Perrysburg, Ohio, USA " :	(-83.65,41.55)	,
"Memelburg Klaipėda, Lithuania " :	(21.13,55.71)	,
"Fort Miamis Maumee, Ohio, USA " :	(-83.63,41.57)	,
"Fort Mifflin Philadelphia, Pennsylvania, USA " :	(-75.21,39.88)	,
"Fortaleza de São Miguel Luanda, Angola " :	(13.22,-8.81)	,
"Fort Miradoux Collioure, France " :	(3.08,42.53)	,
"Fort Mississauga Niagara-on-the-Lake, Ontario, Canada " :	(-79.08,43.26)	,
"Fort Monckton Gosport, UK " :	(-1.13,50.78)	,
"Fort Monroe Hampton, Virginia, USA " :	(-76.30,37.02)	,
"Monte Fort Macau, China " :	(113.54,22.20)	,
"Fort Montgomery Rouses Point, New York, USA " :	(-73.35,45.01)	,
"Castillo de Montjuïc Barcelona, Spain " :	(2.17,41.36)	,
"Fort Mont Louis Mont-Louis, Pyrénées-Orientales, France " :	(2.12,42.51)	,
"Fort du Mont-Valerien Paris, France " :	(2.22,48.87)	,
"Fort Moultrie Charleston, South Carolina, USA " :	(-79.86,32.76)	,
"Fort Morgan Mobile, Alabama, USA " :	(-88.02,30.23)	,
"Munkholmen Trondheim, Norway " :	(10.38,63.45)	,
"Muralla Real Ceuta, Spain " :	(-5.32,35.89)	,
"Naarden Naarden-Vesting, Holland " :	(5.16,52.30)	,
"Nádasdy-vár Sárvár, Hungary " :	(16.94,47.25)	,
"Fort Napoléon Toulon, France " :	(5.89,43.09)	,
"Fort Nassau Banda Neira, Moluccas, Indonesia " :	(129.90,-4.53)	,
"Fort Negley Nashville, Tennessee, USA " :	(-86.78,36.14)	,
"Fort Nelson Portsmouth, UK " :	(-1.14,50.86)	,
"Fort New Amsterdam Paramaribo, Suriname " :	(-55.09,5.89)	,
"New Dvina Fort Archangel, Russia " :	(43.25,62.78)	,
"Fort Niagara Youngstown, New York, USA " :	(-79.06,43.26)	,
"Fuerte de Niebla Niebla, Chile " :	(-73.40,-39.87)	,
"Fort Nieulay Calais, France " :	(1.82,50.95)	,
"Fort Ninety Six Ninety Six, South Carolina, USA " :	(-82.02,34.18)	,
"Nis Fortress Nis, Serbia " :	(21.90,43.33)	,
"Fort Norfolk Norfolk, Virginia, USA " :	(-76.30,36.86)	,
"Forte de Nossa Senhora da Luz de Cascais Cascais, Portugal " :	(-9.42,38.69)	,
"Forte de Nossa Senhora da Graça Elvas, Portugal " :	(-7.16,38.89)	,
"Novo-Alexandrovskiy Fort Mangystau Oblast, Kazakhstan " :	(53.85,44.59)	,
"Fort No. 1 Lévis, Québec, Canada " :	(-71.24,46.76)	,
"Fort Ogé Cayes-Jacmel, Haiti " :	(-72.48,18.27)	,
"Fort Ontario Oswego, New York, USA " :	(-76.51,43.47)	,
"Oradea Fortress Oradea, Romania " :	(21.94,47.05)	,
"Fort Orange Itamaracá Island, Brazil " :	(-34.84,-7.81)	,
"Fort Oswegatchie Ogdensburg, New York, USA " :	(-75.10,44.24)	,
"Fort of Our Lady of the Conception: Hormuz Island, Iran " :	(56.45,27.10)	,
"Palmanova Palmanova, Italy " :	(13.31,45.91)	,
"Ciudadela de Pamplona Pamplona, Spain " :	(-1.65,42.81)	,
"Panikota Diu, India " :	(71.00,20.72)	,
"Fortifications of Paris Paris, France " :	(2.35,48.86)	,
"Fort Pâté Île du Pâté, France " :	(-0.68,45.12)	,
"Fortaleza São Pedro da Barra Luanda, Angola " :	(13.29,-8.77)	,
"Pendennis Castle Falmouth, Cornwall, UK " :	(-5.05,50.15)	,
"Fortaleza de Peniche Peniche, Portugal " :	(-9.38,39.35)	,
"Perekop Fortresse Perekop, Crimea, Ukraine " :	(33.69,46.16)	,
"Le Citadelle Perpignan, France " :	(2.89,42.69)	,
"Peter and Paul Fortress St. Petersburg, Russia " :	(30.32,59.95)	,
"Zitadelle Petersberg Erfurt, Germany " :	(11.02,50.98)	,
"Petrovaradin Fortress Novi Sad, Serbia " :	(19.86,45.25)	,
"Fort Pickens Santa Rosa Island, Florida, USA " :	(-87.29,30.33)	,
"Fort Pilar Zamboanga, Philippines " :	(122.08,6.90)	,
"Pillau Citadel Baltiysk, Russia " :	(19.92,54.66)	,
"Fort Pike New Orleans, Louisiana, USA " :	(-89.74,30.17)	,
"Fort Plaisance Placentia, Newfoundland and Labrador, Canada " :	(-53.96,47.24)	,
"Fort Platte Saline Alderney, Channel Islands, UK " :	(-2.21,49.72)	,
"Royal Citadel Plymouth, UK " :	(-4.14,50.36)	,
"Fortezza di Poggio Imperiale Poggiobonsi, Siena, Italy " :	(11.16,43.46)	,
"Fort Point San Francisco, California, USA " :	(-122.48,37.81)	,
"Fort Popham Phippsburg, Maine, USA " :	(-69.78,43.76)	,
"Fort Preble Portland, Maine, USA " :	(-70.23,43.65)	,
"Fort de la Pree Ile de Re, France " :	(-1.29,46.18)	,
"Prince of Wales Fort Churchill, Manitoba, Canada " :	(-94.21,58.80)	,
"Pula Fortress Pula, Croatia " :	(13.85,44.87)	,
"Fort Pulaski Cockspur Island, Georgia, USA " :	(-80.89,32.03)	,
"Fort Purbrook Portsmouth, UK " :	(-1.04,50.85)	,
"Fort Putnam West Point, New York, USA " :	(-73.96,41.39)	,
"Citadelle de Quebec Quebec, Canada " :	(-71.21,46.81)	,
"Fort Quesnard Alderney, Channel Islands, UK " :	(-3.44,55.38)	,
"Fort Rammekens Ritthem, Netherlands " :	(3.65,51.45)	,
"Fort Isle de Raz Alderney, Channel Islands, UK " :	(-2.17,49.72)	,
"Fuerte de Real Felipe Callao, Peru " :	(-77.15,-12.06)	,
"Castillo de la Real Fuerza Havana, Cuba " :	(-82.35,23.14)	,
"Forte dos Reis Magos Natal, Brazil " :	(-35.19,-5.76)	,
"Château Renault Grand Île, Chausey, France " :	(-1.83,48.87)	,
"Schloss Rheydt Mönchengladbach, Germany " :	(6.48,51.18)	,
"Fort Ricasoli Kalkara, Malta " :	(14.53,35.90)	,
"Fort Richmond Staten Island, New York, USA " :	(-74.05,40.61)	,
"Kastro Riou Rio, Greece " :	(21.78,38.30)	,
"Fort Risban Calais, France " :	(1.85,50.96)	,
"Fort Roberdeau Sinking Spring Valley, Pennsylvania, USA " :	(-76.01,40.33)	,
"Rocroi Ardennes, France " :	(4.52,49.93)	,
"The Fortifications of Rome " :	(12.48,41.90)	,
"Festung Rothenberg Schnaittach, Germany " :	(11.36,49.55)	,
"Fort Royal Placentia, Newfoundland and Labrador, Canada " :	(-54.10,47.53)	,
"Château Royal de Collioure Collioure, France " :	(3.08,42.53)	,
"Royal Walls Ceuta, Spain " :	(-5.32,35.89)	,
"Russian Fort Elizabeth Kauai, Hawaii, USA " :	(-159.66,21.95)	,
"Fort St. Anthony St. Paul, Minnesota, USA " :	(-93.19,44.96)	,
"Fort Saint Elmo Collioure, France " :	(3.09,42.52)	,
"Fort Saint Elmo Valetta, Malta " :	(14.52,35.90)	,
"Fort St. Frédéric Crown Point, New York, USA " :	(-73.43,44.03)	,
"Fort St. George Chennai, India " :	(80.29,13.08)	,
"Fort Saint-Louis Fort-de-France, Martinique " :	(-61.07,14.60)	,
"Fort Saint Louis Placentia, Newfoundland and Labrador, Canada " :	(-53.96,47.25)	,
"Citadel de Saint-Martin Ile de Re, France " :	(-1.39,46.19)	,
"Fort des Salettes Briançon, France " :	(6.65,44.90)	,
"Castillo de San Antón La Coruña, Galicia, Spain " :	(-8.39,43.37)	,
"San Carlos Fortress Perote, Mexico " :	(-97.24,19.57)	,
"Fort San Carlos Amelia Island, Florida, USA " :	(-81.46,30.63)	,
"Fortaleza San Carlos Palma, Majorca, Spain " :	(2.66,39.57)	,
"Castillo de San Carlos de la Barra San Carlos Island, Zulia, Venezuela " :	(-71.71,11.04)	,
"Fortaleza de San Carlos de la Cabana Havana, Cuba " :	(-82.35,23.15)	,
"Castillo San Cristóbal San Juan, Puerto Rico " :	(-66.11,18.47)	,
"Fuerte de San Diego Acapulco, Mexico " :	(-99.82,16.90)	,
"Castillo de San Felipe Ferrol, Spain " :	(-8.28,43.46)	,
"Castillo San Felipe Puerto Cabello, Venezuela " :	(-68.01,10.48)	,
"Fuerte de San Felipe de Bacalar Bacalar, Quintana Roo, Mexico " :	(-88.39,18.68)	,
"Fort San Felipe del Morro San Juan, Puerto Rico " :	(-66.12,18.47)	,
"Castillo de San Fernando Figueres, Spain " :	(2.95,42.27)	,
"Fortaleza de San Fernando Oama, Honduras " :	(-88.04,15.78)	,
"Forte Sangallo Civita Castellana, Italy " :	(12.41,42.29)	,
"Fortín de San Gerónimo San Juan, Puerto Rico " :	(-66.08,18.46)	,
"Castillo San Giacomo Favignana, Italy " :	(12.33,37.93)	,
"Fortaleza de San Juan de Ulúa Veracruz, Mexico " :	(-96.13,19.21)	,
"Castillo de San Marcos St. Augustine, Florida, USA " :	(-81.31,29.90)	,
"Abbazia di San Miniato al Monte Florence, Italy " :	(11.26,43.76)	,
"Castillo de San Salvador de la Punta Havana, Cuba " :	(-82.36,23.15)	,
"Castillo de San Pedro de la Roca Santiago, Cuba " :	(-75.87,19.97)	,
"Fuerte de San Pedro Cebu City, Cebu, Philippines " :	(123.91,10.29)	,
"Castillo de San Sebastián Cádiz, Spain " :	(-6.32,36.53)	,
"Castillo de San Severino Matanzas, Cuba " :	(-81.56,23.06)	,
"Fortezza Santa Barbara Pistoia, Italy " :	(10.92,43.93)	,
"Castel Sant'Angelo Rome, Italy " :	(12.47,41.90)	,
"Forte di Santa Catarina Favignana, Italy " :	(12.33,37.93)	,
"Castel Sant'Elmo Naples, Italy " :	(14.24,40.84)	,
"Forte de Santa Luzia Elvas, Portugal " :	(-7.16,38.87)	,
"Fortaleza de Santa Teresa Rocha, Uruguay " :	(-53.55,-33.97)	,
"Torre de Santo António de Cascais Cascais, Portugal " :	(-9.40,38.72)	,
"Forte Real de São Filipe Cidade Velha, Santiago, Cabo Verde " :	(-23.60,14.92)	,
"Fortaleza de Sao Joao Baptista do Monte Brasil Angra do Heroismo, Terciera, Azores " :	(-27.23,38.65)	,
"Forte de São João da Barra Tavira, Portugal " :	(-7.59,37.14)	,
"Fortaleza de São José de Macapá Macapá, Brazil " :	(-51.05,0.03)	,
"Forte de Sao Juliao da Barra Lisbon, Portugal " :	(-9.33,38.67)	,
"Forte de Sao Mateus Cabo Frio, Brazil " :	(-42.01,-22.89)	,
"Fortezza di Sarzana Sarzana, Italy " :	(9.97,44.12)	,
"Fort Scammell House Island, Portland, Maine, USA " :	(-70.21,43.65)	,
"Fort Schuyler New York, New York, USA " :	(-73.79,40.81)	,
"Fort Senneville Senneville, Quebec, Canada " :	(-73.97,45.43)	,
"Sheshmin Fortress Sheshminskaya, Samarskaya Oblast, Russia " :	(50.47,53.42)	,
"Fort Sint Pieter Maastricht, Netherlands " :	(5.68,50.84)	,
"Skansin Tórshavn, Faroe Islands, Denmark " :	(-6.77,62.01)	,
"Slavonski Brod Fortress Slavonski Brod, Croatia " :	(18.01,45.16)	,
"Fort Snelling St. Paul, Minnesota, USA " :	(-93.18,44.89)	,
"Southsea Castle Portsmouth, Hampshire, UK " :	(-1.09,50.78)	,
"Fort Southwick Portsmouth, Hampshire, UK " :	(-1.11,50.86)	,
"Zitadelle Spandau Spandau, Germany " :	(13.21,52.54)	,
"Špilberk Castle Brno, Czech Republic " :	(16.60,49.19)	,
"Spit Fort Klaipėda, Lithuania " :	(21.14,55.70)	,
"Twierdza Srebrnogórska Srebrna Góra, Poland " :	(16.64,50.57)	,
"Fort Stanwix Rome, New York, USA " :	(-75.46,43.21)	,
"Star Castle St. Mary's Island, Isles of Scilly " :	(-6.32,49.92)	,
"Fort Stevens Point Adams, Oregon, USA " :	(-123.96,46.20)	,
"Star Fort Matara, Sri Lanka " :	(80.55,5.95)	,
"Cetățuia de pe Strajă Brașov, Romania " :	(25.59,45.65)	,
"Fort Sumter Charleston, South Carolina, USA " :	(-79.88,32.75)	,
"Svartholm Fortress Loviisa, Finland " :	(26.30,60.38)	,
"Fort Tartenson Fort-de-France, Martinique " :	(-61.08,14.61)	,
"Tatsuoka Castle Taguchi Saku City, Nagano, Japan " :	(138.50,36.20)	,
"Terezin Terezin, Czech Republic " :	(14.15,50.51)	,
"Fort Thüngen Luxembourg City, Luxembourg " :	(6.14,49.62)	,
"Le Fort des Têtes Briançon, France " :	(6.65,44.90)	,
"Fort Ticonderoga Ticonderoga, New York, USA " :	(-73.39,43.84)	,
"Tilbury Fort London, UK " :	(-0.13,51.51)	,
"Fort Tompkins Staten Island, New York, USA " :	(-74.06,40.60)	,
"Fort Totten New York, New York, USA " :	(-73.78,40.79)	,
"The Fortifications of Toulon Toulon, France " :	(5.93,43.13)	,
"Fort Toulouse Wetumpka, Alabama, USA " :	(-86.25,32.51)	,
"Fort Tourgis Alderney, Channel Islands, UK " :	(-2.22,49.72)	,
"Fort Trumbull New London, Connecticut, USA " :	(-72.10,41.34)	,
"Fort Union Watrous, New Mexico " :	(-105.01,35.90)	,
"Praça-forte de Valença Valença, Portugal " :	(-8.65,42.03)	,
"Fort Vallières Coudekerque-Branche, France " :	(2.40,50.99)	,
"Varberg Fortress Varberg, Sweden " :	(12.24,57.11)	,
"Vardøhus Fortress Vardø, Norway " :	(31.10,70.37)	,
"Fort Vasou Rochefort, France " :	(-1.08,45.96)	,
"Vatican City Rome, Italy " :	(12.45,41.90)	,
"Citadelle Vauban Le Palais, Belle Île, France " :	(-3.15,47.35)	,
"Zitadelle Vechta Vechta, Germany " :	(8.28,52.73)	,
"Vienna Austria (Quondam Starfort) " :	(16.37,48.21)	,
"Vyšehrad Prague, Czech Republic " :	(14.42,50.06)	,
"Fort Wadsworth Staten Island, New York, USA " :	(-74.06,40.60)	,
"Fort Ward Alexandria, Virginia, USA " :	(-77.10,38.83)	,
"Fort Warren Boston, Massachusetts, USA " :	(-70.93,42.32)	,
"Fort Washington Prince George County, Virginia, USA " :	(-77.02,38.71)	,
"Fortifications of Washington DC Washington DC, USA " :	(-77.04,38.91)	,
"Fort Wayne Detroit, Michigan " :	(-83.10,42.30)	,
"Fort Wellington Prescott, Ontario, Canada " :	(-75.51,44.71)	,
"Fort Westmoreland Spike Island, Cork Harbor, Ireland " :	(-8.29,51.83)	,
"Fort Widley Portsmouth, UK " :	(-1.07,50.85)	,
"Willemstad Noord-Brabant, Netherlands " :	(4.44,51.69)	,
"Fort William Augustus Grassy Island, Nova Scotia, Canada " :	(-60.97,45.34)	,
"Fort William Henry Lake George, New York, USA " :	(-73.71,43.42)	,
"Twierdza Wisloujscie Gdansk, Poland " :	(18.68,54.40)	,
"Woerden Woerden, Netherlands " :	(4.86,52.08)	,
"Fort Wood Liberty Island, New York, USA " :	(-74.04,40.69)	,
"Fort Wool The Rip-Raps, Hampton, Virginia, USA " :	(-76.30,36.99)	,
"Festung Wülzburg Weißenburg, Bavaria, Germany " :	(11.00,49.03)	,
"Yedikule Fortress Istanbul, Turkey " :	(28.92,40.99)	,
"Fort York Toronto, Canada " :	(-79.40,43.64)	,
"Fort Zachary Taylor Key West, Florida, USA " :	(-81.81,24.55)	,
"Fort Zeelandia Anping, Tainan, Taiwan " :	(120.16,23.00)



}










# Plot nodes with different markers if needed

for label, (lon, lat) in nodes.items():

    ax.plot(lon, lat, marker='o', markersize=8, color='red', transform=ccrs.PlateCarree())

    ax.text(lon + 2, lat + 2, label, transform=ccrs.PlateCarree(), fontsize=7)



# 72.66°W corridor (MHO, CLO, CO, SO, MVO)

ax.plot([-72.66, -72.66], [-90, 90], transform=ccrs.PlateCarree(), color='blue', linestyle='--', linewidth=2, label='72.66°W Corridor (MHO, CLO, CO, SO, MVO)')


# 31.33°E corridor (Giza Plateau | Adam's Calendar)

ax.plot([31.33, 31.33], [-90, 90], transform=ccrs.PlateCarree(), color='blue', linestyle='--', linewidth=2, label='31°E Corridor (Giza Plateau | Adams Calendar)')

# 107°E corridor (Gunung Padang)

ax.plot([107.1, 107.1], [-90, 90], transform=ccrs.PlateCarree(), color='blue', linestyle='--', linewidth=2, label='107°E Corridor (Gunung Padang)')

# 168°W corridor (Bering Strait)

ax.plot([-168.0, -168.0], [-90, 90], transform=ccrs.PlateCarree(), color='blue', linestyle='--', linewidth=2, label='168°W Corridor (Bering Strait)')



# Tropic lines & Equator

tropic_lines = [23.4367, -23.4367]
equator = [0]

for lat in tropic_lines:

    ax.plot(np.linspace(-180, 180, 100), [lat]*100, transform=ccrs.PlateCarree(),

            color='orange', linestyle='--', linewidth=2, label='Tropics')
for lat in equator:

    ax.plot(np.linspace(-180, 180, 100), [lat]*100, transform=ccrs.PlateCarree(),

            color='black', linestyle='--', linewidth=2, label='Equator')



# Paleopole arcs (approximate)

arc_lats = [-80, -30, 0, 30, 80]

for lat in arc_lats:

    ax.plot(np.linspace(-180, 180, 200), [lat]*200, transform=ccrs.PlateCarree(),

            color='green', linestyle=':', alpha=0.5)



# Title and legend

plt.title("Figure 21: Integrated Harmonic Geodetic Framework (Global View)")

plt.legend(loc='lower left', fontsize='small')



# External Legend
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.5, fontsize='small')

# Corner Glyph (CG-21)
ax.text(160, -40, 'CG-21', transform=ccrs.PlateCarree(),
        fontsize=10, fontweight='bold', color='dimgray',
        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.7))





# Create figure and axis
fig, ax = plt.subplots(figsize=(20, 12), subplot_kw={'projection': ccrs.PlateCarree()})
ax.coastlines()
ax.set_global()

# Plot pyramids – yellow triangles
for label, (lon, lat) in pyramids.items():
    ax.plot(lon, lat, marker='^', markersize=8, color='yellow', transform=ccrs.PlateCarree())
    ax.text(lon + 1, lat + 1, label, transform=ccrs.PlateCarree(), fontsize=7, color='black')

# Plot star forts – green stars with numbered labels (no names shown)
for i, (label, (lon, lat)) in enumerate(forts.items(), 1):
    ax.plot(lon, lat, marker='*', markersize=8, color='green', transform=ccrs.PlateCarree())
    ax.text(lon + 1, lat + 1, f'cG-SF{i}', transform=ccrs.PlateCarree(), fontsize=6, color='gray')

# Plot observatories – red circles
for label, (lon, lat) in nodes.items():
    ax.plot(lon, lat, marker='o', markersize=8, color='red', transform=ccrs.PlateCarree())
    ax.text(lon + 1, lat + 1, label, transform=ccrs.PlateCarree(), fontsize=7, color='black')


# Title
plt.title('Tetrahedral Earth: "3-Up; 1-Down" Geodetic Framework\nChiRLabs | chir.app/codex.html | GitHub: dihedralg/HIA-Geodetic-Codex', fontsize=12)
plt.savefig("ChiRLabs_geodetic_codex.png", dpi=300, bbox_inches='tight')
plt.show()

plt.title("Global Sites: Pyramids, Star Forts, and Observatories", fontsize=14)
plt.tight_layout()
plt.show()


