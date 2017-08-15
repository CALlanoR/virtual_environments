# The RPC server will allow you to listen on a TCP
# socket and accept a single connection from an
# outside TCP client.

erlc –o ebin src/*.erl

# -pa stands for path add, adding a directory to the beginning of the code path.
erl –pa ebin

Eshell V5.6.2 (abort with ^G)
1> application:start(tcp_rpc).
2> ok
2>
