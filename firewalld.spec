#
# Conditional build:
%bcond_with	python3 # CPython 3.x package

Summary:	A firewall daemon with D-Bus interface providing a dynamic firewall
Name:		firewalld
Version:	0.3.14.2
Release:	0.1
License:	GPL v2+
Source0:	https://fedorahosted.org/released/firewalld/%{name}-%{version}.tar.bz2
# Source0-md5:	5984690845a7be38dff3cedff273b73a
Source1:	FedoraServer.xml
Group:		Networking/Admin
Source2:	FedoraWorkstation.xml
Patch0:		MDNS-default.patch
Patch1:		pid_file_RHBZ1233232.patch
URL:		http://www.firewalld.org/
BuildRequires:	desktop-file-utils
BuildRequires:	docbook-style-xsl
BuildRequires:	gettext
BuildRequires:	glib2
# glib2-devel is needed for gsettings.m4
BuildRequires:	glib2-devel
BuildRequires:	intltool
BuildRequires:	python-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.713
BuildRequires:	systemd-units
%if %{with python3}
BuildRequires:	python3-devel
%endif
Requires:	ebtables
Requires:	iptables
Requires(post):	systemd
Requires(preun):	systemd
Requires(postun):	systemd
Requires:	firewalld-config
Requires:	firewalld-filesystem = %{version}-%{release}
Requires:	python-firewall = %{version}-%{release}
Obsoletes:	firewalld-config-cloud <= 0.3.15
Obsoletes:	firewalld-config-server <= 0.3.15
Obsoletes:	firewalld-config-standard <= 0.3.15
Obsoletes:	firewalld-config-workstation <= 0.3.15
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
firewalld is a firewall service daemon that provides a dynamic
customizable firewall with a D-Bus interface.

%package -n python-firewall
Summary:	Python2 bindings for firewalld
Group:		Libraries/Python
Requires:	pygobject3-base
Requires:	python-dbus
Requires:	python-decorator
Requires:	python-slip-dbus
Provides:	python2-firewall
Obsoletes:	python2-firewall

%description -n python-firewall
Python2 bindings for firewalld.

%package -n python3-firewall
Summary:	Python3 bindings for firewalld
Group:		Libraries/Python
Requires:	python3-dbus
Requires:	python3-decorator
Requires:	python3-gobject
Requires:	python3-slip-dbus

%description -n python3-firewall
Python3 bindings for firewalld.

%package -n firewalld-filesystem
Summary:	Firewalld directory layout and rpm macros
Group:		Base

%description -n firewalld-filesystem
This package provides directories and rpm macros which are required by
other packages that add firewalld configuration files.

%package -n firewall-applet
Summary:	Firewall panel applet
Group:		X11/Applications
Requires:	%{name} = %{version}-%{release}
Requires:	NetworkManager-glib
Requires:	PyQt4
Requires:	firewall-config = %{version}-%{release}
Requires:	hicolor-icon-theme
Requires:	libnotify
Requires:	pygobject3-base

%description -n firewall-applet
The firewall panel applet provides a status information of firewalld
and also the firewall settings.

%package -n firewall-config
Summary:	Firewall configuration application
Group:		Base
Requires:	%{name} = %{version}-%{release}
Requires:	NetworkManager-glib
Requires:	gtk+3
Requires:	hicolor-icon-theme
Requires:	pygobject3-base

%description -n firewall-config
The firewall configuration application provides an configuration
interface for firewalld.

%package config-standard
Summary:	Firewalld standard configuration settings
Group:		Base
Requires:	firewalld = %{version}-%{release}
Provides:	firewalld-config
Conflicts:	firewalld-config-server
Conflicts:	firewalld-config-workstation
Conflicts:	system-release-server
Conflicts:	system-release-workstation

%description config-standard
Standard product firewalld configuration settings.

