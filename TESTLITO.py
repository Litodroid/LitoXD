import os
import sys
import requests
import json
from dotenv import load_dotenv
from colorama import Fore, Style, init
from argparse import ArgumentParser

# Inicializar Colorama
init(autoreset=True)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Clave y host de RapidAPI
api_key = os.getenv("RAPIDAPI_KEY")
api_host = os.getenv("RAPIDAPI_HOST")

# Verificación de variables
if not api_key or not api_host:
    print(f"{Fore.RED}❌ Faltan variables en .env{Style.RESET_ALL}")
    print("Debe existir un archivo .env con el siguiente formato:")
    print("RAPIDAPI_KEY=tu_clave_aqui")
    print("RAPIDAPI_HOST=whatsapp-data1.p.rapidapi.com")
    sys.exit(1)

# Función para imprimir JSON con colores
def imprimir_json_coloreado(data, nivel=0):
    indent = "    " * nivel
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{indent}{Fore.CYAN}{key}{Style.RESET_ALL}:", end=" ")
            if isinstance(value, (dict, list)):
                print()
                imprimir_json_coloreado(value, nivel + 1)
            else:
                print(f"{Fore.YELLOW}{value}{Style.RESET_ALL}")
    elif isinstance(data, list):
        for i, item in enumerate(data, 1):
            print(f"{indent}{Fore.MAGENTA}[{i}]{Style.RESET_ALL}")
            imprimir_json_coloreado(item, nivel + 1)
    else:
        print(f"{indent}{Fore.YELLOW}{data}{Style.RESET_ALL}")

# Función principal de consulta
def consultar_numero_whatsapp(numero_telefono, endpoint_path="number", timeout_seconds=10):
    url = f"https://{api_host}/{endpoint_path}/{numero_telefono}"

    headers = {
        "x-rapidapi-key": api_key.strip(),
        "x-rapidapi-host": api_host.strip(),
        "User-Agent": "whatsapp-data-client/1.0"
    }

    print(f"{Fore.CYAN}Consultando API:{Style.RESET_ALL} {url}")

    try:
        response = requests.get(url, headers=headers, timeout=timeout_seconds)

        if response.status_code in (401, 403):
            print(f"{Fore.RED}❌ Error de autenticación ({response.status_code}): API Key inválida o sin permisos.{Style.RESET_ALL}")
            try:
                print(response.json())
            except Exception:
                print(response.text)
            return

        if response.status_code == 429:
            print(f"{Fore.RED}⚠️ Límite de peticiones alcanzado (429). Espera o revisa tu plan en RapidAPI.{Style.RESET_ALL}")
            return

        response.raise_for_status()

        try:
            data = response.json()
            print(f"{Fore.GREEN}✅ Respuesta recibida correctamente:{Style.RESET_ALL}")
            imprimir_json_coloreado(data)
        except json.JSONDecodeError:
            print(f"{Fore.RED}Error: la respuesta no es JSON válido.{Style.RESET_ALL}")
            print(response.text)

    except requests.exceptions.Timeout:
        print(f"{Fore.RED}⏱️ Timeout: la solicitud tardó más de {timeout_seconds}s.{Style.RESET_ALL}")
    except requests.exceptions.RequestException as err:
        print(f"{Fore.RED}Error en la solicitud: {err}{Style.RESET_ALL}")

# Menú principal
def main():
    parser = ArgumentParser(description="Consulta API RapidAPI (whatsapp-data1) para un número o device_count")
    parser.add_argument("numero", nargs="?", help="Número de teléfono con código de país (ej: 59898297150)")
    parser.add_argument("--device-count", action="store_true", help="Usar endpoint /device_count/<numero> en lugar de /number/<numero>")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout en segundos (por defecto 10)")
    args = parser.parse_args()

    print(Fore.GREEN + """
╔══════════════════════════════════════╗
║     CONSULTA WHATSAPP DATA API       ║
╚══════════════════════════════════════╝
""" + Style.RESET_ALL)

    if args.numero:
        numero = args.numero.strip()
    else:
        numero = input("Introduce el número de teléfono (con código de país): ").strip()

    if not numero:
        print(f"{Fore.RED}Debe ingresar un número válido.{Style.RESET_ALL}")
        sys.exit(1)

    endpoint = "device_count" if args.device_count else "number"
    consultar_numero_whatsapp(numero, endpoint_path=endpoint, timeout_seconds=args.timeout)

if __name__ == "__main__":
    main()
