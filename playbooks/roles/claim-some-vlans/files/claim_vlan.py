import MySQLdb
from datetime import datetime, timedelta

db = MySQLdb.connect(host="10.0.196.2",
                     user="ciuser",
                     passwd="secret",
                     db="ciresources")

cur = db.cursor()

f = '%Y-%m-%d %H:%M:%S'
three_hours_ago_dt = datetime.utcnow() - timedelta(hours=3)
three_hours_ago = three_hours_ago_dt.strftime(f)

cur.execute("SELECT * FROM vlans WHERE locked!=true OR timestamp<'%s' "
            "LIMIT 1 FOR UPDATE" % three_hours_ago)

row = cur.fetchone()

if row is not None:
    min_vlan = row[0]
    max_vlan = row[1]
    vlans = {"min_vlan": min_vlan, "max_vlan": max_vlan,
             "timestamp": datetime.now().strftime(f)}
    cur.execute("UPDATE vlans SET locked=true, timestamp='%(timestamp)s' "
                "where min_vlan=%(min_vlan)s AND "
                "max_vlan=%(max_vlan)s" % vlans)
else:
    raise Exception("No free VLANs found!")

db.commit()
db.close()

print("%(min_vlan)s:%(max_vlan)s" % vlans)