%package config-server
Summary:	Firewalld server configuration settings
Group:		Base
Requires:	firewalld = %{version}-%{release}
Requires:	system-release-server
Provides:	firewalld-config
Conflicts:	firewalld-config-standard
Conflicts:	firewalld-config-workstation

%description config-server
Server product specific firewalld configuration settings.

%package config-workstation
Summary:	Firewalld workstation configuration settings
Group:		Base
Requires:	firewalld = %{version}-%{release}
Requires:	system-release-workstation
Provides:	firewalld-config
Conflicts:	firewalld-config-server
Conflicts:	firewalld-config-standard

%description config-workstation
Workstation product specific firewalld configuration settings.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%if %{with python3}
rm -rf py3
cp -a . py3
%endif

%build
%configure \
	--enable-sysconfig \
	--enable-rpmmacros \
	PYTHON=%{__python}

%if %{with python3}
cd py3
	%configure \
	--enable-sysconfig \
	--enable-rpmmacros \
	PYTHON=%{__python3}
%endif

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	PYTHON=%{__python} \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with python3}
cd py3
%{__make} -C src \
	install-nobase_dist_pythonDATA \
	PYTHON=%{__python3} \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%find_lang %{name} --all-name

desktop-file-install --delete-original \
	--dir $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart \
	$RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/firewall-applet.desktop

desktop-file-install --delete-original \
	--dir $RPM_BUILD_ROOT%{_desktopdir} \
	$RPM_BUILD_ROOT%{_desktopdir}/firewall-config.desktop

install -d $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/zones/
install -c %{SOURCE1} $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/zones/FedoraServer.xml
install -c %{SOURCE2} $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/zones/FedoraWorkstation.xml

# standard firewalld.conf
mv $RPM_BUILD_ROOT%{_sysconfdir}/firewalld/firewalld.conf \
	$RPM_BUILD_ROOT%{_sysconfdir}/firewalld/firewalld-standard.conf

# server firewalld.conf
cp -a $RPM_BUILD_ROOT%{_sysconfdir}/firewalld/firewalld-standard.conf \
	$RPM_BUILD_ROOT%{_sysconfdir}/firewalld/firewalld-server.conf
sed -i 's|^DefaultZone=.*|DefaultZone=FedoraServer|g' \
	$RPM_BUILD_ROOT%{_sysconfdir}/firewalld/firewalld-server.conf

# workstation firewalld.conf
cp -a $RPM_BUILD_ROOT%{_sysconfdir}/firewalld/firewalld-standard.conf \
	$RPM_BUILD_ROOT%{_sysconfdir}/firewalld/firewalld-workstation.conf
sed -i 's|^DefaultZone=.*|DefaultZone=FedoraWorkstation|g' \
	$RPM_BUILD_ROOT%{_sysconfdir}/firewalld/firewalld-workstation.conf

rm -f $RPM_BUILD_ROOT%{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post firewalld.service

%preun
%systemd_preun firewalld.service

%postun
%systemd_postun_with_restart firewalld.service

%posttrans
# If we don't yet have a symlink or existing file for firewalld.conf,
# create it. Note: this will intentionally reset the policykit policy
# at the same time, so they are in sync.

# Import %{_sysconfdir}/os-release to get the variant definition
. %{_sysconfdir}/os-release || :

if [ ! -e %{_sysconfdir}/firewalld/firewalld.conf ]; then
	case "$VARIANT_ID" in
		server)
			ln -sf firewalld-server.conf %{_sysconfdir}/firewalld/firewalld.conf || :
			;;
		workstation)
			ln -sf firewalld-workstation.conf %{_sysconfdir}/firewalld/firewalld.conf || :
			;;
		*)
			ln -sf firewalld-standard.conf %{_sysconfdir}/firewalld/firewalld.conf
			;;
    esac
fi

if [ ! -e %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy ]; then
	case "$VARIANT_ID" in
		workstation)
			ln -sf org.fedoraproject.FirewallD1.desktop.policy %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy || :
			;;
		*)
			# For all other editions, we'll use the Server polkit policy
			ln -sf org.fedoraproject.FirewallD1.server.policy %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy || :
	esac
