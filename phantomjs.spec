%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}

Name:       phantomjs
Version:    2.1.1
Release:    2%{?dist}

Summary:    a headless WebKit with JavaScript API
Group:      Utilities/Misc
License:    BSD
URL:        http://phantomjs.org/
Packager:   Frankie Dintino <fdintino@theatlantic.com>

Source0:    https://github.com/nkovacs/selenium-standalone-phantomjs/raw/62f2a2a56ddbce1c13218aabe60f516afdeffdd8/phantomjs
Source1:    LICENSE.BSD
Source2:    README.md
Source3:    ChangeLog

Requires:   fontconfig

%description
PhantomJS is a headless WebKit with JavaScript API. It has fast and native
support for various web standards: DOM handling, CSS selector, JSON,
Canvas, and SVG. PhantomJS is created by Ariya Hidayat.

%prep
%setup -q -D -T -c

%install
install -p -d -m 0755 %{buildroot}%{_bindir}
install -p -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/phantomjs
install -p -d -m 0755 %{buildroot}%{_pkgdocdir}
install -p -m 0644 -t %{buildroot}%{_pkgdocdir} %{SOURCE1} %{SOURCE2} %{SOURCE3}

%files
%doc %dir %{_pkgdocdir}
%doc %{_pkgdocdir}/ChangeLog
%doc %{_pkgdocdir}/README.md
%license %{_pkgdocdir}/LICENSE.BSD
%{_bindir}/phantomjs

%changelog
* Thu Mar 09 2017 Frankie Dintino <fdintino@theatlantic.com>
- Add fix for setting cookies

* Thu Dec 08 2016 Frankie Dintino <fdintino@theatlantic.com>
- first rpm version
