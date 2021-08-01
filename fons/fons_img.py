import os, sys
from typing import Any, List, Optional, Tuple

from PIL import Image

from conf import config

def scale_image(img_dict):
    temp_dir = img_dict.get("temp_dir")
    os.mkdir(temp_dir)
    if os.path.exists(temp_dir):
        outfile = os.path.join(temp_dir, os.path.basename(img_dict["selected_image"]))
        try:
            with Image.open(img_dict["selected_image"]) as im:
                im.thumbnail(img_dict["scale_size"])
                im.save(outfile, "JPEG")
                scaled_image = outfile
                status = "Image Scaled..."
        except OSError:
            status = f"Error: Cannot create {infile}."
            scaled_image = None
    else:
        status = f"{temp_dir} does not exist."
        scaled_image = None
    return status, scaled_image

def save_image(img_dict):
    try:
        _, ext = os.path.splitext(img_dict["scaled_image"])
        old = img_dict["scaled_image"]
        new = os.path.join(img_dict["saved_img_dir"], (img_dict["hex_file_name"] + ext))
        print("ch old", old)
        print("ch new", new)
        os.renames(old, new)
        print("ch 5")
        status = f'Saved, {img_dict["hex_file_name"]}\nin {img_dict["saved_img_dir"]}...'
        print("Saved image, deleted old...")
    except OSError:
        status = f"Error: Cannot save file."
    return status

def process_photo(img_dict):
    if img_dict["status"] == "setup_req":
        img_dict.update(config.config(section="fons_img"))
        img_dict["scale_size"] = (
            int(img_dict["scale_x"]),
            int(img_dict["scale_y"]))
        del img_dict["scale_x"], img_dict["scale_y"]
        return img_dict

    if img_dict["status"] == "scaled_req":
        img_dict["status"], img_dict["scaled_image"] = scale_image(img_dict)
        return img_dict

    if img_dict["status"] == "save_req":
# Reverse order, pad, convert to hex.
        file_name = "{1:0>6X}_{0:0>4X}".format(*img_dict["table_pk_fk"])
        img_dict["hex_file_name"] = file_name
        img_dict["status"] = save_image(img_dict)
        return img_dict


if __name__ == '__main__':

    img_dict = config.config(section="fons_gui")
    print(f"\nimg_dict= {img_dict.items()} \n")

    img_dict["status"] = "setup_req"
    process_photo(img_dict)
    print(f"\nimg_dict= {img_dict.items()} \n")

    img_dict["status"] = "scaled_req"
    img_dict["selected_image"] = "/home/chom/Pictures/pupillae_photos/0002.jpg"
    process_photo(img_dict)
    print(f"\nimg_dict= {img_dict.items()} \n")

    img_dict["status"] = "save_req"
    img_dict["table_pk_fk"] = (2000, 60000)
    process_photo(img_dict)
    print(f"\nimg_dict= {img_dict.items()} \n")
