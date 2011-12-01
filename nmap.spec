#TODO: stop using local copy of libdnet, once system distributed version supports sctp (grep sctp /usr/include/dnet.h)
Summary: Network exploration tool and security scanner
Name: nmap
Version: 5.21
Release: 3%{?dist}
# nmap is GPLv2
# zenmap is GPLv2 and LGPLv2+ (zenmap/higwidgets) and GPLv2+ (zenmap/radialnet)
# libdnet-stripped is BSD (advertising clause rescinded by the Univ. of California in 1999) with some parts as Public Domain (crc32)
# openssl is OpenSSL
# openssl and libdnet-striped is removed in %%prep section
License: GPLv2 and LGPLv2+ and GPLv2+ and BSD
Group: Applications/System
Source0: http://nmap.org/dist/%{name}-%{version}.tar.bz2
Source1: zenmap.desktop
Source2: zenmap-root.pamd
Source3: zenmap-root.consoleapps

#prevent possible race condition for shtool, rhbz#158996
Patch1: nmap-4.03-mktemp.patch

#don't suggest to scan microsoft
Patch2: nmap-4.52-noms.patch

#don't strip debuginfo
Patch3: nmap-4.68-nostrip.patch

URL: http://nmap.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Epoch: 2
BuildRequires: openssl-devel, gtk2-devel, lua-devel, libpcap-devel, pcre-devel
BuildRequires: desktop-file-utils, dos2unix

%define pixmap_srcdir zenmap/share/pixmaps

%description
Nmap is a utility for network exploration or security auditing.  It supports
ping scanning (determine which hosts are up), many port scanning techniques
(determine what services the hosts are offering), and TCP/IP fingerprinting
(remote host operating system identification). Nmap also offers flexible target
and port specification, decoy scanning, determination of TCP sequence
predictability characteristics, reverse-identd scanning, and more.

%package frontend
Summary: The GTK+ front end for nmap
Group: Applications/System
Requires: nmap = %{epoch}:%{version} gtk2 python >= 2.5 pygtk2 usermode
BuildRequires: python >= 2.5 python-devel pygtk2-devel libpng-devel
BuildArch: noarch
%description frontend
This package includes zenmap, a GTK+ front end for nmap. The nmap package must
be installed before installing nmap front end.

%prep
%setup -q
%patch1 -p1 -b .mktemp
%patch2 -p1 -b .noms
%patch3 -p1 -b .nostrip

#be sure we're not using tarballed copies of some libraries
rm -rf liblua libpcap libpcre macosx mswin32

#fix locale dir
mv zenmap/share/zenmap/locale zenmap/share
sed -i -e "s|^locale_dir =.*$|locale_dir = os.path.join('share','locale')|" \
 -e 's|join(self.install_data, data_dir)|join(self.install_data, "share")|' zenmap/setup.py
sed -i 's|^LOCALE_DIR = .*|LOCALE_DIR = join(prefix, "share", "locale")|' zenmap/zenmapCore/Paths.py


%build
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"
%configure  --with-libpcap=/usr
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install
rm -f $RPM_BUILD_ROOT%{_bindir}/uninstall_zenmap

#use consolehelper
rm -f $RPM_BUILD_ROOT%{_datadir}/applications/zenmap*.desktop
rm -f $RPM_BUILD_ROOT%{_datadir}/zenmap/su-to-zenmap.sh
ln -s consolehelper $RPM_BUILD_ROOT%{_bindir}/zenmap-root
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d \
	$RPM_BUILD_ROOT%{_sysconfdir}/security/console.apps
install -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/zenmap-root
install -m 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/security/console.apps/zenmap-root

