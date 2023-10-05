#!/bin/bash

# Ensure server response policy zone resolves fut.opensync.io domain
fut_zone_domain="fut.opensync.io"
fut_zone_ip="192.168.200.1"
org_zone_policy="/etc/bind/db.response-policy-zone"
if [ -f "${org_zone_policy}" ]; then
    echo "${org_zone_policy} exists"
    res=$(cat "${org_zone_policy}" | grep "${fut_zone_domain}.*${fut_zone_ip}")
    if [ "$?" -eq 0 ]; then
        echo "${fut_zone_domain} present in ${org_zone_policy} at ${fut_zone_ip}"
    else
        echo "Enabling ${fut_zone_domain} for ${fut_zone_ip} in ${org_zone_policy}"
        sudo sh -c "sed -i '/${fut_zone_domain}/d' ${org_zone_policy}"
        sudo sh -c "echo '${fut_zone_domain}     A       ${fut_zone_ip}' >> ${org_zone_policy}"
        sudo service bind9 restart
        if [ "$?" -eq 0 ]; then
            echo "${fut_zone_domain} enabled on ${fut_zone_ip}"
        else
            echo "FAIL: Failed to enable ${fut_zone_domain} for ${fut_zone_ip}"
            exit 1
        fi
    fi
else
    echo "WARNING: ${org_zone_policy} is missing on RPI Server"
    echo "WARNING: Some FUT testcases may fail!"
    echo "WARNING: Consider upgrading to latest RPI Server image!"
fi
