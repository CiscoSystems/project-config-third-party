import MySQLdb
import argparse

parser = argparse.ArgumentParser(description="Release some vlans")
parser.add_argument('min_vlan', help="the min vlan of the range")
parser.add_argument('max_vlan', help="the max vlan of the range")

args = parser.parse_args()

db = MySQLdb.connect(host="10.0.196.2",
                     user="ciuser",
                     passwd="secret",
                     db="ciresources")

cur = db.cursor()

vlans = {"min_vlan": args.min_vlan, "max_vlan": args.max_vlan}
cur.execute("UPDATE vlans SET locked=false where min_vlan=%(min_vlan)s AND max_vlan=%(max_vlan)s" % vlans)

db.commit()
db.close()
