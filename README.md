# Banco Ágil

Atendimento de um banco digital fictício feito por agentes de IA. Cada agente tem um assunto. Para o cliente, a conversa parece um único atendimento: a troca de agente não é anunciada.

Todos os dados são sintéticos e servem só para demonstração. Os CPFs são identificadores fictícios, como `11111111111`. A validação do dígito verificador não faz parte deste desafio.

# Visão Geral

O cliente entra por uma tela simples, informa CPF e data de nascimento e, depois de autenticado, pede limite, aumento de crédito ou cotação. Se o aumento for recusado, pode passar por uma entrevista que recalcula o score e devolve o assunto ao crédito.

Quatro agentes:

1. **Triagem.** Porta de entrada. Cumprimenta, pede CPF e data de nascimento e confere os dois em `clientes.csv`. Só depois da autenticação o assunto segue. Há no máximo três tentativas. Na terceira falha, o atendimento encerra.
2. **Crédito.** Informa o limite atual e registra o pedido de aumento. O pedido vai para `solicitacoes_aumento_limite.csv`. A aprovação usa a faixa de `score_limite.csv`: se o novo limite cabe no score, o status é `aprovado` e o cadastro é atualizado; se não cabe, o status é `rejeitado` e o cliente pode ir para a entrevista.
3. **Entrevista de crédito.** Coleta renda mensal, tipo de emprego (formal, autônomo ou desempregado), despesas fixas, número de dependentes e se existem dívidas ativas. O score, de 0 a 1000, é calculado em Python, gravado em `clientes.csv`, e o cliente volta ao crédito para uma nova análise.
4. **Câmbio.** Consulta a cotação de uma moeda em relação ao real numa API externa e responde com o valor ou com uma frase clara se a consulta falhar.

A qualquer momento, um pedido explícito de encerramento termina a conversa. Frases como "quero encerrar", "pode finalizar meu atendimento" e "tchau" encerram. "Fim de semana" e "sair do emprego" não encerram.

O modelo conversa, classifica a intenção e chama ferramentas. Autenticação, score e decisão de limite ficam em Python.

# Arquitetura

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
LangChain (classificação, extração ou tool calling)
    ↓
Ferramenta
    ↓
Regra em Python
    ↓
CSV ou API de câmbio
```

O orquestrador decide o turno em Python:

- atendimento já encerrado: responde e para;
- pedido explícito de fim: encerra;
- cliente sem autenticação: triagem;
- autenticado, ainda sem assunto: classifica entre crédito, câmbio ou encerrar;
- assunto já escolhido: permanece nele até o fim, ou até a entrevista devolver o cliente ao crédito.

A sessão guarda o histórico, o CPF, as tentativas, o agente ativo e os dados já coletados na entrevista. Ela fica na memória do processo.

Cada agente tem um `skill.yaml` com o comportamento esperado: nome, descrição, instruções, tópicos, passos e actions. O YAML descreve. O Python executa. As actions do YAML não criam ferramentas sozinhas; as ferramentas de cada agente estão registradas no código daquele agente.

Dados:

| Arquivo | Uso |
|---|---|
| `data/clientes.csv` | CPF, nascimento, nome, limite e score |
| `data/score_limite.csv` | Faixa de score e limite máximo |
| `data/solicitacoes_aumento_limite.csv` | Pedido com data ISO 8601 e status `aprovado` ou `rejeitado` |

O score da entrevista segue a fórmula do desafio e depois é limitado ao intervalo de 0 a 1000:

```text
score = (renda_mensal / (despesas + 1)) * 30
      + peso_emprego
      + peso_dependentes
      + peso_dividas
```

Emprego: formal 300, autônomo 200, desempregado 0. Dependentes: 0 → 100, 1 → 80, 2 → 60, 3 ou mais → 30. Dívida ativa: −100. Sem dívida: 100.

O câmbio consulta `https://api.frankfurter.app`, com timeout. Moeda inválida, demora, API fora e resposta inesperada viram texto para o cliente.

# Funcionalidades Implementadas

| Método | Caminho | Função |
|---|---|---|
| GET | `/` | Confirma que a API subiu |
| GET | `/api/v1/health` | API no ar e se a chave do modelo está configurada |
| POST | `/api/v1/sessions` | Abre um atendimento |
| GET | `/api/v1/sessions/{session_id}` | Estado e histórico |
| POST | `/api/v1/sessions/{session_id}/messages` | Envia a fala do cliente |

Ferramentas de cada agente:

| Agente | Ferramentas |
|---|---|
| Triagem | autenticar cliente, encerrar |
| Crédito | consultar limite, solicitar aumento, encerrar |
| Entrevista | calcular score, atualizar score, encerrar |
| Câmbio | consultar cotação, encerrar |

A tela Streamlit inicia a conversa, mostra o histórico e encerra. Ela só fala com a API por HTTP.

# Desafios Enfrentados e Como Foram Resolvidos

Separar conversa de regra financeira. O modelo interpreta a intenção e escolhe a ferramenta. Python autentica, calcula o score e aprova ou rejeita o limite.

Trocar de agente sem o cliente perceber. A sessão guarda o agente ativo. O orquestrador chama o módulo certo. A ida para a entrevista, quando o aumento é rejeitado e o cliente aceita, é uma decisão explícita no agente de crédito.

