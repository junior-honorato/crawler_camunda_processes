🤖 RPA Camunda → Automação de Tarefas BPMN
Automação web baseada em Python (Selenium) para emular a navegação de usuário e executar em lote o fluxo de triagem, "Claim" e "Complete" em tarefas pendentes no motor de processos Camunda BPM.

📌 Problema
Durante a gestão de rotinas financeiras e de backoffice, a movimentação de processos no Camunda exige esforço manual repetitivo.
Porém:

A operação perde horas preciosas clicando, aprovando e movendo processos manualmente na interface web.

Aguardar o time de Engenharia de Software desenvolver uma integração nativa via API levaria semanas e impactaria o Sprint Goal (foco em novas features de receita).

A lentidão na execução manual gera gargalos operacionais e aumenta o tempo de resposta (SLA) do produto.

A navegação humana em listas paginadas longas é suscetível a "pulos" de tarefas e erros de triagem.

🎯 Objetivo da Ferramenta
Automatizar a triagem e execução das tarefas no Camunda, liberando a operação do trabalho braçal de "clicar e aprovar", atuando como uma solução paliativa de alto impacto (RPA) enquanto integrações sistêmicas definitivas não entram no roadmap.

A aplicação:

Acessa a URL do Camunda e realiza o login seguro (credenciais em variáveis de ambiente).

Identifica dinamicamente a paginação e a quantidade total de processos pendentes.

Percorre linha a linha as tarefas da lista.

Executa as ações de Claim (assumir a tarefa) e Complete (finalizar/avançar a tarefa).

Trata exceções comuns de interface (elementos obsoletos ou tempo de carregamento).

Gera um arquivo físico de Log de Auditoria na pasta logs/ detalhando o que foi feito.

🧪 Exemplo de Execução
Plaintext
LOG DE EXECUÇÃO - 20260219_153000
==================================================

[2026-02-19 15:30:05] [INFO] - Acessando página de login...
[2026-02-19 15:30:08] [SUCESSO] - Login realizado com sucesso
[2026-02-19 15:30:10] [INFO] - Total de páginas encontradas: 5
[2026-02-19 15:30:12] [INFO] - Processando 10 tarefas na página 1
[2026-02-19 15:30:15] [SUCESSO] 1234567890 - Processo completado
[2026-02-19 15:30:18] [SUCESSO] 1234567891 - Processo completado
...
[2026-02-19 15:35:00] [RESUMO] - Processos completados: 48
[2026-02-19 15:35:00] [RESUMO] - Processos pulados: 2

💼 Impacto no Negócio

A ferramenta contribui diretamente para:

Desafogamento Imediato: Redução drástica do retrabalho manual no backoffice da operação.

Eficiência de Engenharia: Zero impacto no backlog e no custo do time de desenvolvimento (Tech PM Hands-on).

Agilidade de SLA: Acelera o fluxo das esteiras operacionais e financeiras que dependem de aprovação.

Segurança e Compliance: O uso de .env protege dados sensíveis e a geração de relatórios txt cria uma trilha de auditoria clara.

⚙️ Funcionalidades

✔ Arquitetura em POO (Classes com responsabilidades únicas).

✔ Gestão de credenciais ocultas (Compliance).

✔ Navegação inteligente e tratamento dinâmico de paginação Web.

✔ Sistema de Resiliência (Explicit Waits e tratativas para StaleElementReferenceException).

✔ Geração automática de Logs locais com timestamp.

🛠 Tecnologias Utilizadas

Python 3

Selenium WebDriver (Navegação Web)

python-dotenv (Gestão de variáveis de ambiente)

RegEx / re (Extração de IDs de processo)

🖥️ Como usar

Clone o repositório -> Instale as dependências: pip install -r requirements.txt -> Crie um arquivo oculto chamado .env na raiz do projeto contendo as variáveis: URL_CAMUNDA, CAMUNDA_USER, CAMUNDA_PASS e EDGE_DRIVER_PATH -> Execute o script principal: python crawler.py -> Acompanhe a execução diretamente pelo terminal e confira o resumo da operação dentro da pasta /logs.

📂 Estrutura do Projeto
Plaintext
crawler_camunda_processes/

├── crawler.py

├── requirements.txt

├── .gitignore

├── .env (Oculto localmente)

├── logs/

└── README.md

🤖 Uso de Inteligência Artificial
A IA generativa (DeepSeek) foi utilizada como copiloto técnico para o PM, auxiliando na prototipação da lógica do Selenium, estruturação das classes em POO (Programação Orientada a Objetos) e tratativas de exceções.

O conhecimento de produto e negócio (mapeamento do DOM do Camunda, fluxos do BPMS, regra de negócio das tarefas e estratégia de contorno de gargalos operacionais) foi aplicado manualmente.

👤 Autor
Arlindo Júnior Honorato
Technical Product Manager | Automação | IA aplicada a Produtos Financeiros e Eficiência de Backoffice