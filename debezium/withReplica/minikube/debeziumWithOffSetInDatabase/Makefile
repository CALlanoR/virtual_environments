# Makefile top-level para gestionar los dos stacks (mysql5.7 + mysql8) sobre
# mini-kubernetes (minikube). Equivalente del Makefile de ../../docker-compose/.
# El monitoreo (presente en docker-compose/monitoring/) NO se incluye.

KUBECTL ?= kubectl
MINIKUBE ?= minikube
DOCKER ?= docker

# Namespace único post-consolidación. Ambos stacks (mysql5.7 y mysql8) viven aquí,
# distinguidos por la label `stack: mysql57` o `stack: mysql8`.
NS         := cdc-lab
STACK_57   := mysql57
STACK_8    := mysql8

IMG  := withreplica/debezium-server-mysql:3.5.0.Final
DEBEZIUM_BUILD_CTX := ../../docker-compose/mysql8/debezium

IMG_57 := withreplica/debezium-server-mysql57-jdbc:2.4.2.Final
DEBEZIUM_57_BUILD_CTX := images/debezium-server-mysql57-jdbc

.PHONY: help image-build image-load image-unload image-clean \
        image-build-57 image-load-57 image-unload-57 image-clean-57 \
        up up-5.7 up-8 \
        wait-healthy wait-healthy-5.7 wait-healthy-8 \
        ps ps-5.7 ps-8 \
        logs-sink-5.7 logs-sink-8 \
        load-5.7 load-8 \
        down down-5.7 down-8

help:
	@echo "Targets que operan sobre minikube (namespace $(NS)):"
	@echo ""
	@echo "  image-build      docker build de la imagen custom de Debezium 3.5 (stack 8)"
	@echo "  image-load       Carga la imagen al daemon de minikube"
	@echo "  image-unload     Borra la imagen custom del daemon de minikube"
	@echo "  image-clean      image-unload + docker image rm (limpia tambien el host)"
	@echo ""
	@echo "  image-build-57   docker build de la imagen custom de Debezium 2.4 + JDBC storage (stack 5.7)"
	@echo "  image-load-57    Carga la imagen 5.7 al daemon de minikube"
	@echo "  image-unload-57  Borra la imagen 5.7 del daemon de minikube"
	@echo "  image-clean-57   image-unload-57 + docker image rm"
	@echo ""
	@echo "  up               Levanta todo en $(NS): namespace + state-store + ambos stacks"
	@echo "  up-5.7           Aplica solo recursos del stack 5.7 (label $(STACK_57)); presume namespace + state-store ya existen"
	@echo "  up-8             Aplica solo recursos del stack 8 (label $(STACK_8))"
	@echo ""
	@echo "  wait-healthy     Bloquea hasta que los 4 Pods MySQL esten Ready"
	@echo "  ps               kubectl get all en $(NS)"
	@echo ""
	@echo "  logs-sink-5.7    Sigue eventos CDC del stack 5.7"
	@echo "  logs-sink-8      Sigue eventos CDC del stack 8"
	@echo ""
	@echo "  load-5.7         Lanza un Job de load-generator contra el stack 5.7"
	@echo "  load-8           Lanza un Job de load-generator contra el stack 8"
	@echo ""
	@echo "  down             Borra TODO el namespace $(NS) (ambos stacks + state-store + PVCs)"
	@echo "  down-5.7         Borra solo los recursos del stack 5.7 (preserva state-store y stack 8)"
	@echo "  down-8           Borra solo los recursos del stack 8"
	@echo ""
	@echo "  dashboard        Abre el dashboard de minikube"
	@echo ""
	@echo "Monitoreo: NO incluido en esta variante. Ver ../../docker-compose/monitoring/"

image-build:
	@echo "==> Construyendo $(IMG) desde $(DEBEZIUM_BUILD_CTX)"
	$(DOCKER) build -t $(IMG) $(DEBEZIUM_BUILD_CTX)

image-load: image-build
	@echo "==> Cargando $(IMG) a minikube"
	$(MINIKUBE) image load $(IMG)
	@echo "Verificando..."
	@$(MINIKUBE) image ls | grep -q "$(IMG)" && echo "  OK" || (echo "  FALLO: imagen no aparece en minikube image ls" && exit 1)

image-unload:
	@echo "==> Borrando $(IMG) del daemon de minikube"
	-$(MINIKUBE) image rm $(IMG)
	@echo "Verificando..."
	@if $(MINIKUBE) image ls 2>/dev/null | grep -q "$(IMG)"; then \
		echo "  AVISO: la imagen sigue apareciendo en minikube image ls"; \
	else \
		echo "  OK (imagen ya no esta en minikube)"; \
	fi

image-clean: image-unload
	@echo "==> Borrando $(IMG) del daemon de Docker del host"
	-$(DOCKER) image rm $(IMG)
	@echo "Listo. Para reconstruir: make image-build && make image-load"

# --- Imagen custom para stack 5.7 (Debezium 2.4 + debezium-storage-jdbc) -----

image-build-57:
	@echo "==> Construyendo $(IMG_57) desde $(DEBEZIUM_57_BUILD_CTX)"
	$(DOCKER) build -t $(IMG_57) $(DEBEZIUM_57_BUILD_CTX)

