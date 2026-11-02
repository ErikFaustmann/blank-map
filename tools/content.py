# Curated quiz content for Mapolo. build_data.py joins this with Natural Earth geometry.

# Display name | Natural Earth name ('' = same) | capital | country aliases | capital aliases
COUNTRIES = {
    "Africa": """
Algeria||Algiers||
Angola||Luanda||
Benin||Porto-Novo||
Botswana||Gaborone||
Burkina Faso||Ouagadougou||
Burundi||Gitega||
Cabo Verde||Praia|Cape Verde|
Cameroon||Yaoundé||
Central African Republic|Central African Rep.|Bangui|CAR|
Chad||N'Djamena||Ndjamena
Comoros||Moroni||
Republic of the Congo|Congo|Brazzaville|Congo; Congo-Brazzaville|
Democratic Republic of the Congo|Dem. Rep. Congo|Kinshasa|DR Congo; DRC; Congo-Kinshasa; Zaire|
Côte d'Ivoire|Côte d'Ivoire|Yamoussoukro|Ivory Coast|Abidjan
Djibouti||Djibouti|Djibouti City|Djibouti City
Egypt||Cairo||
Equatorial Guinea|Eq. Guinea|Malabo||
Eritrea||Asmara||
Eswatini|eSwatini|Mbabane|Swaziland|Lobamba
Ethiopia||Addis Ababa||
Gabon||Libreville||
Gambia||Banjul|The Gambia|
Ghana||Accra||
Guinea||Conakry||
Guinea-Bissau||Bissau||
Kenya||Nairobi||
Lesotho||Maseru||
Liberia||Monrovia||
Libya||Tripoli||
Madagascar||Antananarivo||
Malawi||Lilongwe||
Mali||Bamako||
Mauritania||Nouakchott||
Mauritius||Port Louis||
Morocco||Rabat||
Mozambique||Maputo||
Namibia||Windhoek||
Niger||Niamey||
Nigeria||Abuja||
Rwanda||Kigali||
São Tomé and Príncipe|São Tomé and Principe|São Tomé|Sao Tome|
Senegal||Dakar||
Seychelles||Victoria||
Sierra Leone||Freetown||
Somalia||Mogadishu||
South Africa||Pretoria||Cape Town; Bloemfontein
South Sudan|S. Sudan|Juba||
Sudan||Khartoum||
Tanzania||Dodoma||Dar es Salaam
Togo||Lomé||
Tunisia||Tunis||
Uganda||Kampala||
Zambia||Lusaka||
Zimbabwe||Harare||
""",
    "Asia": """
Afghanistan||Kabul||
Armenia||Yerevan||
Azerbaijan||Baku||
Bahrain||Manama||
Bangladesh||Dhaka||
Bhutan||Thimphu||
Brunei||Bandar Seri Begawan||
Cambodia||Phnom Penh||
China||Beijing||Peking
Cyprus||Nicosia||
Georgia||Tbilisi||
India||New Delhi||Delhi
Indonesia||Jakarta||
Iran||Tehran||
Iraq||Baghdad||
Israel||Jerusalem||
Japan||Tokyo||
Jordan||Amman||
Kazakhstan||Astana||Nur-Sultan
Kuwait||Kuwait City||Kuwait
Kyrgyzstan||Bishkek||
Laos||Vientiane||
Lebanon||Beirut||
Malaysia||Kuala Lumpur||
Maldives||Malé||
Mongolia||Ulaanbaatar||Ulan Bator
Myanmar||Naypyidaw|Burma|Nay Pyi Taw
Nepal||Kathmandu||
North Korea||Pyongyang||
Oman||Muscat||
Pakistan||Islamabad||
Palestine|||West Bank; Gaza|
Philippines||Manila|The Philippines|
Qatar||Doha||
Saudi Arabia||Riyadh||
Singapore||Singapore||Singapore City
South Korea||Seoul||
Sri Lanka||Sri Jayawardenepura Kotte||Kotte; Colombo
Syria||Damascus||
Taiwan||Taipei||
Tajikistan||Dushanbe||
Thailand||Bangkok||
Timor-Leste||Dili|East Timor|
Turkey||Ankara|Türkiye|
Turkmenistan||Ashgabat||
United Arab Emirates||Abu Dhabi|UAE; Emirates|
Uzbekistan||Tashkent||
Vietnam||Hanoi||
Yemen||Sanaa||Sana'a
""",
    "Europe": """
Albania||Tirana||
Andorra||Andorra la Vella||
Austria||Vienna||Wien
Belarus||Minsk||
Belgium||Brussels||Bruxelles
Bosnia and Herzegovina|Bosnia and Herz.|Sarajevo|Bosnia|
Bulgaria||Sofia||
Croatia||Zagreb||
Czechia||Prague|Czech Republic|Praha
Denmark||Copenhagen||København
Estonia||Tallinn||
Finland||Helsinki||
France||Paris||
Germany||Berlin||
Greece||Athens||
Hungary||Budapest||
Iceland||Reykjavík||
Ireland||Dublin||
Italy||Rome||Roma
Kosovo||Pristina||Prishtina
Latvia||Riga||
Liechtenstein||Vaduz||
Lithuania||Vilnius||
Luxembourg||Luxembourg||Luxembourg City
Malta||Valletta||
Moldova||Chișinău||Chisinau
Monaco||Monaco||Monaco City
Montenegro||Podgorica||
Netherlands||Amsterdam|The Netherlands; Holland|
North Macedonia|Macedonia|Skopje|Macedonia|
Norway||Oslo||
Poland||Warsaw||Warszawa
Portugal||Lisbon||Lisboa
Romania||Bucharest||
Russia||Moscow|Russian Federation|Moskva
San Marino||San Marino||
Serbia||Belgrade||
Slovakia||Bratislava||
Slovenia||Ljubljana||
Spain||Madrid||
Sweden||Stockholm||
Switzerland||Bern||Berne
Ukraine||Kyiv||Kiev
United Kingdom||London|UK; Great Britain; Britain|
Vatican City|Vatican|Vatican City|Vatican; Holy See|Vatican
""",
    "North America": """
Antigua and Barbuda|Antigua and Barb.|Saint John's||St Johns
Bahamas||Nassau|The Bahamas|
Barbados||Bridgetown||
Belize||Belmopan||
Canada||Ottawa||
Costa Rica||San José||
Cuba||Havana||La Habana
Dominica||Roseau||
Dominican Republic|Dominican Rep.|Santo Domingo||
El Salvador||San Salvador||
Grenada||Saint George's||St Georges
Guatemala||Guatemala City||Guatemala
Haiti||Port-au-Prince||
Honduras||Tegucigalpa||
Jamaica||Kingston||
Mexico||Mexico City||Ciudad de Mexico
Nicaragua||Managua||
Panama||Panama City||Panama
Saint Kitts and Nevis|St. Kitts and Nevis|Basseterre|St Kitts|
Saint Lucia||Castries|St Lucia|
Saint Vincent and the Grenadines|St. Vin. and Gren.|Kingstown|St Vincent; Saint Vincent|
Trinidad and Tobago||Port of Spain|Trinidad|
United States|United States of America|Washington, D.C.|USA; US; America; United States of America|Washington; Washington DC
""",
    "South America": """
Argentina||Buenos Aires||
Bolivia||Sucre||La Paz
Brazil||Brasília||Brazil
Chile||Santiago||
Colombia||Bogotá||
Ecuador||Quito||
Guyana||Georgetown||
Paraguay||Asunción||
Peru||Lima||
Suriname||Paramaribo||
Uruguay||Montevideo||
Venezuela||Caracas||
""",
    "Oceania": """
Australia||Canberra||
Fiji||Suva||
Kiribati||Tarawa||South Tarawa
Marshall Islands|Marshall Is.|Majuro||
Micronesia||Palikir|Federated States of Micronesia|
Nauru||Yaren||
New Zealand||Wellington||
Palau||Ngerulmud||
Papua New Guinea||Port Moresby|PNG|
Samoa||Apia||
Solomon Islands|Solomon Is.|Honiara||
Tonga||Nukuʻalofa||Nukualofa
Tuvalu||Funafuti||
Vanuatu||Port Vila||
""",
}

