import change_gps_2
import kml_to_geojson
import auto_nadir
import subprocess as sp
import os

CAMERA = ""


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


def menu():
    choix = None
    while choix not in [1, 2, 3]:
        print(
            "1- Go Pro max"
            "\n"
            "2- Insta 360 one x2 \n"
            "3- Push panoramax OSM \n"
            "4- Exit"
        )
        choix = int(
            input(
                "Entrez le numero associé a la camera "
                "utilisé ou 3 si vous voulez arréter le programme: "
            )
        )
    if choix == 1:
        CAMERA = "Go Pro max"
        menu_go_pro()
    elif choix == 2:
        CAMERA = "Insta 360 one x2"
        menu_insta()
    elif choix == 3:
        loc_photos = None
        while loc_photos not in [1, 2, 3]:
            print(
                "1-img_to_be_changed/ \n"
                "2-img_to_be_changed/changed/ \n"
                "3-img_logo/ \n"
                "4-Exit"
            )
            loc_photos = int(
                input(
                    "Entré le nombre associez au chemin de vos photo ou 4 si vous voulez retourné au menu"
                )
            )
        if loc_photos == 1:
            path = "img_to_be_changed/"
        elif loc_photos == 2:
            path = "img_to_be_changed/changed/"
        elif loc_photos == 3:
            path = "img_logo/"
        else:
            menu()
        sp.run(
            ["panoramax_cli upload --api-url https://panoramax.openstreetmap.fr/", path]
        )
    else:
        exit


def menu_go_pro():
    choix = None
    while choix not in [1, 2, 3, 4]:
        print(
            "1-Ajuster les coordonnées GPS \n"
            "2-Ajouter un logo \n"
            "3-Revenir au choix de camera \n"
            "4-Exit"
        )
        choix = int(input("Entrez le numero associé a l'action de votre choix: "))
    if choix == 1:
        change_gps_2.main()
        menu_go_pro()
    elif choix == 2:
        loc_photos = None
        while loc_photos not in [1, 2]:
            print("1- img_to_be_changed/ \n" "2- img_to_be_changed/changed/")
            loc_photos = int(
                input("Entrez le numero associé au chemin de vos photos: ")
            )
        if loc_photos == 1:
            path = "img_to_be_changed/"
            # auto_nadir.auto(path)
        else:
            # auto_nadir.auto(path)
            path = "img_to_be_changed/changed/"
        sp.run(["./script_logo_insta.sh", path])
        menu_go_pro()
    elif choix == 3:
        menu()
    else:
        exit


def menu_insta():
    choix = None
    while choix not in [1, 2, 3, 4, 5]:
        print(
            "1-Ajuster les coordonnées GPS \n"
            "2-Ajouter un logo \n"
            "3-Revenir au choix de camera \n"
            "4-Adapter l'image a panoramax \n"
            "5-Exit"
        )
        choix = int(input("Entrez le numero associé a votre choix : "))
    if choix == 1:
        change_gps_2.main()
        menu_insta()
    elif choix == 2:
        loc_photos = None
        while loc_photos not in [1, 2]:
            print("1- img_to_be_changed/ \n" "2- img_to_be_changed/changed/")
            loc_photos = int(
                input("Entrez le numero associé au chemin de vos photos: ")
            )
        if loc_photos == 1:
            path = "img_to_be_changed/"
            # auto_nadir.auto(path)
            sp.run(["./script_logo_insta.sh", path])
        else:
            # auto_nadir.auto(path)
            path = "img_to_be_changed/changed/"
            sp.run(["./script_logo_insta.sh", path])
        menu_insta()
    elif choix == 3:
        menu()

    elif choix == 4:
        loc_photos = None
        while loc_photos not in [1, 2, 3]:
            print(
                "1- img_to_be_changed/ \n"
                "2- img_to_be_changed/changed/ \n"
                "3- img_logo/"
            )
            loc_photos = int(
                input("Entrez le numero associé au chemin de vos photos: ")
            )
        if loc_photos == 1:
            path = "img_to_be_changed/"
        elif loc_photos == 2:
            path = "img_to_be_changed/changed/"
        elif loc_photos == 3:
            path = "img_logo/"
        sp.run(["./meta_insta.sh", path])
        menu_insta()
    else:
        exit


menu()
