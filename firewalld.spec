Summary:	A firewall daemon with D-Bus interface providing a dynamic firewall
Name:		firewalld
Version:	1.2.0
Release:	3
License:	GPL v2+
Source0:	https://github.com/firewalld/firewalld/releases/download/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	cbb120864ecb83544f7329c09367250f
Group:		Networking/Admin
URL:		http://www.firewalld.org/
BuildRequires:	desktop-file-utils
BuildRequires:	docbook-style-xsl
BuildRequires:	gettext
BuildRequires:	glib2
# glib2-devel is needed for gsettings.m4
BuildRequires:	glib2-devel
BuildRequires:	intltool
BuildRequires:	python3
BuildRequires:	python3-modules
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.713
BuildRequires:	sed >= 4.0
BuildRequires:	systemd-units
Requires:	iptables
Suggests:	ipset
Requires(post):	systemd
Requires(preun):	systemd
Requires(postun):	systemd
Requires:	python3-firewall = %{version}-%{release}
Obsoletes:	firewalld-config-cloud
Obsoletes:	firewalld-config-server
Obsoletes:	firewalld-config-standard
Obsoletes:	firewalld-config-workstation
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
firewalld is a firewall service daemon that provides a dynamic
customizable firewall with a D-Bus interface.

%package -n python-firewall
Summary:	Python2 bindings for firewalld
Group:		Libraries/Python
Requires:	python-dbus
Requires:	python-decorator
Requires:	python-slip-dbus
Requires:	python3-pygobject3
Provides:	python2-firewall
Obsoletes:	python2-firewall

%description -n python-firewall
Python2 bindings for firewalld.

%package -n python3-firewall
Summary:	Python3 bindings for firewalld
Group:		Libraries/Python
Requires:	python3-dbus
Requires:	python3-decorator
Requires:	python3-pygobject3
Requires:	python3-slip-dbus

%description -n python3-firewall
Python3 bindings for firewalld.

%package -n firewall-applet
Summary:	Firewall panel applet
Group:		X11/Applications
Requires:	%{name} = %{version}-%{release}
Requires:	NetworkManager-libs
Requires:	firewall-config = %{version}-%{release}
Requires:	hicolor-icon-theme
Requires:	libnotify
Requires:	python3-PyQt5
Requires:	python3-pygobject3

%description -n firewall-applet
The firewall panel applet provides a status information of firewalld
and also the firewall settings.

%package -n firewall-config
Summary:	Firewall configuration application
Group:		Base
Requires:	%{name} = %{version}-%{release}
Requires:	NetworkManager-libs
Requires:	gtk+3
Requires:	hicolor-icon-theme
Requires:	python3-pygobject3

%description -n firewall-config
The firewall configuration application provides an configuration
interface for firewalld.

%prep
%setup -q

%build
%configure \
	--enable-sysconfig \
	--enable-rpmmacros \
	--with-systemd-unitdir=%{systemdunitdir} \
	--with-iptables=%{_sbindir}/iptables \
	--with-iptables-restore=%{_sbindir}/iptables-restore \
	--with-ip6tables=%{_sbindir}/ip6tables \
	--with-ip6tables-restore=%{_sbindir}/ip6tables-restore \
	--with-ebtables=%{_sbindir}/ebtables \
	--with-ebtables-restore=%{_sbindir}/ebtables-restore \
	--with-ipset=%{_sbindir}/ipset \
	PYTHON=%{__python3}

%install
rm -rf $RPM_BUILD_ROOT

# Python 2 library, in case anything still wants this
%{__make} -C src \
        install-nobase_dist_pythonDATA \
	pythondir=%{py_sitescriptdir} \
	pyexecdir=%{py_sitescriptdir} \
        PYTHON=%{__python} \
        DESTDIR=$RPM_BUILD_ROOT

%{__make} install \
	pythondir=%{py3_sitescriptdir} \
	pyexecdir=%{py3_sitescriptdir} \
	PYTHON=%{__python3} \
	DESTDIR=$RPM_BUILD_ROOT

%find_lang %{name} --all-name

desktop-file-install --delete-original \
	--dir $RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart \
	$RPM_BUILD_ROOT%{_sysconfdir}/xdg/autostart/firewall-applet.desktop

desktop-file-install --delete-original \
	--dir $RPM_BUILD_ROOT%{_desktopdir} \
	$RPM_BUILD_ROOT%{_desktopdir}/firewall-config.desktop

