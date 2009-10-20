%define rname squidGuard

%define _requires_exceptions perl(
%define _provides_exceptions perl(

Summary:	Filter, redirector and access controller plugin for Squid
Name:		squidguard
Version:	1.4
Release:	%mkrel 5
License:	GPL
Group:		System/Servers
URL:		http://www.squidguard.org
Source0:	http://www.squidguard.org/Downloads/%{rname}-%{version}.tar.gz
Source1:	%{rname}.conf.sample
Source2:	blacklists-readme
Source3:	%{rname}.cgi
Source4:	nulbanner.png
Source5:	blacklist-update
Source6:	%{rname}.logrotate
Patch0:		squidGuard-1.2.0.default_dir.patch
Patch1:		squidGuard-DESTDIR.diff
Patch2:		squidGuard-1.4-dnsbl.patch
Patch3:		squidGuard-1.4-20091015.patch
BuildRequires:	bison 
BuildRequires:	db4-devel
BuildRequires:	flex
BuildRequires:	openldap-devel
Requires:	squid 
Provides:	squidGuard = %{version}
Obsoletes:	squidGuard
Buildroot:	%{_tmppath}/%{rname}-%{version}-%{release}-buildroot

%description
SquidGuard is a combined filter, redirector and access controller plugin for
Squid. It is free, very flexible, extremely fast, easily installed, portable.
SquidGuard can be used to 
- limit the web access for some users to a list of accepted/well known web
servers and/or URLs only. 
- block access to some listed or blacklisted web servers and/or URLs for
some users. 
- block access to URLs matching a list of regular expressions or words for
some users. 
- enforce the use of domainnames/prohibit the use of IP address in URLs. 
- redirect blocked URLs to an "intelligent" CGI based info page.
- redirect unregistered user to a registration form. 
- redirect popular downloads like Netscape, MSIE etc. to local copies. 
- redirect banners to an empty GIF.
- have different access rules based on time of day, day of the week, date
etc. 
- have different rules for different user groups. 

Neither squidGuard nor Squid can be used to 

- filter/censor/edit text inside documents 
- filter/censor/edit embeded scripting languages 
  like JavaScript or VBscript inside HTML 


%prep

%setup -q -n %{rname}-%{version}

# fix attribs
find . -type d -perm 0750 -exec chmod 755 {} \;
find . -type f -perm 0640 -exec chmod 644 {} \;

%patch0 -p1
%patch1 -p0
%patch2 -p1
%patch3 -p0 -b .20091015
cp %{SOURCE6} %{rname}.logrotate

%build
%serverbuild

%configure2_5x \
    --with-ldap \
    --with-sg-config=%{_sysconfdir}/squid/%{rname}.conf \
    --with-sg-logdir=/var/log/squidGuard \
    --with-sg-dbhome=%{_datadir}/%{rname}-%{version}/db

%make

%install
rm -rf %{buildroot}

Q=%{buildroot}%{_datadir}/%{rname}-%{version}

install -d %{buildroot}%{_sysconfdir}/squid
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}/var/log/squidGuard
install -d %{buildroot}/var/www/cgi-bin
install -d %{buildroot}%{_bindir}
install -d %{buildroot}%{_datadir}/%{rname}-%{version}/contrib
install -d %{buildroot}%{_datadir}/%{rname}-%{version}/db/{advertising,bannedsource,banneddestination}
install -d %{buildroot}%{_datadir}/%{rname}-%{version}/db/{timerestriction,lansource,privilegedsource}
install -d %{buildroot}%{_datadir}/%{rname}-%{version}/db/{porn,adult,audio-video,forums,hacking,redirector}
install -d %{buildroot}%{_datadir}/%{rname}-%{version}/db/{warez,ads,aggressive,drugs,gambling,publicite,violence}

%makeinstall_std SQUIDUSER="`id -nu`"

install -m0644 %{rname}.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{rname}

touch $Q/db/advertising/{domains,urls}
touch $Q/db/banneddestination/{domains,urls,expressions}
touch $Q/db/bannedsource/ips
touch $Q/db/lansource/lan
touch $Q/db/timerestriction/lan
touch $Q/db/privilegedsource/ips

# the blacklists default directories (Fabrice Pringent's one)
touch $Q/db/porn/{domains,urls,expressions}
touch $Q/db/adult/{domains,urls,expressions}
touch $Q/db/audio-video/{domains,urls}
touch $Q/db/forums/{domains,urls,expressions}
touch $Q/db/hacking/{domains,urls}
touch $Q/db/redirector/{domains,urls,expressions}
touch $Q/db/warez/{domains,urls}
touch $Q/db/ads/{domains,urls}
touch $Q/db/aggressive/{domains,urls}
touch $Q/db/drugs/{domains,urls}
touch $Q/db/gambling/{domains,urls}
touch $Q/db/publicite/{domains,urls,expressions}
touch $Q/db/violence/{domains,urls,expressions}

cd samples/dest/
tar xzf blacklists.tar.gz
cp -af blacklists/* $Q/db
cd -

cp -a contrib/hostbyname/hostbyname $Q/contrib/
cp -a contrib/sgclean/sgclean $Q/contrib/
cp -a contrib/squidGuardRobot/{squidGuardRobot,RobotUserAgent.pm} $Q/contrib/

cp -a samples/dest $Q/samples
cp -a samples/*{.conf,.cgi} $Q/samples

cp -a %{SOURCE2} .
cp -a %{SOURCE5} .

rm -rf $Q/test/test*.conf.*

# default config files
# log & error files
touch %{buildroot}/var/log/%{rname}/%{rname}.{log,error}
touch %{buildroot}/var/log/%{rname}/advertising.log

# conf file
install %{SOURCE1} %{buildroot}/etc/squid/%{rname}.conf.sample
cp -af %{SOURCE3} %{SOURCE4} %{buildroot}/var/www/cgi-bin
rm -rf %{buildroot}%{_datadir}/%{rname}-%{version}/samples/dest

# cleanup
rm -rf %{buildroot}%{_prefix}/squidGuard

# fix attribs
find %{buildroot} -type d -perm 0750 -exec chmod 755 {} \;
find %{buildroot} -type f -perm 0640 -exec chmod 644 {} \;

%preun
if [ $1 = 0 ] ; then
        rm -f /var/log/squidGuard/*
fi

%post
rm -rf `find %{_datadir}/%{rname}-%{version}/db |grep "\.db"`
%{_bindir}/%{rname} -c  %{_sysconfdir}/squid/%{rname}.conf.sample -C all 
for i in privilegedsource bannedsource timerestriction lansource banneddestination advertising; do
    rm -rf /usr/share/%{rname}-%{version}/db/$i/*.db 
done
chown -R squid:squid /usr/share/%{rname}-%{version}/db

echo "WARNING !!! WARNING !!! WARNING !!! WARNING !!!"
echo ""
echo "Modify the following line in the /etc/squid/squid.conf file:"
echo "redirect_program /usr/bin/squidGuard -c /etc/squid/squidGuard.conf"

%postun
if [ "$1" = "0" ]; then
    rm -rf %{_datadir}/%{rname}-%{version}
fi

%triggerun -- squidGuard <= 1.2.0-13mdv2007.1
mv %{_datadir}/%{rname}-%{version} %{_datadir}/%{rname}-%{version}.bk

%triggerpostun -- squidGuard <= 1.2.0-13mdv2007.1
mv %{_datadir}/%{rname}-%{version}.bk %{_datadir}/%{rname}-%{version}

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc COPYING GPL README README.LDAP ANNOUNCE CHANGELOG blacklists-readme doc/*.{html,gif,txt}
%config(noreplace) %{_sysconfdir}/squid/*
%config(noreplace) %{_sysconfdir}/logrotate.d/%{rname}
%{_bindir}/*
%attr(0755,apache,apache) /var/www/cgi-bin/*.cgi
%attr(0755,apache,apache) /var/www/cgi-bin/*.png
%{_datadir}/%{rname}-%{version}/contrib
%{_datadir}/%{rname}-%{version}/samples
%{_datadir}/%{rname}-%{version}/db
%dir %attr(-,squid,squid)/var/log/%{rname}
%attr(-,squid,squid)/var/log/%{rname}/*
