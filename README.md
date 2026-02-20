🤖 RPA Camunda: Automação de Backoffice (Tech PM Case)
🎯 O Problema de Negócio
Durante a gestão de rotinas financeiras, identificou-se um gargalo operacional crítico nas tarefas de usuário do Camunda BPMN. A operação perdia horas preciosas aprovando e movendo processos manualmente na interface.

Aguardar o time de Engenharia desenvolver uma integração nativa via API levaria semanas e impactaria o Sprint Goal (foco em novas features de receita).

💡 A Solução (Hands-on Product Management)
Como Technical PM, utilizei IA Generativa (DeepSeek) como copiloto para prototipar e desenvolver unilateralmente um script em Python (Selenium).

O script atua como um Web Crawler e RPA, emulando a navegação do usuário, tratando paginações dinâmicas, identificando tarefas pendentes e executando o "Claim" e "Complete" de forma automatizada e segura, gerando logs de auditoria.

🛠️ Tecnologias Utilizadas
Python 3 & Selenium: Orquestração e navegação Web.

POO (Orientação a Objetos): Arquitetura limpa dividida em classes de responsabilidade única (Logger, PaginationHandler, TaskProcessor).

Dotenv: Gestão segura de credenciais e compliance.

Explicit Waits: Tratamento de exceções avançadas (StaleElementReference) para resiliência do robô.

🚀 Resultados
Desafogamento imediato do backoffice operacional.

Zero impacto no backlog e no custo do time de Engenharia de Software.