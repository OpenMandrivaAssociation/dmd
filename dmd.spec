%bcond bootstrap_ldc	0

%define bits %{__isa_bits}
%define phobos %mklibname phobos-dmd

Summary:	D Programming Language compiler
Name:		dmd
Version:	2.112.0_beta.1
%define realver 2.112.0-beta.1
%define docver 2.111.0
Release:	1
License:	Boost
Group:		Development/Tools
URL:		https://dlang.org/
Source0:	https://github.com/dlang/%{name}/archive/refs/tags/v%{realver}.tar.gz#/%{name}-%{realver}.tar.gz
Source1:	https://github.com/dlang/phobos/archive/refs/tags/v%{realver}.tar.gz#/phobos-%{realver}.tar.gz
Source2:	https://downloads.dlang.org/releases/2.x/%{docver}/dmd.%{docver}.linux.tar.xz
Patch0:	21371.patch
Patch1:	21372.patch
Patch2:	no-gc-sections.patch
%if %{with bootstrap_ldc}
BuildRequires:	ldc
%else
BuildRequires:	dmd
%endif

%description
DMD is the reference compiler for the D programming language.

%package -n %{phobos}
Summary:	D Programming Language runtime
Group:		Development/Tools
License:	Boost

%description -n %{phobos}
DMD is the reference compiler for the D programming language.

This package contains the runtime library.

%package doc
Summary:	D Programming Language documentation
Group:		Development/Tools
License:	Boost
BuildArch:	noarch

%description doc
DMD is the reference compiler for the D programming language.

This package contains the documentation.

%files
%license LICENSE.txt
%{_bindir}/dmd
%{_sysconfdir}/dmd.conf
%{_mandir}/man1/*.1
%{_mandir}/man5/*.5
%{_libdir}/libphobos2.a
%{_includedir}/dlang/dmd/*

%files -n %{phobos}
%{_libdir}/libphobos2.so*

%files doc
%{_datadir}/d/html/*

%prep
ln -s %{name}-%{realver} %{name}
ln -s phobos-%{realver} phobos
%setup -b2 -n dmd2
%setup -b1 -n phobos-%{realver}
%autosetup -p1 -n %{name}-%{realver}

%build
%if %{with bootstrap_ldc}
export HOST_DMD=%{_bindir}/ldmd2
%else
export HOST_DMD=%{_bindir}/dmd
%endif

%if %{with bootstrap_ldc}
# XXX enable release mode later after figuring out the segfault
DFLAGS=
mkdir generated
$HOST_DMD -ofgenerated/build -g compiler/src/build.d
generated/build HOST_DMD="$HOST_DMD" CC=cc CXX=c++ DFLAGS="$DFLAGS" INSTALL_DIR=bootstrap install -v
cd druntime
make DMD=../generated/linux/release/%{bits}/dmd PIC=1
make install INSTALL_DIR=../bootstrap
cd ../../phobos
make DMD=../%{name}/generated/linux/release/%{bits}/dmd PIC=1
make install INSTALL_DIR=../%{name}/bootstrap
cd ../%{name}
rm -rf generated
rm -rf ../phobos/generated
export HOST_DMD=$(pwd)/bootstrap/linux/bin%{bits}/dmd
%endif

DFLAGS=
mkdir generated
$HOST_DMD -ofgenerated/build -g compiler/src/build.d -release -O
generated/build HOST_DMD="$HOST_DMD" CC=cc CXX=c++ BUILD=release ENABLE_RELEASE=1 DFLAGS="$DFLAGS" INSTALL_DIR=install install -v
cd druntime
make DMD=../generated/linux/release/%{bits}/dmd BUILD=release ENABLE_RELEASE=1 PIC=1
make install INSTALL_DIR=../install
cd ../../phobos
make DMD=../%{name}/generated/linux/release/%{bits}/dmd BUILD=release ENABLE_RELEASE=1 PIC=1
make install INSTALL_DIR=../%{name}/install
cd ../%{name}
make -C compiler/docs DMD=$HOST_DMD

install -d %{buildroot}%{_bindir}
install -D -m755 install/linux/bin%{bits}/dmd %{buildroot}%{_bindir}/dmd

install -d %{buildroot}%{_sysconfdir}
cat <<EOF > %{buildroot}%{_sysconfdir}/dmd.conf
[Environment32]
DFLAGS=-I%{_includedir}/dlang/dmd -L-L%{_prefix}/lib -L--export-dynamic -fPIC

[Environment64]
DFLAGS=-I%{_includedir}/dlang/dmd -L-L%{_prefix}/lib64 -L--export-dynamic -fPIC
EOF

install -d %{buildroot}%{_mandir}/man1/
cp generated/docs/man/man1/dmd.1 %{buildroot}%{_mandir}/man1/
install -d %{buildroot}%{_mandir}/man5/
cp generated/docs/man/man5/*.5 %{buildroot}%{_mandir}/man5/

install -d %{buildroot}%{_libdir}
cp -P install/linux/lib%{bits}/* %{buildroot}%{_libdir}/

install -d %{buildroot}%{_includedir}/dlang/dmd
cp -r install/src/phobos/* %{buildroot}%{_includedir}/dlang/dmd/
cp -r install/src/druntime/import/* %{buildroot}%{_includedir}/dlang/dmd/

install -d %{buildroot}%{_datadir}/d
cp -r ../dmd2/html %{buildroot}%{_datadir}/d/