# Natural Earth pieces folded into the country that the UN recognises.
MERGE_INTO = {"Somalia": ["Somaliland"], "Cyprus": ["N. Cyprus"]}

# Places missing from the 50m map, drawn as a small dot-sized polygon: name -> (lon, lat).
ADD_POINT_COUNTRIES = {"Tuvalu": (179.2, -8.52)}

# Capitals Natural Earth's populated places don't list or lists under another spelling: (lon, lat).
CAPITAL_COORDS = {
    "Gitega": (29.925, -3.427),
    "Yamoussoukro": (-5.276, 6.818),
    "Dodoma": (35.746, -6.163),
    "Sri Jayawardenepura Kotte": (79.902, 6.890),
    "Astana": (71.430, 51.128),
    "Naypyidaw": (96.078, 19.763),
    "Ngerulmud": (134.624, 7.501),
    "Yaren": (166.920, -0.547),
    "Palikir": (158.158, 6.917),
    "Tarawa": (173.018, 1.329),
    "Andorra la Vella": (1.521, 42.507),
    "Copenhagen": (12.568, 55.676),
    "Port of Spain": (-61.517, 10.652),
    "Nukuʻalofa": (-175.200, -21.139),
}

CAPITAL_NOTES = {
    "Jerusalem": "Israel's declared capital. Most embassies are in Tel Aviv.",
    "Sucre": "Bolivia's constitutional capital. La Paz is the seat of government and also counts.",
    "Pretoria": "One of South Africa's three capitals. Cape Town and Bloemfontein also count.",
    "Yamoussoukro": "The official capital. Abidjan is the economic centre and also counts.",
    "Sri Jayawardenepura Kotte": "The official capital, a suburb of Colombo, which also counts.",
}

