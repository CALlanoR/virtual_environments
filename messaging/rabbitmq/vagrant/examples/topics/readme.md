Extracted from: https://www.rabbitmq.com/tutorials/tutorial-five-python.html

To receive all the logs run:
python receive.py "#"

To receive all logs from the facility "kern":
python receive.py "kern.*"

Or if you want to hear only about "critical" logs:
python receive.py "*.critical"

You can create multiple bindings:
python receive.py "kern.*" "*.critical"

And to emit a log with a routing key "kern.critical" type:

python emit.py "kern.critical" "A critical kernel error