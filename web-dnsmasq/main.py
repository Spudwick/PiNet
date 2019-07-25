import PyDNSMasq

#dnsmasq = PyDNSMasq.DNSMasq("C:\\Users\\TO01\\Documents\\GitHub\\PiNet\\web-dnsmasq\\PyDNSMasq\\configs\\test_config1.conf","C:\\Users\\TO01\\Documents\\GitHub\\PiNet\\web-dnsmasq\\PyDNSMasq\\leases\\dnsmasq.leases")

conf = PyDNSMasq.DNSMasq_file("PyDNSMasq/configs/test_config1.conf")

conf.add("dhcp-host",["rpi1", "192.168.10.10"])
conf.pop("dhcp-host", 2)

for line in conf.lines:
    if len(line) > 1:
        print(f'{ line[0] } : { line[1] }')
    else:
        print(f'{ line[0] }')