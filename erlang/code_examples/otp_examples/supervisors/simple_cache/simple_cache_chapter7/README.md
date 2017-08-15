https://github.com/erlware/Erlang-and-OTP-in-Action-Source

simple_cache: The user API; the application’s face to the outside
sc_app: The application behaviour implementation
sc_sup: The root supervisor implementation
sc_store: A module to encapsulate your key-to-pid mapping
sc_element: Code for the individual processes that store the cached data


Data flow
=========
1. Request to web server
  1.1 Check cache for package list
  1.2 if cache miss, request package lists
    1.2.1 Pull full package if no cache result
  1.3 Aggregate lists


                                   ----------
                                   | sc_sup |
                                   ----------
                                       |               
                                       |
----------------        ----------------------------------
| simple_cache |--------| sc_element |...| sc_element(N) |
----------------        ----------------------------------
       |
--------------
| sc_storage |
--------------

To copy to erlang docker use this: sudo docker cp file <<docker_container_name or UID>>:<<path>>
Example:

sudo docker cp *.gz determined_lewin:/workspace/


To compile (From the root directory of the application): erlc –o ebin src/*.erl
To execute:  erl –pa ebin

root@9863674f3e67:/workspace/simple_cache# erl -pa ebin  
Erlang/OTP 20 [erts-9.0.1] [source] [64-bit] [smp:4:4] [ds:4:4:10] [async-threads:10] [hipe] [kernel-poll:false]

Eshell V9.0.1  (abort with ^G)
1> application:start(simple_cache).
ok
2> simple_cache:lookup(1).  
{error,not_found}
3> simple_cache:insert(1, 2000).
true
4> simple_cache:lookup(1).      
{ok,2000}
5>
