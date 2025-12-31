#!/usr/bin/env python3
"""
Webhook para receber mensagens do WhatsApp via Make
Endpoint: https://agentes-whatsapp.onrender.com
"""

from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from enviar_mensagem import enviar_mensagem
import anthropic

load_dotenv()

app = Flask(__name__)

# Configurações
VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'confirmacaowebhookguara')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# Cliente Anthropic
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def processar_mensagem_com_claude(mensagem_usuario):
    """Processa mensagem do usuário com Claude e retorna resposta"""
    try:
        if not ANTHROPIC_API_KEY:
            print("❌ ERRO: ANTHROPIC_API_KEY não configurada!")
            return "Erro de configuração: API key não encontrada."

        print(f"🔑 API Key presente: {ANTHROPIC_API_KEY[:20]}...")

        # Tenta com modelo mais recente primeiro, fallback para versões anteriores
        modelos = [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-sonnet-20240229"
        ]

        mensagem = None
        for modelo in modelos:
            try:
                print(f"🔄 Tentando modelo: {modelo}")
                mensagem = client.messages.create(
                    model=modelo,
                    max_tokens=1024,
                    messages=[
                        {"role": "user", "content": mensagem_usuario}
                    ]
                )
                print(f"✅ Sucesso com modelo: {modelo}")
                break
            except Exception as model_error:
                print(f"❌ Falha com {modelo}: {model_error}")
                continue

        if not mensagem:
            return "Erro: Nenhum modelo Claude disponível para esta API key."
        return mensagem.content[0].text
    except Exception as e:
        print(f"❌ Erro ao processar com Claude: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return f"Desculpe, ocorreu um erro: {type(e).__name__}"


@app.route('/webhook', methods=['GET'])
def verificar_webhook():
    """
    Endpoint para verificação do webhook (GET)
    Usado pelo Make ou WhatsApp para validar o webhook
    """
    # Pega os parâmetros da query string
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    print("="*70)
    print("🔍 VERIFICAÇÃO DE WEBHOOK")
    print("="*70)
    print(f"Mode: {mode}")
    print(f"Token recebido: {token}")
    print(f"Token esperado: {VERIFY_TOKEN}")
    print(f"Challenge: {challenge}")
    print("="*70)

    # Verifica se o token corresponde
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("✅ Token verificado com sucesso!")
        return challenge, 200
    else:
        print("❌ Falha na verificação do token")
        return 'Forbidden', 403


@app.route('/webhook', methods=['POST'])
def receber_mensagem():
    """
    Endpoint para receber mensagens (POST)
    Recebe dados do Make via HTTP request
    """
    try:
        data = request.get_json()

        print("="*70)
        print("📨 MENSAGEM RECEBIDA DO MAKE")
        print("="*70)
        print(f"Dados recebidos: {data}")
        print("="*70)

        # Extrai informações da mensagem
        # Suporta múltiplos formatos do WhatsApp/Make
        numero_remetente = data.get('from') or data.get('numero') or data.get('phone')

        # Tenta extrair a mensagem de diferentes formatos
        mensagem_texto = None
        if 'text' in data and isinstance(data['text'], dict) and 'body' in data['text']:
            # Formato WhatsApp API: {"text": {"body": "mensagem"}}
            mensagem_texto = data['text']['body']
        elif 'message' in data:
            # Formato simples: {"message": "mensagem"}
            mensagem_texto = data['message']
        elif 'mensagem' in data:
            # Formato português: {"mensagem": "mensagem"}
            mensagem_texto = data['mensagem']
        elif 'text' in data and isinstance(data['text'], str):
            # Formato direto: {"text": "mensagem"}
            mensagem_texto = data['text']

        if not numero_remetente or not mensagem_texto:
            print("❌ Dados incompletos na requisição")
            return jsonify({
                "status": "error",
                "message": "Campos 'from' e 'message' são obrigatórios"
            }), 400

        print(f"📱 De: {numero_remetente}")
        print(f"💬 Mensagem: {mensagem_texto}")
        print("="*70)

        # Processa a mensagem com Claude
        print("🤖 Processando com Claude...")
        resposta_claude = processar_mensagem_com_claude(mensagem_texto)
        print(f"💡 Resposta do Claude: {resposta_claude}")
        print("="*70)

        # Envia resposta via WhatsApp
        print("📤 Enviando resposta via WhatsApp...")
        resultado_envio = enviar_mensagem(numero_remetente, resposta_claude)

        if resultado_envio:
            return jsonify({
                "status": "success",
                "message": "Mensagem processada e resposta enviada",
                "resposta_enviada": resposta_claude
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Erro ao enviar resposta"
            }), 500

    except Exception as e:
        print(f"❌ Erro ao processar requisição: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se o servidor está funcionando"""
    return jsonify({
        "status": "ok",
        "message": "Webhook WhatsApp está funcionando"
    }), 200


@app.route('/', methods=['GET', 'POST'])
def index():
    """Página inicial - também aceita POST para compatibilidade com Make"""
    if request.method == 'POST':
        # Redireciona POST requests para o handler de webhook
        return receber_mensagem()

    # GET request - retorna informações da API
    return jsonify({
        "app": "WhatsApp Webhook",
        "version": "1.0",
        "endpoints": {
            "webhook_verification": "GET /webhook",
            "receive_message": "POST /webhook ou POST /",
            "health": "GET /health"
        }
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("="*70)
    print("🚀 INICIANDO SERVIDOR WEBHOOK WHATSAPP")
    print("="*70)
    print(f"🌐 Porta: {port}")
    print(f"🔑 Token de verificação: {VERIFY_TOKEN}")
    print("="*70)
    print("\nEndpoints disponíveis:")
    print("  GET  /           - Informações da API")
    print("  GET  /health     - Health check")
    print("  GET  /webhook    - Verificação do webhook")
    print("  POST /webhook    - Receber mensagens")
    print("="*70)

    app.run(host='0.0.0.0', port=port, debug=True)
