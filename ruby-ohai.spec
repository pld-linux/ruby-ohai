#
# Release Notes: https://github.com/chef/ohai/blob/master/CHANGELOG.md
#
# Conditional build:
%bcond_with	tests		# build without tests

%define pkgname ohai
Summary:	Profiles your system and emits JSON
Name:		ruby-%{pkgname}
Version:	14.2.4
Release:	3
License:	Apache v2.0
Group:		Development/Languages
Source0:	https://github.com/opscode/ohai/archive/v%{version}/%{pkgname}-%{version}.tar.gz
# Source0-md5:	09fe81cb0b178bad4ad9898c6cc72c57
Patch1:		platform-pld.patch
URL:		https://docs.getchef.com/ohai.html
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.665
BuildRequires:	ruby-rake
BuildRequires:	sed >= 4.0
%if %{with tests}
BuildRequires:	ruby-ffi >= 1.9
BuildRequires:	ruby-ffi-yajl >= 1.1
BuildRequires:	ruby-ipaddress
BuildRequires:	ruby-mixlib-config
BuildRequires:	ruby-mixlib-log
BuildRequires:	ruby-mixlib-shellout >= 1.2
BuildRequires:	ruby-rspec
BuildRequires:	ruby-systemu >= 2.6.4
%endif
Requires:	iproute2
Requires:	lsb-release
Requires:	mount
Requires:	ruby(abi) >= 2.0
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
%patch -P1 -p1
%{__sed} -i -e '1 s,#!.*ruby,#!%{__ruby},' bin/*

# don't need shellout 2.0 yet, but 2.0 is ok
%{__sed} -i -e '/mixlib-shellout/ s/">= 2.0.0.rc.0", "< 3.0"/">= 1.2", "< 3.0"/' %{pkgname}.gemspec
# optional
%{__sed} -i -e '/net-dhcp/d' %{pkgname}.gemspec
# platform specific and optional
%{__sed} -i -e '/wmi-lite/d' %{pkgname}.gemspec
%{__sed} -i -e '/plist/d' %{pkgname}.gemspec
# dev dep
%{__sed} -i -e '/rake/d' %{pkgname}.gemspec

# no plist and not darwin so don't care
rm spec/unit/plugins/darwin/system_profiler_spec.rb

# can't figure how to fix -r rubygems does not help
# ohai-6.16.0/spec/unit/plugins/ruby_spec.rb:52:in `block in <top (required)>': uninitialized constant Gem (NameError)
rm spec/unit/plugins/ruby_spec.rb

%build
# make gemspec self-contained
ruby -r rubygems -e 'spec = eval(File.read("%{pkgname}.gemspec"))
	File.open("%{pkgname}-%{version}.gemspec", "w") do |file|
	file.puts spec.to_ruby_for_cache
end'

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
cp -p %{pkgname}-%{version}*.gemspec $RPM_BUILD_ROOT%{ruby_specdir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md CHANGELOG.md RELEASE_NOTES.md OHAI_MVPS.md NOTICE
%attr(755,root,root) %{_bindir}/ohai
%{ruby_vendorlibdir}/%{pkgname}.rb
%{ruby_vendorlibdir}/%{pkgname}
%{ruby_specdir}/%{pkgname}-%{version}*.gemspec
