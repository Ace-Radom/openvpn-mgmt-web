bind = "127.0.0.1:9532"
workers = 4
forwarded_allow_ips = "*"

accesslog = "-"
access_log_format = '%(t)s %(p)s %({X-Real-IP}i)s "%(r)s" %(s)s'

errorlog = "-"