# name, lat, lon, elevation m, range, where, aliases, region
MOUNTAINS = [
    ("Mount Everest", 27.988, 86.925, 8849, "Himalayas", "Nepal and China", "Everest; Sagarmatha; Chomolungma", "Asia"),
    ("K2", 35.881, 76.513, 8611, "Karakoram", "Pakistan and China", "Godwin-Austen; Chogori", "Asia"),
    ("Kangchenjunga", 27.703, 88.147, 8586, "Himalayas", "Nepal and India", "Kanchenjunga", "Asia"),
    ("Nanga Parbat", 35.237, 74.589, 8126, "Himalayas", "Pakistan", "", "Asia"),
    ("Annapurna", 28.596, 83.820, 8091, "Himalayas", "Nepal", "", "Asia"),
    ("Ismoil Somoni Peak", 38.943, 72.016, 7495, "Pamir", "Tajikistan", "Ismoil Somoni; Communism Peak", "Asia"),
    ("Jengish Chokusu", 42.035, 80.125, 7439, "Tian Shan", "Kyrgyzstan and China", "Pobeda Peak; Victory Peak", "Asia"),
    ("Mount Damavand", 35.955, 52.110, 5610, "Alborz", "Iran", "Damavand", "Asia"),
    ("Mount Ararat", 39.702, 44.298, 5137, "Armenian Highlands", "Turkey", "Ararat; Agri Dagi", "Asia"),
    ("Mount Fuji", 35.361, 138.727, 3776, "Fuji volcanic zone", "Japan", "Fuji; Fujisan; Fujiyama", "Asia"),
    ("Mount Kinabalu", 6.075, 116.558, 4095, "Crocker Range", "Malaysia", "Kinabalu", "Asia"),
    ("Mont Blanc", 45.833, 6.865, 4806, "Alps", "France and Italy", "Monte Bianco", "Europe"),
    ("Matterhorn", 45.977, 7.658, 4478, "Alps", "Switzerland and Italy", "Monte Cervino; Cervin", "Europe"),
    ("Mount Elbrus", 43.355, 42.439, 5642, "Caucasus", "Russia", "Elbrus", "Europe"),
    ("Zugspitze", 47.421, 10.985, 2962, "Alps", "Germany and Austria", "", "Europe"),
    ("Mount Etna", 37.751, 14.993, 3357, "volcano on Sicily", "Italy", "Etna", "Europe"),
    ("Mount Olympus", 40.085, 22.359, 2917, "Olympus massif", "Greece", "Olympus", "Europe"),
    ("Mulhacén", 37.053, -3.311, 3479, "Sierra Nevada", "Spain", "", "Europe"),
    ("Ben Nevis", 56.797, -5.004, 1345, "Grampians", "Scotland", "", "Europe"),
    ("Kilimanjaro", -3.076, 37.353, 5895, "volcano in East Africa", "Tanzania", "Mount Kilimanjaro; Kibo", "Africa"),
    ("Mount Kenya", -0.152, 37.308, 5199, "volcano in East Africa", "Kenya", "", "Africa"),
    ("Mount Stanley", 0.386, 29.872, 5109, "Rwenzori", "DR Congo and Uganda", "Margherita Peak; Stanley", "Africa"),
    ("Ras Dashen", 13.236, 38.372, 4550, "Semien Mountains", "Ethiopia", "Ras Dejen", "Africa"),
    ("Toubkal", 31.060, -7.916, 4167, "Atlas Mountains", "Morocco", "Jebel Toubkal", "Africa"),
    ("Mount Cameroon", 4.203, 9.170, 4040, "volcano in West Africa", "Cameroon", "", "Africa"),
    ("Denali", 63.069, -151.007, 6190, "Alaska Range", "United States", "Mount McKinley; McKinley", "North America"),
    ("Mount Logan", 60.567, -140.405, 5959, "Saint Elias Mountains", "Canada", "Logan", "North America"),
    ("Pico de Orizaba", 19.030, -97.268, 5636, "Trans-Mexican Volcanic Belt", "Mexico", "Citlaltépetl; Orizaba", "North America"),
    ("Popocatépetl", 19.023, -98.628, 5426, "Trans-Mexican Volcanic Belt", "Mexico", "Popocatepetl", "North America"),
    ("Mount Whitney", 36.578, -118.292, 4421, "Sierra Nevada", "United States", "Whitney", "North America"),
    ("Mount Rainier", 46.853, -121.760, 4392, "Cascades", "United States", "Rainier", "North America"),
    ("Aconcagua", -32.653, -70.011, 6961, "Andes", "Argentina", "", "South America"),
    ("Ojos del Salado", -27.109, -68.541, 6893, "Andes", "Chile and Argentina", "", "South America"),
    ("Huascarán", -9.122, -77.604, 6768, "Andes", "Peru", "Huascaran", "South America"),
    ("Chimborazo", -1.469, -78.817, 6263, "Andes", "Ecuador", "", "South America"),
    ("Cotopaxi", -0.681, -78.438, 5897, "Andes", "Ecuador", "", "South America"),
    ("Puncak Jaya", -4.079, 137.158, 4884, "Sudirman Range", "Indonesia", "Carstensz Pyramid", "Oceania"),
    ("Aoraki / Mount Cook", -43.594, 170.142, 3724, "Southern Alps", "New Zealand", "Aoraki; Mount Cook; Cook", "Oceania"),
    ("Mount Kosciuszko", -36.456, 148.263, 2228, "Snowy Mountains", "Australia", "Kosciuszko; Kosciusko", "Oceania"),
    ("Mauna Kea", 19.821, -155.468, 4207, "volcano on Hawaiʻi", "United States", "", "Oceania"),
    ("Vinson Massif", -78.525, -85.617, 4892, "Ellsworth Mountains", "Antarctica", "Vinson; Mount Vinson", "Antarctica"),
    ("Mount Erebus", -77.530, 167.153, 3794, "Ross Island", "Antarctica", "Erebus", "Antarctica"),
]

