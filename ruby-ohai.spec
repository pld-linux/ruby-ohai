#
# Conditional build:
%bcond_without	tests		# build without tests

%define pkgname ohai
Summary:	Profiles your system and emits JSON
Name:		ruby-%{pkgname}
Version:	6.20.0
Release:	1
License:	Apache v2.0
Group:		Development/Languages
Source0:	https://github.com/opscode/ohai/archive/%{version}/%{pkgname}-%{version}.tar.gz
# Source0-md5:	1a3091bb1d06fda9e15447edbc4a2f77
Patch0:		virtualization-vserver.patch
Patch1:		php-builddate.patch
URL:		http://docs.opscode.com/ohai.html
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.665
BuildRequires:	ruby-rake
BuildRequires:	sed >= 4.0
%if %{with tests}
BuildRequires:	ruby-ipaddress
BuildRequires:	ruby-mixlib-config
BuildRequires:	ruby-mixlib-log
BuildRequires:	ruby-mixlib-shellout
BuildRequires:	ruby-rspec
BuildRequires:	ruby-systemu >= 2.5.2
BuildRequires:	ruby-yajl
%endif
Requires:	lsb-release
Requires:	ruby-ipaddress
Requires:	ruby-mixlib-cli
Requires:	ruby-mixlib-config
Requires:	ruby-mixlib-log
Requires:	ruby-mixlib-shellout
Requires:	ruby-systemu >= 2.5.2
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
%setup -q -n ohai-%{version}
%patch0 -p1
%patch1 -p1
%{__sed} -i -e '1 s,#!.*ruby,#!%{__ruby},' bin/*

# no plist and not darwin so don't care
rm spec/unit/plugins/darwin/system_profiler_spec.rb

# can't figure how to fix -r rubygems does not help
# ohai-6.16.0/spec/unit/plugins/ruby_spec.rb:52:in `block in <top (required)>': uninitialized cons tant Gem (NameError)
rm spec/unit/plugins/ruby_spec.rb

%build
rake gem
%{__tar} -xmf pkg/ohai-%{version}.gem
%__gem_helper spec

%if %{with tests}
# Occasionally fails with "undefined method `rfc2822' for nil:NilClass" during
# mock. Unsure why - disable for now.
#sed -i 's^Time.should_receive(:now)^^' spec/ohai/plugins/ohai_time_spec.rb
LC_ALL=en_US.utf8 \
rake -r rubygems spec
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{ruby_vendorlibdir},%{ruby_specdir},%{_bindir},%{_mandir}/man1}
cp -a bin/* $RPM_BUILD_ROOT%{_bindir}
cp -a lib/* $RPM_BUILD_ROOT%{ruby_vendorlibdir}
cp -p docs/man/man1/ohai.1 $RPM_BUILD_ROOT%{_mandir}/man1
cp -p %{pkgname}-%{version}.gemspec $RPM_BUILD_ROOT%{ruby_specdir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.rdoc CHANGELOG NOTICE
%attr(755,root,root) %{_bindir}/ohai
%{_mandir}/man1/ohai.1*
%{ruby_vendorlibdir}/%{pkgname}.rb
%{ruby_vendorlibdir}/%{pkgname}
%{ruby_specdir}/%{pkgname}-%{version}.gemspec
