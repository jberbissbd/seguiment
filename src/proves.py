import configparser

creador_config = configparser.ConfigParser()
creador_config.add_section('Categories')
literal_categories = "Informació acadèmica, Incidències, Famílies (reunions), Escolta'm, Observacions"
creador_config.set('Categories', 'Defecte', literal_categories)
with open('config.ini', 'w') as configfile:
    creador_config.write(configfile)
