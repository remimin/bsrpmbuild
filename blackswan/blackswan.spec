%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%define gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**};

%global import_path     github.com/blackswan


Name:		blackswan	
Epoch:          1
Version:	0.1
Release:	1wocloud%{?dist}
Summary:	"Openstack Compute Instance HA Tool"

License: Personal Reserved
URL:	github.com/remimin/blackswan	
Source0: blackswan-%{upstream_version}.tar.gz

ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 %{arm}}
ExcludeArch: ppc64
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

Provides:      golang(%{import_path}/blackswan-server) = %{epoch}:%{version}-%{release}
Provides:      golang(%{import_path}/blackswan-watcher) = %{epoch}:%{version}-%{release}
Provides:      golang(%{import_path}/bsctl) = %{epoch}:%{version}-%{release}

%description 
%{summary}

%package -n blackswan-server
Summary: Blackswan server service monitor all compute nodes.

Requires: consul
Requires: ipmitool

%description -n blackswan-server
Blackswan server service monitor all compute nodes.

%package -n blackswan-watcher
Summary: Blackswan watcher service run on compute node, report compute node health.
Requires: consul

%description -n blackswan-watcher
Blackswan watcher service run on compute node, report compute node health.

%package -n bsctl
Summary: blackswan service command line

%description -n bsctl
blackswan service command line

%prep
#%setup -q
%setup -q

%build
export GO111MODULE=on
export GOPROXY=https://goproxy.io
mkdir -p %{gopath}/src/github.com
rm -f %{gopath}/src/github.com/blackswan
ln -s %{_builddir}/blackswan-%{upstream_version} %{gopath}/src/github.com/blackswan
%gobuild -o bin/blackswan %{gopath}/src/github.com/blackswan/main.go
%gobuild -o bin/bsctl %{gopath}/src/github.com/blackswan/cli.go

%install
#make install DESTDIR=%{buildroot}
# Setup directories
install -d -m 0755 %{buildroot}%{_sharedstatedir}/blackswan
install -d -m 0750 %{buildroot}%{_localstatedir}/log/blackswan

install -D -p -m 0755 bin/blackswan %{buildroot}%{_bindir}/blackswan
install -D -p -m 0755 bin/bsctl %{buildroot}%{_bindir}/bsctl
install -p -D -m 0644 etc/blackswan-server.service %{buildroot}%{_unitdir}/blackswan-server.service
install -p -D -m 0644 etc/blackswan-watcher.service %{buildroot}%{_unitdir}/blackswan-watcher.service

# Setup config example
install -p -D -m 0644 etc/server.json %{buildroot}%{_sysconfdir}/blackswan/server.json
install -p -D -m 0644 etc/watcher.json %{buildroot}%{_sysconfdir}/blackswan/watcher.json


# Install logrotate
install -p -D -m 0644 etc/blackswan.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/blackswan

%post -n blackswan-server
%systemd_post blackswan-server.service

%post -n blackswan-watcher
%systemd_post blackswan-watcher.service

%files -n blackswan-server
%{_bindir}/bsctl
%{_bindir}/blackswan
%{_unitdir}/blackswan-server.service
%dir %{_sysconfdir}/blackswan
%dir %{_localstatedir}/log/blackswan
%config(noreplace) %{_sysconfdir}/blackswan/server.json
%config(noreplace) %{_sysconfdir}/logrotate.d/blackswan

%files -n blackswan-watcher
%{_bindir}/bsctl
%{_bindir}/blackswan
%{_unitdir}/blackswan-watcher.service
%dir %{_sysconfdir}/blackswan
%dir %{_localstatedir}/log/blackswan
%config(noreplace) %{_sysconfdir}/blackswan/watcher.json
%config(noreplace) %{_sysconfdir}/logrotate.d/blackswan

%files -n bsctl
%{_bindir}/bsctl

%changelog
