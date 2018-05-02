import MySQLdb
from datetime import datetime, timedelta
import argparse
import json
import sys


parser = argparse.ArgumentParser(description="Claim a specific CI resource")
parser.add_argument('resource_type', help="The type of resource to claim")
parser.add_argument('--release', help="claimed resource to release json file")
parser.add_argument('--list', help="list all resources of the type",
                    action="store_true")
args = parser.parse_args()

ci_resource_name = args.resource_type

db = MySQLdb.connect(host="10.0.196.2",
                     user="ciuser",
                     passwd="secret",
                     db="ciresources")

fields = {
    'vlan': [
        'min_vlan',
        'max_vlan'
    ],
    'cimc_baremetal': [
        'id',
        'bmc_address',
        'nexus_port',
        'mac_address'
    ],
    'ucsm_baremetal': [
        'id',
        'bmc_address',
        'service_profile',
        'mac_address'
    ],
    'region_id': [
        'region_id'
    ]
}

ci_resource_fields = fields[ci_resource_name]

f = '%Y-%m-%d %H:%M:%S'
three_hours_ago_dt = datetime.utcnow() - timedelta(hours=3)
three_hours_ago = three_hours_ago_dt.strftime(f)

cur = db.cursor()


def generate_where_clause(data):
    equals = []
    data.pop("type", None)
    for k, v in data.items():
        equals.append("%s=\"%s\"" % (k, v))
    return " AND ".join(equals)

if args.list:
    select_fields = ", ".join(ci_resource_fields)
    cur.execute("SELECT %s FROM %ss" %
                (select_fields, ci_resource_name))
    data = []
    for row in cur:
        row_data = {}
        for i in range(len(ci_resource_fields)):
            row_data[ci_resource_fields[i]] = row[i]
        data.append(row_data)

    print(json.dumps(data))
    db.close()
    sys.exit()

if args.release:

    with open(args.release) as json_data:
        d = json.load(json_data)

    if not all(field in d for field in ci_resource_fields):
        raise Exception('Missing field information from claimed resource')

    where = generate_where_clause(d)
    cur.execute("UPDATE %ss SET locked=false where %s" % (ci_resource_name,
                                                          where))

else:
    select_fields = ", ".join(ci_resource_fields)

    cur.execute("SELECT %s FROM %ss WHERE locked!=true OR timestamp<'%s' "
                "LIMIT 1 FOR UPDATE" % (select_fields, ci_resource_name,
                                        three_hours_ago))
    row = cur.fetchone()

    if row is not None:
        data = {}
        for i in range(len(ci_resource_fields)):
            data[ci_resource_fields[i]] = row[i]

        query = ("UPDATE %(resource)ss SET locked=true, "
                 "timestamp='%(timestamp)s' where %(where)s")

        where = generate_where_clause(data)
        cur.execute(query % {'where': where, 'resource': ci_resource_name,
                             'timestamp': datetime.now().strftime(f)})
    else:
        raise Exception("No free VLANs found!")

    data['type'] = ci_resource_name

    print(json.dumps(data))

db.commit()
db.close()
