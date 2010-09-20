%define major 1
%define libname %mklibname %{name}_ %{major}
%define develname %mklibname %{name} -d

%define buildpdf 0

Summary:	Extremely powerful file compression utility
Name:		bzip2
Version:	1.0.6
Release:	%mkrel 1
License:	BSD
Group:		Archiving/Compression
URL:		http://www.bzip.org/index.html
Source0:	http://www.bzip.org/%{version}/%{name}-%{version}.tar.gz
Source1:	bzgrep
Source2:	bzme
Source3:	bzme.1
Patch0:		bzip2-1.0.6-makefile.diff
Requires:	mktemp
Requires:	%{libname} = %{version}-%{release}
%if %buildpdf
BuildRequires:	tetex-dvips
BuildRequires:	tetex-latex
%endif
BuildRequires:	texinfo
BuildRequires:	libtool
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Bzip2 compresses files using the Burrows-Wheeler block-sorting text
compression algorithm, and Huffman coding. Compression is generally
considerably better than that achieved by more conventional LZ77/LZ78-based
compressors, and approaches the performance of the PPM family of statistical
compressors.

The command-line options are deliberately very similar to those of GNU Gzip,
but they are not identical.

%package -n %{libname}
Summary:	Libraries for developing apps which will use bzip2
Group:		System/Libraries

%description -n	%{libname}
Library of bzip2 functions, for developing apps which will use the
bzip2 library (aka libz2).

%package -n %{develname}
Summary:	Header files for developing apps which will use bzip2
Group:		Development/C
Requires:	%{libname} = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Obsoletes:	%{mklibname bzip2_ 1 -d} < 1.0.5-3
Provides:	%{mklibname bzip2_ 1 -d}

%description -n	%{develname}
Header files and static library of bzip2 functions, for developing apps which
will use the bzip2 library (aka libz2).

%prep

%setup -q
%patch0 -p1 -b .makefile

echo "lib = %{_lib}" >> config.in
echo "CFLAGS = %{optflags}" >> config.in
echo "LDFLAGS = %{ldflags}" >> config.in

cp %{SOURCE1} bzgrep
cp %{SOURCE2} bzme
cp %{SOURCE3} bzme.1

%build
%make -f Makefile-libbz2_so
%make

%if %buildpdf
texi2dvi --pdf manual.texi
%endif

%install
rm -rf %{buildroot}

%makeinstall_std

install -m0755 bzme %{buildroot}%{_bindir}/
install -m0755 bzgrep %{buildroot}%{_bindir}/
install -m0644 bzgrep.1 %{buildroot}%{_mandir}/man1/

cat > %{buildroot}%{_bindir}/bzless <<EOF
#!/bin/sh
%{_bindir}/bunzip2 -c "\$@" | %{_bindir}/less
EOF
chmod 755 %{buildroot}%{_bindir}/bzless
install -m 644 %{SOURCE3} %{buildroot}%{_mandir}/man1/

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,755)
%doc README LICENSE CHANGES
%{_bindir}/*
%{_mandir}/man1/*

%files -n %{libname}
%defattr(-,root,root,755)
%doc LICENSE
%{_libdir}/libbz2.so.%{major}*

%files -n %{develname}
%defattr(-,root,root,755)
%doc *.html LICENSE
%if %buildpdf
%doc manual.pdf
%endif
%{_libdir}/libbz2.a
%{_libdir}/libbz2.la
%{_libdir}/libbz2.so
%{_includedir}/*.h
