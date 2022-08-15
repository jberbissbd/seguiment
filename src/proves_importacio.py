import configparser

nom_arxiu = 'config.ini'
config = configparser.ConfigParser()
config.read(nom_arxiu)
valors_categories = config.get('Categories', 'Defecte').split(', ')
for valor in valors_categories:
    print(valor)
print(valors_categories[0])
