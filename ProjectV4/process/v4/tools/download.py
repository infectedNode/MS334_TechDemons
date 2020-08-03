import requests

import tensorflow as tf


def download_file_from_google_drive(file_id, destination, target_size=None):
    google_drive_base_url = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(google_drive_base_url, params={"id": file_id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {"id": file_id, "confirm": token}
        response = session.get(google_drive_base_url, params=params, stream=True)

    save_response_content(response, destination, target_size)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            return value

    return None


def save_response_content(response, destination, target_size=None):
    chunk_size = 32768

    progbar = tf.keras.utils.Progbar(target_size) if target_size is not None else None

    with open(destination, "wb") as file:
        for chunk_index, chunk in enumerate(response.iter_content(chunk_size)):
            if chunk:  # filter out keep-alive new chunks
                file.write(chunk)
                if progbar:
                    progbar.update(chunk_index * chunk_size)