fi

%post -n firewall-applet
%update_icon_cache hicolor

%postun -n firewall-applet
%update_icon_cache hicolor
%glib_compile_schemas

%posttrans -n firewall-applet
%update_icon_cache hicolor
%glib_compile_schemas

%post -n firewall-config
%update_icon_cache hicolor

%postun -n firewall-config
%update_icon_cache hicolor
%glib_compile_schemas

%posttrans -n firewall-config
%update_icon_cache hicolor
%glib_compile_schemas

%post config-standard
if [ $1 -eq 1 ]; then # Initial installation
	# link standard config
	rm -f %{_sysconfdir}/firewalld/firewalld.conf
	ln -sf firewalld-standard.conf %{_sysconfdir}/firewalld/firewalld.conf || :
fi

%triggerin config-standard -- firewalld
if [ $1 -eq 1 ]; then
	# link server policy
	rm -f %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy
	ln -sf org.fedoraproject.FirewallD1.server.policy %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy || :
fi

%post config-server
if [ $1 -eq 1 ]; then # Initial installation
	# link server config
	rm -f %{_sysconfdir}/firewalld/firewalld.conf
	ln -sf firewalld-server.conf %{_sysconfdir}/firewalld/firewalld.conf || :
fi

%triggerin config-server -- firewalld
if [ $1 -eq 1 ]; then
	# link server policy
	rm -f %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy
	ln -sf org.fedoraproject.FirewallD1.server.policy %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy || :
fi

%post config-workstation
if [ $1 -eq 1 ]; then # Initial installation
	# link workstation config
	rm -f %{_sysconfdir}/firewalld/firewalld.conf
	ln -sf firewalld-workstation.conf %{_sysconfdir}/firewalld/firewalld.conf || :
fi

%triggerin config-workstation -- firewalld
if [ $1 -eq 1 ]; then
	# link desktop policy
	rm -f %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy
	ln -sf org.fedoraproject.FirewallD1.desktop.policy %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy || :
