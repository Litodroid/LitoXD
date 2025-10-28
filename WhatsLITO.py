# BY: HACK UNDERWAY  (mejorado)
import os
import sys
import requests
import json
from dotenv import load_dotenv
from colorama import Fore, Style, init
from argparse import ArgumentParser

# Inicializar Colorama
init(autoreset=True)

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Clave de API y host desde el archivo .env
api_key = os.getenv('RAPIDAPI_KEY')
api_host = os.getenv('RAPIDAPI_HOST')

# Comprobar credenciales
if not api_key or not api_host:
    print(f"{Fore.RED}Falta RAPIDAPI_KEY o RAPIDAPI_HOST en .env. Revisa tu archivo .env{Style.RESET_ALL}")
    print("Formato .env esperado:")
    print("RAPIDAPI_KEY=tu_clave_aqui")
    print("RAPIDAPI_HOST=whatsapp-data1.p.rapidapi.com")
    sys.exit(1)

# Función para imprimir el JSON con formato y colores (mejor manejo de listas/indentación)
def imprimir_json_coloreado(data, nivel=0):
    indent = "    " * nivel
    if isinstance(data, dict):
        for key, value in data.items():
            # key en cyan
            print(f"{indent}{Fore.CYAN}{key}{Style.RESET_ALL}:", end=" ")
            # renderizar value en siguiente nivel si es compuesto
            if isinstance(value, (dict, list)):
                print()  # salto de línea antes del objeto/array
                imprimir_json_coloreado(value, nivel + 1)
            else:
                # valor simple en amarillo
                print(f"{Fore.YELLOW}{value}{Style.RESET_ALL}")
    elif isinstance(data, list):
        for i, item in enumerate(data, 1):
            # índice en magenta
            print(f"{indent}{Fore.MAGENTA}[{i}]{Style.RESET_ALL}")
            imprimir_json_coloreado(item, nivel + 1)
    else:
        # valor simple
        print(f"{indent}{Fore.YELLOW}{data}{Style.RESET_ALL}")

# Función para consultar datos de WhatsApp (ruta: /number/<numero>)
def consultar_numero_whatsapp(numero_telefono, endpoint_path="number", timeout_seconds=10):
    # Construir URL y headers
    url = f"https://{api_host}/{endpoint_path}/{numero_telefono}"
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host,
        "User-Agent": "whatsapp-data-client/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout_seconds)

        # Manejo de códigos HTTP comunes
        if response.status_code in (401, 403):
            print(f"{Fore.RED}Error de autenticación ({response.status_code}). API key inválida o sin permisos.{Style.RESET_ALL}")
            # Si RapidAPI responde JSON con message, mostrarlo:
            try:
                print(response.json())
            except Exception:
                print(response.text)
            return

        if response.status_code == 429:
            print(f"{Fore.RED}Rate limit alcanzado (429). Espera o revisa tu plan en RapidAPI.{Style.RESET_ALL}")
            return

        # Levantar para otros 4xx/5xx y permitir catch más abajo
        response.raise_for_status()

        # Parsear JSON
        datos = response.json()

        # Imprimir JSON bien formateado y coloreado
        imprimir_json_coloreado(datos)

    except requests.exceptions.Timeout:
        print(f"{Fore.RED}Timeout: la solicitud tardó más de {timeout_seconds}s.{Style.RESET_ALL}")
    except requests.exceptions.HTTPError as http_err:
        # Mostrar status y cuerpo (si hay)
        print(f"{Fore.RED}Error HTTP: {http_err} (status {response.status_code}){Style.RESET_ALL}")
        try:
            print(response.json())
        except Exception:
            print(response.text)
    except requests.exceptions.RequestException as req_err:
        print(f"{Fore.RED}Error en la solicitud: {req_err}{Style.RESET_ALL}")
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: la respuesta no es JSON válido.{Style.RESET_ALL}")
        print("Respuesta cruda:")
        print(response.text if 'response' in locals() else "Sin respuesta")
    except Exception as err:
        print(f"{Fore.RED}Ocurrió un error inesperado: {err}{Style.RESET_ALL}")

def main():
    parser = ArgumentParser(description="Consulta API RapidAPI (whatsapp-data1) para un número o device_count")
    parser.add_argument("numero", nargs="?", help="Número de teléfono con código de país (ej: 59898297150)")
    parser.add_argument("--device-count", action="store_true", help="Usar endpoint /device_count/<numero> en lugar de /number/<numero>")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout en segundos para la petición (por defecto 10s)")
    args = parser.parse_args()

    # Banner
    print(Fore.GREEN + """
 __i
|---|    
|[_]|    
|:::|    
|:::|    
`\\   \\   
  \\_=_\\ 
Consulta de datos de número de WhatsApp
""" + Style.RESET_ALL)

    # Obtener número desde argumento o input
    if args.numero:
        numero = args.numero.strip()
    else:
        numero = input("Introduce el número de teléfono (con código de país): ").strip()

    if not numero:
        print(f"{Fore.RED}Debe ingresar un número de teléfono válido.{Style.RESET_ALL}")
        sys.exit(1)

    # Escoger endpoint
    endpoint = "device_count" if args.device_count else "number"

    # Llamar a la API
    consultar_numero_whatsapp(numero, endpoint_path=endpoint, timeout_seconds=args.timeout)

if __name__ == "__main__":
    main()
