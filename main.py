from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uuid
from database import SessionLocal, ProvisioningOrder
from tasks import pipeline_provisionamento_saga

app = FastAPI(title="OrionProv Engine")
templates = Jinja2Templates(directory=".")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API: Criação de Ordem de Ativação
@app.post("/api/v1/provision")
def create_provision(customer_id: str, service_type: str, db: Session = Depends(get_db)):
    order_id = str(uuid.uuid4())[:8]
    new_order = ProvisioningOrder(
        id=order_id,
        customer_id=customer_id,
        service_type=service_type,
        status="PENDING",
        steps_completed=[]
    )
    db.add(new_order)
    db.commit()
    
    # Dispara a Saga de forma totalmente assíncrona no ecossistema do Celery
    pipeline_provisionamento_saga.delay(order_id)
    
    return {"status": "accepted", "order_id": order_id}

# FRONTEND: Painel de Controle de Operações (NOC)
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    orders = db.query(ProvisioningOrder).order_by(ProvisioningOrder.updated_at.desc()).all()
    
    # Interface HTML simples injetada diretamente (Foco em scannability)
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OrionProv Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <meta http-equiv="refresh" content="3"> <!-- Auto-refresh a cada 3s para simular tempo real -->
    </head>
    <body class="bg-slate-900 text-slate-100 p-8">
        <div class="max-w-6xl mx-auto">
            <header class="mb-8 border-b border-slate-700 pb-4 flex justify-between items-center">
                <h1 class="text-2xl font-bold tracking-wider text-indigo-400">⚡ ORION PROV // OSS ENGINE</h1>
                <span class="text-xs text-slate-400">Atualizando automaticamente a cada 3s</span>
            </header>

            <!-- Formulário para Simulação de Compra/Ativação -->
            <div class="bg-slate-800 p-6 rounded-lg mb-8 border border-slate-700">
                <h2 class="text-lg font-semibold mb-4 text-slate-300">Simular Ativação de Cliente</h2>
                <form action="/action/provision" method="post" class="flex gap-4">
                    <input type="text" name="customer_id" placeholder="ID do Cliente (ex: CLI-99)" required class="bg-slate-700 px-4 py-2 rounded text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 w-1/3">
                    <select name="service_type" class="bg-slate-700 px-4 py-2 rounded text-white focus:outline-none w-1/3">
                        <option value="FIBRA_200MB">Fibra Óptica 200 Mbps</option>
                        <option value="FIBRA_500MB">Fibra Óptica 500 Mbps</option>
                        <option value="FIBRA_1GB">Premium Link Dedicated 1 Gbps</option>
                    </select>
                    <button type="submit" class="bg-indigo-600 hover:bg-indigo-500 px-6 py-2 rounded font-bold transition w-1/3">Disparar Provisionamento</button>
                </form>
            </div>

            <!-- Tabela de Monitoramento de Circuitos/Ordens -->
            <div class="bg-slate-800 rounded-lg overflow-hidden border border-slate-700">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-slate-700 text-slate-300 uppercase text-xs tracking-wider">
                            <th class="p-4">ID Ordem</th>
                            <th class="p-4">Cliente</th>
                            <th class="p-4">Serviço</th>
                            <th class="p-4">Status</th>
                            <th class="p-4">Passos Concluídos</th>
                            <th class="p-4">Logs / Erros de Hardware</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-slate-700 text-sm">
                        {% for order in orders %}
                        <tr class="hover:bg-slate-750 transition">
                            <td class="p-4 font-mono font-bold text-indigo-300">#{{ order.id }}</td>
                            <td class="p-4">{{ order.customer_id }}</td>
                            <td class="p-4 text-slate-300">{{ order.service_type }}</td>
                            <td class="p-4">
                                {% if order.status == 'SUCCESS' %}
                                    <span class="bg-emerald-950 text-emerald-400 border border-emerald-800 px-2.5 py-1 rounded-full text-xs font-bold">✓ ATIVO</span>
                                {% elif order.status == 'PROCESSING' %}
                                    <span class="bg-amber-950 text-amber-400 border border-amber-800 px-2.5 py-1 rounded-full text-xs font-bold animate-pulse">⚙ PROVISIONANDO</span>
                                {% elif order.status == 'ROLLBACKED' %}
                                    <span class="bg-rose-950 text-rose-400 border border-rose-800 px-2.5 py-1 rounded-full text-xs font-bold">🛟 ROLLBACKED</span>
                                {% else %}
                                    <span class="bg-slate-700 text-slate-300 px-2.5 py-1 rounded-full text-xs font-bold">{{ order.status }}</span>
                                {% endif %}
                            </td>
                            <td class="p-4 font-mono text-xs text-slate-400">{{ order.steps_completed }}</td>
                            <td class="p-4 text-xs max-w-xs truncate text-rose-300" title="{{ order.error_log }}">{{ order.error_log or '-' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return templates.TemplateResponse(request=request, name="inline_template.html", context={"orders": orders})

# Rota auxiliar para processar o clique do botão do formulário
@app.post("/action/provision")
def action_provision(customer_id: str = Form(...), service_type: str = Form(...), db: Session = Depends(get_db)):
    create_provision(customer_id, service_type, db)
    return RedirectResponse(url="/", status_code=303)

# Hack rápido para rodar o template embutido string sem precisar criar arquivo separado
with open("inline_template.html", "w") as f:
    f.write("")