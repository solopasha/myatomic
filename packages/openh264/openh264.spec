# To get the gmp-api commit to use, run:
# rm -rf gmp-api;make gmp-bootstrap;cd gmp-api;git rev-parse HEAD
%global commit1 e7d30b921df736a1121a0c8e0cf3ab1ce5b8a4b7
%global shortcommit1 %(c=%{commit1}; echo ${c:0:7})

# Filter out soname provides for the mozilla plugin
%global __provides_exclude_from ^%{_libdir}/mozilla/plugins/

## WARNING ##
#
# These builds can not end up in the main buildroot automatically for
# legal reasons.
#
# It needs to be built into dedicated openh264 tags with:
#
#    fedpkg build --target=f*-openh264
#
Name:           openh264
Version:        2.5.1
Release:        1%{?dist}
Summary:        H.264 codec library

License:        BSD-2-Clause
URL:            https://www.openh264.org/
Source0:        https://github.com/cisco/openh264/archive/%{version}/openh264-%{version}.tar.gz
Source1:        https://github.com/mozilla/gmp-api/archive/%{commit1}/gmp-api-%{shortcommit1}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  nasm

# Replace the stub package
Obsoletes:      noopenh264 < 1:0

%description
OpenH264 is a codec library which supports H.264 encoding and decoding. It is
suitable for use in real time applications such as WebRTC.



%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
# Replace the stub package
Obsoletes:      noopenh264-devel < 1:0

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package     -n mozilla-openh264
Summary:        H.264 codec support for Mozilla browsers
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       mozilla-filesystem%{?_isa}

%description -n mozilla-openh264
The mozilla-openh264 package contains a H.264 codec plugin for Mozilla
browsers.


%prep
%setup -q

# Extract gmp-api archive
tar -xf %{S:1}
mv gmp-api-%{commit1} gmp-api


%build
# Update the makefile with our build options
# Must be done in %%build in order to pick up correct LDFLAGS.
sed -i -e 's|^CFLAGS_OPT=.*$|CFLAGS_OPT=%{optflags}|' Makefile
sed -i -e 's|^PREFIX=.*$|PREFIX=%{_prefix}|' Makefile
sed -i -e 's|^LIBDIR_NAME=.*$|LIBDIR_NAME=%{_lib}|' Makefile
sed -i -e 's|^SHAREDLIB_DIR=.*$|SHAREDLIB_DIR=%{_libdir}|' Makefile
sed -i -e '/^CFLAGS_OPT=/i LDFLAGS=%{__global_ldflags}' Makefile

# First build the openh264 libraries
make %{?_smp_mflags}

# ... then build the mozilla plugin
make plugin %{?_smp_mflags}


%install
%make_install

# Install mozilla plugin
mkdir -p $RPM_BUILD_ROOT%{_libdir}/mozilla/plugins/gmp-gmpopenh264/system-installed
cp -a libgmpopenh264.so* gmpopenh264.info $RPM_BUILD_ROOT%{_libdir}/mozilla/plugins/gmp-gmpopenh264/system-installed/

mkdir -p $RPM_BUILD_ROOT%{_libdir}/firefox/defaults/pref
cat > $RPM_BUILD_ROOT%{_libdir}/firefox/defaults/pref/gmpopenh264.js << EOF
pref("media.gmp-gmpopenh264.autoupdate", false);
pref("media.gmp-gmpopenh264.version", "system-installed");
EOF

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/profile.d
cat > $RPM_BUILD_ROOT%{_sysconfdir}/profile.d/gmpopenh264.sh << 'EOF'
if [[ ":$MOZ_GMP_PATH:" != *":%{_libdir}/mozilla/plugins/gmp-gmpopenh264/system-installed:"* ]]; then
    MOZ_GMP_PATH="${MOZ_GMP_PATH}${MOZ_GMP_PATH:+:}%{_libdir}/mozilla/plugins/gmp-gmpopenh264/system-installed"
    export MOZ_GMP_PATH
fi
EOF

