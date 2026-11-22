# Rotas de entrega com ACO

Projeto de Inteligência Artificial (UniSantos). Simulamos um dia de entregas de uma loja virtual e usamos o Ant System (colônia de formigas) para montar as rotas dos veículos.

## Problema

Tem um depósito no meio de uma área de 20 x 20 km e 40 clientes espalhados. Cada cliente fez um pedido de 5 a 15 unidades e só pode receber dentro de uma janela de 2 a 3 horas. São 5 veículos com capacidade de 100 unidades cada. Eles saem às 8h e têm que voltar até as 18h, andando a 30 km/h, e cada entrega leva 10 minutos. Se o veículo chegar antes da janela abrir ele espera, mas depois que a janela fecha não pode mais entregar.

O objetivo é atender todo mundo rodando a menor distância possível.

## Como rodar

Precisa do Python 3 e do matplotlib:

```
pip install matplotlib
python main.py
```

Demora poucos segundos. Os resultados vão para a pasta `resultados`. Para rodar os testes: `python -m unittest`.

## Arquivos

- `parametros.py`: todos os valores do problema e do ACO
- `problema.py`: distâncias, restrições e avaliação das rotas
- `dados.py`: sorteia os clientes
- `guloso.py`: solução do vizinho mais próximo, usada para comparar
- `aco.py`: o algoritmo de colônia de formigas
- `graficos.py`: mapa das rotas, convergência e horários
- `main.py`: roda tudo e salva os resultados
- `tests/`: testes

Na pasta `resultados` ficam os clientes sorteados (`clientes.csv`), as rotas com horário de cada parada (`rotas.csv`), um resumo da melhor solução (`resumo.txt`), a comparação com a gulosa (`comparacao.txt`), tudo junto em `resultados.json` e os três gráficos.

## Resultados

A solução gulosa deu 216,43 km. Rodamos o ACO 5 vezes (sementes 1 a 5): a melhor deu 199,36 km, a média ficou em 203,25 km e a pior em 209,69 km. Em todas as execuções os 40 clientes foram atendidos dentro da janela, da capacidade e do horário, usando os 5 veículos.

## Observações

- A semente da instância é 42, mas com a 42 e a 43 nem a solução gulosa conseguia atender todos os clientes com 5 veículos, então o gerador pula para a próxima e acaba usando a 44.
- Para testar outros valores (alfa, beta, evaporação, número de formigas etc.) é só mudar o `parametros.py` e rodar o `main.py` de novo.
