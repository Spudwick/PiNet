import PyDNSMasq

dnsmasq = PyDNSMasq.DNSMasq("C:\\Users\\TO01\\Documents\\GitHub\\PiNet\\web-dnsmasq\\PyDNSMasq\\configs\\test_config1.conf","C:\\Users\\TO01\\Documents\\GitHub\\PiNet\\web-dnsmasq\\PyDNSMasq\\leases\\dnsmasq.leases")

dnsmasq.start()

print(dnsmasq.tohost("192.168.10.109"))
print(dnsmasq.tohost("172.20.150.91"))
print(dnsmasq.tohost(mac="45:fd:6e:34:12:45"))