mkdir -p $RPM_BUILD_ROOT%{_datadir}/fish/vendor_conf.d
cat > $RPM_BUILD_ROOT%{_datadir}/fish/vendor_conf.d/gmpopenh264.fish << 'EOF'
set -x --path MOZ_GMP_PATH $MOZ_GMP_PATH
set dir %{_libdir}/mozilla/plugins/gmp-gmpopenh264/system-installed
if not contains $dir $MOZ_GMP_PATH
    set -p MOZ_GMP_PATH $dir
end
set -e dir
EOF

# Remove static libraries
rm $RPM_BUILD_ROOT%{_libdir}/*.a


%files
%license LICENSE
%doc README.md
%{_libdir}/libopenh264.so.7
%{_libdir}/libopenh264.so.%{version}

%files devel
%{_includedir}/wels/
%{_libdir}/libopenh264.so
%{_libdir}/pkgconfig/openh264.pc

%files -n mozilla-openh264
%{_sysconfdir}/profile.d/gmpopenh264.sh
%dir %{_libdir}/firefox
%dir %{_libdir}/firefox/defaults
%dir %{_libdir}/firefox/defaults/pref
%{_libdir}/firefox/defaults/pref/gmpopenh264.js
%{_libdir}/mozilla/plugins/gmp-gmpopenh264/
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/gmpopenh264.fish


%changelog
* Wed Mar 12 2025 Wim Taymans <wtaymans@redhat.com> - 2.5.1-1
- Update to 2.5.1

* Wed Feb 26 2025 Wim Taymans <wtaymans@redhat.com> - 2.6.0-1
- Update to 2.6.0
- Add patch to revert the Makefile major version increase.

* Sat Nov 09 2024 Kalev Lember <klember@redhat.com> - 2.5.0-1
- Update to 2.5.0

* Fri Feb 09 2024 Kalev Lember <klember@redhat.com> - 2.4.1-2
- Drop the gstreamer plugin as it's part of Fedora proper now

* Fri Feb 02 2024 Kalev Lember <klember@redhat.com> - 2.4.1-1
- Update to 2.4.1
- Update gstreamer plugin to 1.22.9

* Mon Dec 04 2023 Kalev Lember <klember@redhat.com> - 2.4.0-2
- Fix off by one regression in decoder
- Filter out soname provides for mozilla gmp plugin

* Fri Nov 24 2023 Kalev Lember <klember@redhat.com> - 2.4.0-1
- Update to 2.4.0
- Update gstreamer plugin to 1.22.7
- Obsolete noopenh264 stub package
- Use SPDX license identifiers

* Wed Nov 22 2023 NoisyCoil <noisycoil@tutanota.com> - 2.3.1-4
- Set MOZ_GMP_PATH for fish user shell
- Partially resolves: rhbz#2250527

* Thu Aug 17 2023 Dominik Mierzejewski <dominik@greysector.net> - 2.3.1-3
- Add Mozilla plugin path to MOZ_GMP_PATH instead of overriding unconditionally
- Resolves: rhbz#2225112

* Mon Mar 13 2023 Kalev Lember <klember@redhat.com> - 2.3.1-2
- Update gstreamer plugin to 1.22.1

* Thu Sep 29 2022 Kalev Lember <klember@redhat.com> - 2.3.1-1
- Update to 2.3.1

* Wed Aug 10 2022 Kalev Lember <klember@redhat.com> - 2.3.0-2
- Rebuild

* Mon Aug 01 2022 Kalev Lember <klember@redhat.com> - 2.3.0-1
- Update to 2.3.0
- Update gstreamer plugin to 1.20.3

* Wed Mar 16 2022 David King <amigadave@amigadave.com> - 2.2.0-1
- Update to 2.2.0
- Update gstreamer plugin to 1.20.0

* Tue Sep 07 2021 Kalev Lember <klember@redhat.com> - 2.1.1-3
- Update gstreamer plugin to 1.19.1

* Thu Feb 11 2021 Kalev Lember <klember@redhat.com> - 2.1.1-2
- Update gstreamer plugin to 1.18.2
- Remove totem supplements as totem has recommends on
  gstreamer1-plugin-openh264 instead

* Fri May 22 2020 Kalev Lember <klember@redhat.com> - 2.1.1-1
- Update to 2.1.1
- Add totem supplements to gstreamer1-plugin-openh264

* Tue Mar 10 2020 Kalev Lember <klember@redhat.com> - 2.1.0-1
- Update to 2.1.0
- Update gstreamer plugin to 1.16.2

* Mon Jun 17 2019 Kalev Lember <klember@redhat.com> - 2.0.0-1
- Update openh264 to 2.0.0
- Update gstreamer plugin to 1.16.0

* Fri Feb 22 2019 Kalev Lember <klember@redhat.com> - 1.8.0-3
- Update gstreamer plugin to 1.15.1

* Wed Sep 12 2018 Kalev Lember <klember@redhat.com> - 1.8.0-2
- Update gstreamer plugin to 1.14.2

* Wed Jun 27 2018 Kalev Lember <klember@redhat.com> - 1.8.0-1
- Update openh264 to 1.8.0
- Update gstreamer plugin to 1.14.1

* Tue Mar 06 2018 Kalev Lember <klember@redhat.com> - 1.7.0-6
- Update gstreamer plugin to 1.13.90

* Sat Dec 16 2017 Kalev Lember <klember@redhat.com> - 1.7.0-5
- Update gstreamer plugin to 1.12.4

* Tue Sep 19 2017 Kalev Lember <klember@redhat.com> - 1.7.0-4
- Update gstreamer plugin to 1.12.3

* Thu Jul 20 2017 Kalev Lember <klember@redhat.com> - 1.7.0-3
- Update gstreamer plugin to 1.12.2

* Tue Jun 20 2017 Kalev Lember <klember@redhat.com> - 1.7.0-2
- Update gstreamer plugin to 1.12.1

* Fri Jun 16 2017 Kalev Lember <klember@redhat.com> - 1.7.0-1
- Update openh264 to 1.7.0
- Update gstreamer plugin to 1.12.0

* Mon Mar 06 2017 Kalev Lember <klember@redhat.com> - 1.6.0-5
- Update gstreamer plugin to 1.10.4

* Mon Jan 30 2017 Kalev Lember <klember@redhat.com> - 1.6.0-4
- Update gstreamer plugin to 1.10.3

* Mon Dec 05 2016 Kalev Lember <klember@redhat.com> - 1.6.0-3
- Update gstreamer plugin to 1.10.2

* Fri Sep 02 2016 Kalev Lember <klember@redhat.com> - 1.6.0-2
- Update gstreamer plugin to 1.9.2

* Thu Aug 25 2016 Kalev Lember <klember@redhat.com> - 1.6.0-1
- Update openh264 to 1.6.0
- Update gstreamer plugin to 1.8.3

* Thu Apr 28 2016 Kalev Lember <klember@redhat.com> - 1.5.3-0.1.git2706e36
- Update openh264 to 1.5.3 git snapshot
- Update gstreamer plugin to 1.8.1

* Mon Mar 21 2016 Dennis Gilmore <dennis@ausil.us> - 1.5.2-0.4.git21e44bd
- move the mozila-openh264 definition before gstreamer1-plugin-openh264
- gstreamer1-plugin-openh264 redefines version and release messing up requires

* Mon Nov 30 2015 Kalev Lember <klember@redhat.com> - 1.5.2-0.3.git21e44bd
- Include the gstreamer plugin in gstreamer1-plugin-openh264 subpackage

* Thu Nov 26 2015 Kalev Lember <klember@redhat.com> - 1.5.2-0.2.git21e44bd
- Pass Fedora LDFLAGS to the build to get full relro (#1285338)

* Tue Nov 24 2015 Kalev Lember <klember@redhat.com> - 1.5.2-0.1.git21e44bd
- Initial Fedora packaging
