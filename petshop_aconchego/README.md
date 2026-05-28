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
- Equipe organizada por funcao: gerente, administrador, 4 funcionarios de banho/tosa e 4 cuidadores da creche.
- Area de creche para registrar entrada, saida prevista, cuidador responsavel e status do pet.
- Planos da creche com valor automatico por raca/porte: diaria avulsa, pacote 2x semana, pacote 3x semana e mensal livre.
- Bloqueio de agendamento em data/hora passada.
- Trava financeira para impedir novo agendamento de pet com pagamento pendente.
- Cancelamento e exclusao de atendimentos.
- Estoque com unidade de medida, nivel critico e reposicao.
- Baixa de insumos ao finalizar servico.
- Exibicao dos itens utilizados ao finalizar um servico.
- Registro de intercorrencias pelo operacional.
- Cronometro regressivo do atendimento com pausa.
- Perfis de acesso: Gerente, Administrativo e Operacional.
- Dashboard com composicao da equipe, taxa de ocupacao geral, ocupacao por funcionario de banho/tosa, pets ativos na creche, receita prevista da creche, ruptura de estoque, ticket medio e alertas.

## O que foi adicionado

- Equipe organizada por funcao:
  - 1 gerente.
  - 1 administrador.
  - 4 funcionarios de banho e tosa.
  - 4 cuidadores da creche.
- Campo de funcionario de banho/tosa na agenda.
- Botao para excluir atendimento.
- Botao para pausar cronometro.
- Cronometro separado por atendimento.
- Aba "Creche".
- Registro de entrada e saida de pets na creche.
- Cuidador responsavel na creche.
- Observacoes para o pet na creche.
- Planos da creche com valor automatico:
  - Diaria avulsa.
  - Pacote 2x semana.
  - Pacote 3x semana.
  - Mensal livre.
- Preco da creche calculado por raca/porte.
- Receita prevista da creche no dashboard.
- Quantidade de pets ativos na creche no dashboard.
- Distribuicao dos pets por cuidador no dashboard.

## Dados

Ao rodar pela primeira vez, o sistema cria automaticamente o arquivo:

```text
petshop_aconchego_dados.json
```

Esse arquivo guarda produtos, agendamentos, pagamentos, status de servico e consumo estimado.
