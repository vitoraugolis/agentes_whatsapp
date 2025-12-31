#!/usr/bin/env python3
"""
Ponto de entrada principal para o webhook WhatsApp
Este arquivo é usado pelo Render.com como entrypoint
"""

from webhook_whatsapp import app

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
