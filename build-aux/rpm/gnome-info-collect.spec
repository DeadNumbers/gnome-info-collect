%define name gnome-info-collect
%define version 1.0
%define release 4

Summary: A simple utility to collect system information.
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
Source0: %{name}-%{version}.tar.gz
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
BuildRequires: meson

%description
A GNOME system and user data collection tool. The collected data is anonymous and is sent to a secure server. The data will be used only for the purpose of enhancing usability and user experience of GNOME.

%prep
%setup -n %{name}-%{version} -q

%build
%meson

%install
%meson_install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%license LICENSE
%{_bindir}/%{name}
%defattr(-,root,root)
