
import json
import os
import hashlib
from typing import List, Optional

from cliente import Cliente
from transacao import Transacao


# Estado global
clientes = []
CAMINHO = 'clientes.json'

# ========
# GERAR ID
# ========
def gerar_id(clientes_lista):
    """
    Gera o próximo ID com base na lista recebida.
    Mantém a assinatura original que recebe a lista.
    """
    if not clientes_lista:
        return 1
    return max(cliente.id for cliente in clientes_lista) + 1

# =============
# CRIAR CLIENTE
# =============
def criar_cliente(id, nome, senha, saldo):
    """
    Cria um cliente. Mantém a assinatura com 'id' (mesmo que não seja usado).
    Se 'id' vier None, gera automaticamente.
    """
    clientes_lista = carregar_clientes()  # garante que temos a lista atual
    novo_id = id if id is not None else gerar_id(clientes_lista)

    cliente = Cliente(novo_id, nome, senha, saldo)
    clientes_lista.append(cliente)

    salvar_clientes(clientes_lista)
    return cliente

# =========
# ADICIONAR
# =========
def adicionar_cliente(nome, saldo=0):
    """
    Adiciona um cliente em formato dict (mantendo sua estrutura original).
    Para manter compatibilidade, define 'senha' como string vazia se não informada.
    """
    clientes_lista = carregar_clientes()
    cliente = {
        "id": gerar_id(clientes_lista),
        "nome": nome,
        "senha": "",           # garante compatibilidade com salvar_clientes
        "saldo": saldo,
        "historico": [],
        "transacoes": []
    }
    clientes_lista.append(cliente)
    salvar_clientes(clientes_lista)
    print(f"Cliente {nome} adicionado com sucesso!")

