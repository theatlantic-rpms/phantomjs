%global _hardened_build 1

# See https://github.com/ariya/phantomjs/tree/master/src/qt for submodule info
%define hash_qtbase   b5cc008
%define hash_qtwebkit e7b7433

Summary:    Headless WebKit with JavaScript API
Name:       phantomjs
Version:    2.1.1
Release:    4%{?dist}
License:    BSD
Group:      Applications/Internet
Source0:    https://github.com/ariya/phantomjs/archive/%{version}.tar.gz
Source1:    https://github.com/Vitallium/qtbase/archive/%{hash_qtbase}.tar.gz
Source2:    https://github.com/Vitallium/qtwebkit/archive/%{hash_qtwebkit}.tar.gz

# support multilib optflags
Patch2: qtbase-multilib_optflags.patch

# fix QTBUG-35459 (too low entityCharacterLimit=1024 for CVE-2013-4549)
Patch4: qtbase-opensource-src-5.3.2-QTBUG-35459.patch

# unconditionally enable freetype lcdfilter support
Patch12: qtbase-opensource-src-5.2.0-enable_ft_lcdfilter.patch

# hack out largely useless (to users) warnings about qdbusconnection
# (often in kde apps), keep an eye on https://git.reviewboard.kde.org/r/103699/
Patch25: qtbase-opensource-src-5.5.1-qdbusconnection_no_debug.patch

# upstreamable patches
# support poll
# https://bugreports.qt-project.org/browse/QTBUG-27195
# NEEDS REBASE
Patch50: qt5-poll.patch

# Qt5 application crashes when connecting/disconnecting displays
# https://bugzilla.redhat.com/show_bug.cgi?id=1083664
Patch51: qtbase-opensource-src-5.5-disconnect_displays.patch
# Followup https://codereview.qt-project.org/#/c/138201/ adapted for 5.5
Patch52: https://smani.fedorapeople.org/138201.patch

## upstream patches
# workaround https://bugreports.qt-project.org/browse/QTBUG-43057
# 'make docs' crash on el6, use qSort instead of std::sort
Patch100: qtbase-opensource-src-5.4.0-QTBUG-43057.patch
Patch200:     phantomjs-2.1.1-adsecure1.patch
Patch201:     cookiejar-fix.patch

# smaller debuginfo s/-g/-g1/ (debian uses -gstabs) to avoid 4gb size limit
Patch303: qtwebkit-opensource-src-5.0.1-debuginfo.patch

# tweak linker flags to minimize memory usage on "small" platforms
Patch304: qtwebkit-opensource-src-5.2.0-save_memory.patch

# truly madly deeply no rpath please, kthxbye
Patch308: qtwebkit-opensource-src-5.2.1-no_rpath.patch


# Do not check any files in %%{_qt5_plugindir}/platformthemes/ for requires.
# Those themes are there for platform integration. If the required libraries are
# not there, the platform to integrate with isn't either. Then Qt will just
# silently ignore the plugin that fails to load. Thus, there is no need to let
# RPM drag in gtk2 as a dependency for the GTK+ 2 dialog support.
%global __requires_exclude_from ^%{_qt5_plugindir}/platformthemes/.*$

# workaround gold linker bug by not using it
# https://bugzilla.redhat.com/show_bug.cgi?id=1193044
#https://sourceware.org/bugzilla/show_bug.cgi?id=16992
%if 0%{?fedora} > 21
%define use_gold_linker -no-use-gold-linker
%endif

BuildRequires: flex
BuildRequires: bison
BuildRequires: gperf
BuildRequires: ruby
BuildRequires: python
BuildRequires: openssl-devel
BuildRequires: freetype-devel
BuildRequires: fontconfig-devel
BuildRequires: libicu-devel
BuildRequires: sqlite-devel
BuildRequires: libpng-devel
BuildRequires: libjpeg-devel


