# BY: HACK UNDERWAY - Versión actualizada para whatsapp-data.p.rapidapi.com

import os
import sys
import requests
import json
from dotenv import load_dotenv
from colorama import Fore, Style, init
from argparse import ArgumentParser

# Inicializar Colorama
init(autoreset=True)

# Cargar variables desde .env
load_dotenv()

# Leer clave y host desde .env
api_key = os.getenv("RAPIDAPI_KEY")
api_host = os.getenv("RAPIDAPI_HOST")

# Validar variables
if not api_key or not api_host:
    print(f"{Fore.RED}❌ Faltan variables RAPIDAPI_KEY o RAPIDAPI_HOST en el archivo .env{Style.RESET_ALL}")
    print("Ejemplo de archivo .env correcto:")
    print("RAPIDAPI_KEY=tu_clave_aqui")
    print("RAPIDAPI_HOST=whatsapp-data.p.rapidapi.com")
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

# -------------------------------
#  CONSULTA API WHATSAPP-DATA
# -------------------------------
def consultar_numero_whatsapp(numero_telefono, timeout_seconds=10):
    url = f"https://{api_host}/bizname?phone={numero_telefono}"

    headers = {
        "x-rapidapi-key": api_key.strip(),
        "x-rapidapi-host": api_host.strip(),
        "User-Agent": "whatsapp-data-client/2.0"
    }

    print(f"{Fore.CYAN}Consultando API:{Style.RESET_ALL} {url}\n")

    try:
        response = requests.get(url, headers=headers, timeout=timeout_seconds)

        if response.status_code in (401, 403):
            print(f"{Fore.RED}❌ Error de autenticación ({response.status_code}) — API Key inválida o falta suscripción.{Style.RESET_ALL}")
            try:
                print(response.json())
            except Exception:
                print(response.text)
            return

        if response.status_code == 429:
            print(f"{Fore.RED}⚠️  Límite de peticiones alcanzado (429). Espera o revisa tu plan RapidAPI.{Style.RESET_ALL}")
            return

        response.raise_for_status()

        try:
            data = response.json()
            print(f"{Fore.GREEN}✅ Respuesta recibida correctamente:{Style.RESET_ALL}\n")
            imprimir_json_coloreado(data)
        except json.JSONDecodeError:
            print(f"{Fore.RED}Error: la respuesta no es JSON válido.{Style.RESET_ALL}")
            print(response.text)

    except requests.exceptions.Timeout:
        print(f"{Fore.RED}⏱️ Timeout: la solicitud tardó más de {timeout_seconds}s.{Style.RESET_ALL}")
    except requests.exceptions.RequestException as err:
        print(f"{Fore.RED}Error en la solicitud: {err}{Style.RESET_ALL}")

# -------------------------------
#  MENÚ PRINCIPAL
# -------------------------------
def main():
    parser = ArgumentParser(description="Consulta API RapidAPI (whatsapp-data) para obtener información de un número")
    parser.add_argument("numero", nargs="?", help="Número de teléfono con código de país (ej: 13022612667)")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout en segundos (por defecto 10)")
    args = parser.parse_args()

    print(Fore.GREEN + """
╔══════════════════════════════════════╗
║     CONSULTA WHATSAPP DATA LITO      ║
╚══════════════════════════════════════╝
""" + Style.RESET_ALL)

    if args.numero:
        numero = args.numero.strip()
    else:
        numero = input("Introduce el número de teléfono (con código de país): ").strip()

    if not numero:
        print(f"{Fore.RED}Debe ingresar un número válido.{Style.RESET_ALL}")
        sys.exit(1)

    consultar_numero_whatsapp(numero, timeout_seconds=args.timeout)

if __name__ == "__main__":
    main()
