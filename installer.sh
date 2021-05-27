#!/bin/bash

ip=$1
username=$2
password=$3

ssh="sshpass -p $password ssh -o StrictHostKeyChecking=no $username@$ip"
scp="sshpass -p $password scp -o StrictHostKeyChecking=no"

generateServise(){
	name=$1
	echo """[Unit] 
Description=SAI Chalanger container 

Requires=docker.service 
After=docker.service 
After=rc-local.service 
StartLimitIntervalSec=1200 
StartLimitBurst=3 

[Service] 
User=root 
ExecStartPre=/usr/bin/$name.sh start 
ExecStart=/usr/bin/$name.sh wait 
ExecStop=/usr/bin/$name.sh stop 
Restart=always 
RestartSec=30 

[Install] 
WantedBy=multi-user.target
""" > $name.service
}

generateScript(){
	name=$1
	echo """#!/bin/bash
start(){
	docker inspect --type container \${DOCKERNAME} 2>/dev/null > /dev/null
	if [ \"\$?\" -eq \"0\" ]; then
            echo \"Starting existing \${DOCKERNAME} container\"
            docker start \${DOCKERNAME}
            exit $?
        fi
	echo \"Creating new \${DOCKERNAME} container\"	
	docker create --privileged -t --name \$DOCKERNAME -v \$(pwd):/sai-challenger -p 6379:6379 saivs-server
	
	echo \"Starting \${DOCKERNAME} container\"
	docker start \$DOCKERNAME
}
wait() {
	docker wait \$DOCKERNAME
}
stop() {
	echo \"Stoping \${DOCKERNAME} container\"
	docker stop \$DOCKERNAME
}

DOCKERNAME=saivs

case \"\$1\" in
    start|wait|stop)
        \$1
        ;;
    *)
        echo \"Usage: \$0 {start|wait|stop}\"
        exit 1
        ;;
esac
""" > $name.sh
}

install(){
	name=$1
	docker build -f Dockerfile.saivs.server -t saivs-server .
	docker build -f Dockerfile.saivs.client -t saivs-client .

	docker inspect --type container \sai-challenger 2>/dev/null > /dev/null\
		&& docker container rm sai-challenger -f
	docker create --privileged -t \
		--name sai-challenger \
		-v $(pwd):/sai-challenger \
		--cap-add=NET_ADMIN \
		--device /dev/net/tun:/dev/net/tun \
		saivs-client

	docker save -o saivs_server.tar saivs-server
	ssh-keygen -f "/root/.ssh/known_hosts" -R "$ip"
	$scp saivs_server.tar $username@$ip:/home/admin/saivs_server.tar
	$ssh docker load -i /home/admin/saivs_server.tar
	$ssh rm -rf /home/admin/saivs_server.tar

	docker inspect --type container \saivs 2>/dev/null \
		&& docker container rm saivs -f
	
	generateServise $name
	generateScript $name
	sudo chmod +x $name.sh
	sudo echo "$name.service" > generated_services.conf
	
	$scp $name.service $username@$ip:/home/admin/$name.service
	$scp $name.sh $username@$ip:/home/admin/$name.sh
	$scp generated_services.conf $username@$ip:/home/admin/generated_services.conf
	
	sudo rm $name.service
	sudo rm $name.sh
	sudo rm generated_services.conf
	
	$ssh sudo mv /home/admin/$name.service /usr/lib/systemd/system/$name.service
	$ssh sudo mv /home/admin/$name.sh /usr/bin/$name.sh
	$ssh sudo mv /etc/sonic/generated_services.conf /etc/sonic/generated_services.conf.bak
	$ssh sudo mv /home/admin/generated_services.conf /etc/sonic/generated_services.conf
	
	$ssh sudo reboot
}
remove(){
	name=$1
	$ssh sudo rm /usr/lib/systemd/system/$name.service
	$ssh sudo rm /usr/bin/$name.sh
	$ssh [ -f /etc/sonic/generated_services.conf.bak ] && $ssh sudo rm /etc/sonic/generated_services.conf
	$ssh [ -f /etc/sonic/generated_services.conf.bak ] && $ssh sudo mv /etc/sonic/generated_services.conf.bak /etc/sonic/generated_services.conf
	$ssh sudo reboot
}
usage(){
	echo "Usage: $0 <ip of device> <user name> <passwod> {install|remove}"
	exit 1
}
[ -z "$1" ] && usage
[ -z "$2" ] && usage
[ -z "$3" ] && usage
case "$4" in
    install|remove)
	$4 saivs
	;;
    *)
	usage
	;;
esac
