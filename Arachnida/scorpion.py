# It display basic attributes such as the creation date, as well as EXIF data
# ./scorpion FILE1 [FILE2 ...]

# authorised_extension = ["jpg", "jpeg", "png", "gif", "bmp"]

# modify delete metadatas
# graphical interface

import customtkinter as ctk

# 1. Configuration du thème (Optionnel, à mettre avant de créer la fenêtre)
ctk.set_appearance_mode("dark")        # Modes : "system" (suit Windows/Mac), "dark", "light"
ctk.set_default_color_theme("blue")    # Thèmes : "blue", "green", "dark-blue"

# 2. Création de la fenêtre
app = ctk.CTk()
app.title("Scorpion - images metadata editor")   # Titre de la fenêtre

largeur = 800
hauteur = 600
app.geometry(f"{largeur}x{hauteur}")
app.minsize(largeur, hauteur)
app.maxsize(largeur, hauteur)
app.resizable(False, False)

sidebar = ctk.CTkScrollableFrame(app, width=200, corner_radius=10)
sidebar.pack(side="right", fill="y")

main_area = ctk.CTkFrame(master=app, fg_color="transparent")
main_area.pack(side="left", expand=True, fill="both")


title_label = ctk.CTkLabel(main_area, text="Tableau de bord", font=("segoe ui", 20, "bold"))
title_label.pack(anchor="n", pady=(10, 0))


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
    print("Valeur actuelle :", combo.get())

btn = ctk.CTkButton(main_area, text="Récupérer l'état", command=valider)
btn.pack(anchor="w", pady=5)



app.mainloop()



# def main():
# 	dwd


# if __name__ == '__main__':
#     main()