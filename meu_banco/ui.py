from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align

console = Console()

# ============
# MENU INICIAL
# ============

def menu_inicial():

    titulo = "[bold cyan]💳 SISTEMA BANCÁRIO PYBANK[/bold cyan]"

    menu = """
    [1] Administrador
    [2] Cliente
    [0] Sair
    """

    console.print("\n")
    console.print(Align.center(titulo))

    console.print(
        Panel(
            menu,
            title="MENU INICIAL",
            border_style="cyan",
            padding=(1,4)
        )
    )

    opcao = Prompt.ask(
        "Escolha uma opção",
        choices=["1", "2", "0"]
    )

    return opcao

# ============
# TELA INICIAL
# ============
def tela_inicial():
    console.clear()
    console.print(
        Panel(
            '[bold white]SISTEMA BANCÁRIO[/bold white]\n[dim]Versão 1.0[/dim]',
            expand=False,
            border_style='grey37'
        )
    )

# ============
# MENU CLIENTE
# ============
def menu_principal():
    console.print('\n[bold]MENU DOS CLIENTES[/bold]\n')
    console.print('[1] Cadastrar cliente')
    console.print('[2] Listar clientes')
    console.print('[3] Gerenciar clientes')
    console.print('[4] Apagar cliente')
    console.print('[5] Ver histórico')
    console.print('[0] Sair\n')

    # Restringe entradas às opções válidas
    return Prompt.ask('Escolha uma opção', choices=['0','1','2','3','4','5'], default='0')

# ===============
# MENU DO CLIENTE
# ===============
def menu_cliente(cliente):
    console.clear()
    conteudo = (
        f'[bold]Cliente:[/bold] {cliente.nome}\n'
        f'Saldo atual: R${cliente.saldo:.2f}'
    )
    console.print(
        Panel(
            conteudo,
            border_style='grey37',
            expand=False
        )
    )
    console.print('\n[1] Depositar')
    console.print('[2] Sacar')
    console.print('[3] Limite')
    console.print('[4] Ver extrato')
    console.print('[0] Sair\n')

    return Prompt.ask('Escolha uma opção', choices=['0','1','2','3','4'], default='0')

# ==================
# TABELA DE CLIENTES
# ==================
def mostrar_clientes(clientes):
    tabela = Table(
        title='👥 Clientes',
        style='white',
        border_style='grey37',
        header_style='bold white'
    )
    tabela.add_column('ID', style='dim', justify='right', no_wrap=True)
    tabela.add_column('Nome', style='white')
    tabela.add_column('Status', justify='center')

    for cliente in clientes:
        status = "[red]BLOQUEADO[/red]" if getattr(cliente, 'bloqueado', False) else "[green]ATIVO[/green]"
        tabela.add_row(
            str(cliente.id),
            cliente.nome,
            status
        )

    console.print(tabela)

# ====================
# LISTA TRANSFERÊNCIAS
# ====================
def mostrar_historico(transacoes):
    tabela = Table(
        title='📜 Histórico de transações',
        border_style='grey37',
        header_style='bold white'
    )

    tabela.add_column('Tipo')
    tabela.add_column('Valor', justify='right')
    tabela.add_column('Origem')
    tabela.add_column('Destino')
    tabela.add_column('Data', justify='center')
    tabela.add_column('Hora', justify='center')

    for t in transacoes:
        # Cores por tipo de movimento (ex.: entrada verde, saída vermelha)
        tipo = (t.tipo or "").strip().lower()
        is_saida = tipo in ('saque', 'transferência enviada', 'transferencia enviada', 'pagamento', 'tarifa')
        cor_valor = 'red' if is_saida else 'green'

        valor_formatado = f'[bold {cor_valor}]R${t.valor:.2f}[/bold {cor_valor}]'

        tabela.add_row(
            t.tipo,
            valor_formatado,
            str(t.origem) if getattr(t, 'origem', None) is not None else '-',
            str(t.destino) if getattr(t, 'destino', None) else '-',
            t.data.strftime("%d/%m/%Y"),
            t.data.strftime("%H:%M:%S")
        )

    console.print(tabela)

# =========
# MENSAGENS
# =========
def mensagem_sucesso(txt):
    console.print(f'[green]✔ {txt}[/green]')

def mensagem_erro(txt):
    console.print(f'[red]✖ {txt}[/red]')