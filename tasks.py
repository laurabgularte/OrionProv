from celery import Celery
import random
import time
from database import SessionLocal, ProvisioningOrder
from config import REDIS_URL

celery_app = Celery("tasks", broker=REDIS_URL, backend=REDIS_URL)

# -------------------------------------------------------------------------
# SIMULADORES DE EQUIPAMENTO DE REDE (MOCKS DE TELECOM)
# -------------------------------------------------------------------------
def simulate_radius_server(customer_id: str, action: str):
    """Simula autenticação AAA (Radius)"""
    time.sleep(1.5) # Simula latência de rede
    if action == "create":
        return {"status": "success", "msg": f"User {customer_id}@orion fiber created."}
    elif action == "delete":
        return {"status": "success", "msg": f"User {customer_id}@orion fiber removed."}

def simulate_olt_gpon(customer_id: str, action: str):
    """Simula a configuração física da porta de Fibra na OLT"""
    time.sleep(2.0)
    if action == "provision":
        # Injetando falha intermitente de 40% para testar a resiliência do Sênior
        if random.random() < 0.4:
            raise Exception("OLT_TIMEOUT: Equipamento de rede não respondeu ao comando CLI via SSH.")
        return {"status": "success", "profile": "500_MBPS_VLAN_100"}
    elif action == "deprovision":
        return {"status": "success", "msg": "Port cleared."}

# -------------------------------------------------------------------------
# ORQUESTRADOR DA SAGA (WORKERS CELERY)
# -------------------------------------------------------------------------
@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)
def pipeline_provisionamento_saga(self, order_id: str):
    db = SessionLocal()
    order = db.query(ProvisioningOrder).filter(ProvisioningOrder.id == order_id).first()
    
    if not order:
        return "Order not found"

    order.status = "PROCESSING"
    db.commit()

    steps = order.steps_completed or []

    try:
        # PASSO 1: Provisionar no Servidor de Autenticação Radius
        if "RADIUS_AUTH" not in steps:
            print(f"[*] Executando PASSO 1 (RADIUS) para ordem {order_id}")
            simulate_radius_server(order.customer_id, "create")
            steps.append("RADIUS_AUTH")
            order.steps_completed = steps
            db.commit()

        # PASSO 2: Provisionar Perfil de Velocidade na OLT GPON (Gargalo de hardware)
        if "OLT_GPON" not in steps:
            print(f"[*] Executando PASSO 2 (OLT GPON) para ordem {order_id}")
            simulate_olt_gpon(order.customer_id, "provision")
            steps.append("OLT_GPON")
            order.steps_completed = steps
            db.commit()

        # Se tudo der certo
        order.status = "SUCCESS"
        db.commit()
        print(f"[✓] Ordem {order_id} provisionada com sucesso absoluto.")

    except Exception as exc:
        db.refresh(order)
        # Se falhou no PASSO 2 e ainda temos tentativas, aplica Exponential Backoff
        if self.request.retries < self.max_retries:
            order.error_log = f"Tentativa {self.request.retries + 1} falhou: {str(exc)}. Tentando novamente..."
            db.commit()
            db.close()
            # Multiplica o delay a cada falha (Exponencial)
            countdown = int(self.default_retry_delay * (2 ** self.request.retries))
            raise self.retry(exc=exc, countdown=countdown)
        
        # EXCEDEU RETENTATIVAS: Iniciar Mecanismo de Rollback (Transação Compensatória)
        print(f"[🛟] Iniciando transações compensatórias para a ordem {order_id}...")
        order.status = "FAILED"
        order.error_log = f"Falha definitiva após 3 tentativas. Motivo: {str(exc)}"
        db.commit()

        # Executa rollback inverso das etapas concluídas
        if "RADIUS_AUTH" in steps:
            try:
                simulate_radius_server(order.customer_id, "delete")
                steps.remove("RADIUS_AUTH")
                print(f"[🛟] Rollback: Usuário removido do Radius com sucesso.")
            except Exception as e:
                print(f"[CRÍTICO] Falha ao desfazer Radius: {str(e)}")

        order.status = "ROLLBACKED"
        order.steps_completed = steps
        db.commit()
    
    finally:
        db.close()