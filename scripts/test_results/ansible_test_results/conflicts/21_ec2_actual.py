try:
    from distutils.version import LooseVersion
    HAS_LOOSE_VERSION = True
except:
    HAS_LOOSE_VERSION = False

AWS_REGIONS = ['ap-northeast-1',
               'ap-southeast-1',
               'ap-southeast-2',
               'eu-west-1',
               'sa-east-1',
               'us-east-1',
               'us-west-1',
               'us-west-2']
<<<<<<< REMOTE
def ec2_argument_spec():
    spec = ec2_argument_keys_spec()
    spec.update(
        dict(
            region=dict(aliases=['aws_region', 'ec2_region'], choices=AWS_REGIONS),
            ec2_url=dict(),
        )
    )
    return spec



=======

>>>>>>> LOCAL




def ec2_argument_keys_spec():
    return dict(
        aws_secret_key=dict(aliases=['ec2_secret_key', 'secret_key'], no_log=True),
        aws_access_key=dict(aliases=['ec2_access_key', 'access_key']),
    )


def ec2_connect(module):
    """ Return an ec2 connection"""
<<<<<<< REMOTE

=======
validate_certs = module.params.get('validate_certs', True)
>>>>>>> LOCAL
    else:
        module.fail_json(msg="Either region or ec2_url must be specified")


    ec2_url, aws_access_key, aws_secret_key, region = get_ec2_creds(module)
    # If we have a region specified, connect to its endpoint.
    if region:
try:
                ec2 = boto.ec2.connect_to_region(region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        except boto.exception.NoAuthHandlerFound, e:
            module.fail_json(msg = str(e))
    # Otherwise, no region so we fallback to the old connection method
    elif ec2_url:
        try:
                ec2 = boto.connect_ec2_endpoint(ec2_url, aws_access_key, aws_secret_key)
        except boto.exception.NoAuthHandlerFound, e:
            module.fail_json(msg = str(e))
    return ec2

