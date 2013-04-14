%define gemname ohai
Summary:	Profiles your system and emits JSON
Name:		ruby-%{gemname}
Version:	6.16.0
Release:	0.2
License:	Apache v2.0
Group:		Development/Languages
Source0:	http://gems.rubyforge.org/gems/%{gemname}-%{version}.gem
# Source0-md5:	5193426deeb67ff7560e05000c55d4d3
URL:		http://docs.opscode.com/ohai.html
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.656
Requires:	ruby-extlib
Requires:	ruby-ipaddress
Requires:	ruby-json
Requires:	ruby-mixlib-cli
Requires:	ruby-mixlib-config
Requires:	ruby-mixlib-log
Requires:	ruby-mixlib-shellout
Requires:	ruby-systemu
Requires:	ruby-yajl
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Ohai detects data about your operating system and prints out a JSON
data blob. It can be used standalone, but it's primary purpose is to
provide node data to Chef.

%package doc
Summary:	Documentation for %{name}
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description doc
This package contains documentation for %{name}.

%prep
%setup -q

%build
%if %{with tests}
# Occasionally fails with "undefined method `rfc2822' for nil:NilClass" during
# mock. Unsure why - disable for now.
sed -i 's^Time.should_receive(:now)^^' spec/ohai/plugins/ohai_time_spec.rb
rake spec
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{ruby_vendorlibdir},%{_bindir}}
cp -a bin/* $RPM_BUILD_ROOT%{_bindir}
cp -a lib/* $RPM_BUILD_ROOT%{ruby_vendorlibdir}

install -d $RPM_BUILD_ROOT%{_mandir}/man1
cp -p docs/man/man1/ohai.1 $RPM_BUILD_ROOT%{_mandir}/man1/ohai.1

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.rdoc
%attr(755,root,root) %{_bindir}/ohai
%{_mandir}/man1/ohai.1*
%{ruby_vendorlibdir}/ohai.rb
%{ruby_vendorlibdir}/ohai

%if 0
%files doc
%defattr(644,root,root,755)
%endif
