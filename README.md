# Agent AI on Kubernetes

Sistema multi-agente basato sul framework [Kagent](https://kagent.dev) per il deploy automatizzato di applicazioni Flask su Kubernetes, con supporto ISSU (In-Service Software Upgrade) per aggiornamenti a zero downtime.

Progetto di tesi triennale in Ingegneria Informatica — Università degli Studi di Salerno.

---

## Architettura

Il sistema è composto da un **orchestrator** che coordina tre sub-agent specializzati:

```
orchestrator-agent
├── stage-agent       → Crea ambiente di staging, applica modifiche, preview
├── prepare-agent     → Copia staging in produzione, build immagine, pulizia
└── deploy-agent      → Deploy diretto o programmato tramite Kubernetes Job
```

L'orchestrator calcola tutte le variabili necessarie (tag immagini, nomi deployment, ecc.) e le passa ai sub-agent, che agiscono come esecutori puri. La verifica ISSU è gestita direttamente dall'orchestrator.

## Flusso di Deploy

1. **Staging** — L'utente richiede una modifica. L'orchestrator chiama lo `stage-agent` che crea una copia del sito, applica le modifiche, builda l'immagine e deploya un'anteprima accessibile su `http://192.168.49.2:32333`.

2. **Revisione** — L'utente sceglie:
   - **APPLICA** → procede con la preparazione
   - **SCARTA** → annulla e pulisce le risorse di staging
   - **MODIFICA** → applica ulteriori modifiche

3. **Preparazione** — Il `prepare-agent` copia i file di staging nella directory di produzione, builda la nuova immagine, aggiorna il tag nel manifest Kubernetes e pulisce tutte le risorse di staging.

4. **ISSU Check** — L'orchestrator verifica se il servizio è attualmente in uso tramite lo script `issu_check.py`.

5. **Deploy** — In base allo stato ISSU:
   - **Servizio libero** → deploy immediato tramite `deploy-agent`
   - **Servizio occupato** → l'utente sceglie tra:
     - **ATTENDI** — un Kubernetes Job attende che il servizio si liberi e poi deploya automaticamente
     - **ORARIO HH:MM** — il Job attende l'orario specificato, poi attende che il servizio si liberi e deploya
     - **DEPLOY** — procede immediatamente ignorando lo stato ISSU

## Tecnologie

- **Kagent** — Framework per agenti AI nativi su Kubernetes
- **Kubernetes** (Minikube) — Orchestrazione container
- **OpenAI GPT-4o** — Modello LLM per gli agenti
- **Flask** — Applicazione web dimostrativa
- **Docker** — Build immagini container
- **Kubernetes Jobs** — Deploy programmati asincroni

## Struttura Repository

```
├── agents/                    # Manifest YAML degli agenti Kagent
│   ├── orchestrator-agent.yaml
│   ├── stage-agent.yaml
│   ├── prepare-agent.yaml
│   └── deploy-agent.yaml
├── skills/                    # Skill degli agenti (immagini OCI)
│   ├── agente-stage-skill/
│   ├── agente-prepare-skill/
│   └── agente-deploy-skill/
├── scripts/                   # Script ISSU
│   └── issu_check.py
├── infra/                     # Risorse infrastrutturali
│   ├── deploy-rbac.yaml
│   └── yt-flask-svc.yaml
└── flask-app/                 # Applicazione Flask dimostrativa
    ├── app.py
    ├── Dockerfile
    ├── templates/
    ├── static/
    └── k8s/
        └── deployment.yaml
```

## Prerequisiti

- [Minikube](https://minikube.sigs.k8s.io/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Docker](https://www.docker.com/)
- [Kagent](https://kagent.dev) installato nel cluster
- API Key OpenAI

## Installazione

### 1. Avvio Minikube

```bash
minikube start
minikube ssh "sudo ln -sf /usr/share/zoneinfo/Europe/Rome /etc/localtime"
minikube mount ~/Desktop:/host-desktop &
```

### 2. Configurazione ModelConfig

Creare un file `infra/modelconfig.yaml` con la propria API Key:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: openai-gpt-4o
  namespace: kagent
type: Opaque
stringData:
  OPENAI_API_KEY: "sk-proj-..."
---
apiVersion: kagent.dev/v1alpha2
kind: ModelConfig
metadata:
  name: openai-gpt-4o
  namespace: kagent
spec:
  apiKeySecret: openai-gpt-4o
  apiKeySecretKey: OPENAI_API_KEY
  model: gpt-4o
  provider: OpenAI
  openAI:
    temperature: "0.3"
    timeout: 300
```

```bash
kubectl apply -f infra/modelconfig.yaml
```

### 3. Applicazione Infrastruttura

```bash
kubectl apply -f infra/deploy-rbac.yaml
kubectl apply -f infra/yt-flask-svc.yaml
```

### 4. Build e Push Skill

```bash
docker build -t localhost:5000/agente-stage-skill:latest skills/agente-stage-skill/
docker build -t localhost:5000/agente-prepare-skill:latest skills/agente-prepare-skill/
docker build -t localhost:5000/agente-deploy-skill:latest skills/agente-deploy-skill/
docker push localhost:5000/agente-stage-skill:latest
docker push localhost:5000/agente-prepare-skill:latest
docker push localhost:5000/agente-deploy-skill:latest
```

### 5. Deploy Agenti

```bash
kubectl apply -f agents/stage-agent.yaml
kubectl apply -f agents/prepare-agent.yaml
kubectl apply -f agents/deploy-agent.yaml
kubectl apply -f agents/orchestrator-agent.yaml
```

### 6. Accesso UI Kagent

```bash
kubectl port-forward -n kagent svc/kagent-ui 8082:8080 &
```

Aprire `http://localhost:8082` e selezionare `orchestrator-agent`.

## Utilizzo

Nella chat dell'orchestrator scrivere:

```
Cambia lo sfondo in rosso nel sito /desktop/flask-app, namespace kagent
```

L'orchestrator guiderà il processo mostrando menu interattivi per confermare o annullare ogni fase.

## Autore

**Antonio Manuel** — Università degli Studi di Salerno, Ingegneria Informatica
