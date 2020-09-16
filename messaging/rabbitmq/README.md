# messaging
Messaging examples.


vagrant plugin install vagrant-scp
vagrant scp <some_local_file_or_dir> [vm_name]:<somewhere_on_the_vm>

tar czvf examples.tgz examples/ -R
vagrant scp examples.tgz rabbitmq.client:/home/vagrant/
vagrant ssh rabbitmq.client
tar xzvf examples.tgz


http://192.168.56.115:15672