#!/bin/bash

CONF_FILE="/etc/nginx/conf.d/cloudflare-realip.conf"

curl -s https://www.cloudflare.com/ips-v4 -o /tmp/cf_ipv4.txt
curl -s https://www.cloudflare.com/ips-v6 -o /tmp/cf_ipv6.txt

{
    echo "# Cloudflare IPs - Auto generated"

    while read ip; do
        [ -n "$ip" ] && echo "set_real_ip_from $ip;"
    done < /tmp/cf_ipv4.txt

    while read ip; do
        [ -n "$ip" ] && echo "set_real_ip_from $ip;"
    done < /tmp/cf_ipv6.txt

} > "$CONF_FILE"

nginx -t && systemctl reload nginx.service
