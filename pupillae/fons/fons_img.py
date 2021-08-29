import os
import sys
from typing import Any, Dict, Tuple, Union

from PIL import Image

from pupillae.conf import config

def scale_image(img_dict: Dict[str, Union[str, Tuple[int, int]]]) -> Union[str, Any]:
    """Scales image according to kwargs.

    Parameters
    ----------
    `img_dict` : dict

    Returns
    -------
    `status`: str
    `scaled_image`: str
        Path

    Raises
    ------
    Exception
        Returns [string, None]

    """
    temp_dir = img_dict.get("temp_img_dir")
    outfile = os.path.join(temp_dir, os.path.basename(img_dict["selected_image"]))
    try:
        with Image.open(img_dict["selected_image"]) as im:
            im.thumbnail(img_dict["scale_size"])
            im.save(outfile, "JPEG")
            scaled_image = outfile
            status = "Image Scaled..."
    except Exception:
        status = f"Error: Cannot create {infile}."
        scaled_image = None
    return status, scaled_image

def save_image(img_dict: Dict[str, Union[str, Tuple[int, int]]]) -> str:
    """Save image according to kwargs.

    Parameters
    ----------
    `img_dict` : dict

    Returns
    -------
    `status`: str

    Raises
    ------
    Exception
        Returns [string]

    """
    try:
        _, ext = os.path.splitext(img_dict["scaled_image"])
        new = os.path.join(img_dict["saved_img_dir"], (img_dict["hex_file_name"] + ext))
        with Image.open(img_dict["scaled_image"]) as im:
            im.save(new, "JPEG")
        os.remove(img_dict["scaled_image"])
        print("Saved image, deleted temporary image...")
        status = f'Saved: {img_dict["hex_file_name"]}\nin {img_dict["saved_img_dir"]}'
    except Exception:
        status = f"Error: Cannot save file."
    return status

def process_photo(img_dict: Dict[str, str]) -> Dict[str, Union[str, Tuple[int, int]]]:
    """Update `img_dict`, save/scale image according to kwargs.

    Parameters
    ----------
    `img_dict` : dict

    Returns
    -------
    `img_dict`: dict

    """
    if img_dict["status"] == "setup_req":
        img_params = config.config(section="fons_img")
        config.initialise_dirs(img_params)
        img_dict.update(img_params)
        img_dict["scale_size"] = (
            int(img_dict["scale_x"]),
            int(img_dict["scale_y"]))
        del img_dict["scale_x"], img_dict["scale_y"]
        img_dict["status"] = "--Complete"
        return img_dict

    if img_dict["status"] == "scaled_req" and img_dict["selected_image"] != None:
        img_dict["status"], img_dict["scaled_image"] = scale_image(img_dict)
        return img_dict

    if img_dict["status"] == "save_req" and img_dict["scaled_image"] != None:
# Reverse order, pad, convert to hex.
# Image will not save if m_id is None, and temporary images will persist.
        file_name = "{1:0>4X}_{0:0>4X}".format(*img_dict["table_pk_fk"])
        img_dict["hex_file_name"] = file_name
        img_dict["status"] = save_image(img_dict)
        return img_dict


#if __name__ == '__main__':
