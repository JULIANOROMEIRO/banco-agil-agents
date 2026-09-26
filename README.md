# Banco Ágil

Atendimento de um banco digital fictício, com quatro agentes de IA. O cliente conversa em uma tela só. Por trás, cada assunto tem um agente, uma ferramenta e uma regra em Python.

Os dados são sintéticos. Os CPFs, como `11111111111`, não são documentos reais e não passam por dígito verificador.

**Chat para avaliação:** https://banco-agil-chat.jk5mhc.easypanel.host/

**API:** https://banco-agil-agents.jk5mhc.easypanel.host/docs

## Visão Geral

O cliente informa CPF e data de nascimento. Com os dados conferidos em `clientes.csv`, o atendimento oferece três serviços:

1. Consultar o limite de crédito.
2. Solicitar aumento de limite.
3. Consultar a cotação de uma moeda.

Há no máximo três tentativas de autenticação. Na terceira falha, a conversa encerra.

| Agente | O que faz |
|---|---|
| Triagem | Autentica CPF e data de nascimento e só então apresenta os serviços. |
| Crédito | Consulta o limite e registra o aumento em `solicitacoes_aumento_limite.csv`. Aprova se o novo valor é maior que o atual e cabe na faixa de `score_limite.csv`. |
| Entrevista de crédito | Se o aumento é rejeitado e o cliente aceita, coleta renda, emprego, despesas, dependentes e dívidas. Recalcula o score e devolve o cliente ao crédito. |
| Câmbio | Consulta a cotação em uma API externa e traduz falha de rede, moeda ou payload em uma frase. |

O modelo classifica a intenção, extrai os campos da entrevista e chama a ferramenta. Quem autentica, calcula o score e aprova o limite é Python.

Um pedido explícito encerra a conversa: "quero encerrar", "pode finalizar meu atendimento", "tchau". "Fim de semana" e "sair do emprego" não encerram.

## Arquitetura

```text
Streamlit
    ↓
FastAPI  /api/v1
    ↓
Sessão
    ↓
Orquestrador
    ↓
Agente do turno
    ↓
LangChain
    ↓
Ferramenta
    ↓
Regra em Python
    ↓
CSV ou API de câmbio
```

O orquestrador decide o turno:

- atendimento já encerrado: responde e para;
- pedido explícito de fim: encerra;
- cliente sem autenticação: triagem;
- autenticado e ainda sem assunto: classifica crédito, câmbio ou encerrar;
- assunto já escolhido: permanece nele, salvo pedido explícito do outro serviço;
- entrevista: não troca de assunto no meio das respostas. No fim, devolve o cliente ao crédito.

A sessão fica na memória do processo. Guarda histórico, CPF, tentativas, agente ativo e os dados já ditos na entrevista.

Cada agente tem um `skill.yaml` com nome, descrição, instruções, tópicos, passos e actions. O YAML descreve o atendimento. O Python executa. O menu exibido depois da autenticação é lido dos passos do tópico `oferecer_servicos`, na skill da triagem. As actions do YAML não criam ferramentas. Cada agente registra as suas no próprio código.

Os schemas Pydantic seguem o papel do template FastAPI do projeto: validar entrada e saída da API e os dados coletados na entrevista. Eles não guardam texto de conversa.

### Dados

| Arquivo | Conteúdo |
|---|---|
| `data/clientes.csv` | CPF, nascimento, nome, limite e score |
| `data/score_limite.csv` | Faixa de score e limite máximo |
| `data/solicitacoes_aumento_limite.csv` | Pedido com data ISO 8601 e status `aprovado` ou `rejeitado` |

Faixas de limite:

| Score | Limite máximo |
|---|---|
| 0 a 299 | 1.000 |
| 300 a 599 | 5.000 |
| 600 a 799 | 15.000 |
| 800 a 1000 | 50.000 |

O score da entrevista usa a fórmula do desafio e fica entre 0 e 1000:

```text
score = (renda_mensal / (despesas + 1)) * 30
      + peso_emprego
      + peso_dependentes
      + peso_dividas
```

Emprego: formal 300, autônomo 200, desempregado 0. Dependentes: 0 recebe 100, 1 recebe 80, 2 recebe 60, 3 ou mais recebe 30. Dívida ativa tira 100. Sem dívida soma 100.

O câmbio consulta `https://api.frankfurter.app`, com timeout de 5 segundos.

## Funcionalidades Implementadas

| Método | Caminho | Função |
|---|---|---|
| GET | `/` | Confirma que a API subiu |
| GET | `/api/v1/health` | API no ar e se a chave do modelo está configurada |
| POST | `/api/v1/sessions` | Abre um atendimento |
| GET | `/api/v1/sessions/{session_id}` | Estado e histórico |
| POST | `/api/v1/sessions/{session_id}/messages` | Envia a fala do cliente |

| Agente | Ferramentas |
|---|---|
| Triagem | autenticar cliente, encerrar |
| Crédito | consultar limite, solicitar aumento, encerrar |
| Entrevista | calcular score, atualizar score, encerrar |
| Câmbio | consultar cotação, encerrar |

A tela Streamlit só fala com a API por HTTP. Ela não importa agente nem lê CSV.

## Desafios Enfrentados e Como Foram Resolvidos

A regra financeira não pode depender do texto do modelo. O modelo escolhe a ferramenta. Python autentica, calcula o score e aprova ou rejeita. A frase de limite, aprovação e cotação que o cliente vê é o retorno da ferramenta, não uma reescrita livre.

