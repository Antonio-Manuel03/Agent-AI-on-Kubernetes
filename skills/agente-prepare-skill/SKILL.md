---
name: agente-prepare-skill
description: Copia staging in prod, builda, pulisce staging. Sub-agent skill.
---

# Agente Prepare Skill

Ricevi dall'orchestrator TUTTE le variabili gia calcolate:
PROJECT_DIR, STAGING_DIR, STAGING_IMAGE, NAMESPACE, DEPLOYMENT_NAME, PROD_IMAGE, CURRENT_TAG, NEW_TAG.
NON calcolare nulla. Usa i valori ricevuti.

---

PASSO 1. Tool: execute_command
Comando: cp -r STAGING_DIR/. PROJECT_DIR/ && echo copia ok

PASSO 2. Tool: build_image
path: PROJECT_DIR, tag: PROD_IMAGE:NEW_TAG

PASSO 3. Tool: edit_file
Usa il parametro file_path (NON path), old_string, new_string.
NON usare: path, edits.
file_path: PROJECT_DIR/k8s/deployment.yaml
old_string: image: PROD_IMAGE:CURRENT_TAG
new_string: image: PROD_IMAGE:NEW_TAG

PASSO 4. Tool: execute_command
Comando: rm -rf STAGING_DIR

PASSO 5. Tool: k8s_delete_resource
Elimina deployment STAGING_IMAGE in NAMESPACE.

PASSO 6. Tool: k8s_delete_resource
Elimina service STAGING_IMAGE-svc in NAMESPACE.

PASSO 7. Tool: list_images
name: STAGING_IMAGE

PASSO 8. Tool: remove_image
Rimuovi una per una le immagini trovate al passo 7.

Rispondi: Preparazione completata.
