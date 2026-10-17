# CLAUDE.md — crawler_camunda_processes

RPA em Selenium que faz login no Camunda BPM e executa em lote "Claim" e "Complete" nas tarefas pendentes, gerando log de auditoria.

## Stack

- Python 3 + Selenium 4 + python-dotenv (`requirements.txt`).
- Script único: `crawler_Camunda_Deep.py` (classes `Config`, `Logger`, `BrowserManager`, `CamundaLogin`, `PaginationHandler`, `TaskProcessor`, `TaskHandler`).

## Como rodar localmente (macOS)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python crawler_Camunda_Deep.py
```

## Variáveis de ambiente (`.env`)

- `URL_CAMUNDA`, `CAMUNDA_USER`, `CAMUNDA_PASS`
- `EDGE_DRIVER_PATH` (opcional; padrão `msedgedriver.exe`)

## Armadilhas

- Feito para Windows: usa Microsoft Edge + EdgeDriver (`msedgedriver.exe`). No macOS é preciso instalar o Edge e apontar `EDGE_DRIVER_PATH` para o `msedgedriver` do Mac.
- `requirements.txt` está em ASCII com quebras de linha CRLF (gerado no Windows) e sem newline final.
- Logs são gravados em `logs/` (ignorado pelo git). Não há `.env.example`.

## Fluxo de trabalho

- Autonomia para commitar e dar push na main (projeto pessoal).
- Responder sempre em português do Brasil.
