from fastapi import Request, HTTPException

# 국내 IP의 주요 대역 프리픽스만 체크 (간단한 방식)
# 일부 주요 국내 통신사와 클라우드 제공업체의 IP 대역 프리픽스
KOREAN_IP_PREFIXES = ["1.11.","1.176.","1.201.","1.208.","1.224.","101.101.128.","139.150.","101.202.","101.235.","101.250.","101.53.64.","49.50.","103.129.184.","103.122.184.","103.124.100.","103.125.108.","103.126.64.","103.127.212.","103.132.32.","103.132.36.","103.138.228.","103.139.84.","103.139.118.","103.139.214.","103.139.216.","123.253.172.","103.140.12.","103.141.18.","103.143.78.","103.143.176.","103.144.30.","103.145.214.","103.146.180.","103.150.62.","103.150.160.","103.150.162.","103.150.204.","103.153.44.","103.157.158.","103.157.208.","103.159.160.","103.161.4.","103.162.52.","103.162.180.","103.164.78.","103.166.222.","103.175.200.","103.178.80.","103.182.126.","103.182.250.","103.186.170.","103.187.34.","103.187.108.","103.188.89.","103.141.190.","103.21.188.","103.21.190.","103.42.60.","103.104.86.","103.71.4.","103.122.144.","103.126.234.","203.191.134.","203.160.130.","103.67.58.","115.187.20.","180.94.4.","157.66.64.","160.30.106.","160.30.235.","160.30.229.","160.30.232.","160.187.186.","160.250.154.","160.250.152.","163.61.222.","163.223.94.","163.223.162.","106.10.","106.240.","106.96.","110.35.96.","110.35.128.","110.44.32.","118.91.144.","110.44.192.","110.45.","110.4.64.","203.223.177.","110.5.128.","110.34.64.","110.35.","110.45.128.","110.68.","110.46.","110.93.112.","110.165.64.","110.172.64.","110.232.96.","111.171.","111.218.","111.221.32.","180.80.","111.65.128.","111.67.208.","111.67.224.","111.91.160.","111.91.144.","111.91.128.","111.118.","112.108.","112.109.32.","112.121.","112.121.192.","112.133.128.","112.144.","112.136.128.","112.133.","112.140.144.","112.140.152.","112.216.","112.140.192.","112.140.64.","112.137.176.","112.160.","112.196.192.","110.8.","112.212.","112.213.","112.214.","112.72.16.","112.72.128.","112.76.","113.130.128.","113.131.","113.192.64.","36.38.","113.197.80.","113.216.","113.199.","113.29.192.","113.30.","113.30.64.","113.29.128.","113.59.128.","113.52.192.","113.60.","113.52.136.","113.61.","113.61.104.","113.130.64.","113.198.","114.108.128.","114.110.24.","114.111.32.","114.111.48.","114.111.192.","114.129.64.","114.129.192.","114.141.","114.110.128.","111.92.188.","42.16.","114.141.224.","114.199.","114.141.40.","114.200.","114.199.128.","115.","115.40.","114.30.128.","114.31.32.","114.31.112.","114.70.","114.30.48.","114.52.","115.126.192.","115.144.","115.145.","115.160.","115.161.","115.165.176.","115.178.64.","115.178.32.","113.10.","115.187.80.","113.21.","115.31.96.","115.68.","115.69.96.","115.84.160.","115.88.","115.85.160.","115.136.","115.86.","116.193.80.","116.200.","116.199.160.","116.212.","116.255.64.","118.139.192.","119.18.64.","115.71.","116.67.","116.68.232.","116.120.","116.68.32.","203.129.6.","116.84.","116.89.160.","116.93.192.","117.16.","116.90.216.","116.193.88.","124.153.128.","117.20.80.","203.169.4.","117.20.192.","117.53.64.","117.53.96.","117.53.192.","117.55.128.","117.58.128.","152.99.","117.110.","117.123.","118.107.160.","210.4.216.","210.4.88.","121.50.224.","203.17.226.","118.176.","118.216.","118.32.","118.67.128.","118.91.","118.91.64.","118.91.96.","118.103.192.","118.128.","119.161.","119.30.128.","119.31.240.","202.174.88.","119.31.248.","119.42.160.","119.64.","119.59.","119.75.64.","119.75.128.","119.63.224.","119.77.96.","119.82.32.","203.82.219.","203.82.220.","119.148.112.","119.148.128.","119.149.","120.136.64.","124.66.176.","120.142.","120.143.192.","114.29.128.","120.143.160.","114.30.","121.1.64.","121.55.128.","121.127.128.","121.127.64.","121.55.64.","203.207.16.","121.254.128.","203.210.16.","122.99.128.","122.49.64.","122.199.128.","122.199.64.","121.64.","121.100.64.","203.133.160.","59.86.192.","121.200.64.","121.254.","121.101.192.","121.101.224.","118.127.192.","202.165.56.","125.208.224.","119.17.64.","119.17.","121.54.192.","210.192.64.","121.126.","122.101.","122.129.248.","116.32.","122.153.","122.202.32.","122.202.128.","123.199.","122.203.","122.252.64.","122.252.192.","123.254.64.","123.98.160.","123.98.192.","122.128.128.","122.128.32.","122.128.64.","122.128.192.","122.129.208.","203.166.208.","122.129.240.","123.","125.208.192.","202.43.48.","203.81.8.","123.32.","122.32.","123.108.16.","61.245.224.","123.108.160.","123.212.","123.109.","123.111.","123.140.","123.228.","123.250.","123.254.128.","210.87.192.","121.0.64.","121.78.","123.99.64.","122.254.128.","210.57.224.","121.0.128.","121.53.","124.136.","124.146.","124.195.160.","124.195.224.","114.29.","124.197.128.","124.198.","124.199.","124.199.128.","124.254.128.","124.28.","124.2.","124.217.192.","118.234.","124.3.","124.46.","124.46.128.","61.4.224.","203.84.240.","203.210.32.","124.80.","125.240.","125.248.","125.57.","125.60.","125.60.64.","125.176.","128.134.","129.254.","134.75.","137.68.","14.0.64.","14.0.32.","14.128.128.","14.206.","14.129.","14.138.","14.192.80.","27.122.128.","49.8.","141.223.","143.248.","147.43.","147.46.","147.47.","147.6.","150.150.","150.183.","150.197.","152.149.1.","152.149.2.","152.149.3.","152.149.4.","152.149.5.","152.149.6.","152.149.7.","152.149.8.","152.149.9.","152.149.10.","152.149.11.","152.149.12.","152.149.13.","152.149.14.","152.149.15.","152.149.16.","152.149.17.","152.149.18.","152.149.19.","152.149.20.","152.149.21.","152.149.22.","152.149.23.","152.149.24.","152.149.25.","152.149.26.","152.149.27.","152.149.28.","152.149.29.","152.149.30.","152.149.31.","152.149.32.","152.149.33.","152.149.34.","152.149.35.","152.149.36.","152.149.37.","152.149.255.","152.149.213.","152.149.214.","152.149.215.","152.149.216.","152.149.217.","152.149.218.","152.149.219.","152.149.220.","152.149.221.","152.149.222.","152.149.223.","152.149.224.","152.149.225.","152.149.226.","152.149.227.","152.149.228.","152.149.229.","152.149.230.","152.149.231.","152.149.232.","152.149.233.","152.149.234.","152.149.235.","152.149.236.","152.149.237.","152.149.238.","152.149.239.","152.149.240.","152.149.241.","152.149.242.","152.149.243.","152.149.244.","152.149.245.","152.149.246.","152.149.247.","152.149.248.","152.149.249.","152.149.250.","152.149.251.","152.149.252.","152.149.253.","152.149.254.","152.149.74.","152.149.75.","152.149.76.","152.149.77.","152.149.78.","152.149.79.","152.149.80.","152.149.81.","152.149.82.","152.149.83.","152.149.84.","152.149.85.","152.149.86.","152.149.87.","152.149.88.","152.149.89.","152.149.90.","152.149.91.","152.149.92.","152.149.93.","152.149.94.","152.149.95.","152.149.149.","152.149.150.","152.149.151.","152.149.152.","152.149.153.","152.149.154.","152.149.155.","152.149.156.","152.149.157.","152.149.158.","152.149.159.","152.149.160.","152.149.161.","152.149.162.","152.149.163.","152.149.164.","152.149.165.","152.149.166.","152.149.167.","152.149.168.","152.149.169.","152.149.170.","152.149.171.","152.149.172.","152.149.173.","152.149.174.","152.149.175.","152.149.176.","152.149.177.","152.149.178.","152.149.179.","152.149.180.","152.149.181.","152.149.182.","152.149.183.","152.149.184.","152.149.185.","152.149.186.","152.149.187.","152.149.188.","152.149.189.","152.149.190.","152.149.191.","152.149.192.","152.149.193.","152.149.194.","152.149.195.","152.149.196.","152.149.197.","152.149.198.","152.149.199.","152.149.200.","152.149.201.","152.149.202.","152.149.203.","152.149.204.","152.149.205.","152.149.206.","152.149.207.","152.149.208.","152.149.209.","152.149.210.","152.149.211.","152.149.212.","152.149.50.","152.149.51.","152.149.52.","152.149.53.","152.149.54.","152.149.55.","152.149.56.","152.149.57.","152.149.58.","152.149.59.","152.149.60.","152.149.61.","152.149.62.","152.149.63.","152.149.64.","152.149.65.","152.149.66.","152.149.67.","152.149.68.","152.149.69.","152.149.70.","152.149.71.","152.149.72.","152.149.73.","152.149.109.","152.149.110.","152.149.111.","152.149.112.","152.149.113.","152.149.114.","152.149.115.","152.149.116.","152.149.117.","152.149.118.","152.149.119.","152.149.120.","152.149.121.","152.149.122.","152.149.123.","152.149.124.","152.149.125.","152.149.126.","152.149.127.","152.149.128.","152.149.129.","152.149.130.","152.149.131.","152.149.132.","152.149.133.","152.149.134.","152.149.135.","152.149.136.","152.149.137.","152.149.138.","152.149.139.","152.149.140.","152.149.141.","152.149.142.","152.149.143.","152.149.144.","152.149.145.","152.149.146.","152.149.147.","152.149.148.","152.149.38.","152.149.39.","152.149.40.","152.149.41.","152.149.42.","152.149.43.","152.149.44.","152.149.45.","152.149.46.","152.149.47.","152.149.48.","152.149.49.","163.152.","152.149.96.","152.149.97.","152.149.98.","152.149.99.","152.149.100.","152.149.101.","152.149.102.","152.149.103.","152.149.104.","152.149.105.","152.149.106.","152.149.107.","152.149.108.","152.149.","154.10.","155.230.","156.147.","157.197.","158.44.","161.122.","163.180.","163.213.","163.222.","163.229.","163.239.","163.255.","164.124.","164.125.","165.132.","165.141.","165.186.","165.194.","165.213.","165.229.","165.243.","165.244.","166.103.","166.104.","166.125.","168.115.","168.126.","168.131.","168.219.","168.248.","168.78.","169.140.","169.208.","175.112.","175.176.128.","175.192.","175.45.192.","175.45.160.","175.106.64.","175.107.64.","175.111.16.","175.158.","180.131.","180.148.180.","101.55.","180.150.192.","180.150.224.","180.182.","180.189.64.","180.189.176.","210.211.64.","180.210.192.","180.210.","180.211.","180.222.220.","180.233.192.","180.236.","180.224.","180.64.","180.92.64.","180.92.240.","180.132.","182.161.128.","182.163.128.","27.176.","182.161.96.","182.192.","182.172.","182.173.160.","202.128.100.","182.208.","182.173.80.","182.173.96.","182.162.","182.224.","182.237.192.","182.252.128.","182.255.128.","1.16.","182.237.32.","182.237.64.","182.252.","182.50.32.","27.1.","183.78.128.","183.78.192.","183.86.192.","183.90.128.","183.91.192.","175.28.32.","175.41.","183.96.","192.132.15.","218.209.","192.132.247.","192.249.16.","58.102.","192.195.40.","192.195.39.","165.246.","192.203.140.","58.224.","192.203.144.","192.245.249.","192.245.251.","192.203.139.","192.203.138.","203.109.","192.203.145.","210.210.192.","192.203.146.","192.100.2.","58.120.","202.133.16.","58.65.64.","203.130.96.","202.136.112.","203.132.160.","192.104.15.","220.230.","202.136.128.","124.","203.175.32.","124.5.","202.14.103.","202.6.95.","202.14.165.","202.21.","202.14.90.","110.92.22.","110.92.21.","110.92.23.","110.92.20.","117.52.","202.148.48.","103.77.84.","103.79.132.","103.85.80.","103.87.116.","103.90.244.","103.90.209.","202.179.148.","103.105.160.","103.105.156.","103.106.140.","103.109.64.","103.114.62.","103.114.124.","103.117.","202.158.144.","125.61.","202.163.128.","203.130.64.","124.194.","202.171.248.","122.0.32.","122.100.32.","123.200.64.","59.151.192.","59.152.128.","121.160.","202.20.83.","202.20.82.","202.20.84.","202.20.86.","202.20.128.","202.20.99.","202.20.119.","202.30.","202.3.16.","202.8.160.","39.4.","202.43.56.","119.192.","202.59.216.","203.190.4.","103.2.76.","103.2.92.","103.2.84.","103.3.36.","103.22.220.","103.4.48.","103.10.92.","103.246.56.","103.4.180.","103.4.148.","103.4.176.","103.10.216.","103.5.128.","103.246.236.","103.5.144.","103.11.24.","103.11.44.","103.11.56.","103.11.128.","103.11.248.","103.23.84.","103.23.80.","103.28.64.","103.28.60.","103.247.232.","103.247.220.","103.6.80.","103.6.72.","103.6.100.","103.6.172.","103.7.32.","103.7.244.","103.8.100.","103.8.230.","103.9.32.","103.9.128.","103.13.52.","103.12.248.","103.12.252.","103.13.160.","103.20.116.","103.21.200.","103.30.108.","103.30.160.","103.30.204.","103.31.180.","103.244.108.","103.19.124.","103.24.8.","103.25.16.","103.248.104.","103.249.28.","103.27.128.","103.27.148.","103.251.104.","103.240.28.","103.240.48.","103.243.200.","103.226.76.","103.226.96.","103.226.72.","103.229.156.","103.230.112.","103.231.128.","45.64.152.","45.64.140.","45.64.172.","150.107.68.","150.107.80.","150.107.84.","45.64.144.","103.234.4.","103.235.24.","150.129.224.","150.242.144.","150.242.132.","163.53.156.","103.237.20.","43.247.104.","43.247.192.","103.238.248.","43.254.244.","103.239.112.","43.255.252.","43.255.248.","103.239.236.","103.239.240.","43.241.104.","43.241.108.","43.242.112.","103.38.24.","43.243.216.","103.39.36.","43.250.152.","103.42.184.","43.251.120.","103.43.64.","43.224.104.","103.43.120.","43.227.116.","43.227.120.","43.228.160.","103.49.44.","43.230.","202.73.132.","202.167.208.","203.170.96.","203.171.160.","125.208.64.","125.209.","202.86.8.","192.5.90.","210.16.192.","168.154.","202.89.124.","110.76.64.","110.92.128.","110.93.24.","110.93.128.","110.165.","202.89.248.","124.216.","203.142.160.","203.152.160.","202.150.176.","125.7.128.","125.7.192.","125.31.128.","125.128.","203.142.216.","203.128.236.","119.235.192.","119.235.240.","120.29.128.","120.50.64.","120.50.128.","120.73.","203.149.112.","123.248.","203.153.144.","203.215.192.","121.128.","203.173.96.","202.179.176.","125.252.","203.175.188.","112.106.","203.190.26.","114.108.","203.212.96.","203.212.160.","210.0.32.","124.111.","203.216.160.","203.223.96.","210.2.32.","124.243.","203.224.","203.225.","203.226.","203.228.","203.230.","203.232.","203.234.","203.236.","203.240.","203.244.","203.248.","203.252.","203.81.128.","203.83.128.","59.150.","203.82.240.","58.180.","203.90.32.","59.186.","210.100.","210.104.","210.108.","210.112.","210.116.","210.120.","210.124.","210.178.","210.180.","210.182.","210.204.","210.211.","210.216.","210.220.","210.89.160.","121.50.64.","121.88.","210.90.","210.92.","210.97.","210.97.128.","210.96.","210.97.192.","210.98.","210.99.","211.104.","211.112.","211.168.","211.176.","211.192.","211.200.","211.206.","211.212.","211.216.","211.226.","211.232.","211.32.","211.40.","211.52.","218.144.","218.232.","218.234.","218.36.","218.48.","218.50.","219.240.","219.248.","220.103.","220.116.","220.149.","220.64.","220.72.","220.92.","221.132.64.","203.100.160.","165.133.","221.133.128.","203.123.192.","202.126.112.","61.47.192.","203.128.160.","203.128.192.","58.72.","221.138.","221.144.","222.231.","222.232.","222.251.128.","124.48.","222.96.","223.130.128.","223.194.","223.165.128.","14.64.","223.168.","223.255.192.","223.130.64.","27.118.64.","14.32.","223.26.128.","14.4.","223.28.128.","27.120.","223.32.","27.100.128.","1.96.","27.102.","27.115.192.","27.116.64.","27.115.128.","223.131.","27.116.128.","27.117.","27.117.192.","27.119.","27.117.64.","27.117.128.","223.222.","27.118.128.","27.119.128.","223.253.","27.124.128.","49.50.32.","49.254.","27.125.","27.126.","27.160.","27.232.","27.255.64.","27.255.96.","27.111.96.","27.112.128.","27.113.","27.35.","27.96.128.","27.101.","39.112.","39.16.","42.32.","42.8.","42.82.","43.230.80.","43.230.76.","43.230.216.","103.50.40.","45.112.112.","45.112.88.","103.51.168.","45.112.96.","103.51.184.","103.51.172.","103.51.176.","45.112.92.","45.112.116.","103.51.188.","45.112.100.","103.51.192.","45.112.104.","103.51.196.","103.51.200.","45.112.108.","45.112.168.","103.51.252.","45.112.164.","103.51.248.","103.51.240.","103.51.244.","45.112.156.","45.112.152.","45.112.160.","103.52.200.","45.113.48.","45.113.44.","103.53.114.","103.55.35.","45.115.152.","103.55.188.","103.57.60.","45.117.12.","103.59.156.","45.119.144.","45.120.64.","45.120.68.","103.60.120.","103.60.124.","45.121.164.","103.62.228.","45.125.232.","103.194.108.","43.246.152.","103.194.252.","58.84.44.","103.7.190.","61.14.208.","103.206.74.","103.253.240.","27.0.236.","139.5.224.","103.212.124.","160.202.176.","103.212.248.","160.202.172.","103.212.244.","144.48.44.","103.214.24.","144.48.40.","103.214.88.","144.48.92.","144.48.100.","157.119.32.","157.119.36.","103.215.144.","45.248.72.","103.216.202.","45.249.64.","103.218.156.","103.218.160.","45.249.160.","45.250.204.","103.219.124.","45.250.208.","103.219.128.","45.250.220.","103.66.192.","103.66.188.","103.68.96.","103.68.152.","103.68.148.","103.254.248.","103.246.172.","202.90.252.","103.74.","49.1.","49.128.192.","49.143.128.","49.142.","49.143.192.","49.246.","49.16.","49.236.64.","49.246.64.","125.209.192.","49.160.","49.238.128.","49.236.128.","49.239.128.","49.238.64.","101.1.32.","101.1.8.","101.79.","49.247.","49.50.16.","49.50.128.","49.143.","49.56.","58.138.192.","221.133.48.","203.217.192.","202.22.32.","202.68.224.","203.130.176.","58.146.192.","61.247.192.","202.131.24.","121.50.16.","122.0.8.","58.87.32.","121.252.","58.145.","58.148.","58.181.","58.184.","58.29.","59.","218.101.128.","168.188.","60.196.","60.253.","60.253.64.","122.152.96.","123.100.160.","125.62.216.","61.245.176.","58.147.176.","124.66.208.","116.93.160.","119.56.128.","110.76.140.","182.31.","61.247.64.","192.245.250.","58.140.","61.248.","61.32.","61.4.192.","61.247.128.","166.79.","61.40.","61.5.160.","121.124.","61.72.","61.78.","61.80.","61.84.","61.96."]

def is_korean_ip_simple(ip_address):
    """주어진 IP 주소가 한국 IP 프리픽스 목록에 있는지 간단히 확인합니다."""
    try:
        # localhost는 항상 허용
        if ip_address == "127.0.0.1" or ip_address == "::1":
            return True
            
        # IPv6는 현재 체크하지 않고 일단 허용 (필요시 추가)
        if ":" in ip_address:
            return True
        
        # IP 주소가 한국 프리픽스로 시작하는지 확인
        for prefix in KOREAN_IP_PREFIXES:
            if ip_address.startswith(prefix):
                return True
        
        return False
    except:
        # 잘못된 IP 형식인 경우
        return False

async def korean_ip_middleware(request: Request, call_next):
    """한국 IP 주소만 허용하는 미들웨어"""
    client_ip = request.client.host
    
    # 간단한 한국 IP 체크
    if not is_korean_ip_simple(client_ip):
        raise HTTPException(status_code=403, detail="Access denied: Non-Korean IP")
    
    return await call_next(request)