import codecs
import json
import os
import sys
import distutils.spawn
import shutil
import signal

# Backport required for earlier versions of Python.
if sys.version_info < (3, 3):
    from backports.shutil_get_terminal_size import get_terminal_size
else:
    from shutil import get_terminal_size

import click
import crayons
import delegator
import pexpect

from . import _pipfile as pipfile
from .project import Project
from .utils import convert_deps_from_pip, convert_deps_to_pip
from .__version__ import __version__
from . import pep508checker


project = Project()

def ensure_latest_pip():
    """Updates pip to the latest version."""
    # Ensure that pip is installed.
    c = delegator.run('{0} install pip'.format(which_pip()))
    # Check if version is out of date.
    if 'however' in c.err:
        # If version is out of date, update.
        click.echo(crayons.yellow('Pip is out of date... updating to latest.'))
        c = delegator.run('{0} install pip --upgrade'.format(which_pip()), block=False)
        click.echo(crayons.blue(c.out))







def ensure_virtualenv(three=None):
    """Creates a virtualenv, if one doesn't exist."""
    if not project.virtualenv_exists:
        do_create_virtualenv(three=three)
    # If --three / --two were passed...
    elif three is not None:
        click.echo(crayons.red('Virtualenv already exists!'), err=True)
        click.echo(crayons.yellow('Removing existing virtualenv...'), err=True)
        # Remove the virtualenv.
        shutil.rmtree(project.virtualenv_location)
        # Call this function again.
        ensure_virtualenv(three=three)













def do_where(virtualenv=False, bare=True):
    """Executes the where functionality."""
    if not virtualenv:
        location = project.pipfile_location
        if not location:
            click.echo('No Pipfile present at project home. Consider running {0} first to automatically generate a Pipfile for you.'.format(crayons.green('`pipenv install`')), err=True)
        elif not bare:
            click.echo('Pipfile found at {0}. Considering this to be the project home.'.format(crayons.green(location)), err=True)
        else:
            click.echo(location)
    else:
        location = project.virtualenv_location
        if not bare:
            click.echo('Virtualenv location: {0}'.format(crayons.green(location)))
        else:
            click.echo(location)






def do_install_dependencies(dev=False, only=False, bare=False, requirements=False, allow_global=False):
    """"Executes the install functionality."""
    # Load the Pipfile.
    p = pipfile.load(project.pipfile_location)
    else:
        if not bare:
            click.echo(crayons.yellow('Installing dependencies from Pipfile.lock...'))
        with open(project.lockfile_location, 'r') as f:
            lockfile = json.load(f)
    # Install default dependencies, always.
    deps = lockfile['default'] if not only else {}
    # Add development deps if --dev was passed.
    if dev:
        deps.update(lockfile['develop'])
    # Convert the deps to pip-compatible arguments.
    deps_path = convert_deps_to_pip(deps)











def do_create_virtualenv(three=None):
    """Creates a virtualenv."""
    click.echo(crayons.yellow('Creating a virtualenv for this project...'))
    # The command to create the virtualenv.
    cmd = ['virtualenv', project.virtualenv_location, '--prompt=({0})'.format(project.name)]
    # Pass a Python version to virtualenv, if needed.
    if three is False:
        cmd = cmd + ['-p', 'python2']
    if three is True:
        cmd = cmd + ['-p', 'python3']
    # Actually create the virtualenv.
    c = delegator.run(cmd, block=False)
    click.echo(crayons.blue(c.out))
    # Say where the virtualenv is.
    do_where(virtualenv=True, bare=False)























def activate_virtualenv(source=True):
    """Returns the string to activate a virtualenv."""
    # Suffix for other shells.
    suffix = ''
    # Support for fish shell.
    if 'fish' in os.environ['SHELL']:
        suffix = '.fish'
    # Support for csh shell.
    if 'csh' in os.environ['SHELL']:
        suffix = '.csh'
    # Escape any spaces located within the virtualenv path to allow
<<<<<<< REMOTE
else:
=======
# for proper activation.
>>>>>>> LOCAL
    venv_location = project.virtualenv_location.replace(' ', '\ ')
    if source:
        return 'source {0}/bin/activate{1}'.format(venv_location, suffix)
    else:
<<<<<<< REMOTE
c = delegator.run('{0} install "{1}" -i {2}'.format(which_pip(allow_global=allow_global), package_name, project.source['url']))
=======
return '{0}/bin/activate'.format(venv_location)
>>>>>>> LOCAL
        return '{0}/bin/activate{1}'.format(project.virtualenv_location, suffix)






def do_activate_virtualenv(bare=False):
    """Executes the activate virtualenv functionality."""
    # Check for environment marker, and skip if it's set.
    if 'PIPENV_ACTIVE' not in os.environ:
        if not bare:
            click.echo('To activate this project\'s virtualenv, run the following:\n $ {0}'.format(
                crayons.red('pipenv shell'))
            )
        else:
            click.echo(activate_virtualenv())


