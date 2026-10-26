# It display basic attributes such as the creation date, as well as EXIF data
# ./scorpion FILE1 [FILE2 ...]

# authorised_extension = ["jpg", "jpeg", "png", "gif", "bmp"]

# modify delete metadatas
# graphical interface

# """
# check argv *
# for each argv
# [How to open multiple windows]
# {Answer: you dont}
# {buttons: next - prev}
# {index depending on next prev}
# {everything in a loop}
# {at the start off the loop check the index depending on that open image infos from the selected file}
# [How to make edit works]
#   open image *
#   open window *
#   [define all possible metadata]
#   get all metadata
#   display them in the view
#   make them editable/deletable
#   [how to edit/delete meadata]
# """

import sys
import customtkinter as ctk
from PIL import Image

def main():

    argc = len(sys.argv)
    if argc < 2:
        print("Error Usage:")
        print("python scorpion.py FILE1 [FILE2 ...]")
        exit(1)
    for i in range(1, argc):
        # tableau d'image
        try:
            user_image = Image.open(sys.argv[1])
        except Exception:
            print (f"Error oppening image {sys.argv[1]}")
            exit(1)

        ####### Window creation and zone creation #######
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        app = ctk.CTk()
        app.title("Scorpion - images metadata editor")   # Titre de la fenêtre

        app.geometry("800x600")
        app.resizable(False, False)

        sidebar = ctk.CTkScrollableFrame(master=app, width=200, corner_radius=10)
        sidebar.pack(side="right", fill="y")

        main_area = ctk.CTkFrame(master=app, fg_color="transparent")
        main_area.pack(side="left", expand=True, fill="both")
        ##########################################



        title_label = ctk.CTkLabel(main_area, text="Tableau de bord", font=("segoe ui", 20, "bold"))
        title_label.pack(anchor="n", pady=(10, 0))



        ####### Image ratio and display #######
        largeur_origine, hauteur_origine = user_image.size
        MAX_LARGEUR = 550
        MAX_HAUTEUR = 400
        ratio = min(MAX_LARGEUR / largeur_origine, MAX_HAUTEUR / hauteur_origine)
        nouvelle_largeur = int(largeur_origine * ratio)
        nouvelle_hauteur = int(hauteur_origine * ratio)

        mon_image_ctk = ctk.CTkImage(light_image=user_image, dark_image=user_image, size=(nouvelle_largeur, nouvelle_hauteur))

        label_image = ctk.CTkLabel(master=main_area, image=mon_image_ctk, text="")
        label_image.pack()
        ##########################################



        data_label = ctk.CTkLabel(main_area, text="Modifie moi!", font=("segoe ui", 14))
        data_label.pack(anchor="w", pady=(10, 0), padx=10)

        mon_input = ctk.CTkEntry(
            sidebar,
            width=150,
            height=35,
            border_width=0,
            placeholder_text="Écris ce que tu veut",
            show=""
        )
        mon_input.pack(anchor="n", pady=10, padx=10)

        def handle_click():
            texte_saisi = mon_input.get()
            data_label.configure(text=texte_saisi)

        action_btn = ctk.CTkButton(sidebar, text="Valider", command=handle_click)
        action_btn.pack(anchor="n", padx=10)


        def selection_change(choice):
            print(f"Option sélectionnée : {choice}")

        # Création du menu déroulant
        combo = ctk.CTkComboBox(
            master=main_area,
            values=["Actif", "En attente", "Archivé"],
            command=selection_change
        )
        combo.pack(anchor="w", pady=10)

        # Récupérer la valeur actuelle
        def valider():
            print(f"Valeur actuelle : {combo.get()}")

        btn = ctk.CTkButton(main_area, text="Récupérer l'état", command=valider)
        btn.pack(anchor="w", pady=5)

        app.mainloop()


if __name__ == '__main__':
    main()