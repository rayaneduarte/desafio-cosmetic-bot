# Cosmetic Bot — Avaliação de Qualidade com DeepEval

Projeto desenvolvido para avaliar a qualidade, confiabilidade e segurança de um chatbot de produtos cosméticos utilizando **DeepEval** e **pytest**.

A avaliação utiliza um **Golden Dataset com 16 casos de teste**, distribuídos entre quatro categorias:

- Consulta direta
- Recomendação por perfil
- Fora de escopo
- Adversarial

O chatbot responde com base no catálogo `catalogo.json` e utiliza **Llama 3.2 3B (`llama3.2:3b`) via Ollama**.

Para as avaliações com LLM-as-a-Judge, foi utilizado o **Gemini 3.5 Flash-Lite (`gemini-3.5-flash-lite`)**.

---

## Estrutura do projeto

```text
desafio-cosmetic-bot/
├── chatbot.py
├── catalogo.json
├── prompt.txt
├── golden_dataset.json
├── testes/
│   └── test_golden_dataset.py
├── demos/
│   └── juiz.py
├── GUIA_INSTALACAO.md
└── README.md
```

### Principais arquivos da avaliação

| Arquivo | Descrição |
| --- | --- |
| `golden_dataset.json` | Golden Dataset contendo os 16 casos de teste |
| `testes/test_golden_dataset.py` | Suíte automatizada de avaliação com DeepEval e pytest |
| `catalogo.json` | Catálogo de produtos utilizado como fonte de referência |
| `prompt.txt` | Prompt do sistema refinado após a análise da baseline |
| `chatbot.py` | Implementação do chatbot avaliado |
| `demos/juiz.py` | Configuração do modelo utilizado como juiz |

---

## Requisitos

Para executar o projeto é necessário:

- Python 3.10 ou superior
- Ollama
- DeepEval 4.x
- Acesso gratuito ao Gemini para utilização do modelo juiz

---

## 1. Criar o ambiente virtual

Na raiz do projeto:

### Windows — PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

---

## 2. Instalar as dependências

Com o ambiente virtual ativado:

```bash
pip install requests deepeval ollama google-genai
```

---

## 3. Configurar o chatbot

O chatbot foi executado localmente utilizando:

- **Provedor:** Ollama
- **Modelo:** `llama3.2:3b`
- **Temperatura:** `0.3`

Baixe o modelo utilizado:

```bash
ollama pull llama3.2:3b
```

Certifique-se de que o Ollama esteja em execução.

Para testar o chatbot manualmente:

```bash
python chatbot.py
```

---

## 4. Configurar o modelo juiz

As avaliações foram realizadas utilizando:

- **Provedor do juiz:** Gemini
- **Modelo:** `gemini-3.5-flash-lite`

A chave da API deve ser configurada por variável de ambiente e **não deve ser adicionada ao repositório**.

### Windows — PowerShell

```powershell
$env:JUIZ_PROVIDER="gemini"
$env:JUIZ_MODEL="gemini-3.5-flash-lite"
$env:GEMINI_API_KEY="SUA_CHAVE_AQUI"
```

### Linux/macOS

```bash
export JUIZ_PROVIDER="gemini"
export JUIZ_MODEL="gemini-3.5-flash-lite"
export GEMINI_API_KEY="SUA_CHAVE_AQUI"
```

---

## 5. Executar a suíte de avaliação

Com o ambiente virtual ativado, o Ollama em execução e o modelo juiz configurado, execute o comando abaixo na raiz do projeto:

```bash
deepeval test run testes/test_golden_dataset.py -s
```

A suíte:

1. Carrega os casos definidos no `golden_dataset.json`;
2. Envia cada pergunta ao Cosmetic Bot;
3. Obtém a resposta do modelo local;
4. Aplica as métricas correspondentes ao caso;
5. Compara os scores obtidos com os thresholds definidos.

---

## Executar um caso específico

Durante a análise e o refinamento do prompt, também é possível executar apenas um caso do Golden Dataset.

Exemplo:

```bash
deepeval test run testes/test_golden_dataset.py -k "GD13" -s
```

