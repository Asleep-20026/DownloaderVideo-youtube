import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

def obtener_enlace_descarga(url, calidad='4k'):
    try:
        # Obtener el contenido de la página web
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar el elemento de la etiqueta <script> que contiene la información del video
        script_tag = soup.find('script', string=lambda x: 'var ytInitialPlayerResponse' in str(x))

        # Extraer la URL del video de alta calidad (idealmente 4K)
        video_info = str(script_tag).split('ytInitialPlayerResponse = ')[1].split(';</script>')[0]
        streaming_data = json.loads(video_info)['streamingData']
        
        # Buscar el stream con la calidad deseada
        if calidad == '4k':
            formats = streaming_data.get('formats')
        else:
            formats = streaming_data.get('adaptiveFormats')

        if formats:
            for stream in formats:
                if stream.get('qualityLabel') == calidad:
                    video_url = stream.get('url')
                    if video_url:
                        print("Enlace de descarga encontrado:", video_url)
                        return video_url
        
        print(f"No se pudo encontrar un enlace de descarga del video en calidad {calidad}.")
        return None
    except Exception as e:
        print("Ocurrió un error durante la obtención del enlace de descarga:", e)
        return None


def descargar_video(url_video, nombre_archivo):
    try:
        video_url = obtener_enlace_descarga(url_video)
        if video_url:
            # Descargar el video directamente
            with open(nombre_archivo, "wb") as f:
                response = requests.get(video_url, stream=True)
                response.raise_for_status()  # Lanzar una excepción si hay un error con la solicitud

                total_length = int(response.headers.get('content-length'))
                if total_length is None:
                    print("No se puede determinar el tamaño del archivo. Descargando sin mostrar progreso.")
                    f.write(response.content)
                else:
                    with tqdm(total=total_length, desc="Descargando video", unit="bytes", unit_scale=True) as pbar:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
            print("Descarga completada.")
        else:
            print("No se pudo obtener el enlace de descarga del video.")
    except requests.exceptions.RequestException as e:
        print("Ocurrió un error durante la descarga del video:", e)
    except Exception as e:
        print("Ocurrió un error inesperado:", e)


url_video = 'https://youtu.be/XvlRAnASaPw'
nombre_archivo = 'video_descargado.mp4'

descargar_video(url_video, nombre_archivo)