A troca de agente não é anunciada. A sessão guarda o agente ativo e o orquestrador chama o módulo certo. Quando o aumento é rejeitado e o cliente aceita, o crédito passa a entrevista. No fim do cálculo, a entrevista devolve o cliente ao crédito.

A instrução do atendimento fica fora da conta. O YAML descreve. A fórmula, a faixa e a comparação do CPF ficam no código.

A API de câmbio falha. Timeout, moeda inválida, serviço fora e payload inesperado viram uma frase. O detalhe técnico fica no log.

"Fim" e "sair" no meio de outra frase encerravam o atendimento. O encerramento passou a exigir intenção explícita.

## Escolhas Técnicas e Justificativas

LangChain cobre três usos: o cliente do modelo, a saída estruturada e a chamada de ferramenta. A primeira mensagem depois da autenticação devolve crédito, câmbio ou encerrar. A entrevista extrai só os campos ditos naquela fala. Crédito e câmbio usam tool calling.

FastAPI é a API. A organização segue o template já usado em outros trabalhos: `api/api_v1/endpoints`, `schemas`, `services`, `crud` e `core`.

LangGraph não entrou. Os estados são poucos: encerrado, autenticado, agente ativo e espera da entrevista. Um orquestrador em Python deixa esse caminho legível e testável.

O YAML descreve o comportamento. Python guarda a regra. Criar um motor que transformasse cada action do YAML em ferramenta seria uma plataforma, e o desafio pede um atendimento.

A chave do modelo é paga, do Azure OpenAI, com deployment próprio. Uma chave de demonstração gratuita corta cota e muda de endereço. Aqui a chave identifica um recurso contratado, com responsável, para outra pessoa testar o atendimento no ar. Ela não decide score nem limite. Se a chave do Azure não estiver preenchida, o desenvolvimento ainda aceita OpenRouter. A regra não muda com o fornecedor.

O CSV ficou porque o desafio pede esses arquivos. Não há banco.

## Como Executar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Em outro terminal:

```powershell
$env:API_BASE_URL = "http://localhost:8000"
streamlit run streamlit_app.py
```

- API local: http://127.0.0.1:8000/docs
- Tela local: http://127.0.0.1:8501

O `.env` não entra no Git. Preencha a chave do Azure ou, na ausência dela, a do OpenRouter.

```powershell
docker compose up --build
```

A API publica a porta 8000 e o Streamlit a 8501. A chave entra só no processo da API.

## Chave do modelo

A chave fica na variável de ambiente da API. A tela, o navegador e o Git não a recebem.

```text
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY
AZURE_OPENAI_API_VERSION
AZURE_OPENAI_DEPLOYMENT_CHAT
```

Com a chave do Azure preenchida, ela tem prioridade. A triagem autentica sem ela. Crédito, entrevista e câmbio precisam do modelo para conversar e escolher a ferramenta.

O health confirma a presença da chave, sem revelá-la: `llm_configured` igual a `true`.

https://banco-agil-agents.jk5mhc.easypanel.host/api/v1/health

## Teste na Hostinger

Abra o chat e clique em **Iniciar atendimento**:

https://banco-agil-chat.jk5mhc.easypanel.host/

A data no CSV está em `AAAA-MM-DD`. No chat, use `DD/MM/AAAA`.

| Cliente | CPF | Nascimento | Limite | Score | Uso na demonstração |
|---|---|---|---|---|---|
| Ana Lima | `11111111111` | `15/05/1990` | 20.000 | 850 | Aumento até 50.000 |
| Bruno Costa | `22222222222` | `02/11/1985` | 2.000 | 450 | Aumento até 5.000 |
| Carla Dias | `33333333333` | `20/01/1992` | 500 | 200 | Pedido acima de 1.000 é rejeitado |

Na mesma conversa, um pedido explícito troca de assunto sem avisar. "Quero a cotação do dólar" sai do crédito e vai ao câmbio. "Quero consultar meu limite" faz o caminho inverso. Um número, como `30000`, não troca: continua sendo o valor do limite. Durante a entrevista, as respostas não mudam de agente.

**Crédito e cotação, na mesma conversa**

1. `11111111111`
2. `15/05/1990`
3. A resposta lista os três serviços.
4. `Quero consultar meu limite`
5. `Quero aumentar meu limite para 30000`
6. O pedido é aprovado: 30.000 é maior que 20.000 e cabe no score 850.
7. `Quero saber a cotação do dólar`
8. `quero encerrar`

`8000` para a Ana é rejeitado. O novo limite precisa ser maior que o atual. Se a rejeição for por estourar a faixa, o crédito oferece a entrevista.

`fim de semana` não encerra. `quero encerrar` encerra.

A documentação da API fica separada do chat: https://banco-agil-agents.jk5mhc.easypanel.host/docs

## Testes

```powershell
.\.venv\Scripts\Activate.ps1
pytest -v
```

A suíte cobre o risco de cada parte do desafio: saúde da API, sessão, autenticação, terceira falha, consulta de limite, aumento aprovado, aumento rejeitado, score, intervalo de 0 a 1000, valor negativo, cotação, timeout da API de câmbio, encerramento explícito, frase parecida que não encerra, e o roteamento de limite para crédito e de dólar para câmbio.

O roteamento usa um modelo falso em `tests/fakes.py`. A suíte não gasta a chave paga.

## Limitações

- A sessão some quando a API reinicia.
- Durante a entrevista, o assunto não muda. Fora dela, limite e cotação se alternam quando o pedido é explícito.
- Aprovado e rejeitado saem na hora. O CSV prevê `pendente`, e esta versão não deixa pedido em análise manual.
- O modelo falso dos testes não substitui a conversa com o Azure.
