import dnsmasq

#dnsmasq_conf = dnsmasq.config(conf_file='dnsmasq/configs/test_config1.conf')
#dnsmasq_conf = dnsmasq.config()

dns_dhcp = dnsmasq.DNSMasq("dnsmasq/configs/test_config1.conf")

print(dns_dhcp["dhcp-host"])

dns_dhcp.write()
dns_dhcp.write(dns_dhcp.conf_files[0])
