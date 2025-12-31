#!/usr/bin/env python3
"""Script para enviar mensagem via WhatsApp Business API"""
import os
from dotenv import load_dotenv
import requests
import sys

load_dotenv()

WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')

def enviar_mensagem(numero, mensagem):
    """Envia mensagem via API do WhatsApp"""
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WHATSAPP_TOKEN}"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": mensagem
        }
    }

    print("="*70)
    print("📤 ENVIANDO MENSAGEM VIA WHATSAPP API")
    print("="*70)
    print(f"De: +55 19 3167-2482 (ID: {WHATSAPP_PHONE_NUMBER_ID})")
    print(f"Para: {numero}")
    print(f"Mensagem: {mensagem}")
    print("="*70)

    try:
        response = requests.post(url, headers=headers, json=payload)

        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📋 Resposta:\n{response.json()}\n")

        if response.status_code == 200:
            print("✅ Mensagem enviada com sucesso!")
            data = response.json()
            if 'messages' in data:
                print(f"🆔 Message ID: {data['messages'][0]['id']}")
        else:
            print("❌ Erro ao enviar mensagem")

        print("="*70)
        return response.json()

    except Exception as e:
        print(f"❌ Erro: {e}")
        print("="*70)
        return None

if __name__ == '__main__':
    print("\n🤖 BOT WHATSAPP - ENVIO DE MENSAGEM")
    print()

    if len(sys.argv) > 1:
        numero = sys.argv[1]
    else:
        numero = input("Digite o número (com código do país, ex: 5519999999999): ").strip()

    if len(sys.argv) > 2:
        mensagem = sys.argv[2]
    else:
        mensagem = input("Digite a mensagem (ou Enter para usar padrão): ").strip()
        if not mensagem:
            mensagem = "✅ Teste de envio via API! O bot está funcionando."

    if numero:
        enviar_mensagem(numero, mensagem)
    else:
        print("❌ Número não fornecido")
