import MySQLdb
from datetime import datetime, timedelta
import argparse
import json
import requests
from contextlib import contextmanager


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


f = '%Y-%m-%d %H:%M:%S'
three_hours_ago_dt = datetime.utcnow() - timedelta(hours=3)
three_hours_ago = three_hours_ago_dt.strftime(f)


def generate_where_clause(data):
    equals = []
    data.pop("type", None)
    for k, v in data.items():
        equals.append("%s=\"%s\"" % (k, v))
    return " AND ".join(equals)


@contextmanager
def ci_resource_db():
    db = MySQLdb.connect(host="10.0.196.2",
                         user="ciuser",
                         passwd="secret",
                         db="ciresources")
    try:
        yield db.cursor()
    finally:
        db.commit()
        db.close()


def list_resource(args):
    ci_resource_name = args.resource_type
    ci_resource_fields = fields[ci_resource_name]

    select_fields = ", ".join(ci_resource_fields)

    with ci_resource_db() as cur:
        cur.execute("SELECT %s FROM %ss" %
                    (select_fields, ci_resource_name))
        data = []
        for row in cur:
            row_data = {}
            for i in range(len(ci_resource_fields)):
                row_data[ci_resource_fields[i]] = row[i]
            data.append(row_data)

    print(json.dumps(data))


def cleanup(args):
    r = requests.get('http://3ci-zuul.ciscolabs.net/api/status')
    cistatus = r.json()

    runningbuildids = []

    for pipeline in cistatus['pipelines']:
        for queue in pipeline['change_queues']:
            for head in queue['heads']:
                for change in head:
                    for job in change['jobs']:
                        if job['uuid'] and not job['result']:
                            runningbuildids.append(job['uuid'])

    joinedbuildids = ','.join("'%s'" % item for item in runningbuildids)

    with ci_resource_db() as cur:
        for ci_resource in fields:
            cur.execute("UPDATE %(ci_resource)ss SET locked=false, "
                        "buildid=null WHERE buildid NOT IN (%(buildids)s)"
                        % {'ci_resource': ci_resource,
                           'buildids': joinedbuildids})


def release(args):
    ci_resource_name = args.resource_type
    ci_resource_fields = fields[ci_resource_name]

    with open(args.resource_json_file) as json_data:
        d = json.load(json_data)

    if not all(field in d for field in ci_resource_fields):
        raise Exception('Missing field information from claimed resource')

    where = generate_where_clause(d)
    with ci_resource_db() as cur:
        cur.execute("UPDATE %ss SET locked=false, "
                    "buildid=null where %s" % (ci_resource_name, where))


def claim(args):
    ci_resource_name = args.resource_type
    ci_resource_fields = fields[ci_resource_name]

    select_fields = ", ".join(ci_resource_fields)

    with ci_resource_db() as cur:
        cur.execute("SELECT %s FROM %ss WHERE locked!=true OR timestamp<'%s' "
                    "LIMIT 1 FOR UPDATE" % (select_fields, ci_resource_name,
                                            three_hours_ago))
        row = cur.fetchone()

        if row is not None:
            data = {}
            for i in range(len(ci_resource_fields)):
                data[ci_resource_fields[i]] = row[i]

            query = ("UPDATE %(resource)ss SET locked=true, "
                     "timestamp='%(timestamp)s', buildid='%(buildid)s' "
                     "where %(where)s")

            where = generate_where_clause(data)
            cur.execute(query % {'where': where, 'resource': ci_resource_name,
                                 'timestamp': datetime.now().strftime(f),
                                 'buildid': args.buildid})
        else:
            raise Exception("No free %s found!" % ci_resource_name)

    data['type'] = ci_resource_name

    print(json.dumps(data))


parser = argparse.ArgumentParser(description="Tool for managing CI resources")
subparsers = parser.add_subparsers()

claim_parser = subparsers.add_parser(
    'claim', help='Claim a specific CI resource')
claim_parser.add_argument(
    'resource_type', help="The type of resource to claim")
claim_parser.add_argument(
    'buildid', help="The build id to claim the resource with")
claim_parser.set_defaults(func=claim)

release_parser = subparsers.add_parser(
    'release', help='Release a specific CI resource')
release_parser.add_argument(
    'resource_type', help="The type of resource to release")
release_parser.add_argument(
    'resource_json_file', help="Claimed resource to release json file")
release_parser.set_defaults(func=release)

list_parser = subparsers.add_parser(
    'list', help='List all of a CI resource')
list_parser.add_argument(
    'resource_type', help="The type of resource to list")
list_parser.set_defaults(func=list_resource)

cleanup_parser = subparsers.add_parser(
    'cleanup', help='Cleanup all orphaned CI resources')
cleanup_parser.set_defaults(func=cleanup)

args = parser.parse_args()
args.func(args)
