import os
import sys
import customtkinter as ctk
from PIL import Image, ExifTags

index = 1

def main():
    MAX_WIDTH = 550
    MAX_HEIGHT = 400

    argc = len(sys.argv)
    if argc < 2:
        print("Error Usage:")
        print("python scorpion.py FILE1 [FILE2 ...]")
        exit(1)
    for i in range(1, argc):
        try:
            Image.open(sys.argv[i])
        except Exception:
            print (f"Error oppening image {sys.argv[i]}")
            exit(1)

    ####### Window creation and zone creation #######
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()
    app.title("Scorpion - images metadata editor")   # Titre de la fenêtre

    app.geometry("800x600")
    app.resizable(False, False)

    sidebar = ctk.CTkFrame(master=app, width=100, fg_color="gray15", corner_radius=10)
    sidebar.pack(side="right", fill="y")
    sidebar.pack_propagate(False)

    main_area = ctk.CTkFrame(master=app, fg_color="transparent")
    main_area.pack(side="left", expand=True, fill="both")
    ##########################################


    ####### Image ratio and display #######
    try:
        user_img = Image.open(sys.argv[1])
    except Exception:
        print (f"Error oppening image {sys.argv[1]}")
        exit(1)

    original_width, original_height = user_img.size
    ratio = min(MAX_WIDTH / original_width, MAX_HEIGHT / original_height)
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)

    image_ctk = ctk.CTkImage(light_image=user_img, dark_image=user_img, size=(new_width, new_height))

    label_image = ctk.CTkLabel(master=main_area, image=image_ctk, text="")
    label_image.pack(side="top", pady=(60, 20))
    ##########################################

    button_frame = ctk.CTkFrame(master=main_area, fg_color="transparent")
    button_frame.pack(side="bottom", pady=(0, 20))
    prev_btn = ctk.CTkButton(button_frame, text="prev", command=lambda: handle_prev_next(0))
    prev_btn.pack(side="left", padx=50)
    next_btn = ctk.CTkButton(button_frame, text="next", command=lambda: handle_prev_next(1))
    next_btn.pack(side="right", padx=50)

    infos = extract_exif_data(user_img)

    filename_var = add_metadata_row(sidebar, 0, "Filename:", user_img.filename)
    format_var = add_metadata_row(sidebar, 1, "Format:", user_img.format)
    dimension_var = add_metadata_row(sidebar, 2, "Dimension:", f"{user_img.size[0]} x {user_img.size[1]}")
    mode_var = add_metadata_row(sidebar, 3, "Mode:", user_img.mode)
    filesize_var = add_metadata_row(sidebar, 4, "File size:", f"{os.path.getsize(user_img.filename)} octets")
    copyright_var = add_metadata_row(sidebar, 5, "Copyright:", infos.get('copyright'))
    hardware_var = add_metadata_row(sidebar, 6, "Hardware:", f"{infos.get('make', '')} {infos.get('model', '')}".strip())
    settings_var = add_metadata_row(sidebar, 7, "Settings:", f"f/{infos.get('f_number')} | {infos.get('exposure_time')}s | ISO {infos.get('iso')}")
    focal_var = add_metadata_row(sidebar, 8, "Focal length:", f"{infos.get('focal_length')}mm")
    date_var = add_metadata_row(sidebar, 9, "Taken on:", f"{infos.get('date')} at {infos.get('time')}")
    gps_var  = add_metadata_row(sidebar, 10, "Gps:", f"{infos.get('gps_lat')}, {infos.get('gps_lon')}")



    def handle_prev_next(n_or_p):
        global index
        if n_or_p == 0:
            index -= 1
        else:
            index += 1
        if index > argc - 1:
            index = 1
        elif index < 1:
            index = argc - 1

        try:
            new_img = Image.open(sys.argv[index])
        except Exception:
            print (f"Error oppening image {sys.argv[index]}")
            exit(1)
        original_width, original_height = new_img.size

        ratio = min(MAX_WIDTH / original_width, MAX_HEIGHT / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        new_ctk_img = ctk.CTkImage(light_image=new_img, dark_image=new_img, size=(new_width, new_height))
        label_image.configure(image=new_ctk_img)

        filename_var.set(new_img.filename)
        format_var.set(new_img.format)
        dimension_var.set(f"{new_img.size[0]} x {new_img.size[1]}")
        mode_var.set(new_img.mode)
        filesize_var.set(f"{os.path.getsize(new_img.filename)} octets")

        new_infos = extract_exif_data(new_img)
        copyright_var.set(new_infos.get('copyright'))
        hardware_var.set(f"{new_infos.get('make', '')} {new_infos.get('model', '')}".strip())
        settings_var.set(f"f/{new_infos.get('f_number')} | {new_infos.get('exposure_time')}s | ISO {new_infos.get('iso')}")
        focal_var.set(f"{new_infos.get('focal_length')}mm")
        date_var.set(f"{new_infos.get('date')} at {new_infos.get('time')}")
        gps_var.set(f"{new_infos.get('gps_lat')}, {new_infos.get('gps_lon')}")


    app.mainloop()



def add_metadata_row(parent, row_idx, title_text, initial_value):
    default_font = ctk.CTkFont(family="segoe ui", size=12)
    bold_font = ctk.CTkFont(family="segoe ui", size=12, weight="bold")

    title_lbl = ctk.CTkLabel(master=parent, text=title_text, font=bold_font, anchor="w")
    title_lbl.grid(row=row_idx, column=0, sticky="nw", padx=(5, 2), pady=2)
    
    var = ctk.StringVar(value=initial_value)
    val_lbl = ctk.CTkLabel(master=parent, textvariable=var, font=default_font, wraplength=150, justify="left", anchor="w")
    val_lbl.grid(row=row_idx, column=1, sticky="nw", padx=(0, 5), pady=2)
    
    return var


def extract_exif_data(img):
    exif_data = img.getexif()
    if not exif_data:
        return {}

    TAG_IDS = {name: tag_id for tag_id, name in ExifTags.TAGS.items()}
    GPS_IDS = {name: tag_id for tag_id, name in ExifTags.GPSTAGS.items()}

    exif = exif_data.get_ifd(TAG_IDS.get("ExifOffset", 0x8769)) or {}
    gps = exif_data.get_ifd(TAG_IDS.get("GPSInfo", 0x8825)) or {}

    date_original = exif.get(TAG_IDS.get("DateTimeOriginal"), None)
    if date_original:
        clean_date = date_original.split(" ")[0].replace(":", "-")
        clean_time = date_original.split(" ")[1]
    else:
        clean_date = "N/A"
        clean_time = "N/A"

    return {
        # Infos générales
        "make": exif_data.get(TAG_IDS.get("Make"), "N/A"),
        "model": exif_data.get(TAG_IDS.get("Model"), "N/A"),
        "copyright": exif_data.get(TAG_IDS.get("Copyright"), "N/A"),
        
        # Réglages (exif)
        "exposure_time": exif.get(TAG_IDS.get("ExposureTime"), "N/A"),
        "f_number": exif.get(TAG_IDS.get("FNumber"), "N/A"),
        "iso": exif.get(TAG_IDS.get("ISOSpeedRatings"), "N/A"),
        "focal_length": exif.get(TAG_IDS.get("FocalLength"), "N/A"),
        "date": clean_date,
        "time": clean_time,
        
        # Coordonnées (gps)
        "gps_lat": gps.get(GPS_IDS.get("GPSLatitude"), "N/A"),
        "gps_lon": gps.get(GPS_IDS.get("GPSLongitude"), "N/A")
    }

if __name__ == '__main__':
    main()