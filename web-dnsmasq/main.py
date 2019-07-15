import PyDNSMasq

#dnsmasq_conf = dnsmasq.config(conf_file='dnsmasq/configs/test_config1.conf')
#dnsmasq_conf = dnsmasq.config()

dns_dhcp = PyDNSMasq.DNSMasq("PyDNSMasq/configs/test_config1.conf")

print(dns_dhcp["dhcp-host"])

dns_dhcp.addOption(dns_dhcp.conf_files[-1],"test-option1")
dns_dhcp.addOption(dns_dhcp.conf_files[-1],"test-option2","hostsandstuff")
dns_dhcp.write()