# ================
# CARREGAR CLIENTE
# ================
def carregar_clientes():
    """
    Carrega clientes do arquivo JSON para a lista global 'clientes'.
    Retorna a própria lista global.
    - Robusta a arquivo ausente ou JSON inválido.
    - Reconstrói objetos Cliente e suas transações (quando possível).
    - Mantém campos opcionais (tentativas_login, bloqueado, totais).
    """
    global clientes

    # Garante que 'clientes' é uma lista
    if not isinstance(clientes, list):
        clientes = []

    if not os.path.exists(CAMINHO):
        clientes.clear()
        return clientes

    try:
        with open(CAMINHO, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except (json.JSONDecodeError, OSError):
        clientes.clear()
        return clientes

    clientes.clear()

    for c in dados.get("clientes", []):
        cliente_obj = Cliente(
            id=c.get("id"),
            nome=c.get("nome", ""),
            senha=c.get("senha", ""),   # pode não existir em alguns cenários
            saldo=c.get("saldo", 0)
        )
        # Campos extras opcionais
        cliente_obj.tentativas_login = c.get("tentativas_login", 0)
        cliente_obj.bloqueado = c.get("bloqueado", False)
        cliente_obj.total_sacado = c.get("total_sacado", 0.0)
        cliente_obj.total_juros = c.get("total_juros", 0.0)

        # Transações: aceita lista de dicts ou já objetos
        transacoes = c.get("transacoes", [])
        cliente_obj.transacoes = []
        for t in transacoes:
            # Se existir from_dict na classe Transacao, usa; senão mantém o dict
            if hasattr(Transacao, "from_dict") and isinstance(t, dict):
                try:
                    cliente_obj.transacoes.append(Transacao.from_dict(t))
                except Exception:
                    # fallback: mantém como está se falhar
                    cliente_obj.transacoes.append(t)
            else:
                cliente_obj.transacoes.append(t)

        clientes.append(cliente_obj)

    return clientes

# ==============
# SALVAR CLIENTE
# ==============
def salvar_clientes(lista_clientes):
    """
    Salva clientes em disco.
    Aceita objetos Cliente OU dicts (para compatibilidade com adicionar_cliente).
    Converte dicts em Cliente temporariamente, preenchendo campos ausentes.
    """
    # Normaliza para objetos Cliente
    lista_para_salvar = []
    for c in list(lista_clientes or []):  # (or []) evita None
        if isinstance(c, dict):
            cliente_obj = Cliente(
                id=c.get("id"),
                nome=c.get("nome", ""),
                senha=c.get("senha", ""),
                saldo=c.get("saldo", 0)
            )
            cliente_obj.tentativas_login = c.get("tentativas_login", 0)
            cliente_obj.bloqueado = c.get("bloqueado", False)
            cliente_obj.total_sacado = c.get("total_sacado", 0.0)
            cliente_obj.total_juros = c.get("total_juros", 0.0)
            # transações podem vir como lista de dicts
            cliente_obj.transacoes = c.get("transacoes", [])
            lista_para_salvar.append(cliente_obj)
        else:
            # Já é Cliente
            lista_para_salvar.append(c)

    try:
        with open(CAMINHO, "w", encoding="utf-8") as f:
            json.dump(
                {"clientes": [c.to_dict() for c in lista_para_salvar]},
                f,
                indent=4,
                ensure_ascii=False
            )
    except OSError:
        # Em caso de erro de escrita, não interrompe o fluxo
        pass

# ======
# LISTAR
# ======
def listar_clientes():
    return clientes

# ======
# BUSCAR
# ======
def buscar_cliente_por_id(id_cliente):
    for cliente in clientes:
        if cliente.id == id_cliente:
            return cliente
    return None

# ===============
# REMOVER CLIENTE
# ===============
def remover_cliente(id_cliente):
    cliente = buscar_cliente_por_id(id_cliente)

    if cliente:
        clientes.remove(cliente)
        salvar_clientes(clientes)
        return True

    return False

# =============
# TRANSFERÊNCIA 
# =============
def transferir(cliente_origem, cliente_destino, valor):
    # validação de valor
    if valor <= 0:
        return False

    # garante tipos corretos (evita 'dict' ou None)
    from meu_banco.cliente import Cliente  # importa local para evitar ciclos
    if not isinstance(cliente_origem, Cliente) or not isinstance(cliente_destino, Cliente):
        # opcional: logar/printar para diagnosticar
        # print("[DEBUG] Tipos inválidos em transferir:", type(cliente_origem), type(cliente_destino))
        return False

    # TENTAR SACAR 
    if not cliente_origem.sacar(valor):
        return False
    
    # DEPOSITAR NO DESTINO 
    if not cliente_destino.depositar(valor):
        # rollback simples (opcional): tentar devolver
        cliente_origem.depositar(valor)
        return False

    salvar_clientes(listar_clientes())  # persiste estado atual
    return True

# =======================
# HISTÓRICO DE TRANSAÇÕES
# =======================
historico = []

def registrar_transacao(self, transacao):
    self.transacoes.append(transacao)
    salvar_transacoes()

def listar_transacoes():
    return historico

def salvar_transacoes():
    try:
        with open('transacoes.json', 'w', encoding='utf-8') as f:
            # Se itens já forem objetos Transacao, usa to_dict; se já forem dicts, mantém
            payload = []
            for t in historico:
                if hasattr(t, "to_dict"):
                    payload.append(t.to_dict())
                else:
                    payload.append(t)
            json.dump(payload, f, indent=4, ensure_ascii=False)
    except OSError:
        pass

def carregar_transacoes():
    global historico

    if not os.path.exists('transacoes.json'):
        historico = []
        return

    try:
        with open('transacoes.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except (json.JSONDecodeError, OSError):
        historico = []
        return

    historico = []
    for t in dados:
        # Tenta reconstruir Transacao; senão mantém dict
        try:
            if isinstance(t, dict) and hasattr(Transacao, "__init__"):
                transacao = Transacao(
                    t.get('tipo'),
                    t.get('valor'),
                    origem=t.get('origem'),
                    destino=t.get('destino')
                )
                historico.append(transacao)
            else:
                historico.append(t)
        except Exception:
            historico.append(t)

# ==================
# AUTENTICAR CLIENTE
# ==================
def autenticar_cliente(id_cliente, senha):
    cliente = buscar_cliente_por_id(id_cliente)
    if cliente and cliente.senha == senha:
        return cliente
    return None

# ==================
# CRIPTOGRAFAR SENHA
# ==================
def criptografar_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# Inicialização
carregar_clientes()
carregar_transacoes()