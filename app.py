# app.py (versão final para o Railway com Dockerfile)

from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import io
import re

app = Flask(__name__)

def extract_data_from_ocr(ocr_text):
    """Extrai informações do comprovante de transferência"""
    data = {}

    try:
        # Valor
        value_match = re.search(r'Valor\s+R\$\s*([\d\.,]+)', ocr_text, re.IGNORECASE)
        if value_match:
            valor_str = value_match.group(1).replace('.', '').replace(',', '.')
            data['valor'] = float(valor_str)

        # Destino - Nome (corrigido para capturar nome completo sem duplicação)
        nome_fragmentado = []

        destino_match = re.search(r'Destino\s+([^\n]+)', ocr_text, re.IGNORECASE)
        if destino_match:
            destino_nome = destino_match.group(1).strip()
            if not destino_nome.lower().startswith("nome"):
                nome_fragmentado.append(destino_nome)

        nome_match = re.search(r'Nome\s+([^\n]+)', ocr_text, re.IGNORECASE)
        if nome_match:
            nome_linha = nome_match.group(1).strip()
            nome_fragmentado.append(nome_linha)

        if nome_fragmentado:
            nome = ' '.join(nome_fragmentado)
            nome = re.sub(r'\bNome\b', '', nome, flags=re.IGNORECASE)
            nome = re.sub(r'\s+CNP[JFP].*$', '', nome)
            nome = ' '.join(nome.split())
            data['destino_nome'] = nome

        # Destino - Instituição (refinado para buscar nomes bancários e ignorar ruído)
        instituicao_match = re.search(r'(BCO|BANCO|SANTANDER|BRADESCO|ITA[ÚU]|INTER|CAIXA|MERCADO PAGO)[^\n]+', ocr_text, re.IGNORECASE)
        if instituicao_match:
            instituicao = instituicao_match.group(0).strip()
            instituicao = ' '.join(instituicao.split())
            data['destino_instituicao'] = instituicao

            # Tipo de instituição (baseado no nome ou texto do comprovante)
            if 'IP' in instituicao.upper() or 'INSTITUIÇÃO DE PAGAMENTO' in ocr_text.upper():
                data['tipo_instituicao'] = 'Instituição de Pagamento'
            elif 'BANCO' in instituicao.upper() or 'BCO' in instituicao.upper():
                data['tipo_instituicao'] = 'Banco'
            else:
                data['tipo_instituicao'] = 'Outro'

        # Destino - Agência
        agencia_match = re.search(r'Ag[êe]ncia\s+(\d{3,5})', ocr_text, re.IGNORECASE)
        if agencia_match:
            data['destino_agencia'] = agencia_match.group(1).strip()

        # Destino - Conta
        conta_match = re.search(r'Conta\s+([\d\-]+)', ocr_text, re.IGNORECASE)
        if conta_match:
            data['destino_conta'] = conta_match.group(1).strip()

        # Destino - Tipo de conta
        account_type_match = re.search(r'Tipo de conta\s+([^\n]+)', ocr_text, re.IGNORECASE)
        if account_type_match:
            data['destino_tipo_conta'] = account_type_match.group(1).strip()

        # ID da transação
        transaction_id_match = re.search(r'ID da transação[:\s]+([A-Za-z0-9\-]{30,})', ocr_text, re.IGNORECASE)
        if transaction_id_match:
            data['id_transacao'] = transaction_id_match.group(1)

    except Exception as e:
        data['erro_extracao'] = str(e)

    return data

@app.route('/extract', methods=['POST'])
def extract_transfer_data():
    """Endpoint para receber imagem e extrair dados do comprovante"""
    try:
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Nenhuma imagem foi enviada. Use a chave "image" no form-data.'
            }), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Arquivo sem nome.'
            }), 400

        image_bytes = file.read()
        image = Image.open(io.BytesIO(image_bytes))

        ocr_text = pytesseract.image_to_string(image, lang='por')

        extracted_data = extract_data_from_ocr(ocr_text)

        return jsonify({
            'success': True,
            'dados_extraidos': extracted_data,
            'ocr_text': ocr_text
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'OK',
        'message': 'API de Extração de Comprovantes está funcionando!'
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Endpoint raiz com informações sobre a API"""
    return jsonify({
        'api': 'API de Extração de Dados de Comprovante de Transferência',
        'versao': '1.0',
        'endpoints': {
            'health': {
                'metodo': 'GET',
                'url': '/health',
                'descricao': 'Verifica se a API está funcionando'
            },
            'extract': {
                'metodo': 'POST',
                'url': '/extract',
                'descricao': 'Extrai dados de um comprovante de transferência',
                'parametros': {
                    'image': 'Arquivo de imagem (form-data)'
                }
            }
        }
    }), 200

# O bloco if __name__ == '__main__': foi removido.
# O servidor Gunicorn, configurado no Dockerfile, cuidará de iniciar a aplicação.
