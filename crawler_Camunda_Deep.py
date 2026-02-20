import os
import re
import time
from datetime import datetime
from selenium import webdriver
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

class Config:
# Usa caminhos relativos para funcionar em qualquer computador
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    
    # Se o driver estiver na mesma pasta do script, ele acha automático. 
    # Senão, você pode configurar nas variáveis de ambiente.
    EDGE_DRIVER_PATH = os.getenv("EDGE_DRIVER_PATH", "msedgedriver.exe")
    
    URL_CAMUNDA = os.getenv("URL_CAMUNDA")
    USUARIO = os.getenv("CAMUNDA_USER")
    SENHA = os.getenv("CAMUNDA_PASS")

    TIMEOUT_GERAL = 30
    TIMEOUT_ACAO = 10
    PAUSA_ENTRE_ACOES = 1
    MAX_TENTATIVAS_PAGINA = 3

class Logger:
    def __init__(self):
        self.log_file = self._setup_log_file()
        self.processos_completados = set()
        self.processos_pulados = set()
        self.todos_processos_vistos = set()

    def _setup_log_file(self):
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(Config.LOG_DIR, f"log_{timestamp}.txt")
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"LOG DE EXECUÇÃO - {timestamp}\n")
            f.write("="*50 + "\n\n")
        return log_path

    def log(self, processo, status, mensagem):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{status}] {processo if processo else '-'} - {mensagem}\n"
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        print(log_entry.strip())

    def log_resumo(self):
        self.log("-", "RESUMO", f"Processos completados: {len(self.processos_completados)}")
        self.log("-", "RESUMO", f"Processos pulados: {len(self.processos_pulados)}")
        self.log("-", "RESUMO", f"Total processados: {len(self.processos_completados) + len(self.processos_pulados)}")
        
        if self.processos_completados:
            self.log("-", "RESUMO", "Detalhes dos completados:")
            for i, proc in enumerate(self.processos_completados, 1):
                self.log("-", "RESUMO", f"{i}. {proc}")
        
        if self.processos_pulados:
            self.log("-", "RESUMO", "Detalhes dos pulados:")
            for i, proc in enumerate(self.processos_pulados, 1):
                self.log("-", "RESUMO", f"{i}. {proc}")

class BrowserManager:
    @staticmethod
    def initialize_driver():
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-infobars")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        
        service = EdgeService(executable_path=Config.EDGE_DRIVER_PATH)
        driver = webdriver.Edge(service=service, options=options)
        driver.set_page_load_timeout(Config.TIMEOUT_GERAL)
        return driver

class CamundaLogin:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
        self.wait = WebDriverWait(driver, Config.TIMEOUT_GERAL)

    def execute(self):
        self.logger.log("-", "INFO", "Acessando página de login...")
        self.driver.get(Config.URL_CAMUNDA)
        
        self._preencher_campo("input[placeholder='Username']", Config.USUARIO)
        self._preencher_campo("input[placeholder='Password']", Config.SENHA)
        
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ol.tasks-list")))
        self.logger.log("-", "SUCESSO", "Login realizado com sucesso")

    def _preencher_campo(self, seletor, valor):
        campo = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, seletor)))
        campo.send_keys(valor)
        time.sleep(Config.PAUSA_ENTRE_ACOES)

class PaginationHandler:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
        self.wait = WebDriverWait(driver, Config.TIMEOUT_GERAL)

    def get_total_pages(self):
        tentativas = 0
        while tentativas < Config.MAX_TENTATIVAS_PAGINA:
            try:
                # Espera até que a paginação esteja visível
                pagination = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.pagination"))
                )
                links = pagination.find_elements(By.TAG_NAME, "a")
                paginas = [int(link.text) for link in links if link.text.isdigit()]
                return max(paginas) if paginas else 1
            except (NoSuchElementException, StaleElementReferenceException) as e:
                tentativas += 1
                self.logger.log("-", "AVISO", f"Tentativa {tentativas} de obter paginação falhou. {str(e)}")
                time.sleep(Config.PAUSA_ENTRE_ACOES * 2)
        
        self.logger.log("-", "ERRO", "Não foi possível obter o total de páginas após várias tentativas")
        return 1

    def go_to_page(self, page_number):
        tentativas = 0
        while tentativas < Config.MAX_TENTATIVAS_PAGINA:
            try:
                pagination = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.pagination"))
                )
                links = pagination.find_elements(By.TAG_NAME, "a")
                
                for link in links:
                    if link.text.strip() == str(page_number):
                        link.click()
                        time.sleep(Config.PAUSA_ENTRE_ACOES * 2)  # Tempo extra para carregar a página
                        
                        # Verifica se a navegação foi bem-sucedida
                        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ol.tasks-list")))
                        self.logger.log("-", "INFO", f"Navegando para página {page_number}")
                        return True
                
                return False
                
            except (NoSuchElementException, StaleElementReferenceException) as e:
                tentativas += 1
                self.logger.log("-", "AVISO", f"Tentativa {tentativas} de navegar para página {page_number} falhou. {str(e)}")
                time.sleep(Config.PAUSA_ENTRE_ACOES * 2)
        
        self.logger.log("-", "ERRO", f"Não foi possível navegar para a página {page_number} após várias tentativas")
        return False