install -d $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/zones/

%{__rm} $RPM_BUILD_ROOT%{_prefix}/lib/firewalld/ipsets/README.md

%{__sed} -E -i -e '1s,#!\s*/usr/bin/env\s+python(\s|$),#!%{__python3}\1,' \
	-e '1s,#!\s*/usr/bin/python(\s|$),#!%{__python3}\1,' $RPM_BUILD_ROOT{%{_sbindir},%{_bindir}}/*

%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir}/firewall
%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir}/firewall

for module in ""  "/config" "/core" "/core/io" "/server"  ; do
    %{__python3} -m compileall -l -d %{py3_sitescriptdir}/firewall$module $RPM_BUILD_ROOT%{py3_sitescriptdir}/firewall$module
    %{__python3} -O -m compileall -l -d %{py3_sitescriptdir}/firewall$module $RPM_BUILD_ROOT%{py3_sitescriptdir}/firewall$module
done
%{__python3} -m compileall -l -d %{_datadir}/firewalld $RPM_BUILD_ROOT%{_datadir}/firewalld
%{__python3} -O -m compileall -l -d %{_datadir}/firewalld $RPM_BUILD_ROOT%{_datadir}/firewalld

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post firewalld.service

%preun
%systemd_preun firewalld.service

%postun
%systemd_reload firewalld.service

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

%files -f %{name}.lang
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/firewalld
%attr(755,root,root) %{_bindir}/firewall-cmd
%attr(755,root,root) %{_bindir}/firewall-offline-cmd
%{bash_compdir}/firewall-cmd
%dir %{_prefix}/lib/firewalld
%dir %{_prefix}/lib/firewalld/helpers
%{_prefix}/lib/firewalld/helpers/*.xml
%dir %{_prefix}/lib/firewalld/icmptypes
%{_prefix}/lib/firewalld/icmptypes/*.xml
%dir %{_prefix}/lib/firewalld/policies
%{_prefix}/lib/firewalld/policies/*.xml
%dir %{_prefix}/lib/firewalld/services
%{_prefix}/lib/firewalld/services/*.xml
%dir %{_prefix}/lib/firewalld/zones
%{_prefix}/lib/firewalld/zones/*.xml
%dir %attr(750,root,root) %dir %{_sysconfdir}/firewalld
%config(noreplace) %{_sysconfdir}/firewalld/firewalld.conf
%attr(750,root,root) %dir %{_sysconfdir}/firewalld/icmptypes
%attr(750,root,root) %dir %{_sysconfdir}/firewalld/services
%attr(750,root,root) %dir %{_sysconfdir}/firewalld/zones
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/firewalld/lockdown-whitelist.xml
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/firewalld
%config(noreplace) %{_sysconfdir}/logrotate.d/firewalld
%config(noreplace) %{_sysconfdir}/modprobe.d/firewalld-sysctls.conf
%{systemdunitdir}/firewalld.service
%{_datadir}/dbus-1/system.d/FirewallD.conf
%{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.desktop.policy.choice
%{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.server.policy.choice
%{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy
%dir %{_datadir}/firewalld
%{_datadir}/%{name}/testsuite
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

%files -n python3-firewall
%defattr(644,root,root,755)
%{py3_sitescriptdir}/firewall

%files -n firewall-applet
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/firewall-applet
%defattr(0644,root,root)
%{_sysconfdir}/xdg/autostart/firewall-applet.desktop
%{_iconsdir}/hicolor/*/apps/firewall-applet*.*
%{_mandir}/man1/firewall-applet*.1*
%dir %{_sysconfdir}/firewall
%config(noreplace) %{_sysconfdir}/firewall/applet.conf

%files -n firewall-config
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/firewall-config
%defattr(0644,root,root)
%{_datadir}/firewalld/__pycache__
%{_datadir}/firewalld/firewall-config.glade
%{_datadir}/firewalld/gtk3_*
%{_desktopdir}/firewall-config.desktop
%{_datadir}/metainfo/firewall-config.appdata.xml
%{_iconsdir}/hicolor/*/apps/firewall-config*.*
%{_datadir}/glib-2.0/schemas/org.fedoraproject.FirewallConfig.gschema.xml
%{_mandir}/man1/firewall-config*.1*
