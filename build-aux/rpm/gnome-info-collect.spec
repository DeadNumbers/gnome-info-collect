%define name gnome-info-collect
%define version 1.0
%define unmangled_version 1.0
%define release 2

Summary: A simple utility to collect system information.
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{unmangled_version}.tar.gz
License: GPLv3+
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Vojtěch Staněk <vstanek@redhat.com>
Url: https://gitlab.gnome.org/vstanek/gnome-info-collect
Requires: python3 >= 3.6
Requires: python3-pip
Requires: python3-requests
Requires: python3-gobject
Requires: gnome-online-accounts
BuildRequires: python3

%description
A GNOME system and user data collection tool. The collected data is anonymous and is sent to a secure server. The data will be used only for the purpose of enhancing usability and user experience of GNOME.

%prep
%setup -n %{name}-%{unmangled_version} -q

%build
python3 -m compileall %{name}.py

%install
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/usr/lib/%{name}

cat > %{buildroot}%{_bindir}/%{name} <<-EOF
#!/bin/bash
/usr/bin/python /usr/lib/%{name}/%{name}.py
EOF

chmod 0755 %{buildroot}/%{_bindir}/%{name}

install -m 0644 ./%{name}.py* %{buildroot}/usr/lib/%{name}/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%license LICENSE
%dir /usr/lib/%{name}/
%{_bindir}/%{name}
/usr/lib/%{name}/%{name}.py*
%defattr(-,root,root)
