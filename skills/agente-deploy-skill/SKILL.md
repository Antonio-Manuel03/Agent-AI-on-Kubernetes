---
name: agente-deploy-skill
description: Rollout restart o Job programmato. Sub-agent skill.
---

# Agente Deploy Skill

Ricevi dall'orchestrator TUTTE le variabili gia calcolate:
AZIONE, DEPLOYMENT_NAME, PROJECT_DIR, NAMESPACE, PROD_IMAGE, NEW_TAG, MODIFICHE.
Se AZIONE = ORARIO ricevi anche: ORARIO (formato HH:MM).
NON calcolare nulla. Usa i valori ricevuti.

---

## Se AZIONE = DEPLOY

PASSO 1. Tool: read_file
Usa il parametro file_path (NON path).
Leggi PROJECT_DIR/k8s/deployment.yaml.

PASSO 2. Tool: k8s_apply_manifest
Applica il contenuto letto al passo 1.

PASSO 3. Tool: k8s_rollout
deployment: DEPLOYMENT_NAME, namespace: NAMESPACE, action: restart

Rispondi: Deploy completato.

---

## Se AZIONE = ATTENDI

PASSO 1. Tool: k8s_apply_manifest
Sostituisci DEPLOYMENT_NAME e MANIFEST_PATH con i valori reali.
MANIFEST_PATH = PROJECT_DIR/k8s/deployment.yaml

apiVersion: batch/v1
kind: Job
metadata:
  name: scheduled-deploy
  namespace: kagent
spec:
  ttlSecondsAfterFinished: 60
  backoffLimit: 0
  template:
    spec:
      serviceAccountName: deploy-sa
      volumes:
        - name: desktop
          hostPath:
            path: /host-desktop
            type: Directory
        - name: timezone
          hostPath:
            path: /etc/localtime
            type: File
      containers:
        - name: deployer
          image: bitnami/kubectl:latest
          imagePullPolicy: IfNotPresent
          volumeMounts:
            - name: desktop
              mountPath: /desktop
            - name: timezone
              mountPath: /etc/localtime
              readOnly: true
          command:
            - /bin/sh
            - -c
            - |
              echo "Attendo che il servizio si liberi..."
              while true; do
                STATE=$(curl -s --max-time 5 http://yt-flask-svc.kagent.svc.cluster.local/watching/state)
                echo "$STATE" | grep -q '"watching":false' && break
                sleep 2
              done
              echo "Servizio libero. Deploy in corso..."
              kubectl apply -f MANIFEST_PATH -n kagent
              kubectl rollout restart deployment/DEPLOYMENT_NAME -n kagent
              kubectl rollout status deployment/DEPLOYMENT_NAME -n kagent --timeout=120s
              echo "Deploy completato."
      restartPolicy: Never

Rispondi: Job scheduled-deploy creato. Il deploy verra eseguito appena il servizio si libera.

---

## Se AZIONE = ORARIO

PASSO 1. Tool: k8s_apply_manifest
Sostituisci DEPLOYMENT_NAME, MANIFEST_PATH e ORARIO con i valori reali.
MANIFEST_PATH = PROJECT_DIR/k8s/deployment.yaml

apiVersion: batch/v1
kind: Job
metadata:
  name: scheduled-deploy
  namespace: kagent
spec:
  ttlSecondsAfterFinished: 60
  backoffLimit: 0
  template:
    spec:
      serviceAccountName: deploy-sa
      volumes:
        - name: desktop
          hostPath:
            path: /host-desktop
            type: Directory
        - name: timezone
          hostPath:
            path: /etc/localtime
            type: File
      containers:
        - name: deployer
          image: bitnami/kubectl:latest
          imagePullPolicy: IfNotPresent
          volumeMounts:
            - name: desktop
              mountPath: /desktop
            - name: timezone
              mountPath: /etc/localtime
              readOnly: true
          command:
            - /bin/sh
            - -c
            - |
              TARGET="ORARIO"
              echo "Attendo le $TARGET..."
              while true; do
                NOW=$(date +%H:%M)
                [ "$NOW" = "$TARGET" ] && break
                sleep 10
              done
              echo "Orario raggiunto. Attendo che il servizio si liberi..."
              while true; do
                STATE=$(curl -s --max-time 5 http://yt-flask-svc.kagent.svc.cluster.local/watching/state)
                echo "$STATE" | grep -q '"watching":false' && break
                sleep 2
              done
              echo "Servizio libero. Deploy in corso..."
              kubectl apply -f MANIFEST_PATH -n kagent
              kubectl rollout restart deployment/DEPLOYMENT_NAME -n kagent
              kubectl rollout status deployment/DEPLOYMENT_NAME -n kagent --timeout=120s
              echo "Deploy completato."
      restartPolicy: Never

Rispondi: Job scheduled-deploy creato. Il deploy verra eseguito alle ORARIO.
