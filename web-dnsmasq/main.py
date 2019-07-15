import dnsmasq

dnsmasq_conf = dnsmasq.config(conf_file='dnsmasq/configs/test_config1.conf')

dnsmasq_conf['test'] = ['this']

for key in dnsmasq_conf.keys():
    print(f'{ key } : { dnsmasq_conf[key] }')

