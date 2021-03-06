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


def ec2_argument_keys_spec():
    return dict(
<<<<<<< HEAD
        region=dict(aliases=['aws_region', 'ec2_region'], choices=AWS_REGIONS),
        ec2_url=dict(),
        ec2_secret_key=dict(aliases=['aws_secret_key', 'secret_key'], no_log=True),
        ec2_access_key=dict(aliases=['aws_access_key', 'access_key']),
        validate_certs=dict(default=True, type='bool'),
=======
        aws_secret_key=dict(aliases=['ec2_secret_key', 'secret_key'], no_log=True),
        aws_access_key=dict(aliases=['ec2_access_key', 'access_key']),
    )


def ec2_argument_spec():
    spec = ec2_argument_keys_spec()
    spec.update(
        dict(
            region=dict(aliases=['aws_region', 'ec2_region'], choices=AWS_REGIONS),
            ec2_url=dict(),
        )
>>>>>>> remote
    )
    return spec


def get_ec2_creds(module):

    # Check module args for credentials, then check environment vars

    ec2_url = module.params.get('ec2_url')
    ec2_secret_key = module.params.get('aws_secret_key')
    ec2_access_key = module.params.get('aws_access_key')
    region = module.params.get('region')

    if not ec2_url:
        if 'EC2_URL' in os.environ:
            ec2_url = os.environ['EC2_URL']
        elif 'AWS_URL' in os.environ:
            ec2_url = os.environ['AWS_URL']

    if not ec2_access_key:
        if 'EC2_ACCESS_KEY' in os.environ:
            ec2_access_key = os.environ['EC2_ACCESS_KEY']
        elif 'AWS_ACCESS_KEY_ID' in os.environ:
            ec2_access_key = os.environ['AWS_ACCESS_KEY_ID']
        elif 'AWS_ACCESS_KEY' in os.environ:
            ec2_access_key = os.environ['AWS_ACCESS_KEY']

    if not ec2_secret_key:
        if 'EC2_SECRET_KEY' in os.environ:
            ec2_secret_key = os.environ['EC2_SECRET_KEY']
        elif 'AWS_SECRET_ACCESS_KEY' in os.environ:
            ec2_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
        elif 'AWS_SECRET_KEY' in os.environ:
            ec2_secret_key = os.environ['AWS_SECRET_KEY']

    if not region:
        if 'EC2_REGION' in os.environ:
            region = os.environ['EC2_REGION']
        elif 'AWS_REGION' in os.environ:
            region = os.environ['AWS_REGION']

    return ec2_url, ec2_access_key, ec2_secret_key, region


def ec2_connect(module):

    """ Return an ec2 connection"""

    ec2_url, aws_access_key, aws_secret_key, region = get_ec2_creds(module)
    validate_certs = module.params.get('validate_certs', True)

    # If we have a region specified, connect to its endpoint.
    if region:
        try:
            if HAS_LOOSE_VERSION and LooseVersion(boto.Version) >= LooseVersion("2.6.0"):
                ec2 = boto.ec2.connect_to_region(region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, validate_certs=validate_certs)
            else:
                ec2 = boto.ec2.connect_to_region(region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
        except boto.exception.NoAuthHandlerFound, e:
            module.fail_json(msg = str(e))
    # Otherwise, no region so we fallback to the old connection method
    elif ec2_url:
        try:
            if HAS_LOOSE_VERSION and LooseVersion(boto.Version) >= LooseVersion("2.6.0"):
                ec2 = boto.connect_ec2_endpoint(ec2_url, aws_access_key, aws_secret_key, validate_certs=validate_certs)
            else:
                ec2 = boto.connect_ec2_endpoint(ec2_url, aws_access_key, aws_secret_key)
        except boto.exception.NoAuthHandlerFound, e:
            module.fail_json(msg = str(e))
    else:
        module.fail_json(msg="Either region or ec2_url must be specified")
    return ec2

