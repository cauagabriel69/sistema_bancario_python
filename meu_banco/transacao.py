from datetime import datetime

class Transacao:

    def __init__(self, tipo, valor, origem=None, destino=None):
        self.tipo = tipo
        self.valor = valor
        self.origem = origem
        self.destino = destino
        self.data = datetime.now()

    def to_dict(self):
        return {
            "tipo": self.tipo,
            "valor": self.valor,
            "origem": self.origem,
            "destino": self.destino,
            "data": self.data.strftime("%d/%m/%Y %H:%M:%S")
        }

    @staticmethod
    def from_dict(dados):

        t = Transacao(
            dados["tipo"],
            dados["valor"],
            dados.get("origem"),
            dados.get("destino")
        )

        t.data = datetime.strptime(dados["data"], "%d/%m/%Y %H:%M:%S")

        return t
