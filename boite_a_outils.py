import change_gps_2
import kml_to_geojson
import subprocess as sp
import os
import sys

CAMERA = ""


def print_banner():
    print(
        """developed by:
                                                                       .                                     
                             .=====                                   
                      :==========:                                    
               .================                                      
               :=====.     =====.                                     
                .==-        ====-                                     
                ===         -===:                                     
               .==:        .====                                      
                ===       =====.                                      
               .=================:                                    
              =============:======-                                   
              ===            .===                                     
                                                                      
                                                                      
      @   -@    @=   @   @ @  @    @   @*                             
     %.@  @@   *:@   @ @   @  @@   @  =-@                             
     @ % *..#  @  @  @@    @  @ *- @  @  @                            
     @  @@  @ @%%%%@ @ .@  @  @  .@@ @%%%%@                           
     @      @ @    @ @   @.@  @    @ @    @                     
                                                                      
   .@@@@@ @@@@@@  @@@@@. @@@@@-:@@  @@-=@@@@=                         
   @@    =@@  .@@ @   @- @@ @@@:@@  @@--@@@%                          
   @@-   .@@  *@@ @@@@-  @@@@. :@@  @@.   .@@                         
    @@@@@  @@@@%  @@  @@ @@     -@@@@- @@@@@                          
                                                   """
    )


def get_user_choice(prompt, options):
    while True:
        try:
            choice = int(input(prompt))
            if choice in options:
                return choice
            else:
                print("Veuillez entrer un nombre valide.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un chiffre.")


def menu():
    global CAMERA

    while True:
        print("\n--- MENU PRINCIPAL ---")
        print("1- GoPro max")
        print("2- Insta360 one x2")
        print("3- Push Panoramax OSM")
        print("4- Quitter")

        choix = get_user_choice("Votre choix: ", [1, 2, 3, 4])

        if choix == 1:
            CAMERA = "GoPro max"
            menu_go_pro()
        elif choix == 2:
            CAMERA = "Insta360 one x2"
            menu_insta()
        elif choix == 3:
            push_panoramax()
        elif choix == 4:
            print("Fin du programme.")
            sys.exit()


def push_panoramax():
    print("\n--- Upload Panoramax ---")
    print("1- img_to_be_changed/")
    print("2- img_to_be_changed/changed/")
    print("3- img_logo/")
    print("4- Retour")

    choix = get_user_choice("Choix du chemin photo: ", [1, 2, 3, 4])
    path = {
        1: "img_to_be_changed/",
        2: "img_to_be_changed/changed/",
        3: "img_logo/",
    }.get(choix)

    if path:
        sp.run(
            [
                "panoramax_cli",
                "upload",
                "--api-url",
                "https://panoramax.openstreetmap.fr/",
                path,
            ]
        )


def menu_go_pro():
    while True:
        print("\n--- MENU GOPRO MAX ---")
        print("1- Mode auto")
        print("2- Ajuster les coordonnées GPS")
        print("3- Ajouter un logo")
        print("4- Retour")
        print("5- Quitter")

        choix = get_user_choice("Votre choix: ", [1, 2, 3, 4, 5])

        if choix == 1:
            mode_auto()
        elif choix == 2:
            change_gps_2.main()
        elif choix == 3:
            add_logo()
        elif choix == 4:
            return
        elif choix == 5:
            sys.exit()


def menu_insta():
    while True:
        print("\n--- MENU INSTA360 ---")
        print("1- Mode auto")
        print("2- Ajuster les coordonnées GPS")
        print("3- Ajouter un logo")
        print("4- Retour")
        print("5- Adapter l'image à Panoramax")
        print("6- Quitter")

        choix = get_user_choice("Votre choix: ", [1, 2, 3, 4, 5, 6])

        if choix == 1:
            mode_auto()
        elif choix == 2:
            change_gps_2.main()
        elif choix == 3:
            add_logo()
        elif choix == 4:
            return
        elif choix == 5:
            adapt_meta_insta()
        elif choix == 6:
            sys.exit()


def add_logo():
    print("\n--- AJOUT DE LOGO ---")
    print("1- img_to_be_changed/")
    print("2- img_to_be_changed/changed/")

    choix = get_user_choice("Choisissez le dossier: ", [1, 2])
    path = "img_to_be_changed/" if choix == 1 else "img_to_be_changed/changed/"
    sp.run(["./script_logo_insta.sh", path])


def adapt_meta_insta():
    print("\n--- MODIFICATION METADONNÉES ---")
    print("1- img_to_be_changed/")
    print("2- img_to_be_changed/changed/")
    print("3- img_logo/")

    choix = get_user_choice("Chemin: ", [1, 2, 3])
    path = {1: "img_to_be_changed/", 2: "img_to_be_changed/changed/", 3: "img_logo/"}[
        choix
    ]
    sp.run(["./meta_insta.sh", path])


def mode_auto():
    global CAMERA

    print("\n--- MODE AUTO ---")
    print("Ce mode effectue automatiquement :")
    print("  - Changement des coordonnées GPS")
    print("  - Ajout de logo")
    print("  - Modification des métadonnées (Insta360 uniquement)")
    print("  - Upload vers Panoramax")
    print("\nAssurez-vous que les fichiers KML, les images et le logo sont prêts.")

    kml_to_geojson.converter_kml()
    change_gps_2.main()

    if CAMERA == "Insta360 one x2":
        sp.run(["./meta_insta.sh", "img_logo/"])
    else:
        sp.run(["./meta_insta.sh", "img_to_be_changed/changed/"])

    sp.run(["./script_logo_insta.sh", "img_to_be_changed/changed/"])

    sp.run(
        [
            "panoramax_cli",
            "upload",
            "--api-url",
            "https://panoramax.openstreetmap.fr/",
            "img_logo/",
        ]
    )


if __name__ == "__main__":
    print_banner()
    menu()