fi

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_sbindir}/firewalld
%attr(755,root,root) %{_bindir}/firewall-cmd
%attr(755,root,root) %{_bindir}/firewall-offline-cmd
%dir %{bash_compdir}
%{bash_compdir}/firewall-cmd
%{_prefix}/lib/firewalld/icmptypes/*.xml
%{_prefix}/lib/firewalld/services/*.xml
%{_prefix}/lib/firewalld/zones/*.xml
%{_prefix}/lib/firewalld/xmlschema/*.xsd
%dir %attr(750,root,root) %dir %{_sysconfdir}/firewalld
#%ghost %config(noreplace) %{_sysconfdir}/firewalld/firewalld.conf
#%config(noreplace) %{_sysconfdir}/firewalld/firewalld-standard.conf
#%config(noreplace) %{_sysconfdir}/firewalld/firewalld-server.conf
#%config(noreplace) %{_sysconfdir}/firewalld/firewalld-workstation.conf
%config(noreplace) %{_sysconfdir}/firewalld/lockdown-whitelist.xml
%attr(750,root,root) %dir %{_sysconfdir}/firewalld/icmptypes
%attr(750,root,root) %dir %{_sysconfdir}/firewalld/services
%attr(750,root,root) %dir %{_sysconfdir}/firewalld/zones
%defattr(0644,root,root)
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/firewalld
#%{systemdunitdir}/firewalld.service
%config(noreplace) /etc/dbus-1/system.d/FirewallD.conf
%{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.desktop.policy
%{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.server.policy
#%ghost %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy
%{_mandir}/man1/firewall*cmd*.1*
%{_mandir}/man1/firewalld*.1*
%{_mandir}/man5/firewall*.5*

%files -n python-firewall
%defattr(644,root,root,755)
%dir %{py_sitescriptdir}/firewall
%dir %{py_sitescriptdir}/firewall/config
%dir %{py_sitescriptdir}/firewall/core
%dir %{py_sitescriptdir}/firewall/core/io
%dir %{py_sitescriptdir}/firewall/server
%{py_sitescriptdir}/firewall/*.py*
%{py_sitescriptdir}/firewall/config/*.py*
%{py_sitescriptdir}/firewall/core/*.py*
%{py_sitescriptdir}/firewall/core/io/*.py*
%{py_sitescriptdir}/firewall/server/*.py*

%if %{with python3}
%files -n python3-firewall
%defattr(644,root,root,755)
%dir %{py3_sitescriptdir}/firewall
%dir %{py3_sitescriptdir}/firewall/__pycache__
%dir %{py3_sitescriptdir}/firewall/config
%dir %{py3_sitescriptdir}/firewall/config/__pycache__
%dir %{py3_sitescriptdir}/firewall/core
%dir %{py3_sitescriptdir}/firewall/core/__pycache__
%dir %{py3_sitescriptdir}/firewall/core/io
%dir %{py3_sitescriptdir}/firewall/core/io/__pycache__
%dir %{py3_sitescriptdir}/firewall/server
%dir %{py3_sitescriptdir}/firewall/server/__pycache__
%{py3_sitescriptdir}/firewall/__pycache__/*.py*
%{py3_sitescriptdir}/firewall/*.py*
%{py3_sitescriptdir}/firewall/config/*.py*
%{py3_sitescriptdir}/firewall/config/__pycache__/*.py*
%{py3_sitescriptdir}/firewall/core/*.py*
%{py3_sitescriptdir}/firewall/core/__pycache__/*.py*
%{py3_sitescriptdir}/firewall/core/io/*.py*
%{py3_sitescriptdir}/firewall/core/io/__pycache__/*.py*
%{py3_sitescriptdir}/firewall/server/*.py*
%{py3_sitescriptdir}/firewall/server/__pycache__/*.py*
%endif

%files -n firewalld-filesystem
%defattr(644,root,root,755)
%dir %{_prefix}/lib/firewalld
%dir %{_prefix}/lib/firewalld/icmptypes
%dir %{_prefix}/lib/firewalld/services
%dir %{_prefix}/lib/firewalld/zones
%dir %{_prefix}/lib/firewalld/xmlschema
#%{_rpmconfigdir}/macros.d/macros.firewalld

%files -n firewall-applet
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/firewall-applet
%defattr(0644,root,root)
%{_sysconfdir}/xdg/autostart/firewall-applet.desktop
%{_iconsdir}/hicolor/*/apps/firewall-applet*.*
%{_mandir}/man1/firewall-applet*.1*

%files -n firewall-config
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/firewall-config
%defattr(0644,root,root)
%{_datadir}/firewalld/firewall-config.glade
%{_datadir}/firewalld/gtk3_chooserbutton.py*
%{_desktopdir}/firewall-config.desktop
%{_datadir}/appdata/firewall-config.appdata.xml
%{_iconsdir}/hicolor/*/apps/firewall-config*.*
%{_datadir}/glib-2.0/schemas/org.fedoraproject.FirewallConfig.gschema.xml
%{_mandir}/man1/firewall-config*.1*

%files config-standard
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/firewalld/firewalld-standard.conf
#%ghost %config(noreplace) %{_sysconfdir}/firewalld/firewalld.conf
#%ghost %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy

%files config-server
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/firewalld/firewalld-server.conf
#%ghost %config(noreplace) %{_sysconfdir}/firewalld/firewalld.conf
#%ghost %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy

%files config-workstation
%defattr(644,root,root,755)
%config(noreplace) %{_sysconfdir}/firewalld/firewalld-workstation.conf
#%ghost %config(noreplace) %{_sysconfdir}/firewalld/firewalld.conf
#%ghost %{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy