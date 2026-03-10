---
name: agente-stage-skill
description: Staging, modifica, preview. Sub-agent skill.
---

# Agente Stage Skill

Ricevi dall'orchestrator una richiesta con AZIONE e TUTTE le variabili gia calcolate.
NON calcolare nulla. Usa i valori ricevuti.

---

## Se AZIONE = STAGING

PASSO 1. Tool: execute_command
Comando: cp -r PROJECT_DIR STAGING_DIR && chmod -R 777 STAGING_DIR && chmod -R 777 PROJECT_DIR

PASSO 2. Tool: read_multiple_files
Usa il parametro paths (NON path).
Leggi i file principali: STAGING_DIR/templates/index.html, STAGING_DIR/static/css/style.css, STAGING_DIR/app.py

PASSO 3. Tool: edit_file
Usa il parametro file_path (NON path), old_string, new_string.
NON usare: path, edits.
Applica la modifica richiesta sui file in STAGING_DIR.

PASSO 4. Tool: build_image
path: STAGING_DIR, tag: STAGING_IMAGE:STAGING_TAG

PASSO 5. Tool: k8s_apply_manifest
Sostituisci le variabili con i valori ricevuti:

apiVersion: apps/v1
kind: Deployment
metadata:
  name: STAGING_IMAGE
  namespace: NAMESPACE
spec:
  replicas: 1
  selector:
    matchLabels:
      app: STAGING_IMAGE
  template:
    metadata:
      labels:
        app: STAGING_IMAGE
    spec:
      containers:
        - name: STAGING_IMAGE
          image: STAGING_IMAGE:STAGING_TAG
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: STAGING_IMAGE-svc
  namespace: NAMESPACE
spec:
  type: NodePort
  selector:
    app: STAGING_IMAGE
  ports:
    - port: 80
      targetPort: 5000
      nodePort: 32333

Rispondi: Staging completato.

---

## Se AZIONE = MODIFICA

PASSO 1. Tool: read_multiple_files
Usa il parametro paths (NON path).
Leggi i file necessari in STAGING_DIR.

PASSO 2. Tool: edit_file
Usa il parametro file_path (NON path), old_string, new_string.
NON usare: path, edits.
Applica la nuova modifica.

PASSO 3. Tool: build_image
path: STAGING_DIR, tag: STAGING_IMAGE:STAGING_TAG

PASSO 4. Tool: k8s_apply_manifest
Applica lo stesso manifest di STAGING con il nuovo STAGING_TAG.

Rispondi: Modifica completata.

---

## Se AZIONE = SCARTA

PASSO 1. Tool: execute_command
Comando: rm -rf STAGING_DIR

PASSO 2. Tool: k8s_delete_resource
Elimina deployment STAGING_IMAGE in NAMESPACE.

PASSO 3. Tool: k8s_delete_resource
Elimina service STAGING_IMAGE-svc in NAMESPACE.

PASSO 4. Tool: list_images
name: STAGING_IMAGE

PASSO 5. Tool: remove_image
Rimuovi una per una le immagini trovate.

Rispondi: Staging scartato.