Manter a instrução fora da regra. O YAML descreve o atendimento. A fórmula, a faixa de score e a comparação do CPF ficam no código.

A API de câmbio pode falhar. A integração traduz timeout, moeda inválida, indisponibilidade e payload inesperado. O erro técnico fica no log. O cliente recebe uma frase.

Uma palavra solta como "fim" ou "sair" encerrava a conversa no meio de outra frase. O encerramento passou a exigir uma intenção explícita, como "quero encerrar" ou "tchau".

# Escolhas Técnicas e Justificativas

LangChain entra em três pontos: o cliente do modelo, a saída estruturada e a chamada de ferramentas. A classificação depois da autenticação devolve crédito, câmbio ou encerrar. A entrevista extrai só os campos ditos na mensagem. Crédito e câmbio usam tool calling.

FastAPI é a API do atendimento. A tela não importa os agentes.

LangGraph não foi usado. Os estados são poucos e conhecidos: encerrado, autenticado, agente ativo e espera da entrevista. A orquestração em Python deixa o caminho visível e testável.

As skills YAML separam a instrução conversacional da regra. YAML descreve o comportamento. Python mantém autenticação, score e limite.

O modelo pago fica atrás de variáveis de ambiente. No ambiente publicado a chave é do Azure OpenAI, com endpoint e deployment próprios. O OpenRouter continua aceito em desenvolvimento se a chave do Azure não estiver preenchida. A regra de crédito não muda quando o fornecedor muda.

O CSV ficou porque o desafio pede leitura e gravação nesses arquivos. Não há banco.

Autenticação, score e decisão de limite ficam fora do modelo para o resultado ser o mesmo em todo teste.

# Como Executar

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

- API: http://127.0.0.1:8000/docs
- Tela: http://127.0.0.1:8501

No `.env`, preencha a chave do Azure ou a do OpenRouter. Esse arquivo não entra no Git. O detalhe está na seção da chave, abaixo.

Docker:

```powershell
docker compose up --build
```

A API publica a porta 8000 e o Streamlit a 8501. A chave entra só como variável de ambiente do processo da API.

# Chave do modelo

A conversa usa uma chave paga do Azure OpenAI. A escolha é de operação, não de regra de negócio.

Uma chave paga identifica um deployment contratado, com cota e responsável. Isso é o que se espera num atendimento que sai da máquina de quem desenvolveu e fica no ar para outra pessoa testar. Chave gratuita de demonstração costuma cortar no meio da conversa ou mudar de endereço. A autenticação, o score e a aprovação de limite não dependem dessa chave: continuam em Python. O modelo só classifica a intenção, extrai os campos da entrevista, escolhe a ferramenta e redige a frase.

A chave fica somente na variável de ambiente do processo da API. O Streamlit não a recebe. O navegador não a recebe. O Git não a recebe.

No ambiente publicado, as variáveis são:

```text
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY
AZURE_OPENAI_API_VERSION
AZURE_OPENAI_DEPLOYMENT_CHAT
```

Se a chave do Azure estiver preenchida, ela tem prioridade. `OPENROUTER_API_KEY` só entra quando a do Azure não existe. A triagem autentica sem chave. Crédito, entrevista e câmbio precisam dela para o modelo falar.

Para conferir se o processo enxergou a chave, abra o health. O campo `llm_configured` fica `true` quando a chave está no ambiente. Ele não devolve a chave.

# Teste na Hostinger

A API publicada no EasyPanel da Hostinger:

- Aplicação: https://banco-agil-agents.jk5mhc.easypanel.host/
- Documentação: https://banco-agil-agents.jk5mhc.easypanel.host/docs
- Health: https://banco-agil-agents.jk5mhc.easypanel.host/api/v1/health

Esse endereço é a API, na porta 8000 do aplicativo `agentes`, no projeto `banco-agil`. A tela Streamlit é outro aplicativo e fala com essa API por dentro do painel. Ela não carrega a chave.

Pelo `/docs` dá para abrir uma sessão e enviar mensagem. Sem `llm_configured: true`, a triagem ainda autentica. Crédito, entrevista e câmbio respondem que o modelo não está configurado até a chave estar salva no painel e o aplicativo ser implantado de novo.

# Testes

```powershell
.\.venv\Scripts\Activate.ps1
pytest -v
```

A suíte é curta e cobre os riscos do desafio: saúde da API, abertura de sessão, autenticação válida, terceira falha, consulta de limite, aumento aprovado, aumento rejeitado, cálculo do score, score entre 0 e 1000, valor negativo rejeitado, cotação, timeout da API de câmbio, encerramento explícito, frase parecida que não encerra, e o roteamento de limite para crédito e de dólar para câmbio.

O roteamento usa um modelo falso em `tests/fakes.py`. A suíte não chama o Azure nem o OpenRouter.

# Limitações

- A sessão fica na memória e some quando a API reinicia.
- Depois do roteamento, o assunto permanece no agente escolhido até o encerramento ou até a entrevista devolver o cliente ao crédito.
- Aprovado e rejeitado saem na hora. O desenho do CSV cita o status `pendente`, mas esta versão não deixa pedido em análise manual.
- O modelo falso dos testes não substitui uma conversa com o modelo real.
