%define rname	squidGuard
%define prerel	beta

%if %{_use_internal_dependency_generator}
%define __noautoreq 'perl\\((.*)\\)'
%define __noautoprov 'perl\\((.*)\\)'
%else
%define _requires_exceptions perl(
%define _provides_exceptions perl(
%endif

Summary:	Filter, redirector and access controller plugin for Squid
Name:		squidguard
Version:	1.5
Release:	%{?prerel:0.%{prerel}.}2
License:	GPL
Group:		System/Servers
URL:		http://www.squidguard.org
Source0:	http://www.squidguard.org/Downloads/%{?prerel:Devel/}%{rname}-%{version}%{?prerel:-%{prerel}}.tar.gz
Source1:	%{rname}.conf.sample
Source2:	blacklists-readme
Source3:	%{rname}.cgi
Source4:	nulbanner.png
Source5:	blacklist-update
Source6:	%{rname}.logrotate
Patch0:		squidGuard-1.2.0.default_dir.patch
Patch1:		squidGuard-DESTDIR.diff
Patch2:		squidGuard-1.4-make_default_config_work.diff

#Debian patches
Patch11:	04_update-links-in-doc-files.patch
Patch12:	05_distclean-more-files.patch
Patch13:	06_move-setuserinfo-to-sg-y.patch
Patch15:	09_missing-content-after-percent-sign.patch
Patch16:	10_use-newer-ldapsearch-of-denis.patch
Patch17:	11_fix-for-clean-target-without-syslog.patch

BuildRequires:	bison 
BuildRequires:	db-devel
BuildRequires:	flex
BuildRequires:	openldap-devel
Requires:	squid 
Provides:	squidGuard = %{EVRD}

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

%setup -q -n %{rname}-%{version}%{?prerel:-%{prerel}}

# fix attribs
find . -type d -perm 0750 -exec chmod 755 {} \;
find . -type f -perm 0640 -exec chmod 644 {} \;

%patch0 -p1
%patch1 -p0
%patch2 -p0

%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1

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
echo "url_rewrite_program /usr/bin/squidGuard -c /etc/squid/squidGuard.conf"

%postun
if [ "$1" = "0" ]; then
    rm -rf %{_datadir}/%{rname}-%{version}
fi

%triggerun -- squidGuard <= 1.2.0-13mdv2007.1
mv %{_datadir}/%{rname}-%{version} %{_datadir}/%{rname}-%{version}.bk

%triggerpostun -- squidGuard <= 1.2.0-13mdv2007.1
mv %{_datadir}/%{rname}-%{version}.bk %{_datadir}/%{rname}-%{version}

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


%changelog
* Mon Apr 11 2011 Funda Wang <fwang@mandriva.org> 1.4-15mdv2011.0
+ Revision: 652495
- build with db 5.1

* Sat Oct 16 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4-14mdv2011.0
+ Revision: 585961
- P7 update, trying to fix #60197
- P7 update, trying to fix #60197

* Thu Aug 05 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4-13mdv2011.0
+ Revision: 566115
- P6 test
- P6 test

* Mon Aug 02 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4-12mdv2011.0
+ Revision: 565099
- try to fix #60197

* Mon Aug 02 2010 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4-11mdv2011.0
+ Revision: 565069
- try to fix #60197

* Fri Jan 01 2010 Oden Eriksson <oeriksson@mandriva.com> 1.4-11mdv2010.1
+ Revision: 484727
- rebuilt against bdb 4.8

* Mon Nov 23 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4-10mdv2010.1
+ Revision: 469175
- New P7 to let special chars such as !, &, ( and ) in strings

* Mon Nov 23 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4-9mdv2010.1
+ Revision: 469173
- New P6 for quotes support, this will let SG to accept non alphanumeric characters in parameters such as passwords

* Fri Nov 06 2009 Oden Eriksson <oeriksson@mandriva.com> 1.4-8mdv2010.1
+ Revision: 461160
- sync patches with 1.4-1.1mdv2009.1:
 - P2: make the default config work
 - P3: RBLDNS support
 - P4: security fix for CVE-2009-3700
 - P5: security fix for CVE-2009-3826
- it's "url_rewrite_program" now...

  + Luis Daniel Lucio Quiroz <dlucio@mandriva.org>
    - Rediff P4

* Tue Oct 20 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4-6mdv2010.0
+ Revision: 458468
- New P4: Fixes two bypass problems with URLs having a length closed to the defined MAX_BUF value (4096).
- release updated
- Fixes a buffer overflow problem and prevents squidGuard from going into emergency mode when overlong URLs are encountered (they can be perfectly legal)

* Tue Oct 06 2009 Oden Eriksson <oeriksson@mandriva.com> 1.4-4mdv2010.0
+ Revision: 454613
- fix #46152 (mandrake-linux.com broken url in the default cgi script)

* Fri Oct 02 2009 Oden Eriksson <oeriksson@mandriva.com> 1.4-3mdv2010.0
+ Revision: 452761
- fix build
- the lowercase mafia struck!
- the lowercase mafia struck again!

* Mon Jun 15 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4-2mdv2010.0
+ Revision: 386053
- rebuild

* Mon Jun 15 2009 Luis Daniel Lucio Quiroz <dlucio@mandriva.org> 1.4-1mdv2010.0
+ Revision: 386047
- Patch2 for RBLDNS

* Sat Mar 07 2009 Oden Eriksson <oeriksson@mandriva.com> 1.4-1mdv2009.1
+ Revision: 351703
- 1.4
- drop upstream patches
- rediffed one patch

* Mon Dec 15 2008 Oden Eriksson <oeriksson@mandriva.com> 1.3-2mdv2009.1
+ Revision: 314554
- rediff fuzzy patches
- rebuilt against db4.7

* Tue Aug 12 2008 Oden Eriksson <oeriksson@mandriva.com> 1.3-1mdv2009.0
+ Revision: 271105
- 1.3
- fix spec file, install mess...
- added 3 upstream patches

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 1.2.1-3mdv2009.0
+ Revision: 225473
- rebuild

* Fri Dec 21 2007 Oden Eriksson <oeriksson@mandriva.com> 1.2.1-2mdv2008.1
+ Revision: 136303
- rebuilt against new build deps

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Oct 11 2007 Oden Eriksson <oeriksson@mandriva.com> 1.2.1-1mdv2008.1
+ Revision: 96985
- 1.2.1

  + Thierry Vignaud <tv@mandriva.org>
    - s/Mandrake/Mandriva/

* Tue May 15 2007 Oden Eriksson <oeriksson@mandriva.com> 1.2.0-14mdv2008.0
+ Revision: 26874
- sync changes with the 1.2.0-13.1mdv2007.1 package:
  - fix the %%postun script and add some triggers so that
    /usr/share/squidGuard-[ver] doesn't get completely removed
    on an upgrade


* Wed Mar 07 2007 Oden Eriksson <oeriksson@mandriva.com> 1.2.0-13mdv2007.0
+ Revision: 134473
- Import squidGuard

* Wed Mar 07 2007 Oden Eriksson <oeriksson@mandriva.com> 1.2.0-13mdv2007.1
- bunzip patches

* Sun May 28 2006 Stefan van der Eijk <stefan@eijk.nu> 1.2.0-12mdk
- %%mkrel
- fix URL of source

* Sun Jan 01 2006 Mandriva Linux Team <http://www.mandrivaexpert.com/> 1.2.0-11mdk
- Rebuild

* Tue Apr 20 2004 Florin <florin@mandrakesoft.com> 1.2.0-10mdk
- fix the logrotate bug #9526

* Fri Apr 16 2004 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.2.0-9mdk
- fix build

