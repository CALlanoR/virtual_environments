Modules
=======

useless
=======

Eshell V9.0.1  (abort with ^G)
1> c(useless).
{ok,useless}


3> useless:add(7,2).
9
4> useless:hello().
Hello, world!
ok
5> useless:greet_and_add_two(-3).
Hello, world!
-1

7> useless:module_info().
[{module,useless},
 {exports,[{add,2},
           {hello,0},
           {greet_and_add_two,1},
           {module_info,0},
           {module_info,1}]},
 {attributes,[{vsn,[296174539721071843666185210011547328263]}]},
 {compile,[{options,[]},
           {version,"7.1"},
           {source,"/workspace/useless.erl"}]},
 {native,false},
 {md5,<<222,209,36,56,31,223,59,231,71,237,66,109,149,39,
        223,7>>}]


records
=======
Eshell V9.0.1  (abort with ^G)
1> c(records).
records.erl:2: Warning: export_all flag enabled - all functions will be exported
{ok,records}
2> rr(records).
[robot,user]
3> records:admin_panel(#user{id=2, name="you", group=users, age=66}).
"you is not allowed"
4> records:admin_panel(#user{id=1, name="ferd", group=admin, age=96}).
"ferd is allowed!"
5> records:adult_section(#user{id=21, name="Bill", group=users, age=72}).
allowed
6> records:adult_section(#user{id=22, name="Noah", group=users, age=13}).
forbidden
7> records:repairman(#robot{name="Ulbert", hobbies=["trying to have feelings"]}).
{repaired,#robot{name = "Ulbert",type = industrial,
                 hobbies = ["trying to have feelings"],
                 details = ["Repaired by repairman"]}}
8> records:included().
                
