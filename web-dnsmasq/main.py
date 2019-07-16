import PyDNSMasq

dnsmasq = PyDNSMasq.DNSMasq_file("C:\\Users\\TO01\\Documents\\GitHub\\PiNet\\web-dnsmasq\\PyDNSMasq\\configs\\test_config1.conf")

print(dnsmasq["domain-needed"])
print(dnsmasq["dhcp-host"])
print(dnsmasq["hello"])
print(dnsmasq["server"])

print(dnsmasq.switches)

dnsmasq.write()