image-load-57: image-build-57
	@echo "==> Cargando $(IMG_57) a minikube"
	$(MINIKUBE) image load $(IMG_57)
	@echo "Verificando..."
	@$(MINIKUBE) image ls | grep -q "$(IMG_57)" && echo "  OK" || (echo "  FALLO: imagen no aparece en minikube image ls" && exit 1)

image-unload-57:
	@echo "==> Borrando $(IMG_57) del daemon de minikube"
	-$(MINIKUBE) image rm $(IMG_57)
	@echo "Verificando..."
	@if $(MINIKUBE) image ls 2>/dev/null | grep -q "$(IMG_57)"; then \
		echo "  AVISO: la imagen sigue apareciendo en minikube image ls"; \
	else \
		echo "  OK (imagen ya no esta en minikube)"; \
	fi

image-clean-57: image-unload-57
	@echo "==> Borrando $(IMG_57) del daemon de Docker del host"
	-$(DOCKER) image rm $(IMG_57)
	@echo "Listo. Para reconstruir: make image-build-57 && make image-load-57"

# --- Up -----------------------------------------------------------------------

up: image-load image-load-57
	@echo "==> Creando namespace $(NS) y state-store compartido"
	$(KUBECTL) apply -f shared/
	$(KUBECTL) rollout status deployment/mysql-debezium-state -n $(NS) --timeout=180s
	@echo "==> Aplicando stack 5.7"
	$(KUBECTL) apply -f mysql5.7/
	$(KUBECTL) apply -k load-generator/mysql5.7/
	@echo "==> Aplicando stack 8"
	$(KUBECTL) apply -f mysql8/
	$(KUBECTL) apply -k load-generator/mysql8/

up-5.7: image-load-57
	@echo "==> Aplicando solo manifests del stack 5.7 en $(NS) (presume namespace y state-store ya existen)"
	$(KUBECTL) apply -f mysql5.7/
	$(KUBECTL) apply -k load-generator/mysql5.7/

up-8: image-load
	@echo "==> Aplicando solo manifests del stack 8 en $(NS) (presume namespace y state-store ya existen)"
	$(KUBECTL) apply -f mysql8/
	$(KUBECTL) apply -k load-generator/mysql8/

# --- Wait-healthy -------------------------------------------------------------

wait-healthy: wait-healthy-5.7 wait-healthy-8

wait-healthy-5.7:
	@echo "==> Esperando Pods del stack 5.7..."
	$(KUBECTL) wait --for=condition=ready pod -l app=mysql-primary,stack=$(STACK_57) -n $(NS) --timeout=300s
	$(KUBECTL) wait --for=condition=ready pod -l app=mysql-replica,stack=$(STACK_57) -n $(NS) --timeout=300s
	@echo "  OK stack 5.7"

wait-healthy-8:
	@echo "==> Esperando Pods del stack 8..."
	$(KUBECTL) wait --for=condition=ready pod -l app=mysql-primary,stack=$(STACK_8) -n $(NS) --timeout=300s
	$(KUBECTL) wait --for=condition=ready pod -l app=mysql-replica,stack=$(STACK_8) -n $(NS) --timeout=300s
	@echo "  OK stack 8"

# --- Estado -------------------------------------------------------------------

ps:
	@echo "==> Namespace $(NS) — todo"
	@$(KUBECTL) get all -n $(NS)

ps-5.7:
	@echo "==> Stack 5.7 (label stack=$(STACK_57))"
	@$(KUBECTL) get all -n $(NS) -l stack=$(STACK_57)

ps-8:
	@echo ""
	@echo "==> Stack 8 (label stack=$(STACK_8))"
	@$(KUBECTL) get all -n $(NS) -l stack=$(STACK_8)

# --- Logs del sink ------------------------------------------------------------

logs-sink-5.7:
	$(KUBECTL) logs -n $(NS) deploy/cdc-sink-57 -f

logs-sink-8:
	$(KUBECTL) logs -n $(NS) deploy/cdc-sink-8 -f

# --- Load-generator on-demand -------------------------------------------------

load-5.7:
	@echo "==> Lanzando Job load-generator contra stack 5.7"
	$(KUBECTL) create -f load-generator/job-mysql5.7.yaml

load-8:
	@echo "==> Lanzando Job load-generator contra stack 8"
	$(KUBECTL) create -f load-generator/job-mysql8.yaml

# --- Down ---------------------------------------------------------------------

down:
	@echo "==> Borrando namespace $(NS) (incluye state-store y ambos stacks)"
	-$(KUBECTL) delete namespace $(NS) --ignore-not-found

down-5.7:
	@echo "==> Borrando solo recursos del stack 5.7 (preserva state-store y stack 8)"
	-$(KUBECTL) delete all,configmaps,secrets,pvc -n $(NS) -l stack=$(STACK_57) --ignore-not-found

down-8:
	@echo "==> Borrando solo recursos del stack 8"
	-$(KUBECTL) delete all,configmaps,secrets,pvc -n $(NS) -l stack=$(STACK_8) --ignore-not-found

dashboard:
	$(MINIKUBE) dashboard