class TaskProcessor:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
        self.wait = WebDriverWait(driver, Config.TIMEOUT_ACAO)

    def process_task(self, task_element, task_id):
        try:
            self._scroll_to_element(task_element)
            task_element.click()
            time.sleep(Config.PAUSA_ENTRE_ACOES)

            self._claim_task()
            self._complete_task()
            
            self.logger.log(task_id, "SUCESSO", "Processo completado")
            return True

        except Exception as e:
            self.logger.log(task_id, "ERRO", str(e))
            return False

    def _scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)

    def _claim_task(self):
        try:
            claim_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.claim")))
            claim_btn.click()
            self.logger.log("-", "INFO", "Claim realizado com sucesso")
            time.sleep(Config.PAUSA_ENTRE_ACOES)
        except TimeoutException:
            self.logger.log("-", "INFO", "Claim não necessário")

    def _complete_task(self):
        try:
            complete_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[ng-click='complete()']:not([disabled])"))
            )
            complete_btn.click()
            # Aguarda a confirmação de conclusão
            time.sleep(Config.PAUSA_ENTRE_ACOES * 2)
        except TimeoutException as e:
            raise Exception("Botão Complete não disponível ou desabilitado")

class TaskHandler:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
        self.pagination = PaginationHandler(driver, logger)
        self.task_processor = TaskProcessor(driver, logger)
        self.wait = WebDriverWait(driver, Config.TIMEOUT_GERAL)

    def process_all_tasks(self):
        pagina_atual = 1
        total_paginas = self.pagination.get_total_pages()
        self.logger.log("-", "INFO", f"Total de páginas encontradas: {total_paginas}")

        while pagina_atual <= total_paginas:
            if pagina_atual > 1:
                if not self.pagination.go_to_page(pagina_atual):
                    break  # Se não conseguir navegar, interrompe o loop

            self._process_tasks_on_current_page(pagina_atual)
            
            # Verifica se há mais páginas (pode ter mudado dinamicamente)
            novo_total = self.pagination.get_total_pages()
            if novo_total > total_paginas:
                self.logger.log("-", "INFO", f"Total de páginas atualizado: {novo_total} (anterior: {total_paginas})")
                total_paginas = novo_total
            
            pagina_atual += 1

    def _process_tasks_on_current_page(self, pagina):
        tentativas = 0
        while tentativas < Config.MAX_TENTATIVAS_PAGINA:
            try:
                # Espera até que a lista de tarefas esteja carregada
                lista_processos = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ol.tasks-list"))
                )
                processos = lista_processos.find_elements(By.CSS_SELECTOR, "li.task")
                
                # Coleta todos os IDs da página antes de processar
                tasks_on_page = self._extract_task_ids(processos)
                
                if not tasks_on_page:
                    self.logger.log("-", "INFO", f"Nenhuma tarefa encontrada na página {pagina}")
                    break

                self.logger.log("-", "INFO", f"Processando {len(tasks_on_page)} tarefas na página {pagina}")
                
                for task_id, task_element in tasks_on_page:
                    if task_id in self.logger.todos_processos_vistos:
                        self.logger.processos_pulados.add(task_id)
                        self.logger.log(task_id, "INFO", "Pulando o processo ID já percorrido na busca")
                        continue

                    self.logger.todos_processos_vistos.add(task_id)
                    if self.task_processor.process_task(task_element, task_id):
                        self.logger.processos_completados.add(task_id)
                
                break  # Sai do loop de tentativas se bem-sucedido
                
            except (StaleElementReferenceException, NoSuchElementException) as e:
                tentativas += 1
                self.logger.log("-", "AVISO", f"Tentativa {tentativas} de processar página {pagina} falhou. {str(e)}")
                time.sleep(Config.PAUSA_ENTRE_ACOES * 2)
        
        if tentativas >= Config.MAX_TENTATIVAS_PAGINA:
            self.logger.log("-", "ERRO", f"Não foi possível processar a página {pagina} após várias tentativas")

    def _extract_task_ids(self, tasks):
        tasks_with_ids = []
        for task in tasks:
            try:
                # Extrai o número do processo do texto do elemento
                task_text = task.text
                match = re.search(r'(\d{10})', task_text)
                if match:
                    task_id = match.group(1)
                    tasks_with_ids.append((task_id, task))
            except StaleElementReferenceException:
                continue  # Ignora elementos que não existem mais
        return tasks_with_ids

def main():
    logger = Logger()
    driver = BrowserManager.initialize_driver()
    
    try:
        # Fluxo de login
        login = CamundaLogin(driver, logger)
        login.execute()
        
        # Processamento das tarefas
        task_handler = TaskHandler(driver, logger)
        task_handler.process_all_tasks()
        
    except Exception as e:
        logger.log("-", "ERRO CRÍTICO", f"Erro durante a execução: {str(e)}")
        raise
    finally:
        driver.quit()
        logger.log("-", "INFO", "Navegador fechado com sucesso")
        logger.log_resumo()

if __name__ == "__main__":
    main()