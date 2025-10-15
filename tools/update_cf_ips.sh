#!/bin/bash

REALIP_CONF_FILE="/etc/nginx/conf.d/cloudflare-realip.conf"
GEO_CONF_FILE="/etc/nginx/conf.d/cloudflare-geo.conf"

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

    echo ""
    echo "real_ip_header CF-Connecting-IP;"
    echo "real_ip_recursive on;"
} > "$REALIP_CONF_FILE"

{
    echo "# Cloudflare IPs - Auto generated"

    echo "geo \$request_from_cf {"
    echo "    default 0;"

    while read ip; do
        [ -n "$ip" ] && echo "    $ip 1;"
    done < /tmp/cf_ipv4.txt

    while read ip; do
        [ -n "$ip" ] && echo "    $ip 1;"
    done < /tmp/cf_ipv6.txt

    echo "}"
} > "$GEO_CONF_FILE"

nginx -t && systemctl reload nginx.service
