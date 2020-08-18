## Ansible Hosts Creator

**Description**

Cet outil permet de paramétrer le fichier hosts.txt d'Ansible par l'intermédiaire d'une base de donnée comportant les *ip, hostname, os* des machines détectées par un scan Nmap.

Arborescence: 

```
ansible_hosts_creator/
├── ahc.py
├── analyse_nmap.py
├── DB.db
├── DB.txt
├── DB_functions.py
└── README.md
```


- **ahc.py** : programme principale à éxécuter
- **analyse_nmap.py** : module Python permettant d'extraire les informations d'un scan nmap enregistrées dans un fichier XML
- **DB.db** : base de données comportant les tables correspondant à des wlan.
- **DB.txt** : base de données en .txt comportant les informations de la bases de données .db permettant une modification plus commode pour l'utilisateur.
- **DB_functions.py** : module Python permettant d'intéragir avec la base de donnée
- **README.md** : comporte le guide d'installation et de description

**Prérequis**

AHC s'utilise avec la version 3.8.3 de Python

Installation des packages nessaires pour lancer Python :

`sudo apt update`

`sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev`

Télécharger la release de Python 3.8.3 :
`curl -O https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tar.xz`

Extraire avec :
`tar -xf Python-3.8.3.tar.xz`

Aller dans le repertoire Python-3.8.3:
`cd Python-3.8.3`
`./configure --enable-optimizations`

Démarrer le process:
`make -j 4`

Installer le le bianaire de Python:
`sudo make altinstall`

Vérifier que python a bien été installer:
`python3.8 --version`


(Source pour l'installation (pour 3.8, attention, prensez à remplacer dans les commandes à l'URL suivante la version de python à installer) : https://linuxize.com/post/how-to-install-python-3-8-on-debian-10/)

**Installation**

L'outil s'installe via la commande :
`git clone https://github.com/silverstorm9/ansible_hosts_creator.git`

**Utilisation**

L'outil se lance via la commande :
`sudo python3.8 ansible_hosts_creator/ahc.py`

Commandes:

```
help : affiche l'aide
create [-t tableName|-h hostsPath] : (-t) créer une table dans la base de donnée
                                     (-h) créer le fichier hosts.txt, ne pas oublier l'extension .txt
edit [-t tableName xmlFile|-h hostsPath] : (-t) Extrait ip, hostname, os du du fichier XML comportant le rapport du scan NMAP et insert ces informations de la BDD
                                           (-h) permet d'écrier dans hosts.txt au moyen de requête SQL
show [-t tableName|-h hostsPath] : (-t) affiche le contenu d'une tbale, (* ou all affiche toutes les tables)
                                 : (-h) affiche le contenu du fichier hosts.txt
sql : lance un shell pour entrer des requête SQL
export : exporte la BDD de .db en .txt
import : import la BDD de .txt en .db
exit|quit : quitte le AHC
```

Exemples de commandes :

```
create -t wlan10 # Créer une table wlan10 dans la BDD
create -h ./hosts.txt # Créer un fichier hosts.txt

edit -t wlan10 ./nmap_wlan10.xml # Extrait ip, hostname, os du nmap_wlan10.xml et insert ces informations dans la table wlan10 de la BDD
edit -h ./hosts.txt # Permet d'éditer le fichier hosts.txt

show -t wlan10 # Afficher les éléments de la tables wlan10
show -h ./hosts.txt # Affiche le contenu du fichier hosts.txt

export
import
```

Exemples de commandes SQL :

```
SELECT * FROM wlan10 WHERE os!='Windows'
INSERT INTO wlan10 VALUES ('192.168.10.1','machine1','Linux','CentOS7')
DELETE FROM wlan10 WHERE ip=='192.168.10.1'
UPDATE wlan10 SET hostname = 'machine1', os = 'Linux', dist='Debian10' WHERE ip=='192.168.10.1'
INSERT OR REPLACE INTO wlan10 (ip,hostname,os,dist) VALUES ('192.168.10.1','machine1','no_os','no_dist')
```

Voir aussi : https://sql.sh/cours
