# It display basic attributes such as the creation date, as well as EXIF data
# ./scorpion FILE1 [FILE2 ...]

# authorised_extension = ["jpg", "jpeg", "png", "gif", "bmp"]

# modify delete metadatas
# graphical interface

# """
# check argv *
# for each argv
#   open files
#   get metadata
#   put them in ther field
# ---[How to open multiple windows]---
# ---{Answer: you dont}---
# open window *
# [define all possible metadata]
# get all metadata
# display them in the view
# make them editable/deletable
# [how to edit/delete meadata]
# buttons: next - prev
# def handle_next(): / def handle_prev():
#   index = +1 OR -1
#   if index > argc
#       index = 0
#   else if index < 0
#       index = argc
#   call to fnct open_img_meta
# """

import sys
import customtkinter as ctk
from PIL import Image

index = 1

def main():

    argc = len(sys.argv)
    if argc < 2:
        print("Error Usage:")
        print("python scorpion.py FILE1 [FILE2 ...]")
        exit(1)
    for i in range(1, argc):
        try:
            Image.open(sys.argv[1])
        except Exception:
            print (f"Error oppening image {sys.argv[1]}")
            exit(1)

    def handle_prev_next(n_or_p):
        global index
        if n_or_p == 0:
            print("next")
            index += 1
        else:
            print("prev")
            index -= 1

        if index >= argc:
            index = 1
        elif index < 1:
            index = argc
        try:
            user_image = Image.open(sys.argv[index])
        except Exception:
            print (f"Error oppening image {sys.argv[index]}")
            exit(1)
        # update img
        # update meta

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

    prev_btn = ctk.CTkButton(main_area, text="prev", command=lambda: handle_prev_next(0))
    prev_btn.pack(anchor="s", padx=10)
    next_btn = ctk.CTkButton(main_area, text="next", command=lambda: handle_prev_next(1))
    next_btn.pack(anchor="s", padx=10)
    # comment mettre 2 bouttons sur la meme ligne
    ##########################################


    def handle_click():
        texte_saisi = mon_input.get()
        # check value
        var.set(texte_saisi)
        # edit image metadata
        print(var.get())


    try:
        user_image = Image.open(sys.argv[1])
    except Exception:
        print (f"Error oppening image {sys.argv[1]}")
        exit(1)


    ####### Image ratio and display #######
    original_width, original_height = user_image.size
    MAX_WIDTH = 550
    MAX_HEIGHT = 400
    ratio = min(MAX_WIDTH / original_width, MAX_HEIGHT / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)

    image_ctk = ctk.CTkImage(light_image=user_image, dark_image=user_image, size=(new_width, new_height))

    label_image = ctk.CTkLabel(master=main_area, image=image_ctk, text="")
    label_image.pack()
    ##########################################


    var = ctk.StringVar(value="Bonjour")
    print(var.get())
    mon_input = ctk.CTkEntry(master=sidebar, width=150, height=35, border_width=0, textvariable=var)
    mon_input.pack(anchor="n", pady=10, padx=10)

    update_btn = ctk.CTkButton(sidebar, text="Edit", command=handle_click)
    update_btn.pack(anchor="n", padx=10)
    ## ##

    app.mainloop()


if __name__ == '__main__':
    main()