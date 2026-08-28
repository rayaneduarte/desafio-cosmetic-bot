# Avaliação do Cosmetic Bot com DeepEval

Este documento descreve a suíte de avaliação desenvolvida para o Cosmetic Bot, incluindo o Golden Dataset, as métricas utilizadas e as instruções para reprodução dos testes.

## 1. Estrutura da avaliação

Os principais arquivos utilizados são:

```text
golden_dataset.json
testes/
└── test_golden_dataset.py
prompt.txt
catalogo.json
demos/
└── juiz.py
```

- `golden_dataset.json`: Golden Dataset utilizado nos testes.
- `testes/test_golden_dataset.py`: suíte automatizada com DeepEval.
- `catalogo.json`: catálogo utilizado como fonte de verdade.
- `prompt.txt`: prompt de sistema do chatbot.
- `demos/juiz.py`: configuração do modelo utilizado como juiz.

## 2. Golden Dataset

O Golden Dataset contém 16 casos de teste distribuídos em quatro categorias:

| Categoria | Casos |
|---|---|
| Consulta direta | GD01–GD04 |
| Recomendação por perfil | GD05–GD08 |
| Fora de escopo | GD09–GD12 |
| Adversarial | GD13–GD16 |

Cada caso contém:

- identificador;
- categoria;
- input do usuário;
- critério esperado;
- contexto de referência baseado no catálogo.

Os casos foram construídos para avaliar comportamentos como consulta de preços e ingredientes, recomendações por perfil, recusa de perguntas fora do domínio, produtos inexistentes, prompt injection e claims cosméticos inadequados.

## 3. Métricas

A suíte utiliza métricas do DeepEval de acordo com a categoria do teste.

### Answer Relevancy

Threshold: `0.7`

Avalia se a resposta é relevante para a solicitação apresentada.

### Faithfulness

Threshold: `0.8`

Avalia se as afirmações da resposta são sustentadas pelo contexto de referência extraído do catálogo.

### Conformidade de Claims — G-Eval

Threshold: `0.8`

Avalia se a resposta evita claims inadequados, como:

- promessa de cura;
- tratamento de condições médicas;
- resultados garantidos;
- efeitos terapêuticos não sustentados pelo catálogo.

### Conformidade de Escopo — G-Eval

Utilizada nos casos fora do domínio para verificar se o chatbot reconhece solicitações externas ao escopo de cosméticos e evita responder utilizando conhecimento externo.

## 4. Modelo juiz

As avaliações automatizadas foram executadas utilizando o Gemini através da integração `GeminiModel` do DeepEval.

Modelo utilizado:

```text
gemini-3.5-flash-lite
```

As credenciais não são armazenadas no repositório.

## 5. Configuração

Com o ambiente virtual criado e as dependências instaladas, ative-o no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Configure o juiz:

```powershell
$env:JUIZ_PROVIDER="gemini"
$env:JUIZ_MODEL="gemini-3.5-flash-lite"
$env:GOOGLE_API_KEY="SUA_CHAVE"
```

A chave real da API não deve ser adicionada ao repositório.

O bot deve estar configurado conforme as instruções do `README.md` e do `GUIA_INSTALACAO.md`.

## 6. Executando os testes

Para executar toda a suíte:

```powershell
deepeval test run testes/test_golden_dataset.py -s
```

Para executar apenas um caso:

```powershell
deepeval test run testes/test_golden_dataset.py -k "GD06" -s
```

Basta substituir `GD06` pelo identificador desejado.

## 7. Metodologia

A avaliação foi realizada em duas etapas principais:

1. execução de um baseline com o prompt original;
2. análise das falhas encontradas;
3. refinamento exclusivamente do `prompt.txt`;
4. reexecução dos casos para comparação dos resultados.

O refinamento buscou melhorar principalmente:

- fidelidade ao catálogo;
- correspondência entre categoria e tipo de pele;
- tratamento de produtos inexistentes;
- comportamento fora do escopo;
- resistência a instruções adversariais;
- segurança de claims cosméticos.

O Golden Dataset e os critérios de avaliação foram mantidos durante a comparação, evitando alterar os testes para favorecer o prompt refinado.

## 8. Observações sobre os resultados

As métricas automatizadas utilizam um LLM como juiz. Por esse motivo, os scores podem apresentar variação e não substituem completamente a análise funcional das respostas.

Durante a execução também podem ocorrer erros relacionados à infraestrutura do provedor, como:

- `429 RESOURCE_EXHAUSTED`;
- `503 UNAVAILABLE`;
- timeout.

Esses erros de infraestrutura devem ser diferenciados de uma falha funcional do chatbot.

Os resultados detalhados do baseline, da avaliação após o refinamento e a análise dos casos relevantes são apresentados no relatório final do desafio.