%description
PhantomJS is a headless WebKit with JavaScript API. It has fast and native
support for various web standards: DOM handling, CSS selector, JSON,
Canvas, and SVG. PhantomJS is created by Ariya Hidayat.


%prep
%setup -q -a1 -a2
# Move external sources into place
for dir in qtbase qtwebkit; do
  rmdir src/qt/${dir}
  mv ${dir}-* src/qt/${dir}
  # Trick checks into thinking this isn't a release, but a git clone
  mkdir src/qt/${dir}/.git
done

%patch200 -p1
%patch201 -p1

pushd src/qt/qtbase

%patch2 -p1 -b .multilib_optflags
# drop backup file(s), else they get installed too, http://bugzilla.redhat.com/639463
rm -fv mkspecs/linux-g++*/qmake.conf.multilib-optflags

%patch4 -p1 -b .QTBUG-35459
%patch12 -p1 -b .enable_ft_lcdfilter
%patch25 -p1 -b .qdbusconnection_no_debug

#patch50 -p1 -b .poll
%patch51 -p1 -b .disconnect_displays
%patch52 -p1 -b .138201

%if 0%{?rhel} == 6
%patch100 -p1 -b .QTBUG-43057
%endif

# drop -fexceptions from $RPM_OPT_FLAGS
RPM_OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed 's|-fexceptions||g'`

%define platform linux-g++

sed -i -e "s|-O2|$RPM_OPT_FLAGS|g" \
  mkspecs/%{platform}/qmake.conf

sed -i -e "s|^\(QMAKE_LFLAGS_RELEASE.*\)|\1 $RPM_LD_FLAGS|" \
  mkspecs/common/g++-unix.conf

# undefine QMAKE_STRIP (and friends), so we get useful -debuginfo pkgs (#1065636)
sed -i -e 's|^\(QMAKE_STRIP.*=\).*$|\1|g' mkspecs/common/linux.conf

popd

pushd src/qt/qtwebkit
%patch303 -p1 -b .debuginfo
%patch304 -p1 -b .save_memory
%patch308 -p1 -b .no_rpath
popd


%build
pushd src/qt/qtbase

./configure -v \
  -confirm-license \
  -opensource \
  -prefix . \
  -release \
  -static \
  -no-dbus \
  -no-opengl \
  -no-audio-backend \
  -fontconfig \
  -no-gstreamer \
  -no-journald \
  -no-qml-debug \
  -no-sql-db2 \
  -no-sql-ibase \
  -no-sql-mysql \
  -no-sql-oci \
  -no-sql-odbc \
  -no-sql-psql \
  -no-sql-sqlite \
  -no-sql-sqlite2 \
  -no-sql-tds \
  -no-xcb-xlib \
  -no-tslib \
  -iconv \
  -icu \
  -nomake examples \
  -nomake tests \
  -no-pch \
  -no-rpath \
  -no-separate-debug-info \
%ifarch %{ix86}
  -no-sse2 \
%endif
  -no-strip \
%ifarch %{ix86} x86_64
  -reduce-relocations \
%endif
  -qt-harfbuzz \
  -qt-libjpeg \
  -qt-libpng \
  -qt-pcre \
  -qt-zlib \
  %{?use_gold_linker} \
  -D QT_NO_GRAPHICSVIEW \
  -D QT_NO_GRAPHICSEFFECT \
  -D QT_NO_STYLESHEET \
  -D QT_NO_STYLE_CDE \
  -D QT_NO_STYLE_CLEANLOOKS \
  -D QT_NO_STYLE_MOTIF \
  -D QT_NO_STYLE_PLASTIQUE \
  -D QT_NO_PRINTPREVIEWDIALOG \
  -qpa phantom \
  -openssl \
  -openssl-linked \
  -no-openvg \
  -no-eglfs \
  -no-egl \
  -no-glib \
  -no-gtkstyle \
  -no-cups \
  -no-sm \
  -no-xinerama \
  -no-xkb \
  -no-xcb \
  -no-kms \
  -no-linuxfb \
  -no-directfb \
  -no-mtdev \
  -no-libudev \
  -no-evdev \
  -no-pulseaudio \
  -no-alsa \
  -no-feature-PRINTPREVIEWWIDGET \
  -qt-freetype

make %{?_smp_mflags}

popd

pushd src/qt/qtwebkit

SQLITE3SRCDIR=../qtbase/src/3rdparty/sqlite \
../qtbase/bin/qmake . \
WEBKIT_CONFIG-=build_tests \
WEBKIT_CONFIG-=build_webkit2 \
WEBKIT_CONFIG-=have_glx \
WEBKIT_CONFIG-=have_qtquick \
WEBKIT_CONFIG-=have_qtsensors \
WEBKIT_CONFIG-=have_qttestlib \
WEBKIT_CONFIG-=have_qttestsupport \
WEBKIT_CONFIG-=have_xcomposite \
WEBKIT_CONFIG-=have_xrender \
WEBKIT_CONFIG-=netscape_plugin_api \
WEBKIT_CONFIG-=use_gstreamer \
WEBKIT_CONFIG-=use_gstreamer010 \
WEBKIT_CONFIG-=use_native_fullscreen_video \
WEBKIT_CONFIG-=use_webp \
WEBKIT_CONFIG-=video \
WEBKIT_CONFIG-=web_audio \
WEBKIT_TOOLS_CONFIG-=build_imagediff \
WEBKIT_TOOLS_CONFIG-=build_minibrowser \
WEBKIT_TOOLS_CONFIG-=build_qttestsupport \
WEBKIT_TOOLS_CONFIG-=build_test_npapi \
WEBKIT_TOOLS_CONFIG-=build_wtr
make %{?_smp_mflags}

popd

./src/qt/qtbase/bin/qmake .
make %{?_smp_mflags}


%install
install -D -p -m 0755 bin/phantomjs %{buildroot}%{_bindir}/phantomjs


%files
%defattr(-,root,root,0755)
%doc CONTRIBUTING.md ChangeLog LICENSE.BSD README.md examples
%{_bindir}/phantomjs


%changelog
* Sun Jun 18 2017 Frankie Dintino <fdintino@theatlantic.com> 2.1.1-4
- Retain useful debuginfo when building qt libs

* Tue Jul 19 2016 Matthias Saou <matthias@saou.eu> 2.1.1-1
- Update to 2.1.1.

* Wed Mar 23 2016 Matthias Saou <matthias@saou.eu> 2.0.0-6
- Update patch to adsecure2.

* Wed Mar  9 2016 Matthias Saou <matthias@saou.eu> 2.0.0-5
- Update patch, now renamed to 'adsecure' and include that in the release.

* Tue Feb 16 2016 Matthias Saou <matthias@saou.eu> 2.0.0-4
- Update save patch.

* Tue Feb  9 2016 Matthias Saou <matthias@saou.eu> 2.0.0-3
- Include save patch.

* Mon Aug 10 2015 Matthias Saou <matthias@saou.eu> 2.0.0-2
- Spec file cleanup.

* Sat May 9 2015 Frankie Dintino <fdintino@gmail.com>
- updated to version 2.0, added BuildRequires directives

* Fri Apr 18 2014 Eric Heydenberk <heydenberk@gmail.com>
- add missing filenames for examples to files section

* Tue Apr 30 2013 Eric Heydenberk <heydenberk@gmail.com>
- add missing filenames for examples to files section

* Wed Apr 24 2013 Robin Helgelin <lobbin@gmail.com>
- updated to version 1.9

* Thu Jan 24 2013 Matthew Barr <mbarr@snap-interactive.com>
- updated to version 1.8

* Thu Nov 15 2012 Jan Schaumann <jschauma@etsy.com>
- first rpm version
