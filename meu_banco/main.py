# ===============================================================================
# Simulador de Sistema Bancario Real Simplificado
# Autor: Cauã Gabriel Fernandes Rocha
# github: cauagabriel69
# email: rcaua575@gmail.com
# ===============================================================================
from database import criar_cliente, gerar_id, carregar_clientes, buscar_cliente_por_id, listar_clientes, remover_cliente, transferir, registrar_transacao, listar_transacoes, salvar_clientes, criptografar_senha
from ui import tela_inicial, menu_principal, mostrar_clientes, mostrar_historico, menu_inicial
from rich.prompt import Prompt
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from transacao import Transacao 
from logger import log_info, log_warning, log_error
from cliente import Cliente

clientes = carregar_clientes()
console = Console()

admin_usuario = "admin"
admin_senha = '1234'

def limpar():
        os.system('cls' if os.name == 'nt' else 'clear')

# ============
# MENU INICIAL
# ============
tipo_acesso = menu_inicial()

# ===========
# LOGIN ADMIN
# ===========
if tipo_acesso == '1':
    usuario = Prompt.ask('Usuário')
    senha = Prompt.ask('Senha', password = True)

    if usuario == admin_usuario and senha == admin_senha:
        print('Login admin realizado com sucesso')
        log_info('Administrador acessou o sistema')

    else:
        print('Acesso negado')
        exit()

    # ==================
    # MENU ADMINISTRADOR
    # ==================
    while True:
        limpar()

        console.print('=== MENU ADMINISTRADOR ===')
        console.print('[1] Criar cliente')
        console.print('[2] Listar clientes')
        console.print('[3] Remover cliente')
        console.print('[4] Ver histórico')
        console.print('[5] Desbloquear cliente')
        console.print('[0] Sair')

        opc = Prompt.ask('escolha uma opção')

        # CRIAR CLIENTE
        if opc == '1':

            # Nome não pode ser vazio
            while True:
                nome = Prompt.ask("Digite o nome do cliente")
                if not nome or not nome.strip():
                    print("O nome não pode ficar vazio. Tente novamente.")
                    continue
                nome = nome.strip()
                break

            # Senha não pode ser vazia
            while True:
                senha = Prompt.ask('Crie uma senha', password=True)
                if not senha:
                    print("A senha não pode ficar vazia. Tente novamente.")
                    continue
                break

            # Garante que a lista 'clientes' existe
            if 'clientes' not in locals() and 'clientes' not in globals():
                print("Erro: a lista 'clientes' não está definida.")
                input('Pressione enter para continuar...')
            else:
                # Gera ID novo ANTES de usar
                id_cliente = max([c.id for c in clientes], default=0) + 1

                senha_cripto = criptografar_senha(senha)

                # Cria o objeto com o ID gerado
                novo_cliente = Cliente(id_cliente, nome, senha_cripto)

                # Campos defensivos (se sua classe não definir)
                if not hasattr(novo_cliente, 'bloqueado'):
                    novo_cliente.bloqueado = False
                if not hasattr(novo_cliente, 'tentativas_login'):
                    novo_cliente.tentativas_login = 0
                if not hasattr(novo_cliente, 'transacoes') or novo_cliente.transacoes is None:
                    novo_cliente.transacoes = []

                clientes.append(novo_cliente)
                salvar_clientes(clientes)
                log_info(f'Cliente criado: {nome} | ID {id_cliente}')

                print('Cliente criado com sucesso!')
                input('Pressione enter para continuar...')


        # LISTAR CLIENTES
        elif opc == '2':

            limpar()

            print('=== LISTA DE CLIENTES ===')

            if not clientes:
                print('A lista de clientes está vazia.')
                    
            else:
                for c in clientes:
                    status = 'BLOQUEADO' if getattr(c, 'bloqueado', False) else 'ATIVO'
                    print(f'ID: {c.id} | Nome: {c.nome} | Status: {status}')

            input('Pressione enter para continuar...')


        # REMOVER CLIENTE
        elif opc == '3':

            id_str = Prompt.ask('ID do cliente').strip()
            if not id_str.isdigit():
                print('ID inválido. Digite apenas números.')
                    
            else:
                id_cliente = int(id_str)
                cliente = buscar_cliente_por_id(id_cliente)
                    
                if cliente:
                    clientes.remove(cliente)
                    salvar_clientes(clientes)
                    log_info(f'Cliente removido: {cliente.nome} | ID {cliente.id}')
                    print('Cliente removido com sucesso!')
                        
                else:
                    print('Cliente não encontrado.')

            input('Pressione enter para continuar...')


        # VER HISTÓRICO
        elif opc == '4':

                limpar()
                print('=== HISTÓRICO DE TRANSAÇÕES ===')

                if not clientes:
                    print('Nenhum cliente cadastrado. A lista de clientes está vazia.')
                    input('Pressione enter para continuar...')
                else:
                    houve_transacoes = False

                    for cliente in clientes:
                        transacoes = getattr(cliente, 'transacoes', []) or []
                        if not transacoes:
                            continue

                        for t in transacoes:
                            tipo = getattr(t, 'tipo', '—')
                            valor = getattr(t, 'valor', 0.0)
                            data = getattr(t, 'data', '—')
                            print(f'Cliente: {cliente.nome} | {tipo} | R${valor:.2f} | {data}')
                            houve_transacoes = True

                    if not houve_transacoes:
                        print('O histórico está vazio. Nenhuma transação encontrada.')

                    input('Pressione enter para continuar...')


        # DESBLOQUEAR CLIENTE
        elif opc == '5':

            id_str = Prompt.ask('ID do cliente').strip()
            if not id_str.isdigit():
                print('ID inválido. Digite apenas números.')
            
            else:
                id_cliente = int(id_str)
                cliente = buscar_cliente_por_id(id_cliente)

                if cliente:
                    cliente.bloqueado = False
                    cliente.tentativas_login = 0
                    salvar_clientes(clientes)
                    log_info(f'ADMIN desbloqueou cliente: {cliente.nome} | ID {cliente.id}')
                    print('Cliente desbloqueado!')
                    
                else:
                    print('Cliente não encontrado.')

            input('Pressione enter para continuar...')

        # SAIR
        elif opc == '0':   
            break

        else:
            print('Opção inválida')
            input('Pressione enter para continuar...')