cp docs/zenmap.1 $RPM_BUILD_ROOT%{_mandir}/man1/
gzip $RPM_BUILD_ROOT%{_mandir}/man1/* || :
pushd $RPM_BUILD_ROOT%{_mandir}/man1
ln -s zenmap.1.gz nmapfe.1.gz
ln -s zenmap.1.gz xnmap.1.gz
popd

desktop-file-install --vendor nmap \
	--dir $RPM_BUILD_ROOT%{_datadir}/applications \
	--add-category X-Red-Hat-Base \
	%{SOURCE1};

#for .desktop and app icon
mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/48x48/apps
ln -s ../../../../zenmap/pixmaps/zenmap.png $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/48x48/apps

# fix end-of-line
pushd $RPM_BUILD_ROOT
for fe in ./%{python_sitelib}/zenmapCore/Paths.py
do
  dos2unix <$fe >$fe.new
  touch -r $fe $fe.new
  mv -f $fe.new $fe
done
popd

%find_lang nmap --with-man
%find_lang zenmap

%clean
rm -rf $RPM_BUILD_ROOT

%files -f nmap.lang
%defattr(-,root,root)
%doc COPYING*
%doc docs/README
%doc docs/nmap.usage.txt
%{_bindir}/nmap
%{_bindir}/ncat
%{_bindir}/ndiff
%{_mandir}/man1/ndiff.1.gz
%{_mandir}/man1/nmap.1.gz
%{_mandir}/man1/ncat.1.gz
%{_datadir}/nmap
%{_datadir}/ncat

%files frontend -f zenmap.lang
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/pam.d/zenmap-root
%config(noreplace) %{_sysconfdir}/security/console.apps/zenmap-root
%{_bindir}/zenmap-root
%{_bindir}/zenmap
%{_bindir}/nmapfe
%{_bindir}/xnmap
%{python_sitelib}/*
%{_datadir}/applications/nmap-zenmap.desktop
%{_datadir}/icons/*
%{_datadir}/zenmap
%{_mandir}/man1/zenmap.1.gz
%{_mandir}/man1/nmapfe.1.gz
%{_mandir}/man1/xnmap.1.gz

%changelog
* Mon Jun 21 2010 Michal Hlavinka <mhlavink@redhat.com> - 2:5.21-3
- build -frontend as noarch

* Fri Jun 18 2010 Michal Hlavinka <mhlavink@redhat.com> - 2:5.21-2
- fix multilib issue

* Tue Jun 01 2010 Michal Hlavinka <mhlavink@redhat.com> - 2:5.21-1
- updated to 5.21
- mark localized man pages with %%lang.

* Tue Jan 12 2010 Michal Hlavinka <mhlavink@redhat.com> - 2:5.00-6
- use sqlite3 (instead of sqlite2)

* Mon Dec 01 2009 Michal Hlavinka <mhlavink@redhat.com> - 2:5.00-5
- spec cleanup

* Mon Nov 02 2009 Michal Hlavinka <mhlavink@redhat.com> - 2:5.00-4
- spec cleanup

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2:5.00-3
- rebuilt with new openssl

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:5.00-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 17 2009 Michal Hlavinka <mhlavink@redhat.com> - 2:5.0-1
- updated to 5.0

* Wed Jul 15 2009 Michal Hlavinka <mhlavink@redhat.com> - 2:4.90-0.RC1
- updated to 4.90RC1

* Thu Jun 18 2009 Michal Hlavinka <mhlavink@redhat.com> - 2:4.85-0.BETA10
- updated to 4.85beta10

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:4.76-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> - 2:4.76-3
- rebuild with new openssl

* Mon Dec 15 2008 Michal Hlavinka <mhlavink@redhat.com> - 2:4.77-2
- bump release for rebuild

* Mon Dec 15 2008 Michal Hlavinka <mhlavink@redhat.com> - 2:4.76-1
- new upstream version 4.76
- use consolehelper for root auth

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 2:4.68-4
- Rebuild for Python 2.6

* Mon Aug 11 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2:4.68-3
- add missing BuildRequires to use system libs rather than local copies
- really fix license tag

* Mon Aug 11 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2:4.68-2
- fix license tag

* Thu Jul 24 2008 Tomas Smetana <tsmetana@redhat.com> - 2:4.68-1
- new upstream version

* Mon May 12 2008 Tomas Smetana <tsmetana@redhat.com> - 2:4.62-1
- new upstream version

* Mon Feb 04 2008 Tomas Smetana <tsmetana@redhat.com> - 2:4.53-1
- new upstream version

* Mon Jan 07 2008 Tomas Smetana <tsmetana@redhat.com> - 2:4.52-2
- bump release because of build error

* Mon Jan 07 2008 Tomas Smetana <tsmetana@redhat.com> - 2:4.52-1
- new upstream version

* Wed Dec 05 2007 Tomas Smetana <tsmetana@redhat.com> - 2:4.20-6.1
- rebuild

* Wed Aug 22 2007 Harald Hoyer <harald@redhat.com> - 2:4.20-6
- changed license tag

* Fri Mar 23 2007 Harald Hoyer <harald@redhat.com> - 2:4.20-5
- fixed changelog versions

* Thu Mar 15 2007 Karsten Hopp <karsten@redhat.com> 2:4.20-4
- rebuild with current gtk2 to add png support (#232013)

* Tue Feb 27 2007 Harald Hoyer <harald@redhat.com> - 2:4.20-3
- specfile cleanup
- fixed Florian La Roche's patch

* Tue Jan 30 2007 Florian La Roche <laroche@redhat.com> - 2:4.20-2
- do not strip away debuginfo

* Tue Jan 09 2007 Florian La Roche <laroche@redhat.com> - 2:4.20-1
- version 4.20

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2:4.11-1.1
- rebuild

* Tue Jun 27 2006 Harald Hoyer <harald@redhat.com> - 2:4.11-1
- version 4.11

* Wed May 17 2006 Harald Hoyer <harald@redhat.de> 4.03-2
- added more build requirements (bug #191932)

* Wed May 10 2006 Karsten Hopp <karsten@redhat.de> 4.03-1
- update to 4.03, this fixes #184286
- remove duplicate menu entry in 'Internet' (#183056)
- fix possible tmpdir race condition during build (#158996)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2:4.00-1.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2:4.00-1.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Thu Feb 02 2006 Harald Hoyer <harald@redhat.com> - 2:4.00-1
- version 4.00

* Mon Dec 19 2005 Harald Hoyer <harald@redhat.com> - 2:3.95-1
- version 3.95

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Tue Nov 11 2005 Harald Hoyer <harald@redhat.com> - 2:3.93-3
- fixed wrong __attribute__ test

* Thu Nov 10 2005 Tomas Mraz <tmraz@redhat.com> - 2:3.93-2
- rebuilt against new openssl

* Tue Sep 13 2005 Harald Hoyer <harald@redhat.com> - 2:3.93-1
- version 3.93

* Wed Aug 03 2005 Harald Hoyer <harald@redhat.com> - 2:3.81-4
- removed references how to scan microsoft.com (bz #164962)
- finally got rid of gtk+-devel dependency

* Thu Apr 21 2005 Harald Hoyer <harald@redhat.com> - 2:3.81-3
- removed gtk+ requirement

* Thu Apr 21 2005 Harald Hoyer <harald@redhat.com> - 2:3.81-2
- fixed desktop file and added icons (bug #149157)

* Wed Mar 02 2005 Harald Hoyer <harald@redhat.com> - 2:3.81-1
- version 3.81

* Wed Feb 02 2005 Harald Hoyer <harald@redhat.com> - 2:3.78-2
- evil port of nmapfe to gtk2

* Fri Dec 17 2004 Harald Hoyer <harald@redhat.com> - 2:3.78-1
- version 3.78

* Mon Sep 13 2004 Harald Hoyer <harald@redhat.com> - 2:3.70-1
- version 3.70

* Tue Jul 13 2004 Harald Hoyer <harald@redhat.com> - 2:3.55-1
- new version

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Jan 29 2004 Harald Hoyer <harald@redhat.com> - 2:3.50-2
- added BuildRequires: openssl-devel, gtk+-devel, pcre-devel, libpcap

* Thu Jan 22 2004 Harald Hoyer <harald@redhat.com> - 2:3.50-1
- version 3.50

* Wed Oct  8 2003 Harald Hoyer <harald@redhat.de> 2:3.48-1
- version 3.48

* Tue Sep 23 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- allow disabling frontend if gtk1 is not available

* Mon Jul 30 2003 Harald Hoyer <harald@redhat.de> 2:3.30-1
- version 3.30

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Mon May 26 2003 Harald Hoyer <harald@redhat.de> 2:3.27-1
- version 3.27

* Mon May 12 2003 Harald Hoyer <harald@redhat.de> 2:3.20-2
- changed macro comments to double %% for changelog entries

* Mon Apr 14 2003 Harald Hoyer <harald@redhat.de> 2:3.20-1
- version 3.2

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Jan  9 2003 Harald Hoyer <harald@redhat.de> 3.0-3
- nmap-3.00-nowarn.patch added

* Mon Nov 18 2002 Tim Powers <timp@redhat.com>
- rebuild on all arches
- remove old desktop file from $$RPM_BUILD_ROOT so rpm won't complain

* Thu Aug  1 2002 Harald Hoyer <harald@redhat.de>
- version 3.0

* Mon Jul 29 2002 Harald Hoyer <harald@redhat.de> 2.99.2-1
- bumped version

* Fri Jul 26 2002 Harald Hoyer <harald@redhat.de> 2.99.1-2
- bumped version to 2.99RC1

* Fri Jul 19 2002 Florian La Roche <Florian.LaRoche@redhat.de>
- add an epoch

* Mon Jul  1 2002 Harald Hoyer <harald@redhat.de> 2.54.36-1
- removed desktop file
- removed "BETA" name from version
- update to BETA36

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Sun May 26 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed May 22 2002 Harald Hoyer <harald@redhat.de> 2.54BETA34-1
- update to 2.54BETA34

* Mon Mar 25 2002 Harald Hoyer <harald@redhat.com>
- more recent version (#61490)

* Mon Jul 23 2001 Harald Hoyer <harald@redhat.com>
- buildprereq for nmap-frontend (#49644)

* Sun Jul 22 2001 Heikki Korpela <heko@iki.fi>
- buildrequire gtk+ 

* Tue Jul 10 2001 Tim Powers <timp@redhat.com>
- fix bugs in desktop file (#48341)

* Wed May 16 2001 Tim Powers <timp@redhat.com>
- updated to 2.54BETA22

* Mon Nov 20 2000 Tim Powers <timp@redhat.com>
- rebuilt to fix bad dir perms

* Fri Nov  3 2000 Tim Powers <timp@redhat.com>
- fixed nmapdatadir in the install section, forgot lto include
  $RPM_BUILD_ROOT in the path

* Thu Nov  2 2000 Tim Powers <timp@redhat.com>
- update to nmap-2.54BETA7 to possibly fix bug #20199
- use the desktop file provided by the package instead of using my own
- patches in previous version are depreciated. Included in SRPM for
  reference only

* Mon Jul 24 2000 Prospector <prospector@redhat.com>
- rebuilt

* Mon Jul 10 2000 Tim Powers <timp@redhat.com>
- rebuilt

* Wed Jun 28 2000 Tim Powers <timp@redhat.com>
- rebuilt package

* Thu Jun 8 2000 Tim Powers <timp@redhat.com>
- fixed man pages so that they are in an FHS compliant location
- use %%makeinstall
- use predefined RPM macros wherever possible

* Tue May 16 2000 Tim Powers <timp@redhat.com>
- updated to 2.53
- using applnk now
- use %%configure, and %%{_prefix} where possible
- removed redundant defines at top of spec file

* Mon Dec 13 1999 Tim Powers <timp@redhat.com>
- based on origional spec file from
	http://www.insecure.org/nmap/index.html#download
- general cleanups, removed lots of commenrts since it madethe spec hard to
	read
- changed group to Applications/System
- quiet setup
- no need to create dirs in the install section, "make
	prefix=$RPM_BUILD_ROOT&{prefix} install" does this.
- using defined %%{prefix}, %%{version} etc. for easier/quicker maint.
- added docs
- gzip man pages
- strip after files have been installed into buildroot
- created separate package for the frontend so that Gtk+ isn't needed for the
	CLI nmap 
- not using -f in files section anymore, no need for it since there aren't that
	many files/dirs
- added desktop entry for gnome

* Sun Jan 10 1999 Fyodor <fyodor@dhp.com>
- Merged in spec file sent in by Ian Macdonald <ianmacd@xs4all.nl>

* Tue Dec 29 1998 Fyodor <fyodor@dhp.com>
- Made some changes, and merged in another .spec file sent in
  by Oren Tirosh <oren@hishome.net>

* Mon Dec 21 1998 Riku Meskanen <mesrik@cc.jyu.fi>
- initial build for RH 5.x
