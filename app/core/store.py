from typing import List, Dict
from datetime import datetime

# Lista em memória simulando um "buffer" de transações recebidas via webhook
_transactions_buffer: List[Dict] = []


def append_transaction(tx: Dict):
    """
    Adiciona uma transação no buffer em memória.
    tx é um dict com keys: timestamp, status, count.
    """
    _transactions_buffer.append(tx)


def get_transactions() -> List[Dict]:
    """
    Retorna todas as transações recebidas via webhook.
    """
    return _transactions_buffer.copy()