# ============
# MENU CLIENTE
# ============
elif tipo_acesso =='2':


    while True:
        limpar()
        tela_inicial()
        opcao = menu_principal()

        # =================
        # CADASTRAR CLIENTE
        # =================
        if opcao == '1':

            while True:
                nome = Prompt.ask("Digite o nome do cliente: ").strip()

                if nome == "":
                    print("O nome não pode ficar vazio. Tente novamente.")
                else:
                    break
            senha = Prompt.ask('Crie uma senha')
            senha_cripto = criptografar_senha(senha)
            saldo = float(Prompt.ask('Deposito inicial'))

            clientes = carregar_clientes()
            novo_id = gerar_id(clientes)

            cliente = criar_cliente(novo_id, nome, senha_cripto, saldo)

            if cliente:
                log_info(f'Cliente criado: {cliente.nome} | ID {cliente.id}')
                print('Cliente cadastrado com sucesso!')

            input('Pressione enter para continuar...')

        # ===============
        # LISTAR CLIENTES
        # ===============
        elif opcao == '2': 
            clientes = listar_clientes()

            if not clientes:
                print('Nenhum cliente encontrado')
            
            else:
                mostrar_clientes(clientes)

            input('Pressione enter para continuar...')
            limpar()

        # ==================
        # GERENCIAR CLIENTES
        # ==================    
        elif opcao == '3':
            clientes = listar_clientes()

            if not clientes: 
                print('Cliente não encontrado')
                input('Pressione enter para continuar...')
                continue

            def pedir_clientes():

                while True:
                    try:
                        id_cliente = int(Prompt.ask('Digite o ID do cliente'))
                        senha = Prompt.ask('Senha')

                        cliente = buscar_cliente_por_id(id_cliente)

                        if not cliente:
                            print('Cliente não encontrado')
                            continue

                        if cliente.bloqueado:
                            console.print("[red]Cliente bloqueado[/red]")
                            print('Conta bloqueada. Procure o administrador.')
                            log_info(f'LOGIN BLOQUEADO: tentativa de acesso ID {id_cliente}')
                            input('Pressione enter para continuar...')
                            continue
                        
                        senha_digitada = criptografar_senha(senha)

                        if cliente.senha == senha_digitada:
                                cliente.tentativas_login = 0

                                log_info(f'LOGIN: {cliente.nome} | ID {cliente.id} acessou o terminal')

                                cliente.tentativas_login = 0
                                salvar_clientes(clientes)

                                return cliente

                        else:
                            cliente.tentativas_login += 1

                            log_info(f'ERRO LOGIN: tentativa inválida | ID {cliente.id}')

                            if cliente.tentativas_login >= 3:
                                cliente.bloqueado = True
                                salvar_clientes(clientes)
                                console.print("[red]Cliente bloqueado[/red]")
                                print('Conta bloqueada após 3 tentativas')
                            
                            else: 
                                print('Senha incorreta')

                            input('Pressione enter para continuar...')
                        
                    except ValueError:
                        print('Digite apenas números!')

            # =======================
            # LOOP INTERNO DO CLIENTE 
            # =======================
            cliente = pedir_clientes()

            while True:
                limpar()

                menu = """
                [1] Depositar
                [2] Sacar
                [3] Ver limite
                [4] Ver extrato
                [5] Transferir
                [0] Sair
                """

                console.print(Panel(menu, title="MENU DO CLIENTE", border_style="cyan"))
                opc_cliente = Prompt.ask('Escolha uma opção')

                # DEPOSITAR 
                if opc_cliente == '1':
                    valor = float(Prompt.ask('Valor para depositar'))

                    print(f'Valor digitado: {valor}')

                    if cliente.depositar(valor):

                        transacao = Transacao('DEPÓSITO', valor, origem=cliente.nome)

                        registrar_transacao(transacao)
                        salvar_clientes(clientes)

                        console.print("[green]Depósito realizado com sucesso![/green]")

                    else:
                        print('Valor inválido!')
                        
                    input('Pressione enter para continuar...')

                # SACAR     
                elif opc_cliente == '2':

                    try:
                        valor = float(Prompt.ask('Valor para sacar'))
                    except ValueError:
                        print('Digite um número valido')
                        input('Pressione enter para continuar...')
                        continue


                    if cliente.sacar(valor):
                        salvar_clientes(clientes)
                        log_info(f'Saque: {cliente.nome} sacou R${valor}')

                        console.print("[green]Saque realizado com sucesso![/green]")
                    
                    else:
                        log_warning(f'Tentativa de saque invalida: {cliente.nome} tentou sacar R${valor}')
                        print('Operação não permitida (limite excedido ou valor invalido).')
                        
                    input('Pressione enter para continuar...')
                        

                # VER LIMITE
                elif opc_cliente == '3':
                    print(f'Saques hoje: {cliente.saques_realizados}/3')
                    print(f'Limite pro saque: R$3000')

                    input('Pressione enter para continuar...')

                # VER EXTRATO
                elif opc_cliente == '4':
                    limpar()

                    tabela = Table(title = f'Extrato de {cliente.nome}')

                    tabela.add_column("Tipo", justify="center")
                    tabela.add_column("Valor", justify="right")
                    tabela.add_column("Data", justify="center")   

                    if not cliente.transacoes:
                        print('Nenhuma transação encontrada')   

                    for t in cliente.transacoes:
                        tabela.add_row(
                            t.tipo,
                            f'R$ {t.valor:.2f}',
                            t.data.strftime("%d/%m/%Y %H:%M")
                        )            

                    console.print(tabela)

                    print(f'\nSaldo atual: R${cliente.saldo:.2f}')
                    input('Pressione enter para continuar...')

                # TRANSFERIR 
                elif opc_cliente == '5':
                    try:
                        id_destino = int(Prompt.ask('ID do cliente de destino'))

                        cliente_destino = buscar_cliente_por_id(id_destino)

                        if not cliente_destino:
                            print('Cliente destino não encontrado')
                            input('Pressione enter para continuar...')
                            continue

                        valor = float(Prompt.ask('Valor da transferência'))

                        if transferir(cliente, cliente_destino, valor):

                            # cria a transação
                            transacao = Transacao(
                                "TRANSFERÊNCIA",
                                valor,
                                origem=cliente.nome,
                                destino=cliente_destino.nome
                            )

                            # adiciona no extrato dos dois clientes
                            cliente.transacoes.append(transacao)
                            cliente_destino.transacoes.append(transacao)

                            # registra no histórico geral
                            registrar_transacao(transacao)

                            # salva no JSON
                            salvar_clientes(clientes)

                            log_info(f'Transferência: {cliente.nome} -> {cliente_destino.nome} | R${valor}')

                            print('Transferência realizada com sucesso!')

                        else:
                                log_warning(f'Transferência falhou: {cliente.nome} -> {cliente_destino.nome} | R${valor}')
                                print('Transferência não realizada (saldo insuficiente ou valor inválido).')

                                input('Pressione enter para continuar...')
                                limpar()

                    except ValueError:
                        print('Entrada inválida')
                        input('Pressione enter para continuar...')

                # VOLTAR 
                elif opc_cliente == '0':
                    log_info(f'LOGOUT: {cliente.nome} | ID {cliente.id} saiu do terminal')

                    break

                else:
                    print('Opção inválida.')
                    input('Pressione enter para continuar...')
                    limpar()

        # ==============
        # APAGAR CLIENTE
        # ==============
        elif opcao == '4':
            clientes = listar_clientes()

            if not clientes:
                print('Nenhum cliente encontrado')
                input('Pressione enter para continuar...')
                limpar()
                continue

            mostrar_clientes(clientes)

            id_cliente = int(Prompt.ask('Digite o ID do cliente que deseja apagar'))

            confirmar = Prompt.ask('Tem certeza que deseja apagar? (s/n)').strip().lower()

            if confirmar in ['s', 'sim']:
                if remover_cliente(id_cliente):
                    print('Cliente removido com sucesso!')
                    log_info(f'Cliente removido: ID {id_cliente}')
                
                else:
                    print('Cliente não encontrado ou não pôde ser removido.')
            
            else:
                print('Operação cancelada.')

            input('Pressione enter para continuar...')
            limpar()

        # ============= 
        # VER HISTORICO 
        # ============= 
        elif opcao == '5': 
            transacoes = listar_transacoes() 

            if not transacoes: 
                print('Nenhuma transação encontrada') 

            else: 
                mostrar_historico(transacoes)

            input('Pressione enter para continuar...')
            limpar()

        # ====
        # SAIR
        # ==== 
        elif opcao == '0':
            break

        else:
            print('Opção inválida!')
            input('Pressione enter para continuar...')

elif tipo_acesso == "0":
    print("Encerrando sistema...")
            

        