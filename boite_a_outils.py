import os
import subprocess as sp
import sys
from scripts.geo_perso import change_gps_2, change_gps_vid
from scripts.horizon_redressment import constants , main
from scripts.video import img_extractor
from scripts.geo_perso import kml_to_geojson 

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
    path = input("Entrez le chemin où sont situées vos photos : ").strip()
    if not os.path.exists(path):
        print("Chemin invalide. Veuillez réessayer.")
        return
    try:
        sp.run(
            [
                "panoramax_cli",
                "upload",
                "--api-url",
                "https://panoramax.openstreetmap.fr/",
                path,
            ],
            check=True
        )
    except Exception as e:
        print(f"Erreur lors de l'upload : {e}")


def menu_go_pro():
    while True:
        print("\n--- MENU GOPRO MAX ---")
        print("1- Mode auto")
        print("2- Ajuster les coordonnées GPS")
        print("3- Ajouter un logo")
        print("4- Corriger l'inclinaison (v.BETA)")
        print("5- Retour")
        print("6- Quitter")
        choix = get_user_choice("Votre choix: ", [1, 2, 3, 4, 5, 6])

        if choix == 1:
            mode_auto()
        elif choix == 2:
            change_gps_2.main()
        elif choix == 3:
            add_logo()
        elif choix == 4:
            corrige_inclinaison()
        elif choix == 5:
            return
        else:
            sys.exit()


def menu_insta():
    global CAMERA
    while True:
        print("\n--- MENU INSTA360 ---")
        print("1- Photos")
        print("2- Vidéos")
        print("3- Retour")

        choix_1 = get_user_choice("Votre choix: ", [1, 2, 3])

        if choix_1 == 1:
            while True:
                print("\n--- MENU PHOTO ---")
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
                    break
                elif choix == 5:
                    adapt_meta_insta()
                elif choix == 6:
                    sys.exit()

        elif choix_1 == 2:
            while True:
                print("\n--- MENU VIDEO ---")
                print("1- Mode auto")
                print("2- Extraire les images")
                print("3- Ajuster les coordonnées GPS")
                print("4- Ajouter un logo")
                print("5- Adapter l'image à Panoramax")
                print("6- Retour")
                print("7- Quitter")

                choix = get_user_choice("Votre choix: ", [1, 2, 3, 4, 5, 6, 7])

                if choix == 1:
                    mode_auto_vid()
                elif choix == 2:
                    print("!!! L'algorithme utilise le nom du fichier vidéo. Ne le modifiez pas !!!")
                    print("Assurez-vous d’avoir placé les vidéos dans le dossier 'vids/'.")
                    y_n = input("Avez-vous respecté les prérequis ? [y/n] : ").lower()
                    if y_n == "y":
                        img_extractor.extract_all_real_photos("vids/")
                elif choix == 3:
                    change_gps_vid.main()
                elif choix == 4:
                    add_logo()
                elif choix == 5:
                    adapt_meta_insta()
                elif choix == 6:
                    break
                elif choix == 7:
                    sys.exit()
        elif choix_1 == 3:
            return


def add_logo():
    path = input("Entrez le chemin où sont situées vos photos : ").strip()
    if not os.path.exists(path):
        print("Chemin invalide. Veuillez réessayer.")
        return
    try:
        sp.run(["./script_logo_insta.sh", path], check=True)
    except Exception as e:
        print(f"Erreur lors de l'ajout du logo : {e}")


def adapt_meta_insta():
    path = input("Entrez le chemin où sont situées vos photos : ").strip()
    if not os.path.exists(path):
        print("Chemin invalide. Veuillez réessayer.")
        return
    try:
        sp.run(["./meta_insta.sh", path], check=True)
    except Exception as e:
        print(f"Erreur lors de l'adaptation des métadonnées : {e}")


def corrige_inclinaison():
    print("\n--- CORRECTION D'INCLINAISON ---")
    path = input("Entrez le chemin où sont situées vos photos : ").strip()
    if not os.path.exists(path):
        print("Chemin invalide. Veuillez réessayer.")
        return
    try:
        finale.main.auto_align_roll_for_folder(path)
        print("Correction effectuée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la correction d'inclinaison : {e}")


def mode_auto():
    global CAMERA
    print("\n--- MODE AUTO ---")
    print("Ce mode effectue automatiquement :")
    print("  - Changement des coordonnées GPS")
    print("  - Correction d'inclinaison")
    print("  - Ajout de logo")
    print("  - Modification des métadonnées (Insta360 uniquement)")
    print("  - Upload vers Panoramax")

    try:
        kml_to_geojson.converter_kml()
        change_gps_2.main()
        finale.main.auto_align_roll_for_folder("img_to_be_changed/changed/")
        meta_path = (
            "img_logo/"
            if CAMERA == "Insta360 one x2"
            else f"img_to_be_changed/changed/{finale.constants.CERTAIN_DIR}"
        )

        print(
            "ATTENTION LES IMAGES ÉTANT CLASSIFIÉES COMME INCERTAINES "
            "NE SERONT PAS TRAITÉES PAR LE TRAITEMENT INSTA360 ET NE SERONT PAS PUSH SUR PANORAMAX"
        )

        sp.run(["./meta_insta.sh", meta_path], check=True)
        sp.run(["./script_logo_insta.sh", "img_to_be_changed/changed/"], check=True)
        sp.run(
            [
                "panoramax_cli",
                "upload",
                "--api-url",
                "https://panoramax.openstreetmap.fr/",
                "img_logo/",
            ],
            check=True
        )
    except Exception as e:
        print(f"Erreur dans le mode auto : {e}")


def mode_auto_vid():
    global CAMERA
    print("\n--- MODE AUTO VIDEO Insta360 ---")
    print("Ce mode effectue automatiquement :")
    print("  - Extraction des photos")
    print("  - Changement des coordonnées GPS")
    print("  - Ajout de logo")
    print("  - Modification des métadonnées")
    print("  - Upload vers Panoramax")

    try:
        img_extractor.extract_all_real_photos("vids/")
        kml_to_geojson.converter_kml()
        change_gps_vid.main()

        meta_path = (
            "img_logo/" if CAMERA == "Insta360 one x2" else "img_to_be_changed/changed/"
        )
        sp.run(["./meta_insta.sh", meta_path], check=True)
        sp.run(["./script_logo_insta.sh", "img_to_be_changed/changed/"], check=True)
        sp.run(
            [
                "panoramax_cli",
                "upload",
                "--api-url",
                "https://panoramax.openstreetmap.fr/",
                "img_logo/",
            ],
            check=True
        )
    except Exception as e:
        print(f"Erreur dans le mode auto vidéo : {e}")


if __name__ == "__main__":
    print_banner()
    menu()