Para executar outro caso, basta substituir `GD13` pelo identificador correspondente.

Exemplo:

```bash
deepeval test run testes/test_golden_dataset.py -k "GD14" -s
```

A execução seletiva é útil principalmente durante a investigação de falhas e evita chamadas desnecessárias ao modelo juiz.

---

## Golden Dataset

O arquivo `golden_dataset.json` contém **16 casos de teste**, divididos igualmente entre quatro categorias:

| Categoria | Casos | Objetivo |
| --- | --- | --- |
| Consulta direta | GD01–GD04 | Validar recuperação de informações do catálogo |
| Recomendação por perfil | GD05–GD08 | Validar recomendações considerando os critérios informados |
| Fora de escopo | GD09–GD12 | Verificar se o chatbot evita responder assuntos não relacionados a cosméticos |
| Adversarial | GD13–GD16 | Avaliar resistência a premissas falsas, invenções, prompt injection e claims inadequados |

Foram utilizadas técnicas de design de testes como **particionamento de equivalência**, **tabela de decisão**, **testes negativos** e **testes adversariais**.

---

## Métricas utilizadas

A suíte utiliza métricas do DeepEval para avaliar diferentes dimensões das respostas.

| Métrica | Threshold | Objetivo |
| --- | ---: | --- |
| Answer Relevancy | 0.70 | Avaliar se a resposta atende à solicitação realizada |
| Faithfulness | 0.80 | Avaliar se as afirmações estão fundamentadas no contexto fornecido |
| G-Eval — Conformidade de Claims | 0.80 | Identificar claims inadequados, promessas absolutas ou afirmações não permitidas |
| G-Eval — Conformidade de Escopo | 0.80 | Avaliar se o chatbot respeita seu domínio de atuação |

As métricas aplicadas variam de acordo com a categoria de cada caso de teste.

---

## Metodologia

A avaliação foi realizada em duas etapas principais:

### Baseline

Inicialmente, a suíte foi executada utilizando o comportamento original do chatbot para identificar falhas relacionadas a:

- relevância das respostas;
- fidelidade ao catálogo;
- recomendações;
- controle de escopo;
- claims inadequados;
- resistência a entradas adversariais.

### Refinamento

Após a análise das falhas, o arquivo `prompt.txt` foi refinado.

Durante essa etapa, foram mantidos:

- o mesmo Golden Dataset;
- o mesmo catálogo;
- os mesmos critérios esperados;
- os mesmos thresholds das métricas.

A alteração foi concentrada no **prompt do sistema**, permitindo comparar o comportamento antes e depois do refinamento.

---

## Modelos utilizados

| Função | Provedor | Modelo |
| --- | --- | --- |
| Chatbot | Ollama | `llama3.2:3b` |
| LLM-as-a-Judge | Gemini | `gemini-3.5-flash-lite` |

O chatbot foi executado com temperatura `0.3`.

---

## Limites do provedor

As avaliações com Gemini utilizam o **free tier**, portanto podem ocorrer erros relacionados à infraestrutura do provedor.

Entre os erros encontrados durante as execuções estão:

- `429` — limite de cota/requisições;
- `503` — indisponibilidade temporária do serviço.

Esses erros são tratados como problemas de infraestrutura e não como falhas funcionais do chatbot.

Quando necessário, recomenda-se aguardar e executar novamente apenas o caso afetado:

```bash
deepeval test run testes/test_golden_dataset.py -k "GDXX" -s
```

Isso evita reexecuções desnecessárias da suíte completa e reduz o consumo da cota gratuita.

---

## Segurança

Nenhuma chave de API deve ser adicionada diretamente ao código ou versionada no Git.

As credenciais são fornecidas exclusivamente através de variáveis de ambiente.

Exemplo:

```powershell
$env:GEMINI_API_KEY="SUA_CHAVE_AQUI"
```

Arquivos locais contendo credenciais devem permanecer fora do controle de versão.

---

## Documentação da avaliação

Os principais artefatos da entrega são:

- `golden_dataset.json` — dataset;
- `testes/test_golden_dataset.py` — suíte DeepEval;
- `README.md` — instruções de configuração e execução.