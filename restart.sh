supervisorctl -c scripts/supervisord-vm.conf shutdown
killall python
supervisord -c scripts/supervisord-vm.conf 
echo "DONE"
