"""
Generador de carga para inventory.customers.

Por defecto ejecuta una operación aleatoria (INSERT, UPDATE o DELETE) cada
segundo durante 40 segundos contra el primario del stack elegido con --target,
y termina solo. Configurable con --interval y --duration.

Targets reconocidos:
  --target mysql5.7   -> 127.0.0.1:3306  (stack legacy)
  --target mysql8     -> 127.0.0.1:3308  (stack moderno)

Para parar antes del timeout: presiona 'C' (también funciona Ctrl+C).
"""
from __future__ import annotations

import argparse
import random
import signal
import string
import sys
import termios
import threading
import time
import tty
from datetime import datetime

import pymysql

DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "inventory"

DEFAULT_INTERVAL = 1
DEFAULT_DURATION = 40

TARGET_PORTS = {
    "mysql5.7": 3306,
    "mysql8": 3308,
}

FIRST_NAMES = ["Ada", "Alan", "Grace", "Linus", "Margaret", "Donald", "Edsger", "Barbara", "Ken", "Dennis"]
LAST_NAMES = ["Lovelace", "Turing", "Hopper", "Torvalds", "Hamilton", "Knuth", "Dijkstra", "Liskov", "Thompson", "Ritchie"]
DOMAINS = ["example.com", "kernel.org", "test.dev", "demo.io"]


stop_event = threading.Event()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        "--target",
        choices=sorted(TARGET_PORTS.keys()),
        help="Stack al que apuntar. Determina host=127.0.0.1 y port según el mapeo de TARGET_PORTS.",
    )
    p.add_argument("--host", default=None, help="Override del host (default 127.0.0.1 si se usa --target).")
    p.add_argument("--port", type=int, default=None, help="Override del puerto (default según --target).")
    p.add_argument(
        "-i", "--interval",
        type=float, default=DEFAULT_INTERVAL,
        help=f"Segundos entre operaciones (default: {DEFAULT_INTERVAL}).",
    )
    p.add_argument(
        "-d", "--duration",
        type=float, default=DEFAULT_DURATION,
        help=f"Duración total en segundos. 0 = infinito (corre hasta C/SIGINT). Default: {DEFAULT_DURATION}.",
    )
    args = p.parse_args(argv)
    if args.interval <= 0:
        p.error("--interval debe ser > 0")
    if args.duration < 0:
        p.error("--duration debe ser >= 0 (0 = infinito)")

    if args.target is None and (args.host is None or args.port is None):
        p.error("debes especificar --target {mysql5.7,mysql8} o pasar --host y --port explícitamente")

    if args.host is None:
        args.host = "127.0.0.1"
    if args.port is None:
        args.port = TARGET_PORTS[args.target]
    return args


def random_email(first: str, last: str) -> str:
    suffix = "".join(random.choices(string.digits, k=3))
    return f"{first.lower()}.{last.lower()}{suffix}@{random.choice(DOMAINS)}"


def log(msg: str) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def do_insert(cur) -> None:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    email = random_email(first, last)
    cur.execute(
        "INSERT INTO customers (first_name, last_name, email) VALUES (%s, %s, %s)",
        (first, last, email),
    )
    log(f"INSERT id={cur.lastrowid} ({first} {last} <{email}>)")


def do_update(cur) -> None:
    cur.execute("SELECT id, first_name, last_name FROM customers ORDER BY RAND() LIMIT 1")
    row = cur.fetchone()
    if not row:
        log("UPDATE skipped: tabla vacía")
        return
    new_email = random_email(row["first_name"], row["last_name"])
    cur.execute("UPDATE customers SET email=%s WHERE id=%s", (new_email, row["id"]))
    log(f"UPDATE id={row['id']} -> email={new_email}")


def do_delete(cur) -> None:
    cur.execute("SELECT id, first_name, last_name FROM customers ORDER BY RAND() LIMIT 1")
    row = cur.fetchone()
    if not row:
        log("DELETE skipped: tabla vacía")
        return
    cur.execute("DELETE FROM customers WHERE id=%s", (row["id"],))
    log(f"DELETE id={row['id']} ({row['first_name']} {row['last_name']})")


OPS = [do_insert, do_update, do_delete]


def keyboard_listener() -> None:
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while not stop_event.is_set():
            ch = sys.stdin.read(1)
            if ch in ("c", "C"):
                log("Tecla 'C' detectada — parando.")
                stop_event.set()
                return
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def handle_sigint(signum, frame) -> None:
    log("Señal recibida — parando.")
    stop_event.set()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    signal.signal(signal.SIGINT, handle_sigint)
    signal.signal(signal.SIGTERM, handle_sigint)

    target_label = args.target if args.target else f"{args.host}:{args.port}"
    log(f"Conectando a {args.host}:{args.port} (target={target_label}, db={DB_NAME})")

    if args.duration > 0:
        run_mode = f"cada {args.interval}s durante {args.duration}s"
    else:
        run_mode = f"cada {args.interval}s (infinito)"

    if sys.stdin.isatty():
        threading.Thread(target=keyboard_listener, daemon=True).start()
        log(f"Generador iniciado: {run_mode}. Presiona 'C' (o Ctrl+C) para parar antes.")
    else:
        log(f"Generador iniciado: {run_mode} (stdin no es TTY). Usa Ctrl+C para parar antes.")

    conn = pymysql.connect(
        host=args.host,
        port=args.port,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        autocommit=True,
        cursorclass=pymysql.cursors.DictCursor,
    )

    deadline = time.monotonic() + args.duration if args.duration > 0 else None

    try:
        with conn.cursor() as cur:
            while not stop_event.is_set():
                op = random.choice(OPS)
                try:
                    op(cur)
                except pymysql.err.MySQLError as exc:
                    log(f"Error MySQL en {op.__name__}: {exc}")
                if deadline is not None and time.monotonic() >= deadline:
                    log(f"Duración ({args.duration}s) cumplida — parando.")
                    break
                stop_event.wait(timeout=args.interval)
    finally:
        conn.close()
        log("Conexión cerrada. Bye.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
