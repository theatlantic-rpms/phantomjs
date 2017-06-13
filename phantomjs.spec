Name:       phantomjs
Version:    2.1.1
Release:    2%{?dist}

Summary:    a headless WebKit with JavaScript API
Group:      Utilities/Misc
License:    BSD
URL:        http://phantomjs.org/
Packager:   Frankie Dintino <fdintino@theatlantic.com>

Source0:    https://github.com/nkovacs/selenium-standalone-phantomjs/raw/62f2a2a56ddbce1c13218aabe60f516afdeffdd8/phantomjs
Source1:    README.md
Source2:    ChangeLog
Source3:    LICENSE.BSD
Source4:    third-party.txt

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
install -p -m 0644 %{SOURCE1} README.md
install -p -m 0644 %{SOURCE2} ChangeLog
install -p -m 0644 %{SOURCE3} LICENSE
install -p -m 0644 %{SOURCE4} third-party.txt

%files
%doc ChangeLog README.md
%license LICENSE third-party.txt
%{_bindir}/phantomjs

%changelog
* Thu Mar 09 2017 Frankie Dintino <fdintino@theatlantic.com>
- Add fix for setting cookies

* Thu Dec 08 2016 Frankie Dintino <fdintino@theatlantic.com>
- first rpm version
