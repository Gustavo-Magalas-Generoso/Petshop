# Pet Shop Aconchego

Sistema desktop em Python baseado no PRD 3.0 do Pet Shop Aconchego.

## Como rodar

```bash
python petshop_aconchego.py
```

O programa usa apenas bibliotecas nativas do Python: `tkinter`, `json`, `datetime` e `dataclasses`.

## Funcionalidades entregues

- Agenda com tempo automatico por raca, porte e servico.
- Buffer sanitario obrigatorio de 15 minutos.
- Bloqueio de conflito parcial de horarios considerando duracao e buffer.
- Agenda por funcionario, com validacao de servicos que cada pessoa executa.
- Trava financeira para impedir novo agendamento de pet com pagamento pendente.
- Estoque com unidade de medida, nivel critico e reposicao.
- Baixa de insumos ao finalizar servico.
- Registro de intercorrencias pelo operacional.
- Cronometro regressivo do atendimento.
- Perfis de acesso: Gerente, Administrativo e Operacional.
- Dashboard com taxa de ocupacao geral, ocupacao por funcionario, ruptura de estoque, ticket medio e alertas.

## Dados

Ao rodar pela primeira vez, o sistema cria automaticamente o arquivo:

```text
petshop_aconchego_dados.json
```

Esse arquivo guarda produtos, agendamentos, pagamentos, status de servico e consumo estimado.
