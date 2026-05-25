# Makefile top-level para gestionar los dos stacks (mysql5.7 + mysql8)
# de forma uniforme. NO incluye targets para correr el monitoreo —
# eso es manual vía: ./monitoring/run-comparison.sh

.PHONY: all up down ps wait-healthy help

help:
	@echo "Targets para ambos stacks (mysql5.7 + mysql8):"
	@echo "  all           up + wait-healthy en uno"
	@echo "  up            Levanta ambos stacks con 'docker compose up -d'"
	@echo "  down          Apaga ambos stacks con 'docker compose down -v' (borra volúmenes)"
	@echo "  ps            Estado de ambos stacks"
	@echo "  wait-healthy  Bloquea hasta que los 4 contenedores MySQL estén healthy"
	@echo ""
	@echo "Para monitorear y comparar I/O entre stacks (manual):"
	@echo "  ./monitoring/run-comparison.sh"

all: up wait-healthy
	@echo "Ambos stacks listos"
	@echo "Se puede ejecutar : ./monitoring/run-comparison.sh"

up:
	@echo "==> mysql5.7"
	cd mysql5.7 && docker compose up -d
	@echo "==> mysql8"
	cd mysql8 && docker compose up -d

down:
	@echo "==> mysql5.7"
	-cd mysql5.7 && docker compose down -v
	@echo "==> mysql8"
	-cd mysql8 && docker compose down -v

ps:
	@echo "==> mysql5.7"
	@cd mysql5.7 && docker compose ps
	@echo ""
	@echo "==> mysql8"
	@cd mysql8 && docker compose ps

wait-healthy:
	@echo "Esperando mysql5.7 healthy..."
	@cd mysql5.7 && until docker compose ps --format json 2>/dev/null | grep -q '"Health":"healthy".*"Service":"mysql-replica"'; do sleep 2; done
	@echo "  ✓ mysql5.7 healthy"
	@echo "Esperando mysql8 healthy..."
	@cd mysql8 && until docker compose ps --format json 2>/dev/null | grep -q '"Health":"healthy".*"Service":"mysql-replica"'; do sleep 2; done
	@echo "  ✓ mysql8 healthy"
	@echo "Ambos stacks listos. Puedes correr: ./monitoring/run-comparison.sh"
