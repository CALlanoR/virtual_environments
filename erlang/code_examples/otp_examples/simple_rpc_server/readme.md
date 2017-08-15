erlc rpc_server.erl

Eshell V5.6.2 (abort with ^G)
1> tr_server:start_link(1055).
{ok,<0.33.0>}


$ telnet localhost 1055
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
init:stop().
ok
Connection closed by foreign host.

Eshell V5.6.2 (abort with ^G)
1> eunit:test(tr_server).
  Test passed.
ok
