import MySQLdb

db = MySQLdb.connect(host="localhost",
                     user="ciuser",
                     passwd="secret",
                     db="ciresources")

cur = db.cursor()

cur.execute("SELECT * FROM vlans WHERE locked!=true LIMIT 1 FOR UPDATE")

row = cur.fetchone()

if row is not None:
  min_vlan = row[0]
  max_vlan = row[1]
  vlans = {"min_vlan": min_vlan, "max_vlan":max_vlan}
  cur.execute("UPDATE vlans SET locked=true where min_vlan=%(min_vlan)s AND max_vlan=%(max_vlan)s" % vlans)
else:
  raise Exception("No free VLANs found!")

db.commit()
db.close()

print("%(min_vlan)s:%(max_vlan)s" % vlans)
