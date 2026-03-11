from rich.console import Console
from rich.table import Table
from transacao import Transacao

console = Console()

class Cliente:
    def __init__(self, id, nome, senha, saldo=0):
        self.id = id
        self.nome = nome
        self.senha = senha
        self.saldo = saldo
        self.tentativas_login = 0
        self.bloqueado = False
        self.total_sacado = 0.0
        self.total_juros = 0.0
        self.transacoes = []

        # limites do sistema
        self.limite_credito = -5000     
        self.limite_saque = 3000       
        self.limite_saques = 3         
        self.saques_realizados = 0


    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "senha": self.senha,
            "saldo": self.saldo,
            "tentativas_login": self.tentativas_login,
            "bloqueado": self.bloqueado,
            "total_sacado": self.total_sacado,
            "total_juros": self.total_juros,
            "transacoes": [
                t.to_dict() if hasattr(t, "to_dict") else t
                for t in self.transacoes
            ]
        }

    # =========
    # REGISTRAR
    # =========
    def registrar_transacao(self, transacao):
        # Antes estava recursivo; o certo é só adicionar no extrato do cliente
        self.transacoes.append(transacao)

    def depositar(self, valor):
        if valor <= 0:
            return False

        self.saldo += valor

        transacao = Transacao(
            "Depósito",
            valor,
            origem=self.nome,
            destino=None
        )

        self.transacoes.append(transacao)
        return True

    def sacar(self, valor):
        if valor <= 0:
            return False

        if valor > self.limite_saque:
            print('Limite de saque é R$3000')
            return False

        if self.saques_realizados >= self.limite_saques:
            print('Limite diário de saques atingido')
            return False

        novo_saldo = self.saldo - valor

        if novo_saldo < self.limite_credito:
            print('Limite de crédito excedido')
            return False

        self.saldo = novo_saldo
        self.saques_realizados += 1
        self.total_sacado += valor

        if self.saldo < 0:
            valor_emprestado = abs(self.saldo)
            juros = valor_emprestado * 0.08
            self.saldo -= juros
            self.total_juros += juros

        transacao = Transacao(
            "Saque",
            valor,
            origem=self.nome,
            destino=None
        )

        self.transacoes.append(transacao)
        return True

    # ===============
    # MOSTRAR EXTRATO
    # ===============
    def mostrar_extrato(self):
        tabela = Table(title=f'Extrato Bancário - {self.nome}')

        tabela.add_column('Data', style='cyan')
        tabela.add_column('Tipo', style='green')
        tabela.add_column('Valor', justify='right')
        tabela.add_column('Saldo após operação', justify='right')

        for t in self.transacoes:
            data = t.data.strftime('%d/%m/%Y %H:%M')
            tabela.add_row(
                data,
                t.tipo,
                f'R${t.valor:.2f}',
                f'R${t.saldo_resultante:.2f}'
            )

        console.print(tabela)
        console.print(f'\n[bold]Saldo atual:[/bold yellow] R$ {self.saldo:.2f}')