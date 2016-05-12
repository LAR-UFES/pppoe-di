#!/usr/bin/env python3

from distutils.core import setup
from distutils.command.install import install
from distutils.core import Command

def main():
    
    install.sub_commands.append(('install_dbus_service',None))
    setup(
        # Application name:
        name="PPPoEDI",

        # Version number (initial):
        version="0.0.95",

        # Application author details:
        author="LAR",
        author_email="monitores@inf.ufes.br",

        # Packages
        packages=['pppoediplugin'],
        package_data={'pppoediplugin':["ui/*"]},

        # Include additional files into the package
        #include_package_data=True,

        # Details
        url="http://www.suporte.inf.ufes.br",
        license="LICENSE.txt",
        description="Interface grafica escrita em Python para conexao ao servidor PPPoE do DI.",

        # long_description=open("README.txt").read(),

        # Dependent packages (distributions)
        # install_requires=[
        #    'gi',
        # ],
        data_files=[('/usr/share/dbus-1/system-services/', ['conf/com.lar.PppoeDi.service']),
                    ('/usr/share/polkit-1/actions', ['conf/com.lar.pppoedi.policy']),
                    ('/etc/dbus-1/system.d/', ['conf/com.lar.PppoeDi.conf']),
                    ('/usr/share/applications',['icon/pppoedi.desktop'])],
        scripts=['scripts/pppoedi-service', 'scripts/pppoedi', 'scripts/pppoedi-cli'],
        cmdclass={"install_dbus_service": install_dbus_service}
    )

class install_dbus_service(Command):
    description = "Install DBus .service file, modifying it so that it points to the correct script"
    user_options = []
    
    def initialize_options(self):
        pass
    
    def finalize_options(self):
        pass
    
    def run(self):
        install_bin = self.get_finalized_command('install_scripts')
        script_install_dir = install_bin.install_dir
        output = ""
        ff = open("/usr/share/dbus-1/system-services/com.lar.PppoeDi.service","r")
        for line in ff.readlines():
            if line.strip()[:5] == "Exec=":
                line = line.replace("/usr/bin", script_install_dir)
            output += line
        ff.close()
        ff = open("/usr/share/dbus-1/system-services/com.lar.PppoeDi.service","w")
        ff.write(output)
        ff.close()

if __name__ == "__main__":
    main()