def do_purge(bare=False, downloads=False, allow_global=False):
    """Executes the purge functionality."""

    if downloads:
        if not bare:
            click.echo(crayons.yellow('Clearing out downloads directory...'))
        shutil.rmtree(project.download_location)
        return

    freeze = delegator.run('{0} freeze'.format(which_pip(allow_global=allow_global))).out
    installed = freeze.split()

    if not bare:
        click.echo('Found {0} installed package(s), purging...'.format(len(installed)))
    command = '{0} uninstall {1} -y'.format(which_pip(allow_global=allow_global), ' '.join(installed))
    c = delegator.run(command)

    if not bare:
        click.echo(crayons.blue(c.out))

        click.echo(crayons.yellow('Environment now purged and fresh!'))


def do_init(dev=False, requirements=False, skip_virtualenv=False, allow_global=False):
    """Executes the init functionality."""

    ensure_pipfile()

    # Display where the Project is established.
    do_where(bare=False)

    if not project.virtualenv_exists:
        do_create_virtualenv()

    # Write out the lockfile if it doesn't exist.
    if project.lockfile_exists:

        # Open the lockfile.
        with codecs.open(project.lockfile_location, 'r') as f:
            lockfile = json.load(f)
        p = pipfile.load(project.pipfile_location)
        if not bare:
            click.echo('To activate this project\'s virtualenv, run the following:\n $ {0}'.format(
                crayons.red('pipenv shell'))
            )
        else:
            click.echo(activate_virtualenv())


def do_purge(bare=False, downloads=False, allow_global=False):
    """Executes the purge functionality."""

    if downloads:
        if not bare:
            click.echo(crayons.yellow('Clearing out downloads directory...'))
        shutil.rmtree(project.download_location)
        return

    freeze = delegator.run('{0} freeze'.format(which_pip(allow_global=allow_global))).out
    installed = freeze.split()

    if not bare:
        click.echo('Found {0} installed package(s), purging...'.format(len(installed)))
    command = '{0} uninstall {1} -y'.format(which_pip(allow_global=allow_global), ' '.join(installed))
    c = delegator.run(command)

    if not bare:
        click.echo(crayons.blue(c.out))

        click.echo(crayons.yellow('Environment now purged and fresh!'))


def do_init(dev=False, requirements=False, skip_virtualenv=False, allow_global=False):
    """Executes the init functionality."""

    ensure_pipfile()

    # Display where the Project is established.
    do_where(bare=False)

    if not project.virtualenv_exists:
        do_create_virtualenv()

    # Write out the lockfile if it doesn't exist.
    if project.lockfile_exists:

        # Open the lockfile.
        with codecs.open(project.lockfile_location, 'r') as f:
            lockfile = json.load(f)
        # Update the lockfile if it is out-of-date.
        p = pipfile.load(project.pipfile_location)
        # Check that the hash of the Lockfile matches the lockfile's hash.
        if not lockfile['_meta']['Pipfile-sha256'] == p.hash:
            click.echo(crayons.red('Pipfile.lock out of date, updating...'), err=True)
            do_lock()
    do_install_dependencies(dev=dev, requirements=requirements, allow_global=allow_global)
    # Write out the lockfile if it doesn't exist.
    if not project.lockfile_exists:
        click.echo(crayons.yellow('Pipfile.lock not found, creating...'), err=True)
        do_lock()
        if not bare:
            click.echo(crayons.yellow('Installing dependencies from Pipfile...'))
        lockfile = json.loads(p.lock())
    # Activate virtualenv instructions.
    do_activate_virtualenv()








def which(command):
    return os.sep.join([project.virtualenv_location] + ['bin/{0}'.format(command)])


def which_pip(allow_global=False):
    """Returns the location of virtualenv-installed pip."""
    if allow_global:
        return distutils.spawn.find_executable('pip')
    return which('pip')


def format_help(help):
    """Formats the help string."""
    help = help.replace('  check', str(crayons.green('  check')))
    help = help.replace('  uninstall', str(crayons.yellow('  uninstall', bold=True)))
    help = help.replace('  install', str(crayons.yellow('  install', bold=True)))
    help = help.replace('  lock', str(crayons.red('  lock', bold=True)))
    help = help.replace('  run', str(crayons.blue('  run')))
    help = help.replace('  shell', str(crayons.blue('  shell', bold=True)))
    help = help.replace('  update', str(crayons.yellow('  update')))
    additional_help = """

Usage Examples:
   Create a new project using Python 3:
   $ {0}
   Install all dependencies for a project (including dev):
   $ {1}
   Create a lockfile (& keep [dev-packages] intalled):
   $ {2}




