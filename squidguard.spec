%define _default_patch_fuzz 2
# $Id: squidGuard.spec,v 1.22 2009/10/26 13:30:17 limb Exp $

%define			_dbtopdir		%{_var}/%{name}
%define			_dbhomedir		%{_var}/%{name}/blacklists
%define			_cgibin			/var/www/cgi-bin

Name:			squidGuard
Version:		1.4
Release:		12
Summary:		Filter, redirector and access controller plugin for squid

Group:			System/Servers
License:		GPLv2

Source0:		http://www.squidguard.org/Downloads/squidGuard-%{version}.tar.gz
Source1:		squidGuard.logrotate
Source2:		http://squidguard.mesd.k12.or.us/blacklists.tgz
Source3:		http://cuda.port-aransas.k12.tx.us/squid-getlist.html

Source100:		squidGuard.conf
Source101:		update_squidguard_blacklists
Source104:		squidGuard.service
Source105:		transparent-proxying.service
Source106:		squidGuard-helper
Source107:		transparent-proxying-helper

Patch2:			squid-getlist.html.patch
Patch3:			squidGuard-perlwarning.patch
Patch5:			squidGuard-makeinstall.patch
Patch7:			squidGuard-1.4-20091015.patch
Patch8:			squidGuard-1.4-20091019.patch
Patch9:			squidGuard-1.4-db5.patch

URL:			http://www.squidguard.org/

BuildRequires:		byacc
BuildRequires:		bison
BuildRequires:          db5-devel
BuildRequires:		openldap-devel
BuildRequires:		flex
Provides:		squidguard = %{version}-%{release}
Requires:		squid
Requires(pre):	squid
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(postun): rpm-helper

%description
squidGuard can be used to 
- limit the web access for some users to a list of accepted/well known
  web servers and/or URLs only.
- block access to some listed or blacklisted web servers and/or URLs
  for some users.
- block access to URLs matching a list of regular expressions or words
  for some users.
- enforce the use of domainnames/prohibit the use of IP address in
  URLs.
- redirect blocked URLs to an "intelligent" CGI based info page.
- redirect unregistered user to a registration form.
- redirect popular downloads like Netscape, MSIE etc. to local copies.
- redirect banners to an empty GIF.
- have different access rules based on time of day, day of the week,
  date etc.
- have different rules for different user groups.
- and much more.. 

Neither squidGuard nor Squid can be used to
- filter/censor/edit text inside documents 
- filter/censor/edit embeded scripting languages like JavaScript or
  VBscript inside HTML

%prep
%setup -q
%{__cp} %{SOURCE3} .
%patch2 -p0
%patch3 -p2
%patch5	-p1
%patch7 -p0
%patch8 -p0
%patch9 -p1

%{__cp} %{SOURCE100} ./squidGuard.conf.k12ltsp.template
%{__cp} %{SOURCE101} ./update_squidguard_blacklists.k12ltsp.sh
# fix attribs
find . -type d -perm 0750 -exec chmod 755 {} \;
find . -type f -perm 0640 -exec chmod 644 {} \;

%build
%serverbuild_hardened
%configure2_5x \
	--with-sg-config=%{_sysconfdir}/squid/squidGuard.conf \
	--with-sg-logdir=%{_var}/log/squidGuard \
	--with-sg-dbhome=%{_dbhomedir} \
	--with-ldap=yes
	
%make

pushd contrib
%make
popd

%install
#%{__make} DESTDIR=%{buildroot} install
# This broke as of 1.2.1.
%{__install} -p -D -m 0755 src/squidGuard %{buildroot}%{_bindir}/squidGuard

%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/squidGuard
%{__install} -p -D -m 0644 samples/sample.conf %{buildroot}%{_sysconfdir}/squid/squidGuard.conf
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_dbtopdir}/blacklists.tar.gz

# Don't use SOURCE3, but use the allready patched one #165689
%{__install} -p -D -m 0755 squid-getlist.html %{buildroot}%{_sysconfdir}/cron.daily/squidGuard

#%{__install} -p -D %{SOURCE200} %{buildroot}%{_sysconfdir}/selinux/targeted/src/policy/domains/program/squidGuard.te
#%{__install} -p -D %{SOURCE201} %{buildroot}%{_sysconfdir}/selinux/targeted/src/policy/file_contexts/program/squidGuard.fc

%{__install} -p -d %{buildroot}%{_cgibin}
%{__install} samples/squid*cgi %{buildroot}%{_cgibin}

%{__install} contrib/hostbyname/hostbyname %{buildroot}%{_bindir}
%{__install} contrib/sgclean/sgclean %{buildroot}%{_bindir}

#%{__install} -p -D -m 0755 %{SOURCE102} %{buildroot}%{_initrddir}/squidGuard
#%{__install} -p -D -m 0755 %{SOURCE103} %{buildroot}%{_initrddir}/transparent-proxying

%{__install} -p -D -m 0644 %{SOURCE104} %{buildroot}%{_unitdir}/squidGuard.service
%{__install} -p -D -m 0644 %{SOURCE105} %{buildroot}%{_unitdir}/transparent-proxying.service

%{__install} -p -D -m 0744 %{SOURCE106} %{buildroot}%{_bindir}/squidGuard-helper
%{__install} -p -D -m 0744 %{SOURCE107} %{buildroot}%{_bindir}/transparent-proxying-helper

#pushd %{buildroot}%{_dbhomedir}
tar xfz %{buildroot}%{_dbtopdir}/blacklists.tar.gz
#popd

sed -i "s,dest/adult/,blacklists/porn/,g" %{buildroot}%{_sysconfdir}/squid/squidGuard.conf

%{__install} -p -D -m 0644 samples/babel.* %{buildroot}%{_cgibin}

mkdir -p %{buildroot}%{_localstatedir}/log/squidGuard
mkdir -p %{buildroot}%{_localstatedir}/log/squid
ln -s ../squidGuard/squidGuard.log  %{buildroot}%{_localstatedir}/log/squid/squidGuard.log

%pre
chown -R squid:squid %{buildroot}%{_localstatedir}/log/squidGuard

%post
%_post_service %{name}


echo "WARNING !!! WARNING !!! WARNING !!! WARNING !!!"
echo ""
echo "Modify the following line in the /etc/squid/squid.conf file:"
echo "url_rewrite_program /usr/bin/squidGuard -c /etc/squid/squidGuard.conf"

%preun
%_preun_service %{name}

%files
%doc samples/*.conf
%doc samples/*.cgi
%doc samples/dest/blacklists.tar.gz
%doc COPYING GPL 
%doc doc/*.txt doc/*.html doc/*.gif
%doc squidGuard.conf.k12ltsp.template
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/squid/squidGuard.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/squidGuard
%config(noreplace) %{_sysconfdir}/cron.daily/squidGuard
%{_dbtopdir}/
#%{_sysconfdir}/selinux/targeted/src/policy/domains/program/squidGuard.te
#%{_sysconfdir}/selinux/targeted/src/policy/file_contexts/program/squidGuard.fc
%attr(0755,root,root) %{_cgibin}/*-simple*.cgi
%{_cgibin}/squidGuard.cgi
%{_cgibin}/babel.*
%{_unitdir}/squidGuard.service
%{_unitdir}/transparent-proxying.service
%{_localstatedir}/log/squidGuard
%{_localstatedir}/log/squid/squidGuard.log