# Rivers Natural Earth only keeps a short stretch of, traced by hand: name -> lines of (lon, lat).
RIVER_LINES = {
    "St. Lawrence": [[[-76.4, 44.2], [-75.7, 44.6], [-74.7, 45.0], [-73.55, 45.5], [-72.55, 46.35],
                      [-71.2, 46.8], [-69.6, 47.8], [-68.2, 49.0], [-66.5, 49.7]]],
}

# name, Natural Earth segment names, length km, mouth, aliases, region, optional bbox (w, s, e, n)
RIVERS = [
    ("Nile", "Nile; El Bahr el Abyad; Bahr el Jebel; Albert Nile; Victoria Nile; Rosetta Branch; Damietta Branch", 6650, "the Mediterranean", "", "Africa", None),
    ("Congo", "Congo; Lualaba", 4700, "the Atlantic", "Zaire", "Africa", None),
    ("Niger", "Niger", 4180, "the Gulf of Guinea", "", "Africa", (-13, 3, 12, 20)),
    ("Zambezi", "Zambezi", 2574, "the Indian Ocean", "Zambesi", "Africa", None),
    ("Orange", "Orange", 2200, "the Atlantic", "Gariep", "Africa", None),
    ("Limpopo", "Limpopo", 1750, "the Indian Ocean", "", "Africa", None),
    ("Okavango", "Okavango; Cubango", 1600, "an inland delta in Botswana", "Cubango", "Africa", None),
    ("Senegal", "Sénégal; Bafing", 1086, "the Atlantic", "", "Africa", None),
    ("Yangtze", "Chang Jiang; Yangtze; Jinsha; Tongtian; Tuotuo", 6300, "the East China Sea", "Chang Jiang; Changjiang", "Asia", None),
    ("Yellow River", "Huang", 5464, "the Bohai Sea", "Huang He; Huang", "Asia", None),
    ("Mekong", "Mekong; Lancang", 4350, "the South China Sea", "", "Asia", None),
    ("Lena", "Lena", 4400, "the Laptev Sea", "", "Asia", None),
    ("Yenisey", "Yenisey; Verkhniy Yenisey", 3487, "the Kara Sea", "Yenisei", "Asia", None),
    ("Ob", "Ob", 3650, "the Kara Sea", "", "Asia", None),
    ("Irtysh", "Irtysh; Ertis; Ertix", 4248, "the Ob", "Ertis", "Asia", None),
    ("Amur", "Amur; Heilong Jiang; Argun'", 2824, "the Sea of Okhotsk", "Heilong Jiang", "Asia", None),
    ("Kolyma", "Kolyma", 2129, "the East Siberian Sea", "", "Asia", None),
    ("Ganges", "Ganges", 2525, "the Bay of Bengal", "Ganga", "Asia", None),
    ("Indus", "Indus", 3180, "the Arabian Sea", "", "Asia", None),
    ("Brahmaputra", "Brahmaputra; Dihang; Yarlung", 2900, "the Bay of Bengal", "Yarlung Tsangpo", "Asia", None),
    ("Irrawaddy", "Ayeyarwady; Irrawaddy Delta; Nmai", 2170, "the Andaman Sea", "Ayeyarwady", "Asia", None),
    ("Salween", "Salween; Nu", 3060, "the Andaman Sea", "Nu", "Asia", None),
    ("Euphrates", "Euphrates; Al Furat; Firat", 2800, "the Persian Gulf, via the Shatt al-Arab", "", "Asia", None),
    ("Tigris", "Tigris; Dicle", 1850, "the Persian Gulf, via the Shatt al-Arab", "", "Asia", None),
    ("Amu Darya", "Amu Darya; Panj; Pamir", 2540, "the Aral Sea basin", "Oxus", "Asia", None),
    ("Syr Darya", "Syr Darya; Naryn", 3078, "the Aral Sea", "", "Asia", None),
    ("Volga", "Volga", 3530, "the Caspian Sea", "", "Europe", None),
    ("Danube", "Danube; Donau", 2850, "the Black Sea", "Donau", "Europe", None),
    ("Dnieper", "Dnipro; Dnepre", 2200, "the Black Sea", "Dnipro", "Europe", None),
    ("Don", "Don", 1870, "the Sea of Azov", "", "Europe", (35, 45, 45, 56)),
    ("Ural", "Ural", 2428, "the Caspian Sea", "", "Europe", None),
    ("Rhine", "Rhine; Rhein; Rhin; Waal", 1230, "the North Sea", "Rhein", "Europe", None),
    ("Elbe", "Elbe", 1094, "the North Sea", "", "Europe", None),
    ("Vistula", "Vistula", 1047, "the Baltic Sea", "Wisla", "Europe", None),
    ("Tagus", "Tajo; Tejo", 1007, "the Atlantic", "Tajo; Tejo", "Europe", None),
    ("Loire", "Loire", 1006, "the Atlantic", "", "Europe", None),
    ("Rhône", "Rhône", 813, "the Mediterranean", "Rhone", "Europe", None),
    ("Seine", "Seine", 777, "the English Channel", "", "Europe", None),
    ("Po", "Po", 652, "the Adriatic Sea", "", "Europe", None),
    ("Thames", "Thames", 346, "the North Sea", "", "Europe", None),
    ("Mississippi", "Mississippi", 3730, "the Gulf of Mexico", "", "North America", None),
    ("Missouri", "Missouri", 3768, "the Mississippi", "", "North America", None),
    ("Mackenzie", "Mackenzie", 1738, "the Arctic Ocean", "", "North America", None),
    ("Yukon", "Yukon", 3185, "the Bering Sea", "", "North America", None),
    ("Rio Grande", "Rio Grande", 3051, "the Gulf of Mexico", "Rio Bravo", "North America", None),
    ("Colorado", "Colorado", 2330, "the Gulf of California", "", "North America", (-116, 30.5, -105, 44)),
    ("Columbia", "Columbia", 2000, "the Pacific", "", "North America", None),
    ("St. Lawrence", "St. Lawrence", 1197, "the Gulf of St. Lawrence", "Saint Lawrence; St Lawrence", "North America", None),
    ("Ohio", "Ohio", 1579, "the Mississippi", "", "North America", None),
    ("Hudson", "Hudson", 507, "the Atlantic", "", "North America", (-76, 40, -72, 44.5)),
    ("Amazon", "Amazonas; Ucayali", 6400, "the Atlantic", "Amazonas", "South America", None),
    ("Paraná", "Paraná; Paranaíba", 4880, "the Río de la Plata", "Parana", "South America", None),
    ("Madeira", "Madeira; Mamoré", 3250, "the Amazon", "", "South America", None),
    ("Orinoco", "Orinoco", 2140, "the Atlantic", "", "South America", None),
    ("Tocantins", "Tocantins", 2450, "the Atlantic", "", "South America", None),
    ("São Francisco", "São Francisco", 2914, "the Atlantic", "Sao Francisco", "South America", None),
    ("Uruguay", "Uruguay", 1838, "the Río de la Plata", "", "South America", None),
    ("Magdalena", "Magdalena", 1528, "the Caribbean", "", "South America", None),
    ("Murray", "Murray", 2508, "the Southern Ocean", "", "Oceania", None),
    ("Darling", "Darling; Barwon", 1472, "the Murray", "", "Oceania", None),
]
